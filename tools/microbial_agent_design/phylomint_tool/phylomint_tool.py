#!/usr/bin/env python3
"""
Phylomint工具
用于分析微生物间的代谢互补性和竞争性
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import subprocess
import os
import sys
from pathlib import Path

class PhylomintToolInput(BaseModel):
    phylo_path: Optional[str] = Field(None, description="PhyloMInt可执行文件路径")
    models_path: Optional[str] = Field(None, description="代谢模型目录路径")
    output_path: str = Field(..., description="输出文件路径")
    function_species_csv: Optional[str] = Field(None, description="功能物种列表CSV文件路径")
    skip_preprocess: bool = Field(False, description="是否跳过预处理步骤")

class PhylomintTool(BaseTool):
    name: str = "PhylomintTool"
    description: str = "用于分析微生物间代谢互补性和竞争性的工具"
    args_schema = PhylomintToolInput
    
    def _run(self, output_path: str, phylo_path: Optional[str] = None, models_path: Optional[str] = None, 
             function_species_csv: Optional[str] = None, skip_preprocess: bool = False) -> Dict[str, Any]:
        """
        运行Phylomint工具分析微生物互作关系
        
        Args:
            phylo_path: PhyloMInt可执行文件路径
            models_path: 代谢模型目录路径
            output_path: 输出文件路径
            function_species_csv: 功能物种列表CSV文件路径
            skip_preprocess: 是否跳过预处理步骤
            
        Returns:
            dict: 分析结果
        """
        try:
            # 创建输出目录
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 使用系统Python路径
            python_executable = sys.executable
            
            # 构建命令
            cmd = [python_executable, "/home/axlhuang/Agent-tool/Tool_Phylomint/run_phylomint.py"]
            cmd.extend(["--output", output_path])
            
            if phylo_path:
                cmd.extend(["--phylo", phylo_path])
            
            if models_path:
                cmd.extend(["--models", models_path])
            
            if function_species_csv:
                cmd.extend(["--function-species-csv", function_species_csv])
            
            if skip_preprocess:
                cmd.append("--skip-preprocess")
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"status": "error", "message": f"Phylomint执行失败: {result.stderr}"}
            
            # 检查输出文件是否存在
            if not os.path.exists(output_path):
                return {"status": "error", "message": f"输出文件未生成: {output_path}"}
            
            # 如果有Excel输出文件，也检查其存在性
            excel_output = Path(output_path).with_name("互补微生物识别结果.xlsx")
            excel_exists = os.path.exists(excel_output)
            
            return {
                "status": "success", 
                "data": {
                    "output_path": output_path,
                    "excel_output": str(excel_output) if excel_exists else None,
                    "excel_exists": excel_exists
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"执行Phylomint时出错: {str(e)}"}