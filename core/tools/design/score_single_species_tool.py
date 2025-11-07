#!/usr/bin/env python3
"""
单菌综合评分工具
整合 ScoreEnzymeDegradationTool 与 ScoreEnvironmentTool 的结果，
按指定权重计算 S_microbe。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover - fallback
    class BaseTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()

    print("Warning: crewai 未安装，ScoreSingleSpeciesTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field, validator


class SpeciesEntry(BaseModel):
    """基础物种信息"""

    strain: str = Field(..., description="物种名称")
    source: Optional[str] = Field(default=None, description="来源标签，例如 functional/complement")

    @validator("strain")
    def normalize_strain(cls, value: str) -> str:
        text = " ".join(value.replace("（", "(").replace("）", ")").split()).strip()
        if not text:
            raise ValueError("strain 不能为空")
        return text


class EnzymeScoreEntry(BaseModel):
    """酶降解得分条目"""

    strain: str
    kcat_max: float = 0.0
    kcat_mean: Optional[float] = None
    reference_ratio: Optional[float] = None
    enzyme_diversity: Optional[int] = None
    status: Optional[str] = None
    entries: Optional[List[Dict[str, Any]]] = None
    source: Optional[str] = None

    class Config:
        extra = "allow"


class EnvironmentScoreEntry(BaseModel):
    """环境适应性得分条目"""

    strain: str
    best_score: Optional[float] = None
    records: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    source: Optional[str] = None

    class Config:
        extra = "allow"


class ScoreSingleSpeciesInput(BaseModel):
    """单菌综合评分工具输入"""

    species: List[SpeciesEntry] = Field(
        ..., description="待计算 S_microbe 的物种列表（通常来自 ParseEnvironmentJSONTool）"
    )
    enzyme_results: List[EnzymeScoreEntry] = Field(
        default_factory=list,
        description="ScoreEnzymeDegradationTool 返回的结果列表。",
    )
    environment_results: List[EnvironmentScoreEntry] = Field(
        default_factory=list,
        description="ScoreEnvironmentTool 返回的结果列表。",
    )
    weight_kcat: float = Field(default=0.5, description="kcat 归一化分量权重")
    weight_env: float = Field(default=0.4, description="环境软评分权重")
    weight_enzyme_diversity: float = Field(
        default=0.1,
        description="酶多样性归一化分量权重",
    )
    top_n: Optional[int] = Field(
        default=10,
        description="返回的前 N 条单菌记录（None 表示全部）。",
    )

    @validator("species")
    def ensure_species(cls, value: List[SpeciesEntry]) -> List[SpeciesEntry]:
        if not value:
            raise ValueError("species 列表不能为空")
        return value


class ScoreSingleSpeciesTool(BaseTool):
    """S_microbe 计算工具"""

    name: str = "ScoreSingleSpeciesTool"
    description: str = (
        "结合酶降解得分与环境适应性得分，按 S_microbe = 0.5·Norm01(kcat) "
        "+ 0.4·env_soft_score + 0.1·Norm01(enzyme_diversity) 计算单菌综合评分。"
    )
    args_schema: type[BaseModel] = ScoreSingleSpeciesInput

    def _run(
        self,
        species: List[SpeciesEntry],
        enzyme_results: List[EnzymeScoreEntry],
        environment_results: List[EnvironmentScoreEntry],
        weight_kcat: float = 0.5,
        weight_env: float = 0.4,
        weight_enzyme_diversity: float = 0.1,
        top_n: Optional[int] = 10,
    ) -> Dict[str, Any]:
        try:
            normalized_species: List[SpeciesEntry] = []
            for entry in species:
                if isinstance(entry, SpeciesEntry):
                    normalized_species.append(entry)
                elif isinstance(entry, dict):
                    normalized_species.append(SpeciesEntry.parse_obj(entry))
                else:
                    raise TypeError(
                        f"species 列表中的元素类型不受支持: {type(entry)}。"
                    )

            normalized_enzyme: List[EnzymeScoreEntry] = []
            for entry in enzyme_results:
                if isinstance(entry, EnzymeScoreEntry):
                    normalized_enzyme.append(entry)
                elif isinstance(entry, dict):
                    normalized_enzyme.append(EnzymeScoreEntry.parse_obj(entry))
                else:
                    raise TypeError(
                        f"enzyme_results 列表中的元素类型不受支持: {type(entry)}。"
                    )

            normalized_environment: List[EnvironmentScoreEntry] = []
            for entry in environment_results:
                if isinstance(entry, EnvironmentScoreEntry):
                    normalized_environment.append(entry)
                elif isinstance(entry, dict):
                    normalized_environment.append(EnvironmentScoreEntry.parse_obj(entry))
                else:
                    raise TypeError(
                        f"environment_results 列表中的元素类型不受支持: {type(entry)}。"
                    )

            enzyme_map = {entry.strain: entry for entry in normalized_enzyme}
            env_map = {entry.strain: entry for entry in normalized_environment}

            kcat_values: List[float] = []
            diversity_values: List[float] = []
            env_values: List[float] = []

            intermediate: List[Dict[str, Any]] = []

            for item in normalized_species:
                enzyme_entry = enzyme_map.get(item.strain)
                env_entry = env_map.get(item.strain)

                kcat_max = float(enzyme_entry.kcat_max) if enzyme_entry else 0.0
                enzyme_diversity = (
                    float(enzyme_entry.enzyme_diversity)
                    if enzyme_entry and enzyme_entry.enzyme_diversity is not None
                    else 0.0
                )
                env_score = 0.0
                env_status = None
                env_records = None
                if env_entry:
                    env_status = env_entry.status
                    env_records = env_entry.records
                    if (
                        env_entry.best_score is not None
                        and isinstance(env_entry.best_score, (float, int))
                    ):
                        env_score = float(env_entry.best_score)

                kcat_values.append(kcat_max)
                diversity_values.append(enzyme_diversity)
                env_values.append(env_score)

                intermediate.append(
                    {
                        "strain": item.strain,
                        "source": item.source,
                        "kcat_max": kcat_max,
                        "environment_match": env_score,
                        "enzyme_diversity": enzyme_diversity,
                        "enzyme_detail": (enzyme_entry.entries if enzyme_entry else None),
                        "environment_records": env_records,
                        "environment_status": env_status,
                        "enzyme_status": enzyme_entry.status if enzyme_entry else None,
                    }
                )

            norm_kcat = self._normalize_01(kcat_values)
            norm_diversity = self._normalize_01(diversity_values)

            results: List[Dict[str, Any]] = []
            for idx, row in enumerate(intermediate):
                s_microbe = (
                    weight_kcat * norm_kcat[idx]
                    + weight_env * env_values[idx]
                    + weight_enzyme_diversity * norm_diversity[idx]
                )
                results.append(
                    {
                        "species": row["strain"],
                        "strain": row["strain"],
                        "source": row["source"],
                        "kcat_max": row["kcat_max"],
                        "norm_kcat": norm_kcat[idx],
                        "env_soft_score": env_values[idx],
                        "norm_env": env_values[idx],
                        "enzyme_diversity": row["enzyme_diversity"],
                        "norm_enzyme_diversity": norm_diversity[idx],
                        "S_microbe": s_microbe,
                        "metadata": {
                            "enzyme_detail": row["enzyme_detail"],
                            "environment_records": row["environment_records"],
                            "environment_status": row["environment_status"],
                            "enzyme_status": row["enzyme_status"],
                        },
                    }
                )

            results.sort(key=lambda x: x["S_microbe"], reverse=True)

            total_count = len(results)
            if top_n is not None and top_n > 0:
                results = results[:top_n]

            summary = {
                "total_count": total_count,
                "returned_count": len(results),
                "top_species": results[0]["strain"] if results else None,
                "top_score": results[0]["S_microbe"] if results else None,
                "weight_kcat": weight_kcat,
                "weight_env": weight_env,
                "weight_enzyme_diversity": weight_enzyme_diversity,
            }

            return {
                "status": "success",
                "records": results,
                "summary": summary,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"单菌综合评分失败: {exc}",
            }

    @staticmethod
    def _normalize_01(values: List[float]) -> List[float]:
        if not values:
            return []
        min_v = min(values)
        max_v = max(values)
        if float(max_v) == float(min_v):
            return [1.0 if max_v > 0 else 0.0 for _ in values]
        span = max_v - min_v
        return [(v - min_v) / span for v in values]


__all__ = [
    "ScoreSingleSpeciesTool",
    "ScoreSingleSpeciesInput",
    "SpeciesEntry",
    "EnzymeScoreEntry",
    "EnvironmentScoreEntry",
]
