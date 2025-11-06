#!/usr/bin/env python3
"""
识别阶段 JSON 解析工具（酶降解输入）
负责从 IdentificationAgent 结果中提取功能菌酶序列与污染物 SMILES，
为 ScoreEnzymeDegradationTool 提供标准化输入。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover - fallback
    class BaseTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()

    print("Warning: crewai 未安装，ParseDegradationJSONTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field


class ParseDegradationJSONInput(BaseModel):
    """解析识别阶段 JSON 的输入参数"""

    json_path: Optional[str] = Field(
        default=None,
        description="IdentificationAgent 生成的 JSON 文件路径",
    )
    payload: Optional[Dict[str, Any]] = Field(
        default=None,
        description="直接传入的 JSON 数据对象（与文件内容同结构）。",
    )


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_IDENTIFICATION_DIR = PROJECT_ROOT / "test_results" / "IdentificationAgent"
DEFAULT_IDENTIFICATION_FILE = DEFAULT_IDENTIFICATION_DIR / "IdentificationAgent_Result_2025-06-21T12-45-33.json"


class ParseDegradationJSONTool(BaseTool):
    """提取功能菌酶序列与污染物信息"""

    name: str = "ParseDegradationJSONTool"
    description: str = (
        "解析 IdentificationAgent 输出，收集功能微生物的酶名称、氨基酸序列及多样性，"
        "并提取污染物 SMILES 信息，供 ScoreEnzymeDegradationTool 使用。"
    )
    args_schema: type[BaseModel] = ParseDegradationJSONInput

    def _run(
        self,
        json_path: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            if payload is None and not json_path:
                raise ValueError("必须提供 json_path 或 payload。")
            data = payload or self._load_json(json_path)  # type: ignore[arg-type]
            functional_microbes = data.get("functional_microbes") or []
            if not isinstance(functional_microbes, list):
                raise ValueError("JSON 中的 functional_microbes 格式不正确，应为列表。")

            functional_records: List[Dict[str, Any]] = []
            species_payload: List[Dict[str, Any]] = []
            for entry in functional_microbes:
                strain = str(entry.get("strain") or "").strip()
                enzymes = entry.get("enzymes") or []
                if not strain:
                    continue

                enzyme_entries: List[Dict[str, Any]] = []
                sequences: List[str] = []
                names: List[str] = []
                for enzyme in enzymes:
                    name = str(enzyme.get("name") or "").strip()
                    sequence = str(enzyme.get("sequence") or "").strip()
                    if not sequence:
                        continue
                    enzyme_entries.append(
                        {
                            "name": name or None,
                            "sequence": sequence,
                            "uniprot_id": enzyme.get("uniprot_id"),
                        }
                    )
                    sequences.append(sequence)
                    if name:
                        names.append(name)

                enzyme_diversity = len(set(filter(None, names))) if names else len(sequences)

                functional_records.append(
                    {
                        "strain": strain,
                        "source": "functional",
                        "enzymes": enzyme_entries,
                        "enzyme_sequences": sequences,
                        "enzyme_diversity": enzyme_diversity,
                        "metadata": {
                            "complements": entry.get("complements", []),
                            "degradation_steps": entry.get("degradation_steps"),
                        },
                    }
                )
                species_payload.append(
                    {
                        "strain": strain,
                        "sequences": sequences,
                        "source": "functional",
                        "enzyme_names": names or None,
                        "enzyme_diversity": enzyme_diversity,
                    }
                )

            pollutant_name, pollutant_smiles = self._extract_pollutant(data.get("metadata", {}))

            return {
                "status": "success",
                "pollutant_smiles": pollutant_smiles,
                "pollutant_name": pollutant_name,
                "functional_records": functional_records,
                "species_payload": species_payload,
                "metadata": {
                    "target_environment": data.get("metadata", {}).get("target_environment"),
                    "raw_metadata": data.get("metadata", {}),
                },
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"识别阶段 JSON 解析失败: {exc}",
            }

    @staticmethod
    def _load_json(json_path: Optional[str]) -> Dict[str, Any]:
        if not json_path:
            raise ValueError("未提供 json_path。")

        raw_path = Path(json_path).expanduser()
        candidate_files: List[Path] = []

        if DEFAULT_IDENTIFICATION_FILE.is_file():
            candidate_files.append(DEFAULT_IDENTIFICATION_FILE)

        if raw_path.is_file():
            candidate_files.append(raw_path)
        else:
            if raw_path.name:
                candidate_files.append(DEFAULT_IDENTIFICATION_DIR / raw_path.name)
            if raw_path.is_dir():
                candidate_files.extend(sorted(raw_path.glob("*.json")))

        if DEFAULT_IDENTIFICATION_DIR.exists():
            if DEFAULT_IDENTIFICATION_FILE not in candidate_files and DEFAULT_IDENTIFICATION_FILE.is_file():
                candidate_files.append(DEFAULT_IDENTIFICATION_FILE)
            if raw_path.name:
                candidate_files.append(DEFAULT_IDENTIFICATION_DIR / raw_path.name)
            candidate_files.extend(sorted(DEFAULT_IDENTIFICATION_DIR.glob("*.json")))

        for candidate in candidate_files:
            if candidate.is_file():
                with candidate.open("r", encoding="utf-8") as fh:
                    return json.load(fh)

        raise FileNotFoundError(
            f"未找到 JSON 文件：{json_path}（已在 {DEFAULT_IDENTIFICATION_DIR} 中搜索 *.json）"
        )

    @staticmethod
    def _extract_pollutant(metadata: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        pollutant_meta = metadata.get("pollutant")
        pollutant_name: Optional[str] = None
        pollutant_smiles: Optional[str] = None

        if isinstance(pollutant_meta, dict):
            pollutant_name = (
                pollutant_meta.get("name")
                or pollutant_meta.get("label")
                or pollutant_meta.get("identifier")
            )
            pollutant_smiles = (
                pollutant_meta.get("smiles")
                or pollutant_meta.get("Smiles")
                or pollutant_meta.get("SMILES")
            )
        else:
            if pollutant_meta:
                pollutant_name = str(pollutant_meta)
            pollutant_smiles = (
                metadata.get("pollutant_smiles")
                or metadata.get("Smiles")
                or metadata.get("smiles")
            )

        return pollutant_name, pollutant_smiles


__all__ = ["ParseDegradationJSONTool", "ParseDegradationJSONInput"]
