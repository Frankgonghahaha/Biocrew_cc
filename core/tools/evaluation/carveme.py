#!/usr/bin/env python3
"""
CarveMe 调用封装
利用 core/tools/external/build_GSMM_from_aa.py 批量构建代谢模型。
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field


class CarvemeToolInput(BaseModel):
    """CarveMe 工具输入"""

    input_path: str = Field(..., description="包含 .aa/.faa 的目录")
    output_path: str = Field(..., description="模型输出目录")
    threads: int = Field(default=4, description="并行线程数")
    overwrite: bool = Field(default=False, description="是否覆盖已存在的模型")
    genomes_path: Optional[str] = Field(
        default=None,
        description="可选：包含 .fa/.fna 的目录，先用 Prodigal 生成 .aa",
    )
    carve_cmd: str = Field(default="carve", description="CarveMe 命令名（默认 carve）")
    prodigal_cmd: str = Field(default="prodigal", description="Prodigal 命令名（默认 prodigal）")
    prodigal_mode: str = Field(default="meta", description="Prodigal 模式（meta/single）")
    carve_extra: Optional[List[str]] = Field(
        default=None,
        description="传递给 carve 的额外参数（示例：['--fbc2','--universal-model','bacteria'])",
    )
    validate: bool = Field(
        default=False,
        description="是否启用 validate 标志（占位，用于与旧版调用保持一致）",
    )


class CarvemeTool(BaseTool):
    """CarveMe 工具封装"""

    name: str = "CarvemeTool"
    description: str = "调用 build_GSMM_from_aa.py，根据 .faa/.aa 构建代谢模型"
    args_schema: type[BaseModel] = CarvemeToolInput

    def _run(
        self,
        input_path: str,
        output_path: str,
        threads: int = 4,
        overwrite: bool = False,
        genomes_path: Optional[str] = None,
        carve_cmd: str = "carve",
        prodigal_cmd: str = "prodigal",
        prodigal_mode: str = "meta",
        carve_extra: Optional[List[str]] = None,
        validate: bool = False,
    ) -> Dict[str, Any]:
        try:
            input_dir = Path(input_path).expanduser()
            output_dir = Path(output_path).expanduser()
            if not input_dir.is_dir():
                return {
                    "status": "error",
                    "message": f"输入目录不存在或为空: {input_dir}",
                }
            output_dir.mkdir(parents=True, exist_ok=True)

            script_path = (
                Path(__file__).resolve().parents[1] / "external" / "build_GSMM_from_aa.py"
            )
            if not script_path.is_file():
                return {
                    "status": "error",
                    "message": f"未找到构建脚本: {script_path}",
                }

            cmd = [
                sys.executable,
                str(script_path),
                "--input_path",
                str(input_dir),
                "--output_path",
                str(output_dir),
                "--threads",
                str(threads),
                "--carve_cmd",
                carve_cmd,
                "--prodigal_cmd",
                prodigal_cmd,
                "--prodigal_mode",
                prodigal_mode,
            ]

            if overwrite:
                cmd.append("--overwrite")
            if validate:
                cmd.append("--validate")
            if genomes_path:
                cmd.extend(["--genomes_path", str(Path(genomes_path).expanduser())])
            if carve_extra:
                cmd.append("--carve_extra")
                cmd.extend(carve_extra)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": (
                        "CarveMe 脚本执行失败。\n"
                        f"命令: {' '.join(cmd)}\n"
                        f"stdout: {result.stdout}\n"
                        f"stderr: {result.stderr}"
                    ),
                }

            model_files = sorted(str(p) for p in output_dir.glob("*.xml"))
            return {
                "status": "success",
                "output_path": str(output_dir),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "model_files": model_files,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"CarveMe 调用失败: {exc}",
            }


__all__ = ["CarvemeTool", "CarvemeToolInput"]
