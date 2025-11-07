#!/usr/bin/env python3
"""
环境适应性评分工具
接收 ParseEnvironmentJSONTool 输出的物种清单与目标工况，
计算每个物种的 env_soft_score 及子项评分。
"""

from __future__ import annotations

import math
import numbers
import os
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover
    class BaseTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()

    print("Warning: crewai 未安装，ScoreEnvironmentTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field, validator
from sqlalchemy import MetaData, Table, create_engine, func, or_, select
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError
from sqlalchemy.sql import bindparam

from config.config import Config


class TargetEnvironment(BaseModel):
    """目标环境参数"""

    temperature: Optional[float] = Field(default=None, description="水体温度 (°C)")
    ph: Optional[float] = Field(default=None, description="水体 pH")
    salinity: Optional[float] = Field(default=None, description="水体盐度 (质量分数)")
    oxygen: Optional[str] = Field(default=None, description="氧环境，例如 tolerant / anaerobic")


class SpeciesEnvironmentRequest(BaseModel):
    """待评分的物种请求"""

    strain: str = Field(..., description="物种名称")
    source: Optional[str] = Field(default=None, description="来源标签，例如 functional/complement")
    limit: Optional[int] = Field(default=None, description="可选：覆盖默认查询行数上限")

    @validator("strain")
    def sanitize_strain(cls, value: str) -> str:
        text = " ".join(value.replace("（", "(").replace("）", ")").split()).strip()
        if not text:
            raise ValueError("strain 不能为空")
        return text


class ScoreEnvironmentInput(BaseModel):
    """环境评分批量输入"""

    species: List[SpeciesEnvironmentRequest] = Field(
        ..., description="待计算环境适应性的物种请求列表"
    )
    target_environment: TargetEnvironment = Field(
        ..., description="目标水体环境参数"
    )
    default_limit: int = Field(
        default=5,
        description="默认环境数据库查询行数上限",
    )

    @validator("species")
    def ensure_species(cls, value: List[SpeciesEnvironmentRequest]) -> List[SpeciesEnvironmentRequest]:
        if not value:
            raise ValueError("species 列表不能为空")
        return value


class ScoreEnvironmentTool(BaseTool):
    """S_microbe 环境软评分计算工具"""

    name: str = "ScoreEnvironmentTool"
    description: str = (
        "依据 Sheet_Species_environment 表计算每个物种在目标工况下的 env_soft_score，"
        "支持批量处理 ParseEnvironmentJSONTool 提供的物种清单。"
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
        species: List[SpeciesEnvironmentRequest],
        target_environment: TargetEnvironment | Dict[str, Any],
        default_limit: int = 5,
    ) -> Dict[str, Any]:
        try:
            normalized_requests: List[SpeciesEnvironmentRequest] = []
            for entry in species:
                if isinstance(entry, SpeciesEnvironmentRequest):
                    normalized_requests.append(entry)
                elif isinstance(entry, dict):
                    payload = dict(entry)
                    payload["strain"] = payload.get("strain") or payload.get("species")
                    normalized_requests.append(SpeciesEnvironmentRequest.parse_obj(payload))
                else:
                    raise TypeError(
                        f"species 列表中的元素类型不受支持: {type(entry)}。"
                    )

            if isinstance(target_environment, TargetEnvironment):
                target_env = target_environment
            elif isinstance(target_environment, dict):
                target_env = TargetEnvironment(**target_environment)
            else:
                raise TypeError(
                    f"target_environment 类型不受支持: {type(target_environment)}。"
                )

            aggregate: List[Dict[str, Any]] = []
            for request in normalized_requests:
                limit = request.limit or default_limit
                rows = self._query_environment(request.strain, limit)

                if not rows:
                    aggregate.append(
                        {
                            "strain": request.strain,
                            "source": request.source,
                            "status": "not_found",
                            "message": "未在环境表中找到匹配的物种。",
                        }
                    )
                    continue

                scored_values = [
                    self._score_record(
                        record=row,
                        target=target_env,
                    )
                    for row in rows
                ]

                scored_values.sort(reverse=True)
                best_score = scored_values[0] if scored_values else 0.0

                aggregate.append(
                    {
                        "strain": request.strain,
                        "source": request.source,
                        "status": "success",
                        "best_score": best_score,
                        "records": [{"env_soft_score": value} for value in scored_values],
                    }
                )

            return {
                "status": "success",
                "target_environment": target_env.dict(),
                "results": aggregate,
            }
        except SQLAlchemyError as exc:
            return {
                "status": "error",
                "message": f"数据库查询失败: {exc}",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
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
        target: TargetEnvironment,
    ) -> float:
        temp_score = self._bounded_score(
            target.temperature,
            record.get("temperature_minimum"),
            record.get("temperature_optimum_c"),
            record.get("temperature_maximum"),
        )
        ph_score = self._bounded_score(
            target.ph,
            record.get("ph_minimum"),
            record.get("ph_optimum"),
            record.get("ph_maximum"),
        )
        salinity_score = self._bounded_score(
            target.salinity,
            record.get("salinity_minimum"),
            record.get("salinity_optimum"),
            record.get("salinity_maximum"),
        )
        oxygen_score = self._oxygen_score(
            record.get("oxygen_tolerance"),
            target.oxygen,
        )

        env_soft_score = self._combine_scores(
            [
                (temp_score, self._TEMP_WEIGHT),
                (ph_score, self._PH_WEIGHT),
                (salinity_score, self._SALINITY_WEIGHT),
                (oxygen_score, self._OXYGEN_WEIGHT),
            ]
        )

        return env_soft_score

    def _combine_scores(
        self, weighted_scores: Iterable[tuple[Optional[float], float]]
    ) -> float:
        total_weight = 0.0
        weighted_sum = 0.0
        for score, weight in weighted_scores:
            if score is None:
                continue
            total_weight += weight
            weighted_sum += score * weight
        if math.isclose(total_weight, 0.0):
            return 0.0
        combined = weighted_sum / total_weight
        return float(round(combined, 6))

    def _bounded_score(
        self,
        target_value: Optional[float],
        minimum: Optional[float],
        optimum: Optional[float],
        maximum: Optional[float],
    ) -> Optional[float]:
        if target_value is None:
            return None

        try:
            target = float(target_value)
        except (TypeError, ValueError):
            return None

        min_v = self._safe_number(minimum)
        opt_v = self._safe_number(optimum)
        max_v = self._safe_number(maximum)

        if min_v is None and max_v is None and opt_v is None:
            return None

        if opt_v is not None:
            baseline = opt_v
        elif min_v is not None and max_v is not None:
            baseline = (min_v + max_v) / 2
        else:
            baseline = opt_v or target

        # 三角隶属函数 + 尾部指数衰减
        if min_v is not None and target < min_v:
            return self._tail_decay(target, min_v, baseline)
        if max_v is not None and target > max_v:
            return self._tail_decay(target, max_v, baseline)

        if opt_v is None:
            if min_v is not None and max_v is not None:
                return self._linear_membership(target, min_v, max_v)
            return None

        if min_v is not None and target < opt_v:
            return self._linear_membership(target, min_v, opt_v)
        if max_v is not None and target > opt_v:
            return self._linear_membership(target, opt_v, max_v, reverse=True)

        return 1.0

    def _oxygen_score(
        self, tolerance: Optional[str], target: Optional[str]
    ) -> Optional[float]:
        if target is None:
            return None

        target_normalized = str(target).strip().lower()
        if not target_normalized:
            return None

        tolerance_normalized = (tolerance or "").strip().lower()
        if not tolerance_normalized:
            return 0.5 if target_normalized else None

        if target_normalized in tolerance_normalized:
            return 1.0
        if target_normalized == "unknown":
            return 0.5
        return 0.2

    @staticmethod
    def _linear_membership(
        value: float,
        start: Optional[float],
        end: Optional[float],
        *,
        reverse: bool = False,
    ) -> Optional[float]:
        if start is None or end is None:
            return None
        if math.isclose(start, end):
            return 1.0
        if value < start and not reverse:
            return 0.0
        if value > end and reverse:
            return 0.0
        span = end - start
        if reverse:
            return max(0.0, min(1.0, (end - value) / span))
        return max(0.0, min(1.0, (value - start) / span))

    def _tail_decay(self, value: float, boundary: float, optimum: float) -> float:
        distance = abs(value - boundary)
        span = abs(optimum - boundary) or 1.0
        ratio = distance / span
        decay = math.exp(-self._TAIL_K * ratio)
        return float(round(max(0.0, min(1.0, decay)), 6))

    @staticmethod
    def _safe_number(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, numbers.Number):
            if math.isnan(value):
                return None
            return float(value)
        if isinstance(value, (str, Decimal)):
            try:
                number = float(value)
                if math.isnan(number):
                    return None
                return number
            except (TypeError, ValueError):
                return None
        return None


__all__ = [
    "ScoreEnvironmentTool",
    "ScoreEnvironmentInput",
    "SpeciesEnvironmentRequest",
    "TargetEnvironment",
]
