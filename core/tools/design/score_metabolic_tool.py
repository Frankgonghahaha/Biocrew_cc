#!/usr/bin/env python3
"""
菌群互作强度评分工具
基于微生物互补性数据库计算物种间竞争/互补指数及 Δ
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError
from sqlalchemy.orm import sessionmaker

from core.tools.database.complementarity_model import (
    MicrobialComplementarity,
    init_database,
)


class ScoreMetabolicInput(BaseModel):
    """互作强度计算输入"""

    identification_json_path: Optional[str] = Field(
        default=None,
        description="IdentificationAgent 生成的 JSON 文件路径",
    )
    functional_microbes: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="直接传入的功能微生物列表（结构同 IdentificationAgent JSON）",
    )
    include_complements: bool = Field(
        default=True,
        description="是否将互补微生物也纳入互作计算",
    )
    only_positive_delta: bool = Field(
        default=False,
        description="是否仅保留 Δ>0 的记录",
    )
    top_n: Optional[int] = Field(
        default=None,
        description="按 Δ 值排序后返回的前 N 条结果（None 表示全部）",
    )

    @model_validator(mode="after")
    def validate_inputs(cls, values: "ScoreMetabolicInput") -> "ScoreMetabolicInput":
        path = values.identification_json_path
        fm = values.functional_microbes
        if not path and not fm:
            raise ValueError("必须提供 identification_json_path 或 functional_microbes。")
        if path:
            values.identification_json_path = str(Path(path).expanduser())
        return values


class ScoreMetabolicInteractionTool(BaseTool):
    """查询物种间互作强度的工具"""

    name: str = "ScoreMetabolicInteractionTool"
    description: str = (
        "基于 IdentificationAgent 结果，计算所有相关物种之间的互作指标，"
        "Δ=互补指数-竞争指数，可选仅保留正向互补记录，并返回 Result3_pair_Com_index 风格的数据。"
    )
    args_schema: type[BaseModel] = ScoreMetabolicInput

    def __init__(self) -> None:
        super().__init__()
        database_url = self._resolve_database_url()
        try:
            engine = init_database(database_url)
            Session = sessionmaker(bind=engine)
        except NoSuchTableError as exc:
            raise RuntimeError(
                "未能初始化 microbial_complementarity 表，请确认数据库已导入数据。"
            ) from exc
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"连接互补性数据库失败: {exc}") from exc
        object.__setattr__(self, "_engine", engine)
        object.__setattr__(self, "_Session", Session)

    @staticmethod
    def _resolve_database_url() -> str:
        db_type = os.getenv("DB_TYPE", "sqlite")
        if db_type == "postgresql":
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            name = os.getenv("DB_NAME")
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"
        return "sqlite:///complementarity.db"

    def _run(
        self,
        identification_json_path: Optional[str] = None,
        functional_microbes: Optional[List[Dict[str, Any]]] = None,
        include_complements: bool = True,
        only_positive_delta: bool = False,
        top_n: Optional[int] = None,
    ) -> Dict[str, Any]:
        session = None
        try:
            session = self._Session()  # type: ignore[attr-defined]
            microbe_records = self._load_microbes(
                path=identification_json_path,
                functional_microbes=functional_microbes,
                include_complements=include_complements,
            )
            unique_species = sorted(microbe_records.species)
            results = self._calculate_pair_metrics(
                session=session,
                species_list=unique_species,
                only_positive_delta=only_positive_delta,
            )
            results = self._sort_and_trim(results, top_n)
            summary = self._build_summary(results, microbe_records)
            return {
                "status": "success",
                "species_included": unique_species,
                "pairs": results,
                "summary": summary,
            }
        except SQLAlchemyError as exc:
            return {
                "status": "error",
                "message": f"数据库查询失败: {exc}",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"互作强度计算失败: {exc}",
            }
        finally:
            if session is not None:
                session.close()

    def _load_microbes(
        self,
        path: Optional[str],
        functional_microbes: Optional[List[Dict[str, Any]]],
        include_complements: bool,
    ):
        data = None
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif functional_microbes is not None:
            data = {"functional_microbes": functional_microbes}

        if not data or "functional_microbes" not in data:
            raise ValueError("输入数据中缺少 functional_microbes 信息。")

        func_entries = data["functional_microbes"]
        func_species = []
        complements = []
        for entry in func_entries:
            strain = entry.get("strain")
            if strain:
                func_species.append(self._normalize_name(strain))
            if include_complements:
                for comp in entry.get("complements", []):
                    comp_strain = comp.get("strain")
                    if comp_strain:
                        complements.append(self._normalize_name(comp_strain))

        species = set(func_species)
        if include_complements:
            species.update(complements)

        return MicrobeRecords(
            functional=set(func_species),
            complements=set(complements),
            species=species,
        )

    def _calculate_pair_metrics(
        self,
        session,
        species_list: List[str],
        only_positive_delta: bool,
    ) -> List[Dict[str, Any]]:
        normalized = [self._normalize_name(s) for s in species_list]
        pairs_data: List[Dict[str, Any]] = []
        for a, b in combinations(normalized, 2):
            records = self._fetch_pair_records(session, a, b)
            for record in records:
                delta = self._compute_delta(
                    record.complementarity_index,
                    record.competition_index,
                )
                if only_positive_delta and (delta is None or delta <= 0.0):
                    continue
                pairs_data.append(
                    {
                        "functional_species": record.degrading_microorganism,
                        "complement_species": record.complementary_microorganism,
                        "competition_index": record.competition_index,
                        "complementarity_index": record.complementarity_index,
                        "delta_index": delta,
                        "source": "database",
                    }
                )
        return pairs_data

    def _fetch_pair_records(self, session, species_a: str, species_b: str):
        table = MicrobialComplementarity
        pattern_a = f"%{species_a}%"
        pattern_b = f"%{species_b}%"
        stmt = (
            session.query(table)
            .filter(
                or_(
                    and_(
                        func.lower(table.degrading_microorganism).like(
                            func.lower(pattern_a)
                        ),
                        func.lower(table.complementary_microorganism).like(
                            func.lower(pattern_b)
                        ),
                    ),
                    and_(
                        func.lower(table.degrading_microorganism).like(
                            func.lower(pattern_b)
                        ),
                        func.lower(table.complementary_microorganism).like(
                            func.lower(pattern_a)
                        ),
                    ),
                )
            )
            .all()
        )
        return stmt

    @staticmethod
    def _compute_delta(
        complementarity: Optional[float],
        competition: Optional[float],
    ) -> Optional[float]:
        if complementarity is None or competition is None:
            return None
        if isinstance(complementarity, float) and math.isnan(complementarity):
            return None
        if isinstance(competition, float) and math.isnan(competition):
            return None
        return float(complementarity) - float(competition)

    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join(name.split()).strip()

    @staticmethod
    def _sort_and_trim(
        results: List[Dict[str, Any]],
        top_n: Optional[int],
    ) -> List[Dict[str, Any]]:
        sorted_results = sorted(
            results,
            key=lambda item: (
                item["delta_index"]
                if item.get("delta_index") is not None
                else float("-inf")
            ),
            reverse=True,
        )
        if top_n is not None and top_n > 0:
            return sorted_results[:top_n]
        return sorted_results

    @staticmethod
    def _build_summary(results: List[Dict[str, Any]], records: "MicrobeRecords") -> Dict[str, Any]:
        positives = sum(
            1 for item in results if item.get("delta_index") is not None and item["delta_index"] > 0
        )
        negatives = sum(
            1 for item in results if item.get("delta_index") is not None and item["delta_index"] < 0
        )
        zeros = sum(
            1
            for item in results
            if item.get("delta_index") is not None and math.isclose(item["delta_index"], 0.0)
        )
        missing = sum(1 for item in results if item.get("delta_index") is None)
        return {
            "total_pairs": len(results),
            "positive_delta_pairs": positives,
            "negative_delta_pairs": negatives,
            "zero_delta_pairs": zeros,
            "missing_delta_pairs": missing,
            "functional_species_count": len(records.functional),
            "complement_species_count": len(records.complements),
        }


@dataclass
class MicrobeRecords:
    functional: Set[str]
    complements: Set[str]
    species: Set[str]


__all__ = [
    "ScoreMetabolicInteractionTool",
    "ScoreMetabolicInput",
]
