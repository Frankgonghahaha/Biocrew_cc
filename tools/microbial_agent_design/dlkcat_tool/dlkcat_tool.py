#!/usr/bin/env python3
"""
DLkcat工具
用于预测降解酶对于特定底物的降解速率
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import subprocess
import pandas as pd
import os
import sys
from pathlib import Path

class DLkcatToolInput(BaseModel):
    script_path: str = Field(..., description="prediction_for_input.py的完整路径")
    file_path: str = Field(..., description="输入Excel文件路径")
    output_path: Optional[str] = Field(None, description="输出Excel文件路径")

class DLkcatTool(BaseTool):
    name: str = "DLkcatTool"
    description: str = "用于预测降解酶对于特定底物的降解速率的工具"
    args_schema = DLkcatToolInput
    
    def _run(self, script_path: str, file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        运行DLkcat预测工具
        
        Args:
            script_path: prediction_for_input.py的完整路径
            file_path: 输入Excel文件路径
            output_path: 输出Excel文件路径（可选）
            
        Returns:
            dict: 预测结果
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"输入Excel文件不存在: {file_path}"}
            
            # 检查预测脚本是否存在
            if not os.path.exists(script_path):
                return {"status": "error", "message": f"预测脚本不存在: {script_path}"}
            
            # 使用系统Python路径
            python_executable = sys.executable
            
            # 构建命令
            cmd = [python_executable, "/home/axlhuang/Agent-tool/DesignAgent/Tool_DLkcat/run_DLkcat.py"]
            cmd.extend(["--script-path", script_path])
            cmd.extend(["--file-path", file_path])
            
            if output_path:
                cmd.extend(["--output-path", output_path])
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"status": "error", "message": f"DLkcat执行失败: {result.stderr}"}
            
            # 确定输出文件路径
            if output_path:
                output_file = output_path
            else:
                input_path = Path(file_path)
                output_file = input_path.with_name("Sheet3_Function_enzyme_kact.xlsx")
            
            # 检查输出文件是否存在
            if not os.path.exists(output_file):
                return {"status": "error", "message": f"输出文件未生成: {output_file}"}
            
            # 读取输出文件
            df = pd.read_excel(output_file)
            
            # 提取Kcat值
            kcat_values = []
            if "Kcat value (1/s)" in df.columns:
                kcat_values = df["Kcat value (1/s)"].tolist()
            
            return {
                "status": "success", 
                "data": {
                    "output_file": str(output_file),
                    "kcat_values": kcat_values,
                    "row_count": len(df)
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"执行DLkcat时出错: {str(e)}"}