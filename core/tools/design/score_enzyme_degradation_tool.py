#!/usr/bin/env python3
"""
酶降解能力评分工具
负责计算 S_microbe 中的 kcat 相关指标
"""

from __future__ import annotations

import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover - fallback for standalone tests
    class BaseTool:  # type: ignore
        """后备 BaseTool，用于未安装 CrewAI 时的本地测试"""

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
            super().__init__()

    print("Warning: crewai 未安装，ScoreEnzymeDegradationTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field, validator


class ScoreEnzymeDegradationInput(BaseModel):
    """酶降解评分工具输入"""

    pollutant_smiles: str = Field(..., description="目标污染物的 SMILES 表达式")
    enzyme_sequences: List[str] = Field(
        ..., description="候选酶的氨基酸序列列表（FASTA 中的序列部分）"
    )
    reference_kcat: Optional[float] = Field(
        default=None,
        description="可选基准 kcat（1/s），用于对结果进行归一化时的参考",
    )

    @validator("enzyme_sequences")
    def validate_sequences(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("enzyme_sequences 不能为空")
        for seq in value:
            if not seq or not seq.strip():
                raise ValueError("存在空的氨基酸序列")
            if any(ch.isdigit() for ch in seq):
                raise ValueError("氨基酸序列中不应包含数字")
        return value


class ScoreEnzymeDegradationTool(BaseTool):
    """根据氨基酸序列与污染物描述估算 kcat 指标"""

    name: str = "ScoreEnzymeDegradationTool"
    description: str = (
        "根据候选酶序列与污染物 SMILES 估算降解速率 (kcat)。"
        "返回每条序列的 kcat 估计值、最大值、平均值以及归一化结果。"
    )
    args_schema: type[BaseModel] = ScoreEnzymeDegradationInput

    def _run(
        self,
        pollutant_smiles: str,
        enzyme_sequences: List[str],
        reference_kcat: Optional[float] = None,
    ) -> Dict[str, Any]:
        try:
            raw_scores = [
                self._estimate_kcat(sequence, pollutant_smiles)
                for sequence in enzyme_sequences
            ]
            kcat_max = max(raw_scores)
            kcat_mean = statistics.mean(raw_scores)

            min_score = min(raw_scores)
            score_range = kcat_max - min_score
            if math.isclose(score_range, 0.0):
                norm_scores = [1.0 for _ in raw_scores]
            else:
                norm_scores = [
                    (score - min_score) / score_range for score in raw_scores
                ]

            reference = reference_kcat or kcat_max
            kcat_normalized = (
                kcat_max / reference if reference and reference > 0 else 1.0
            )

            data = [
                {
                    "sequence_index": idx,
                    "length": len(seq),
                    "estimated_kcat": raw,
                    "normalized_within_batch": norm,
                }
                for idx, (seq, raw, norm) in enumerate(
                    zip(enzyme_sequences, raw_scores, norm_scores)
                )
            ]

            return {
                "status": "success",
                "pollutant_smiles": pollutant_smiles,
                "kcat_max": kcat_max,
                "kcat_mean": kcat_mean,
                "relative_to_reference": kcat_normalized,
                "entries": data,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"kcat 估算失败: {exc}",
            }

    @staticmethod
    def _estimate_kcat(sequence: str, smiles: str) -> float:
        """
        使用简单启发式估算 kcat。
        由于缺乏外部模型，这里采用长度、疏水性近似以及污染物复杂度的组合。
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
