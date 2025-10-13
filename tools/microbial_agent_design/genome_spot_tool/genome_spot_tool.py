#!/usr/bin/env python3
"""
GenomeSPOT工具
用于预测微生物的环境适应性特征
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import sys
import os

# 添加Agent-tool到Python路径
sys.path.append("/home/axlhuang/Agent-tool/DesignAgent/Tool_GenomeSPOT/Code")

class GenomeSPOTToolInput(BaseModel):
    fna_path: str = Field(..., description="基因组contigs文件路径（FASTA格式）")
    faa_path: str = Field(..., description="基因组蛋白质文件路径（FASTA格式）")
    models_path: str = Field(..., description="GenomeSPOT模型目录路径")
    output_prefix: Optional[str] = Field(None, description="输出文件前缀")

class GenomeSPOTTool(BaseTool):
    name: str = "GenomeSPOTTool"
    description: str = "用于预测微生物环境适应性特征的工具，包括温度、pH、盐度和氧气耐受性"
    args_schema = GenomeSPOTToolInput
    
    def _run(self, fna_path: str, faa_path: str, models_path: str, output_prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        运行GenomeSPOT预测工具
        
        Args:
            fna_path: 基因组contigs文件路径（FASTA格式）
            faa_path: 基因组蛋白质文件路径（FASTA格式）
            models_path: GenomeSPOT模型目录路径
            output_prefix: 输出文件前缀
            
        Returns:
            dict: 预测结果
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(fna_path):
                return {"status": "error", "message": f"基因组contigs文件不存在: {fna_path}"}
            
            if not os.path.exists(faa_path):
                return {"status": "error", "message": f"基因组蛋白质文件不存在: {faa_path}"}
            
            if not os.path.exists(models_path):
                return {"status": "error", "message": f"模型目录不存在: {models_path}"}
            
            # 导入GenomeSPOT模块
            from genome_spot.genome_spot import run_genome_spot, save_results
            
            # 运行预测
            predictions, genome_features = run_genome_spot(
                fna_path=fna_path,
                faa_path=faa_path,
                path_to_models=models_path
            )
            
            # 保存结果
            if output_prefix:
                save_results(
                    predictions=predictions,
                    genome_features=genome_features,
                    output_prefix=output_prefix
                )
            
            # 格式化结果
            formatted_result = self._format_predictions(predictions)
            return {"status": "success", "data": formatted_result}
            
        except Exception as e:
            return {"status": "error", "message": f"执行GenomeSPOT时出错: {str(e)}"}
    
    def _format_predictions(self, predictions: Dict) -> Dict[str, Any]:
        """
        格式化预测结果
        
        Args:
            predictions: GenomeSPOT原始预测结果
            
        Returns:
            dict: 格式化的预测结果
        """
        result = {}
        
        # 解析温度预测
        if "temperature_optimum" in predictions:
            temp_data = predictions["temperature_optimum"]
            result["temperature_optimum"] = {
                "value": temp_data.get("value"),
                "error": temp_data.get("error"),
                "units": temp_data.get("units"),
                "is_novel": temp_data.get("is_novel")
            }
        
        # 解析pH预测
        if "ph_optimum" in predictions:
            ph_data = predictions["ph_optimum"]
            result["ph_optimum"] = {
                "value": ph_data.get("value"),
                "error": ph_data.get("error"),
                "units": ph_data.get("units"),
                "is_novel": ph_data.get("is_novel")
            }
        
        # 解析盐度预测
        if "salinity_optimum" in predictions:
            salinity_data = predictions["salinity_optimum"]
            result["salinity_optimum"] = {
                "value": salinity_data.get("value"),
                "error": salinity_data.get("error"),
                "units": salinity_data.get("units"),
                "is_novel": salinity_data.get("is_novel")
            }
        
        # 解析氧气耐受性预测
        if "oxygen" in predictions:
            oxygen_data = predictions["oxygen"]
            result["oxygen_tolerance"] = {
                "value": oxygen_data.get("value"),
                "error": oxygen_data.get("error"),
                "units": oxygen_data.get("units"),
                "is_novel": oxygen_data.get("is_novel")
            }
        
        return result