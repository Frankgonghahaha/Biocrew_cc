#!/usr/bin/env python3
"""
识别阶段 JSON 解析工具（环境适应性输入）
提取功能菌及互补菌清单，并解析目标环境参数，供环境评分与后续工具使用。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover - fallback
    class BaseTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()

    print("Warning: crewai 未安装，ParseEnvironmentJSONTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field


class ParseEnvironmentJSONInput(BaseModel):
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


class ParseEnvironmentJSONTool(BaseTool):
    """提取物种清单与目标环境参数"""

    name: str = "ParseEnvironmentJSONTool"
    description: str = (
        "解析 IdentificationAgent 输出的功能菌与互补菌物种，并提取目标环境 "
        "(temperature/ph/salinity/oxygen) 参数，为 ScoreEnvironmentTool 与后续评分提供输入。"
    )
    args_schema: type[BaseModel] = ParseEnvironmentJSONInput

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

            species: List[Dict[str, Any]] = []
            seen: Set[str] = set()

            for entry in functional_microbes:
                strain = str(entry.get("strain") or "").strip()
                if strain:
                    normalized = self._normalize_name(strain)
                    if normalized not in seen:
                        seen.add(normalized)
                        species.append(
                            {
                                "strain": normalized,
                                "source": "functional",
                            }
                        )

                for comp in entry.get("complements", []) or []:
                    comp_strain = str(comp.get("strain") or "").strip()
                    if not comp_strain:
                        continue
                    normalized_comp = self._normalize_name(comp_strain)
                    if normalized_comp in seen:
                        continue
                    seen.add(normalized_comp)
                    species.append(
                        {
                            "strain": normalized_comp,
                            "source": "complement",
                            "parent_functional": strain or None,
                        }
                    )

            metadata = data.get("metadata", {}) or {}
            target_environment = metadata.get("target_environment") or {}
            pollutant_name, pollutant_smiles = ParseEnvironmentJSONTool._extract_pollutant(metadata)

            return {
                "status": "success",
                "species": species,
                "target_environment": target_environment,
                "pollutant_smiles": pollutant_smiles,
                "pollutant_name": pollutant_name,
                "metadata": data.get("metadata", {}),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"环境参数解析失败: {exc}",
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

    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join(name.replace("（", "(").replace("）", ")").split()).strip()


__all__ = ["ParseEnvironmentJSONTool", "ParseEnvironmentJSONInput"]
