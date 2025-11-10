#!/usr/bin/env python3
"""
CarveMe FAA 构建工具
基于 FAA 目录批量构建代谢模型，并输出到 EvaluateAgent 专用目录。
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field, validator

from core.tools.evaluation.carveme import CarvemeTool

DEFAULT_FAA_DIR = (
    Path(__file__).resolve().parents[3]
    / "test_results"
    / "EvaluateAgent"
    / "faa"
)
DEFAULT_MODEL_DIR = (
    Path(__file__).resolve().parents[3]
    / "test_results"
    / "EvaluateAgent"
    / "Model"
)


class CarvemeModelBuildInput(BaseModel):
    """CarveMe FAA 构建工具输入"""

    faa_dir: str = Field(
        default=str(DEFAULT_FAA_DIR),
        description="FAA 文件所在目录（由 FaaBuildTool 生成）",
    )
    output_dir: str = Field(
        default=str(DEFAULT_MODEL_DIR),
        description="模型输出目录，默认 test_results/EvaluateAgent/Model",
    )
    threads: int = Field(default=4, description="CarveMe 并行线程数")
    overwrite: bool = Field(
        default=False,
        description="若输出目录中已存在对应模型，是否强制覆盖",
    )

    @validator("threads")
    def validate_threads(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("threads 必须 > 0")
        return value


class CarvemeModelBuildTool(BaseTool):
    """封装 CarveMe 以 FAA 为输入构建模型的工具"""

    name: str = "CarvemeModelBuildTool"
    description: str = (
        "扫描 FAA 目录，必要时调用 CarvemeTool 构建代谢模型，输出到 test_results/EvaluateAgent/Model"
    )
    args_schema: type[BaseModel] = CarvemeModelBuildInput

    def __init__(self) -> None:
        super().__init__()
        self._carveme = CarvemeTool()

    def _run(
        self,
        faa_dir: str,
        output_dir: str,
        threads: int = 4,
        overwrite: bool = False,
    ) -> Dict[str, Optional[str]]:
        faa_path = Path(faa_dir).expanduser()
        model_path = Path(output_dir).expanduser()

        if not faa_path.is_dir():
            return {
                "status": "error",
                "message": f"FAA 目录不存在：{faa_path}",
            }

        model_path.mkdir(parents=True, exist_ok=True)

        faa_files = sorted(faa_path.glob("*.faa"))
        if not faa_files:
            return {
                "status": "error",
                "message": f"FAA 目录中未找到 .faa 文件：{faa_path}",
            }

        targets: List[str] = []
        skipped: List[str] = []
        for faa_file in faa_files:
            model_file = model_path / f"{faa_file.stem}.xml"
            if model_file.exists() and not overwrite:
                skipped.append(str(model_file))
            else:
                targets.append(str(model_file))

        if not targets:
            return {
                "status": "success",
                "message": "模型已存在，跳过构建。",
                "output_dir": str(model_path),
                "generated_models": skipped,
                "skipped_models": skipped,
            }

        result = self._carveme._run(
            input_path=str(faa_path),
            output_path=str(model_path),
            threads=threads,
            overwrite=overwrite,
        )

        if result.get("status") != "success":
            return result

        model_files = sorted(str(p) for p in model_path.glob("*.xml"))
        return {
            "status": "success",
            "output_dir": str(model_path),
            "generated_models": model_files,
            "skipped_models": skipped,
        }


__all__ = ["CarvemeModelBuildTool", "CarvemeModelBuildInput"]
