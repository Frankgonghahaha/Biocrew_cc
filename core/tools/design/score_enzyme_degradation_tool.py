#!/usr/bin/env python3
"""
酶降解能力评分工具
基于解析后的功能菌酶序列与污染物 SMILES 估算 kcat 指标。
"""

from __future__ import annotations

import math
import statistics
from typing import Any, Dict, List, Optional

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover - fallback
    class BaseTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()

    print("Warning: crewai 未安装，ScoreEnzymeDegradationTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field, validator


class SpeciesEnzymePayload(BaseModel):
    """单个微生物的酶序列信息"""

    strain: str = Field(..., description="物种名称")
    sequences: List[str] = Field(
        default_factory=list,
        description="该物种的氨基酸序列集合（可能为空，表示缺失）。",
    )
    source: Optional[str] = Field(
        default=None,
        description="来源标签，例如 functional / complement。",
    )
    enzyme_names: Optional[List[str]] = Field(
        default=None,
        description="酶名称列表，可用于计算多样性。",
    )
    enzyme_diversity: Optional[int] = Field(
        default=None,
        description="酶多样性计数（去重后）。",
    )

    @validator("strain")
    def normalize_strain(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("strain 不能为空")
        return text

    @validator("sequences", each_item=True)
    def sanitize_sequence(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("存在空的氨基酸序列")
        if any(char.isdigit() for char in text):
            raise ValueError("氨基酸序列中不应包含数字")
        return text


class ScoreEnzymeDegradationInput(BaseModel):
    """酶降解评分工具输入"""

    pollutant_smiles: str = Field(
        ...,
        description="目标污染物的 SMILES 表达式（视作底物描述）。",
    )
    species: List[SpeciesEnzymePayload] = Field(
        ..., description="待评估的微生物及其酶序列列表。"
    )
    reference_kcat: Optional[float] = Field(
        default=None,
        description="可选参考 kcat，用于归一化。",
    )

    @validator("species")
    def ensure_species(cls, value: List[SpeciesEnzymePayload]) -> List[SpeciesEnzymePayload]:
        if not value:
            raise ValueError("species 列表不能为空")
        return value

    @validator("pollutant_smiles")
    def ensure_smiles(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("pollutant_smiles 不能为空")
        return text


class ScoreEnzymeDegradationTool(BaseTool):
    """根据氨基酸序列与污染物描述估算 kcat 指标"""

    name: str = "ScoreEnzymeDegradationTool"
    description: str = (
        "接收 ParseDegradationJSONTool 解析出的酶序列列表以及污染物 SMILES，"
        "对每个物种估算 kcat_max、kcat_mean，并返回序列级别详情。"
    )
    args_schema: type[BaseModel] = ScoreEnzymeDegradationInput

    def _run(
        self,
        pollutant_smiles: str,
        species: List[SpeciesEnzymePayload],
        reference_kcat: Optional[float] = None,
    ) -> Dict[str, Any]:
        try:
            normalized_species: List[SpeciesEnzymePayload] = []
            for entry in species:
                if isinstance(entry, SpeciesEnzymePayload):
                    normalized_species.append(entry)
                elif isinstance(entry, dict):
                    payload = dict(entry)
                    sequences = payload.get("sequences")
                    if sequences is None:
                        sequences = payload.get("enzyme_sequences")
                    payload.setdefault("sequences", sequences or [])
                    payload["strain"] = str(payload.get("strain", "")).strip()
                    normalized_species.append(SpeciesEnzymePayload.parse_obj(payload))
                else:
                    raise TypeError(
                        f"species 列表中的元素类型不受支持: {type(entry)}。"
                    )

            overall_results: List[Dict[str, Any]] = []

            for entry in normalized_species:
                sequences = entry.sequences
                if not sequences:
                    overall_results.append(
                        {
                            "strain": entry.strain,
                            "source": entry.source,
                            "kcat_max": 0.0,
                            "kcat_mean": 0.0,
                            "reference_ratio": 0.0,
                            "entries": [],
                            "sequence_count": 0,
                            "enzyme_diversity": entry.enzyme_diversity or 0,
                            "status": "no_sequence",
                            "message": "未提供氨基酸序列，kcat 设为 0。",
                        }
                    )
                    continue

                raw_scores = [
                    self._estimate_kcat(seq, pollutant_smiles) for seq in sequences
                ]
                kcat_max = max(raw_scores)
                kcat_mean = statistics.mean(raw_scores)

                min_score = min(raw_scores)
                span = kcat_max - min_score
                if math.isclose(span, 0.0):
                    normalized = [1.0 for _ in raw_scores]
                else:
                    normalized = [(score - min_score) / span for score in raw_scores]

                reference = reference_kcat or kcat_max
                ratio = kcat_max / reference if reference and reference > 0 else 1.0

                sequence_details = [
                    {
                        "sequence_index": idx,
                        "length": len(seq),
                        "estimated_kcat": raw,
                        "normalized_within_species": norm,
                    }
                    for idx, (seq, raw, norm) in enumerate(
                        zip(sequences, raw_scores, normalized)
                    )
                ]

                overall_results.append(
                    {
                        "strain": entry.strain,
                        "source": entry.source,
                        "kcat_max": kcat_max,
                        "kcat_mean": kcat_mean,
                        "reference_ratio": ratio,
                        "entries": sequence_details,
                        "sequence_count": len(sequences),
                        "enzyme_diversity": entry.enzyme_diversity or len(sequences),
                        "status": "success",
                    }
                )

            return {
                "status": "success",
                "pollutant_smiles": pollutant_smiles,
                "reference_kcat": reference_kcat,
                "results": overall_results,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"kcat 估算失败: {exc}",
            }

    @staticmethod
    def _estimate_kcat(sequence: str, smiles: str) -> float:
        """
        使用启发式估算 kcat。
        由于缺乏外部模型，这里采用序列长度、氨基酸性质与 SMILES 复杂度的组合。
        """
        seq = sequence.strip().upper()
        length = len(seq)
        hydrophobic_residues = {"A", "V", "I", "L", "M", "F", "W", "Y"}
        polar_residues = {"S", "T", "N", "Q", "C"}

        hydro_count = sum(1 for ch in seq if ch in hydrophobic_residues)
        polar_count = sum(1 for ch in seq if ch in polar_residues)

        smiles_complexity = len(smiles)
        aromatic_count = smiles.count("c")
        hetero_count = sum(smiles.count(atom) for atom in ["N", "O", "S", "P"])

        base = 0.05 * length + 0.02 * hydro_count + 0.01 * polar_count
        modifier = 0.03 * aromatic_count + 0.02 * hetero_count
        complexity = max(1.0, math.log1p(smiles_complexity))

        kcat = base * complexity + modifier
        return max(0.1, round(kcat, 4))


__all__ = [
    "ScoreEnzymeDegradationTool",
    "ScoreEnzymeDegradationInput",
    "SpeciesEnzymePayload",
]
