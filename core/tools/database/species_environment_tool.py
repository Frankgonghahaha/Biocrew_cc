#!/usr/bin/env python3
"""
微生物生长环境查询工具
通过 strain 字段查询物种的生长条件
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import MetaData, Table, create_engine, func, or_, select
from sqlalchemy.sql import bindparam
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError

from config.config import Config
import math
from decimal import Decimal
import numbers


class SpeciesEnvironmentQueryInput(BaseModel):
    """物种生长环境查询的输入参数"""

    strain: str = Field(
        ...,
        description="微生物物种名称，匹配 Sheet_Species_environment 表中的 strain 列",
    )
    temperature: Optional[float] = Field(
        default=None, description="目标水体温度 (°C)"
    )
    ph: Optional[float] = Field(default=None, description="目标水体 pH")
    salinity: Optional[float] = Field(
        default=None, description="目标水体盐度 (质量分数，示例：0.05 表示 5%)"
    )
    oxygen: Optional[str] = Field(
        default=None,
        description="目标水体氧环境，例如 tolerant / not tolerant / unknown",
    )


class SpeciesEnvironmentQueryTool(BaseTool):
    """查询微生物生长环境信息的 CrewAI 工具"""

    name: str = "SpeciesEnvironmentQueryTool"
    description: str = (
        "根据微生物物种名称查询其生长环境，并结合目标水质条件（温度、pH、盐度、氧环境）"
        "计算适应性评分。数据来源为 Sheet_Species_environment 表。"
    )
    args_schema: type[BaseModel] = SpeciesEnvironmentQueryInput
    _TAIL_K: float = math.log(10)
    _TEMP_WEIGHT: float = 0.35
    _PH_WEIGHT: float = 0.35
    _SALINITY_WEIGHT: float = 0.10
    _OXYGEN_WEIGHT: float = 0.20

    def __init__(self) -> None:
        super().__init__()
        engine = self._create_engine()
        table_name = os.getenv("SPECIES_ENV_TABLE", "sheet_species_environment")
        metadata = MetaData()
        try:
            table = Table(table_name, metadata, autoload_with=engine)
        except NoSuchTableError as exc:
            engine.dispose()
            raise RuntimeError(
                f"未能在数据库中找到表 {table_name}，请确认数据已经导入。"
            ) from exc
        object.__setattr__(self, "_engine", engine)
        object.__setattr__(self, "_table_name", table_name)
        object.__setattr__(self, "_table_obj", table)

    def _create_engine(self) -> Engine:
        """创建数据库引擎，优先使用 .env 中的配置。"""
        if Config.DB_TYPE != "postgresql":
            raise ValueError("SpeciesEnvironmentQueryTool 目前仅支持 PostgreSQL 数据库。")
        sslmode = os.getenv("DB_SSLMODE")
        query = {"sslmode": sslmode} if sslmode else None
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            query=query,
        )
        return create_engine(url)

    def _run(
        self,
        strain: str,
        temperature: Optional[float] = None,
        ph: Optional[float] = None,
        salinity: Optional[float] = None,
        oxygen: Optional[str] = None,
    ) -> Dict[str, Any]:
        """执行查询逻辑，并根据目标水质计算适应性打分。"""
        try:
            normalized = strain.strip()
            results = self._query_environment(normalized)
            if not results:
                return {
                    "status": "not_found",
                    "strain": normalized,
                    "message": f"未在表 {self._table_name} 中找到 '{normalized}' 的生长环境数据。",
                }

            scored_records = self._score_results(
                results,
                temperature=temperature,
                ph=ph,
                salinity=salinity,
                oxygen=oxygen,
            )

            payload: Dict[str, Any] = {
                "status": "success",
                "strain": normalized,
                "count": len(scored_records),
                "records": scored_records,
            }
            if scored_records:
                payload["best_record"] = max(
                    scored_records, key=lambda item: item.get("adaptability_score", 0.0)
                )
            return payload
        except SQLAlchemyError as exc:
            return {
                "status": "error",
                "strain": strain,
                "message": f"查询数据库时发生错误: {exc}",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "strain": strain,
                "message": f"处理查询结果时发生错误: {exc}",
            }

    def _query_environment(self, strain: str) -> List[Dict[str, Any]]:
        """从数据库中检索给定物种的生长环境信息。"""
        table = self._table_obj
        normalized = strain.strip()
        stmt = (
            select(table)
            .where(
                or_(
                    func.lower(table.c.strain)
                    == func.lower(bindparam("exact_strain")),
                    table.c.strain.ilike(bindparam("pattern")),
                )
            )
            .limit(25)
        )
        with self._engine.connect() as connection:
            result = connection.execute(
                stmt,
                {
                    "exact_strain": normalized,
                    "pattern": f"%{normalized}%",
                },
            )
            rows = result.mappings().all()
        return [dict(row) for row in rows]

    def _score_results(
        self,
        records: List[Dict[str, Any]],
        *,
        temperature: Optional[float],
        ph: Optional[float],
        salinity: Optional[float],
        oxygen: Optional[str],
    ) -> List[Dict[str, Any]]:
        scored: List[Dict[str, Any]] = []
        for record in records:
            clean_record = {k: self._convert_value(v) for k, v in record.items()}
            score_detail = self._calculate_adaptability(
                clean_record,
                temperature=temperature,
                ph=ph,
                salinity=salinity,
                oxygen=oxygen,
            )
            combined = {**clean_record, **score_detail}
            scored.append(combined)
        scored.sort(key=lambda item: item.get("adaptability_score", 0.0), reverse=True)
        return scored

    def _convert_value(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, numbers.Number):
            return float(value)
        return value

    def _calculate_adaptability(
        self,
        record: Dict[str, Any],
        *,
        temperature: Optional[float],
        ph: Optional[float],
        salinity: Optional[float],
        oxygen: Optional[str],
    ) -> Dict[str, Any]:
        temp_score = self._bounded_score(
            temperature,
            record.get("temperature_minimum"),
            record.get("temperature_optimum_c"),
            record.get("temperature_maximum"),
        )
        ph_score = self._bounded_score(
            ph,
            record.get("ph_minimum"),
            record.get("ph_optimum"),
            record.get("ph_maximum"),
        )
        salinity_score = self._bounded_score(
            salinity,
            record.get("salinity_minimum"),
            record.get("salinity_optimum"),
            record.get("salinity_maximum"),
        )
        oxygen_score = self._oxygen_score(
            record.get("oxygen_tolerance"), oxygen
        )

        adaptability = self._combine_scores(
            [
                (temp_score, self._TEMP_WEIGHT),
                (ph_score, self._PH_WEIGHT),
                (salinity_score, self._SALINITY_WEIGHT),
                (oxygen_score, self._OXYGEN_WEIGHT),
            ]
        )

        return {
            "temperature_score": temp_score,
            "ph_score": ph_score,
            "salinity_score": salinity_score,
            "oxygen_score": oxygen_score,
            "adaptability_score": adaptability,
            "target_temperature": temperature,
            "target_ph": ph,
            "target_salinity": salinity,
            "target_oxygen": oxygen,
        }

    def _bounded_score(
        self,
        target_value: Optional[float],
        min_value: Any,
        optimum_value: Any,
        max_value: Any,
    ) -> Optional[float]:
        value = self._to_float(target_value)
        min_val = self._to_float(min_value)
        max_val = self._to_float(max_value)
        opt_val = self._to_float(optimum_value)
        if value is None or min_val is None or max_val is None:
            return None
        if max_val <= min_val:
            return None
        if min_val <= value <= max_val:
            if opt_val is None or not (min_val <= opt_val <= max_val):
                center = (min_val + max_val) / 2.0
                half = max((max_val - min_val) / 2.0, 1e-9)
                return max(0.0, 1.0 - abs(value - center) / half)
            left = max(opt_val - min_val, 1e-9)
            right = max(max_val - opt_val, 1e-9)
            if value <= opt_val:
                return max(0.0, 1.0 - (opt_val - value) / left)
            return max(0.0, 1.0 - (value - opt_val) / right)
        distance = min_val - value if value < min_val else value - max_val
        span = max(max_val - min_val, 1e-9)
        return math.exp(-self._TAIL_K * (distance / span))

    def _oxygen_score(
        self, recorded_oxygen: Any, target_oxygen: Optional[str]
    ) -> Optional[float]:
        if target_oxygen is None:
            return None
        normalized_target = str(target_oxygen).strip().lower()
        if not normalized_target:
            return None
        recorded = str(recorded_oxygen or "").strip().lower()
        if recorded == normalized_target and recorded:
            return 1.0
        if recorded in {"", "unknown", "nan", "none"}:
            return 0.5
        return 0.2

    def _combine_scores(self, scores: List[tuple[Optional[float], float]]) -> float:
        numerator = 0.0
        denominator = 0.0
        for score, weight in scores:
            if score is None:
                continue
            numerator += score * weight
            denominator += weight
        if denominator == 0:
            return 0.0
        return float(numerator / denominator)

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, numbers.Number):
            return float(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                return float(stripped)
            except ValueError:
                return None
        if isinstance(value, Decimal):
            return float(value)
        return None
