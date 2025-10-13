#!/usr/bin/env python3
"""
Carveme工具
用于批量构建基因组规模代谢模型(GSMM)
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import subprocess
import os
import sys
from pathlib import Path

class CarvemeToolInput(BaseModel):
    input_path: str = Field(..., description="包含.aa/.faa文件的目录路径")
    output_path: str = Field(..., description="输出SBML(.xml)文件的目录")
    genomes_path: Optional[str] = Field(None, description="包含基因组文件的目录路径（可选）")
    threads: int = Field(4, description="并行线程数")
    overwrite: bool = Field(False, description="是否覆盖已存在的模型文件")
    carve_extra: Optional[List[str]] = Field(None, description="透传给CarveMe的额外参数")

class CarvemeTool(BaseTool):
    name: str = "CarvemeTool"
    description: str = "用于批量构建基因组规模代谢模型(GSMM)的工具"
    args_schema = CarvemeToolInput
    
    def _run(self, input_path: str, output_path: str, genomes_path: Optional[str] = None, 
             threads: int = 4, overwrite: bool = False, carve_extra: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        运行Carveme工具构建代谢模型
        
        Args:
            input_path: 包含.aa/.faa文件的目录路径
            output_path: 输出SBML(.xml)文件的目录
            genomes_path: 包含基因组文件的目录路径（可选）
            threads: 并行线程数
            overwrite: 是否覆盖已存在的模型文件
            carve_extra: 透传给CarveMe的额外参数
            
        Returns:
            dict: 构建结果
        """
        try:
            # 检查输入目录是否存在
            if not os.path.exists(input_path):
                return {"status": "error", "message": f"输入目录不存在: {input_path}"}
            
            # 创建输出目录
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # 使用系统Python路径
            python_executable = sys.executable
            
            # 构建命令
            cmd = [python_executable, "/home/axlhuang/Agent-tool/Tool_Carveme/build_GSMM_from_aa.py"]
            cmd.extend(["--input_path", input_path])
            cmd.extend(["--output_path", output_path])
            cmd.extend(["--threads", str(threads)])
            
            if overwrite:
                cmd.append("--overwrite")
            
            if genomes_path:
                cmd.extend(["--genomes_path", genomes_path])
            
            if carve_extra:
                cmd.append("--carve_extra")
                cmd.extend(carve_extra)
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"status": "error", "message": f"Carveme执行失败: {result.stderr}"}
            
            # 统计输出文件
            output_files = list(Path(output_path).glob("*.xml"))
            
            return {
                "status": "success", 
                "data": {
                    "output_path": output_path,
                    "model_count": len(output_files),
                    "output_files": [str(f) for f in output_files]
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"执行Carveme时出错: {str(e)}"}