#!/usr/bin/env python3
"""
基于SQL的蛋白质序列查询工具（更新版）
用于替代传统的.faa文件处理方式，直接从PostgreSQL数据库中查询蛋白质序列
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, text
import math
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ProteinSequenceQuerySQLInput(BaseModel):
    """蛋白质序列SQL查询输入参数"""
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

class ProteinSequenceQuerySQLToolUpdated(BaseTool):
    """基于SQL的蛋白质序列查询工具（更新版）"""
    
    name: str = "ProteinSequenceQuerySQLToolUpdated"
    description: str = """用于从PostgreSQL数据库中查询蛋白质序列的工具。
    可以通过蛋白质序列查询相似的蛋白质，并返回满足阈值条件的结果。
    用于识别具有特定降解功能的微生物。
    """
    args_schema: type[BaseModel] = ProteinSequenceQuerySQLInput
    
    def __init__(self):
        super().__init__()
        # 从环境变量获取数据库配置
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        # 使用__dict__来设置实例属性，避免pydantic的字段验证
        self.__dict__['database_url'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    def _calculate_sequence_identity(self, seq1: str, seq2: str) -> float:
        """
        计算两个序列的相似度百分比
        
        Args:
            seq1: 序列1
            seq2: 序列2
            
        Returns:
            float: 相似度百分比
        """
        if not seq1 or not seq2:
            return 0.0
            
        min_len = min(len(seq1), len(seq2))
        if min_len == 0:
            return 0.0
            
        matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
        return (matches / min_len) * 100.0
    
    def _estimate_evalue(self, alignment_length: int, matched_positions: int) -> float:
        """
        估算E-value（简化版）
        
        Args:
            alignment_length: 比对长度
            matched_positions: 匹配位置数
            
        Returns:
            float: 估算的E-value
        """
        if alignment_length < 10:
            return 1.0
            
        # 简化的E-value计算公式，避免数值过大
        identity = matched_positions / alignment_length if alignment_length > 0 else 0
        
        # 限制指数部分避免数值溢出
        exp_part = -0.3 * (alignment_length - 10)
        if exp_part < -700:  # 避免exp溢出
            exp_part = -700
            
        # 限制幂次部分避免数值溢出
        power_exp = alignment_length
        if power_exp > 100:  # 限制幂次
            power_exp = 100
            
        try:
            evalue = math.exp(exp_part) * 1000000 / (20 ** power_exp)
            return max(evalue, 1e-200)  # 避免过小的值
        except OverflowError:
            return 1e-200  # 如果计算溢出，返回最小值
    
    def _run(self, query_sequence: str, min_identity: float = 30.0,
             max_evalue: float = 1e-3, min_alignment_length: int = 30,
             limit: int = 100) -> Dict[str, Any]:
        """
        执行SQL-based蛋白质序列查询
        
        Args:
            query_sequence: 查询蛋白质序列
            min_identity: 最小序列相似度百分比
            max_evalue: 最大E-value阈值
            min_alignment_length: 最小比对长度
            limit: 返回结果数量限制
            
        Returns:
            dict: 查询结果，包含识别出的潜在降解功能微生物
        """
        try:
            # 检查查询序列是否为空
            if not query_sequence:
                return {
                    "status": "error",
                    "message": "查询序列不能为空"
                }
            
            # 创建数据库引擎
            engine = create_engine(self.database_url)
            
            # 首先通过长度筛选候选序列
            query_length = len(query_sequence)
            length_tolerance = 50  # 长度差异容忍度
            
            with engine.connect() as conn:
                # 查询候选序列
                sql = '''
                SELECT species_name, sequence_id, aa_sequence
                FROM protein_sequences
                WHERE sequence_length BETWEEN :min_length AND :max_length
                ORDER BY ABS(sequence_length - :query_length)
                LIMIT 1000
                '''
                
                result = conn.execute(text(sql), {
                    'min_length': query_length - length_tolerance,
                    'max_length': query_length + length_tolerance,
                    'query_length': query_length
                })
                candidates = result.fetchall()
            
            results = []
            
            # 对候选序列进行详细比对
            for candidate in candidates:
                species_name, sequence_id, sequence = candidate
                
                # 计算序列相似度
                identity = self._calculate_sequence_identity(query_sequence, sequence)
                
                # 计算比对长度
                alignment_length = min(len(query_sequence), len(sequence))
                
                # 估算E-value
                matched_positions = sum(1 for i in range(alignment_length) 
                                      if query_sequence[i] == sequence[i])
                evalue = self._estimate_evalue(alignment_length, matched_positions)
                
                # 检查是否满足所有阈值
                if (identity >= min_identity and 
                    evalue <= max_evalue and 
                    alignment_length >= min_alignment_length):
                    
                    results.append({
                        "species_name": species_name,
                        "sequence_id": sequence_id,
                        "sequence": sequence,
                        "identity": round(identity, 2),
                        "evalue": evalue,
                        "alignment_length": alignment_length
                    })
            
            # 按相似度排序并限制结果数量
            results.sort(key=lambda x: (-x["identity"], x["evalue"]))
            results = results[:limit]
            
            # 提取降解功能微生物列表
            degrading_microorganisms = list(set([r["species_name"] for r in results]))
            
            return {
                "status": "success",
                "query_sequence_length": len(query_sequence),
                "results": results,
                "total_results": len(results),
                "degrading_microorganisms": degrading_microorganisms
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询过程中出错: {str(e)}",
                "query_sequence_length": len(query_sequence) if query_sequence else 0
            }