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
    functional_microbes: Optional[Any] = Field(
        default=None,
        description="直接传入的功能微生物列表（结构同 IdentificationAgent JSON）",
    )
    species: Optional[List[Any]] = Field(
        default=None,
        description="直接传入的物种清单（ParseEnvironmentJSONTool 输出），"
        "支持字符串或带 source 字段的字典。",
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
        species = values.species
        if not path and not fm and not species:
            raise ValueError("必须至少提供 identification_json_path、functional_microbes 或 species。")
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
        functional_microbes: Optional[Any] = None,
        species: Optional[List[Any]] = None,
        include_complements: bool = True,
        only_positive_delta: bool = False,
        top_n: Optional[int] = None,
    ) -> Dict[str, Any]:
        session = None
        try:
            session = self._Session()  # type: ignore[attr-defined]
            if species is not None:
                microbe_records = self._records_from_species(
                    species_list=species,
                    include_complements=include_complements,
                )
            else:
                resolved_path = self._resolve_json_path(identification_json_path)
                microbe_records = self._load_microbes(
                    path=resolved_path,
                    functional_microbes=functional_microbes,
                    include_complements=include_complements,
                )
            unique_species = sorted(self._normalize_name(s) for s in microbe_records.species)
            results = self._calculate_pair_metrics(
                session=session,
                species_list=unique_species,
                allowed_species=microbe_records.species,
                only_positive_delta=only_positive_delta,
            )
            results = self._sort_and_trim(results, top_n)
            return {
                "status": "success",
                "species_included": unique_species,
                "pairs": results,
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

    def _resolve_json_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None

        raw_path = Path(path).expanduser()
        candidate_files: List[Path] = []

        default_dir = (
            Path(__file__).resolve().parents[3]
            / "test_results"
            / "IdentificationAgent"
        )

        if raw_path.is_file():
            candidate_files.append(raw_path)
        else:
            if raw_path.name:
                candidate_files.append(default_dir / raw_path.name)
            if raw_path.is_dir():
                candidate_files.extend(sorted(raw_path.glob("*.json")))

        if default_dir.exists():
            if raw_path.name:
                candidate_files.append(default_dir / raw_path.name)
            candidate_files.extend(sorted(default_dir.glob("*.json")))

        for candidate in candidate_files:
            if candidate.is_file():
                return str(candidate)

        if raw_path.exists():
            return str(raw_path)

        raise FileNotFoundError(f"未找到 JSON 文件：{path}")

    def _records_from_species(
        self,
        species_list: List[Any],
        include_complements: bool,
    ) -> "MicrobeRecords":
        functional: Set[str] = set()
        complements: Set[str] = set()

        for entry in species_list:
            if isinstance(entry, str):
                name = self._normalize_name(entry)
                if not name:
                    continue
                functional.add(name)
            elif isinstance(entry, dict):
                strain_value = str(entry.get("strain") or "")
                name = self._normalize_name(strain_value)
                if not name:
                    continue
                source = str(entry.get("source") or "").strip().lower()
                if source == "complement":
                    if include_complements:
                        complements.add(name)
                else:
                    functional.add(name)
            else:
                continue

        species: Set[str] = set(functional)
        if include_complements:
            species.update(complements)

        return MicrobeRecords(
            functional=functional,
            complements=complements if include_complements else set(),
            species=species,
        )

    def _load_microbes(
        self,
        path: Optional[str],
        functional_microbes: Optional[Any],
        include_complements: bool,
    ):
        records = MicrobeRecords(functional=set(), complements=set(), species=set())

        if functional_microbes is not None:
            self._collect_microbes(
                records=records,
                payload=functional_microbes,
                include_complements=include_complements,
            )

        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._collect_microbes(
                records=records,
                payload=data,
                include_complements=include_complements,
            )

        if not records.species:
            raise ValueError("未识别到可用于互作计算的物种。")

        return records

    def _collect_microbes(
        self,
        records: "MicrobeRecords",
        payload: Any,
        include_complements: bool,
        default_source: str = "functional",
        visited: Optional[Set[int]] = None,
    ) -> None:
        if payload is None:
            return

        if isinstance(payload, str):
            name = self._normalize_name(payload)
            if not name:
                return
            if default_source == "complement":
                if include_complements:
                    records.complements.add(name)
                    records.species.add(name)
            else:
                records.functional.add(name)
                records.species.add(name)
            return

        if visited is None:
            visited = set()

        obj_id = id(payload)
        if obj_id in visited:
            return
        visited.add(obj_id)

        if isinstance(payload, (list, tuple, set)):
            for item in payload:
                self._collect_microbes(
                    records=records,
                    payload=item,
                    include_complements=include_complements,
                    default_source=default_source,
                    visited=visited,
                )
            return

        if isinstance(payload, dict):
            strain_value = payload.get("strain")
            if strain_value:
                source_hint = str(payload.get("source") or default_source).strip().lower()
                if source_hint not in {"functional", "complement"}:
                    source_hint = default_source
                self._collect_microbes(
                    records=records,
                    payload=strain_value,
                    include_complements=include_complements,
                    default_source=source_hint,
                    visited=visited,
                )

            complement_candidates: List[Any] = []
            direct_complements = payload.get("complements")
            if isinstance(direct_complements, (list, tuple, set)):
                complement_candidates.extend(direct_complements)

            metadata = payload.get("metadata")
            if isinstance(metadata, dict):
                meta_complements = metadata.get("complements")
                if isinstance(meta_complements, (list, tuple, set)):
                    complement_candidates.extend(meta_complements)

            if include_complements:
                for comp in complement_candidates:
                    self._collect_microbes(
                        records=records,
                        payload=comp,
                        include_complements=include_complements,
                        default_source="complement",
                        visited=visited,
                    )

            nested_keys = (
                "functional_microbes",
                "functional_records",
                "species",
                "species_payload",
                "records",
                "members",
            )
            for key in nested_keys:
                if key in payload:
                    self._collect_microbes(
                        records=records,
                        payload=payload[key],
                        include_complements=include_complements,
                        default_source=default_source,
                        visited=visited,
                    )

            return

        # 其他类型（数字、布尔等）忽略

    def _calculate_pair_metrics(
        self,
        session,
        species_list: List[str],
        allowed_species: Set[str],
        only_positive_delta: bool,
    ) -> List[Dict[str, Any]]:
        normalized = [self._normalize_name(s) for s in species_list]
        allowed = {self._normalize_name(s) for s in allowed_species}
        pairs_data: List[Dict[str, Any]] = []
        for a, b in combinations(normalized, 2):
            records = self._fetch_pair_records(session, a, b)
            for record in records:
                functional_name = self._normalize_name(record.degrading_microorganism)
                complement_name = self._normalize_name(record.complementary_microorganism)
                if functional_name not in allowed or complement_name not in allowed:
                    continue
                delta = self._compute_delta(
                    record.complementarity_index,
                    record.competition_index,
                )
                if only_positive_delta and (delta is None or delta <= 0.0):
                    continue
                pairs_data.append(
                    {
                        "functional_species": functional_name,
                        "complement_species": complement_name,
                        "competition_index": record.competition_index,
                        "complementarity_index": record.complementarity_index,
                        "delta_index": delta,
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

@dataclass
class MicrobeRecords:
    functional: Set[str]
    complements: Set[str]
    species: Set[str]


__all__ = [
    "ScoreMetabolicInteractionTool",
    "ScoreMetabolicInput",
]
