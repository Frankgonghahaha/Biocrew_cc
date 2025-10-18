#!/usr/bin/env python3
"""
中间产物检查工具
用于检查和验证各阶段中间产物的完整性和正确性
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import os
import json
from pathlib import Path

class IntermediateProductCheckToolInput(BaseModel):
    check_type: str = Field(..., description="检查类型: 'genome_features', 'metabolic_models', 'reactions', 'all'")
    output_dir: str = Field("./outputs", description="输出目录路径")

class IntermediateProductCheckTool(BaseTool):
    name: str = "IntermediateProductCheckTool"
    description: str = "用于检查和验证各阶段中间产物的完整性和正确性"
    args_schema = IntermediateProductCheckToolInput
    
    def _run(self, check_type: str, output_dir: str = "./outputs") -> Dict[str, Any]:
        """
        运行中间产物检查工具
        
        Args:
            check_type: 检查类型 ('genome_features', 'metabolic_models', 'reactions', 'all')
            output_dir: 输出目录路径
            
        Returns:
            dict: 检查结果
        """
        try:
            results = {}
            
            if check_type in ["genome_features", "all"]:
                results["genome_features"] = self._check_genome_features(output_dir)
            
            if check_type in ["metabolic_models", "all"]:
                results["metabolic_models"] = self._check_metabolic_models(output_dir)
            
            if check_type in ["reactions", "all"]:
                results["reactions"] = self._check_reactions(output_dir)
            
            return {
                "status": "success",
                "data": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查中间产物时出错: {str(e)}"
            }
    
    def _check_genome_features(self, output_dir: str) -> Dict[str, Any]:
        """检查基因组特征文件"""
        genome_features_dir = Path(output_dir) / "genome_features"
        
        if not genome_features_dir.exists():
            return {
                "status": "error",
                "message": f"基因组特征目录不存在: {genome_features_dir}"
            }
        
        # 获取所有文件
        json_files = list(genome_features_dir.glob("*.json"))
        tsv_files = list(genome_features_dir.glob("*.tsv"))
        
        # 检查文件配对
        json_names = {f.stem for f in json_files}
        tsv_names = {f.stem for f in tsv_files}
        
        # 检查内容
        valid_files = []
        invalid_files = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # 检查基本结构
                if isinstance(data, dict) and len(data) > 0:
                    valid_files.append(str(json_file))
                else:
                    invalid_files.append((str(json_file), "JSON结构无效"))
            except Exception as e:
                invalid_files.append((str(json_file), f"JSON解析失败: {str(e)}"))
        
        return {
            "status": "success",
            "total_files": len(json_files) + len(tsv_files),
            "json_files": len(json_files),
            "tsv_files": len(tsv_files),
            "paired_files": len(json_names & tsv_names),
            "valid_json_files": len(valid_files),
            "invalid_files": invalid_files,
            "details": {
                "valid_files": valid_files,
                "json_names": list(json_names),
                "tsv_names": list(tsv_names)
            }
        }
    
    def _check_metabolic_models(self, output_dir: str) -> Dict[str, Any]:
        """检查代谢模型文件"""
        metabolic_models_dir = Path(output_dir) / "metabolic_models"
        
        if not metabolic_models_dir.exists():
            return {
                "status": "warning",
                "message": f"代谢模型目录不存在: {metabolic_models_dir} (可能是尚未生成)"
            }
        
        # 获取所有SBML文件
        sbml_files = list(metabolic_models_dir.glob("*.xml"))
        
        # 检查文件大小
        valid_files = []
        empty_files = []
        
        for sbml_file in sbml_files:
            try:
                size = sbml_file.stat().st_size
                if size > 0:
                    valid_files.append((str(sbml_file), size))
                else:
                    empty_files.append(str(sbml_file))
            except Exception as e:
                empty_files.append(f"{sbml_file} (无法获取大小: {str(e)})")
        
        return {
            "status": "success",
            "total_files": len(sbml_files),
            "valid_files": valid_files,
            "empty_files": empty_files,
            "details": {
                "file_list": [str(f) for f in sbml_files]
            }
        }
    
    def _check_reactions(self, output_dir: str) -> Dict[str, Any]:
        """检查反应数据文件"""
        reactions_dir = Path(output_dir.replace("outputs", "data")) / "reactions"
        
        if not reactions_dir.exists():
            reactions_dir = Path(output_dir) / "data" / "reactions"
            if not reactions_dir.exists():
                return {
                    "status": "error",
                    "message": f"反应数据目录不存在: {reactions_dir}"
                }
        
        # 获取所有CSV文件
        csv_files = list(reactions_dir.glob("*.csv"))
        
        # 检查文件内容
        valid_files = []
        invalid_files = []
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                
                # 检查基本结构
                if len(lines) >= 2:  # 至少包含标题行和一行数据
                    header = lines[0].strip().split(',')
                    if 'id' in header and 'Reaction equation' in header:
                        valid_files.append((str(csv_file), len(lines) - 1))  # 减去标题行
                    else:
                        invalid_files.append((str(csv_file), "缺少必要列"))
                else:
                    invalid_files.append((str(csv_file), "文件行数不足"))
            except Exception as e:
                invalid_files.append((str(csv_file), f"文件读取失败: {str(e)}"))
        
        return {
            "status": "success",
            "total_files": len(csv_files),
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "details": {
                "file_list": [str(f) for f in csv_files]
            }
        }