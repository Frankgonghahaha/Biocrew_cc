#!/usr/bin/env python3
"""
降解功能微生物识别工具
结合蛋白质序列查询和微生物互补性查询，识别降解功能微生物及其互补微生物
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from core.tools.design.protein_sequence_query_sql_updated import ProteinSequenceQuerySQLToolUpdated
from core.tools.database.complementarity_query import MicrobialComplementarityDBQueryTool
import json


class DegradingMicroorganismIdentificationInput(BaseModel):
    """降解功能微生物识别工具输入参数"""
    query_sequence: str = Field(..., description="查询蛋白质序列")
    min_identity: float = Field(
        default=30.0,
        description="最小序列相似度百分比 (0-100)"
    )
    max_evalue: float = Field(
        default=1e-3,
        description="最大E-value阈值"
    )
    min_alignment_length: int = Field(
        default=30,
        description="最小比对长度"
    )
    limit: int = Field(
        default=100,
        description="返回结果数量限制"
    )


class DegradingMicroorganismIdentificationTool(BaseTool):
    """降解功能微生物识别工具"""
    
    name: str = "DegradingMicroorganismIdentificationTool"
    description: str = """用于识别降解功能微生物及其互补微生物的工具。
    首先通过蛋白质序列查询识别潜在的降解功能微生物，
    然后通过微生物互补性查询找出互补指数大于竞争指数的互补微生物。
    """
    args_schema: type[BaseModel] = DegradingMicroorganismIdentificationInput
    
    def __init__(self):
        super().__init__()
        # 初始化两个子工具
        # 使用__dict__来设置实例属性，避免pydantic的字段验证
        self.__dict__['protein_query_tool'] = ProteinSequenceQuerySQLToolUpdated()
        self.__dict__['complementarity_query_tool'] = MicrobialComplementarityDBQueryTool()
    
    def _run(self, query_sequence: str, min_identity: float = 30.0,
             max_evalue: float = 1e-3, min_alignment_length: int = 30,
             limit: int = 100) -> Dict[str, Any]:
        """
        识别降解功能微生物及其互补微生物
        
        Args:
            query_sequence: 查询蛋白质序列
            min_identity: 最小序列相似度百分比
            max_evalue: 最大E-value阈值
            min_alignment_length: 最小比对长度
            limit: 返回结果数量限制
            
        Returns:
            dict: 识别结果，包含降解功能微生物和互补微生物信息
        """
        try:
            # 第一步：使用蛋白质序列查询工具识别降解功能微生物
            protein_results = self.protein_query_tool._run(
                query_sequence=query_sequence,
                min_identity=min_identity,
                max_evalue=max_evalue,
                min_alignment_length=min_alignment_length,
                limit=limit
            )
            
            if protein_results["status"] != "success":
                return {
                    "status": "error",
                    "message": f"蛋白质序列查询失败: {protein_results.get('message', '未知错误')}"
                }
            
            # 获取识别出的降解功能微生物列表
            degrading_microorganisms = protein_results.get("degrading_microorganisms", [])
            
            if not degrading_microorganisms:
                return {
                    "status": "success",
                    "message": "未识别到任何降解功能微生物",
                    "degrading_microorganisms": [],
                    "complementary_microorganisms": {}
                }
            
            # 第二步：为每个降解功能微生物查询互补微生物
            complementary_results = {}
            
            for microorganism in degrading_microorganisms:
                # 查询互补指数大于竞争指数的互补微生物
                complementarity_result = self.complementarity_query_tool._run(
                    microorganism_a=microorganism,
                    filter_by_complementarity=True
                )
                
                complementary_results[microorganism] = complementarity_result
            
            return {
                "status": "success",
                "degrading_microorganisms": degrading_microorganisms,
                "complementary_microorganisms": complementary_results,
                "protein_query_results": protein_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"识别降解功能微生物时发生错误: {str(e)}"
            }