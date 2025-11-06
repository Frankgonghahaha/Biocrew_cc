#!/usr/bin/env python3
"""
针对 ScoreCandidateTool 的快速集成测试。
读取识别阶段产出的 JSON 结果，构造候选菌输入并打印综合得分。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.tools.design.score_candidate_tool import (  # noqa: E402
    CandidateMicrobe,
    ScoreCandidateTool,
    TargetEnvironment,
)


def load_microbes_from_json(
    json_path: Path,
) -> tuple[list[CandidateMicrobe], Optional[str], dict[str, Any]]:
    """将识别阶段 JSON 数据转换为 ScoreCandidateTool 输入。"""
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    microbes: list[CandidateMicrobe] = []

    for record in payload.get("functional_microbes", []):
        enzyme_sequences = [
            enzyme.get("sequence", "").strip()
            for enzyme in record.get("enzymes", [])
            if enzyme.get("sequence")
        ]
        microbes.append(
            CandidateMicrobe(
                species=record.get("strain", "unknown"),
                source="functional",
                # 识别阶段未给出 kcat 与环境评分，缺失项在工具内会按 0 处理。
                kcat_max=None,
                kcat_mean=None,
                environment_match=None,
                enzyme_diversity=record.get("enzyme_diversity"),
                enzyme_sequences=enzyme_sequences or None,
                metadata={
                    "degradation_steps": record.get("degradation_steps", []),
                    "complements": record.get("complements", []),
                },
            )
        )

        for comp in record.get("complements", []):
            microbes.append(
                CandidateMicrobe(
                    species=comp.get("strain", "unknown"),
                    source="complement",
                    kcat_max=None,
                    kcat_mean=None,
                    environment_match=comp.get("relation_score", {}).get(
                        "complementarity"
                    ),
                    enzyme_diversity=None,
                    metadata={
                        "relation_score": comp.get("relation_score"),
                        "parent_functional": record.get("strain"),
                    },
                )
            )

    if not microbes:
        raise ValueError("未在 JSON 中找到功能菌或互补菌数据。")

    pollutant_smiles = (
        payload.get("metadata", {})
        .get("pollutant", {})
        .get("smiles")
    )
    target_env = payload.get("metadata", {}).get("target_environment", {})
    return microbes, pollutant_smiles, target_env


def main() -> None:
    target_file = (
        PROJECT_ROOT
        / "test_results"
        / "IdentificationAgent_Result_2025-06-21T12-45-33.json"
    )

    if not target_file.exists():
        raise FileNotFoundError(f"找不到指定 JSON：{target_file}")

    microbes, pollutant_smiles, target_env = load_microbes_from_json(target_file)

    target_env_model = (
        TargetEnvironment(**target_env) if target_env else None
    )

    tool = ScoreCandidateTool()
    result = tool._run(
        microbes=microbes,
        pollutant_smiles=pollutant_smiles,
        target_environment=target_env_model,
    )

    if result.get("status") != "success":
        raise RuntimeError(f"打分失败: {result}")

    summary = result.get("summary", {})
    print("打分成功：")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\n详细打分列表：")
    for record in result.get("records", []):
        print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
