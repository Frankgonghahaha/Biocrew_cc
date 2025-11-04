#!/usr/bin/env python3
"""
环境适应性评分工具
负责计算 S_microbe 中 env_soft_score 指标
"""

from __future__ import annotations

import math
import numbers
import os
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pandas as pd

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover
    class BaseTool:  # type: ignore
        """Fallback BaseTool when CrewAI is unavailable."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
            super().__init__()

    print("Warning: crewai 未安装，ScoreEnvironmentTool 将使用简化 BaseTool。")
from pydantic import BaseModel, Field
from sqlalchemy import MetaData, Table, create_engine, func, or_, select
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError
from sqlalchemy.sql import bindparam

from config.config import Config


class ScoreEnvironmentInput(BaseModel):
    """环境评分工具的输入参数"""

    strain: str = Field(..., description="目标微生物物种名称")
    temperature: Optional[float] = Field(
        default=None, description="目标水体温度 (°C)"
    )
    ph: Optional[float] = Field(default=None, description="目标水体 pH")
    salinity: Optional[float] = Field(
        default=None, description="目标水体盐度 (质量分数，例如 0.05 表示 5%)"
    )
    oxygen: Optional[str] = Field(
        default=None, description="目标水体氧环境，如 tolerant / not tolerant"
    )
    limit: int = Field(
        default=5, description="若匹配多条记录，最多返回的行数"
    )


class ScoreEnvironmentTool(BaseTool):
    """S_microbe 环境软评分计算工具"""

    name: str = "ScoreEnvironmentTool"
    description: str = (
        "依据 Sheet_Species_environment 表计算给定物种在目标工况下的 env_soft_score，"
        "并返回匹配到的环境记录。"
    )
    args_schema: type[BaseModel] = ScoreEnvironmentInput

    _TEMP_WEIGHT = 0.35
    _PH_WEIGHT = 0.35
    _SALINITY_WEIGHT = 0.10
    _OXYGEN_WEIGHT = 0.20
    _TAIL_K = math.log(10)

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
                f"未能在数据库中找到表 {table_name}，请先导入环境数据。"
            ) from exc
        object.__setattr__(self, "_engine", engine)
        object.__setattr__(self, "_table_name", table_name)
        object.__setattr__(self, "_table_obj", table)

    def _create_engine(self) -> Engine:
        if Config.DB_TYPE != "postgresql":
            raise ValueError("ScoreEnvironmentTool 当前仅支持 PostgreSQL。")
        sslmode = os.getenv("DB_SSLMODE")
        query = {"sslmode": sslmode} if sslmode else None
        url = URL.create(
            "postgresql+psycopg2",
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
        limit: int = 5,
    ) -> Dict[str, Any]:
        try:
            rows = self._query_environment(strain, limit)
            if not rows:
                return {
                    "status": "not_found",
                    "strain": strain.strip(),
                    "message": "未在环境表中找到匹配的物种。",
                }
            scored = [
                self._score_record(
                    record=row,
                    temperature=temperature,
                    ph=ph,
                    salinity=salinity,
                    oxygen=oxygen,
                )
                for row in rows
            ]
            scored.sort(
                key=lambda item: item.get("env_soft_score", 0.0), reverse=True
            )
            return {
                "status": "success",
                "strain": strain.strip(),
                "records": scored,
                "best_score": scored[0].get("env_soft_score", 0.0),
            }
        except SQLAlchemyError as exc:
            return {
                "status": "error",
                "strain": strain,
                "message": f"数据库查询失败: {exc}",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "strain": strain,
                "message": f"环境评分失败: {exc}",
            }

    def _query_environment(self, strain: str, limit: int) -> List[Dict[str, Any]]:
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
            .limit(max(1, limit))
        )
        with self._engine.connect() as connection:
            result = connection.execute(
                stmt,
                {"exact_strain": normalized, "pattern": f"%{normalized}%"},
            )
            rows = result.mappings().all()
        return [dict(row) for row in rows]

    def _score_record(
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
        oxygen_score = self._oxygen_score(record.get("oxygen_tolerance"), oxygen)

        env_soft_score = self._combine_scores(
            [
                (temp_score, self._TEMP_WEIGHT),
                (ph_score, self._PH_WEIGHT),
                (salinity_score, self._SALINITY_WEIGHT),
                (oxygen_score, self._OXYGEN_WEIGHT),
            ]
        )

        enriched = dict(record)
        enriched.update(
            {
                "temperature_score": temp_score,
                "ph_score": ph_score,
                "salinity_score": salinity_score,
                "oxygen_score": oxygen_score,
                "env_soft_score": env_soft_score,
                "target_temperature": temperature,
                "target_ph": ph,
                "target_salinity": salinity,
                "target_oxygen": oxygen,
            }
        )
        return enriched

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
        if denominator == 0.0:
            return 0.0
        return float(numerator / denominator)

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, numbers.Number):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                return float(stripped)
            except ValueError:
                return None
        return None
