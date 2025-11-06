#!/usr/bin/env python3
"""
候选微生物综合评分工具
重现 Old_Design_pipeline1 Result2_candidate_scores.csv 的计算流程
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field, validator

from core.tools.design.score_environment_tool import ScoreEnvironmentTool
from core.tools.design.score_enzyme_degradation_tool import (
    ScoreEnzymeDegradationTool,
)


class CandidateMicrobe(BaseModel):
    """单个微生物的原始评分信息"""

    species: str = Field(..., description="物种名称")
    source: str = Field(
        ...,
        description="来源标签，通常为 functional / complement",
    )
    kcat_max: Optional[float] = Field(
        default=None,
        description="该微生物的最大 kcat 估计值",
    )
    kcat_mean: Optional[float] = Field(
        default=None,
        description="该微生物的平均 kcat 估计值",
    )
    environment_match: Optional[float] = Field(
        default=None,
        description="环境适应性软评分（0-1）",
    )
    enzyme_diversity: Optional[int] = Field(
        default=None,
        description="酶种类数量（去重后）",
    )
    enzyme_sequences: Optional[List[str]] = Field(
        default=None,
        description="用于估算 kcat 的酶序列列表",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="附加字段，例如互补菌通过情况等",
    )

    @validator("source")
    def validate_source(cls, value: str) -> str:
        text = value.strip().lower()
        if not text:
            raise ValueError("source 不能为空")
        return text

    @validator("environment_match")
    def clamp_environment(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        return max(0.0, min(1.0, float(value)))

    @validator("enzyme_diversity")
    def non_negative_diversity(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return None
        if value < 0:
            raise ValueError("enzyme_diversity 不能为负数")
        return value

    @validator("enzyme_sequences")
    def sanitize_sequences(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned = [seq.strip() for seq in value if seq and seq.strip()]
        return cleaned or None


class TargetEnvironment(BaseModel):
    """目标水体环境参数"""

    temperature: Optional[float] = Field(default=None, description="°C")
    ph: Optional[float] = Field(default=None, description="无量纲")
    salinity: Optional[float] = Field(default=None, description="质量分数")
    oxygen: Optional[str] = Field(default=None, description="氧环境描述，例如 tolerant")


class ScoreCandidateInput(BaseModel):
    """综合评分工具的输入"""

    microbes: List[CandidateMicrobe] = Field(
        ..., description="待评分的微生物列表，至少包含 1 个功能菌"
    )
    weight_kcat: float = Field(
        default=0.5,
        description="kcat 归一化分量权重",
    )
    weight_env: float = Field(
        default=0.4,
        description="环境软评分权重",
    )
    weight_enzyme_diversity: float = Field(
        default=0.1,
        description="酶多样性归一化分量权重",
    )
    pollutant_smiles: Optional[str] = Field(
        default=None,
        description="目标污染物的 SMILES，用于估算 kcat",
    )
    target_environment: Optional[TargetEnvironment] = Field(
        default=None,
        description="目标水体环境，用于计算 env_soft_score",
    )

    @validator("microbes")
    def ensure_microbes(cls, value: List[CandidateMicrobe]) -> List[CandidateMicrobe]:
        if not value:
            raise ValueError("microbes 列表不能为空")
        return value

    @validator("weight_kcat", "weight_env", "weight_enzyme_diversity")
    def non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("权重必须为非负数")
        return value


class ScoreCandidateTool(BaseTool):
    """功能菌与互补菌综合评分工具"""

    name: str = "ScoreCandidateTool"
    description: str = (
        "接收功能菌与互补菌的原始评分信息，执行 kcat / 环境匹配 / 酶多样性 "
        "归一化并计算 S_microbe，流程参考 Old_Design_pipeline1 的 Result2_candidate_scores。"
    )
    args_schema: type[BaseModel] = ScoreCandidateInput

    def __init__(self) -> None:
        super().__init__()
        self._env_tool: Optional[ScoreEnvironmentTool] = None
        self._env_tool_error: Optional[str] = None
        self._enzyme_tool: Optional[ScoreEnzymeDegradationTool] = None

    def _run(
        self,
        microbes: List[CandidateMicrobe],
        weight_kcat: float = 0.5,
        weight_env: float = 0.4,
        weight_enzyme_diversity: float = 0.1,
        pollutant_smiles: Optional[str] = None,
        target_environment: Optional[TargetEnvironment] = None,
    ) -> Dict[str, Any]:
        try:
            records = [m.dict() for m in microbes]
            enriched = self._enrich_records(
                records,
                pollutant_smiles=pollutant_smiles,
                target_environment=target_environment,
            )
            normalized = self._compute_scores(
                enriched,
                weight_kcat=weight_kcat,
                weight_env=weight_env,
                weight_enzyme_diversity=weight_enzyme_diversity,
            )
            summary = self._build_summary(normalized)
            return {
                "status": "success",
                "records": normalized,
                "summary": summary,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"候选菌评分失败: {exc}",
            }

    def _enrich_records(
        self,
        records: List[Dict[str, Any]],
        *,
        pollutant_smiles: Optional[str],
        target_environment: Optional[TargetEnvironment],
    ) -> List[Dict[str, Any]]:
        for entry in records:
            entry.setdefault("metadata", {})
            if (
                pollutant_smiles
                and entry.get("enzyme_sequences")
                and not entry.get("kcat_max")
            ):
                kcat_info = self._calculate_kcat(
                    entry["enzyme_sequences"], pollutant_smiles
                )
                if kcat_info:
                    entry["kcat_max"] = kcat_info["kcat_max"]
                    entry["kcat_mean"] = kcat_info["kcat_mean"]
                    if kcat_info.get("entries"):
                        entry["metadata"]["kcat_entries"] = kcat_info["entries"]

            if target_environment and entry.get("environment_match") is None:
                env_info = self._calculate_environment(
                    entry.get("species"), target_environment
                )
                if env_info:
                    entry["environment_match"] = env_info["score"]
                    if env_info.get("record"):
                        entry["metadata"]["environment_record"] = env_info["record"]

        for entry in records:
            entry.pop("enzyme_sequences", None)

        return records

    def _get_env_tool(self) -> Optional[ScoreEnvironmentTool]:
        if self._env_tool_error:
            return None
        if self._env_tool is None:
            try:
                self._env_tool = ScoreEnvironmentTool()
            except Exception as exc:  # noqa: BLE001
                self._env_tool_error = str(exc)
                self._env_tool = None
        return self._env_tool

    def _get_enzyme_tool(self) -> Optional[ScoreEnzymeDegradationTool]:
        if self._enzyme_tool is None:
            try:
                self._enzyme_tool = ScoreEnzymeDegradationTool()
            except Exception:
                self._enzyme_tool = None
        return self._enzyme_tool

    def _calculate_kcat(
        self, sequences: List[str], pollutant_smiles: str
    ) -> Optional[Dict[str, Any]]:
        tool = self._get_enzyme_tool()
        if tool is None:
            return None
        smiles = pollutant_smiles.strip()
        if not smiles:
            return None
        parsed_sequences = [seq for seq in sequences if seq.strip()]
        if not parsed_sequences:
            return None
        result = tool._run(
            pollutant_smiles=smiles,
            enzyme_sequences=parsed_sequences,
        )
        if result.get("status") != "success":
            return None
        try:
            return {
                "kcat_max": float(result.get("kcat_max", 0.0)),
                "kcat_mean": float(result.get("kcat_mean", 0.0)),
                "entries": result.get("entries", []),
            }
        except (TypeError, ValueError):
            return None

    def _calculate_environment(
        self, species: Optional[str], target_environment: TargetEnvironment
    ) -> Optional[Dict[str, Any]]:
        if not species:
            return None
        tool = self._get_env_tool()
        if tool is None:
            return None
        result = tool._run(
            strain=species,
            temperature=target_environment.temperature,
            ph=target_environment.ph,
            salinity=target_environment.salinity,
            oxygen=target_environment.oxygen,
        )
        if result.get("status") != "success":
            return None
        records = result.get("records") or []
        best = records[0] if records else {}
        score = best.get("env_soft_score", result.get("best_score"))
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            return None
        return {"score": numeric_score, "record": best or None}

    @staticmethod
    def _compute_scores(
        data: List[Dict[str, Any]],
        *,
        weight_kcat: float,
        weight_env: float,
        weight_enzyme_diversity: float,
    ) -> List[Dict[str, Any]]:
        kcat_values = [float(d.get("kcat_max") or 0.0) for d in data]
        enzyme_values = [float(d.get("enzyme_diversity") or 0.0) for d in data]
        env_values = [
            float(d.get("environment_match") or 0.0) for d in data
        ]

        norm_kcat = ScoreCandidateTool._normalize_01(kcat_values)
        norm_enzyme = ScoreCandidateTool._normalize_01(enzyme_values)
        norm_env = env_values  # 已限制在 0~1（缺失视为 0）

        combined = []
        for idx, row in enumerate(data):
            score = (
                weight_kcat * norm_kcat[idx]
                + weight_env * norm_env[idx]
                + weight_enzyme_diversity * norm_enzyme[idx]
            )
            item = {
                "species": row.get("species"),
                "source": row.get("source"),
                "kcat_max": kcat_values[idx],
                "kcat_mean": float(row.get("kcat_mean") or 0.0),
                "enzyme_diversity": int(enzyme_values[idx]),
                "environment_match": norm_env[idx],
                "norm_kcat": norm_kcat[idx],
                "norm_env": norm_env[idx],
                "norm_enzyme_diversity": norm_enzyme[idx],
                "S_microbe": score,
                "metadata": row.get("metadata", {}),
            }
            combined.append(item)

        combined.sort(key=lambda x: x["S_microbe"], reverse=True)
        return combined

    @staticmethod
    def _normalize_01(values: List[float]) -> List[float]:
        if not values:
            return []
        min_v = min(values)
        max_v = max(values)
        if math.isclose(max_v, min_v):
            return [1.0 for _ in values]
        span = max_v - min_v
        return [(v - min_v) / span for v in values]

    @staticmethod
    def _build_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {
                "count": 0,
                "functional_count": 0,
                "complement_count": 0,
            }
        functional = sum(1 for r in records if r.get("source") == "functional")
        complement = sum(1 for r in records if r.get("source") == "complement")
        return {
            "count": len(records),
            "functional_count": functional,
            "complement_count": complement,
            "top_species": records[0].get("species"),
            "top_score": records[0].get("S_microbe"),
        }


__all__ = [
    "ScoreCandidateTool",
    "ScoreCandidateInput",
    "CandidateMicrobe",
    "TargetEnvironment",
]
