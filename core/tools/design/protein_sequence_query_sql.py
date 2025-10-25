#!/usr/bin/env python3
"""
基于SQL的蛋白质序列查询工具
用于替代传统的.faa文件处理方式，直接从SQL数据库中查询蛋白质序列
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import sqlite3
import math
import os


class ProteinSequenceQuerySQLInput(BaseModel):
    """蛋白质序列SQL查询输入参数"""
    query_sequence: str = Field(..., description="查询蛋白质序列")
    min_identity: float = Field(
        default=50.0,
        description="最小序列相似度百分比 (0-100)"
    )
    max_evalue: float = Field(
        default=1e-5,
        description="最大E-value阈值"
    )
    min_alignment_length: int = Field(
        default=50,
        description="最小比对长度"
    )
    limit: int = Field(
        default=100,
        description="返回结果数量限制"
    )
    database_path: str = Field(
        default="protein_sequences.db",
        description="SQL数据库文件路径"
    )


class ProteinSequenceQuerySQLTool(BaseTool):
    """基于SQL的蛋白质序列查询工具"""
    
    name: str = "ProteinSequenceQuerySQLTool"
    description: str = """用于从SQL数据库中查询蛋白质序列的工具。
    可以通过蛋白质序列查询相似的蛋白质，并返回满足阈值条件的结果。
    替代传统的.faa文件处理方式。
    """
    args_schema: type[BaseModel] = ProteinSequenceQuerySQLInput
    
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
    
    def _run(self, query_sequence: str, min_identity: float = 50.0,
             max_evalue: float = 1e-5, min_alignment_length: int = 50,
             limit: int = 100, database_path: str = "protein_sequences.db") -> Dict[str, Any]:
        """
        执行SQL-based蛋白质序列查询
        
        Args:
            query_sequence: 查询蛋白质序列
            min_identity: 最小序列相似度百分比
            max_evalue: 最大E-value阈值
            min_alignment_length: 最小比对长度
            limit: 返回结果数量限制
            database_path: SQL数据库文件路径
            
        Returns:
            dict: 查询结果
        """
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(database_path):
                return {
                    "status": "error",
                    "message": f"数据库文件不存在: {database_path}"
                }
            
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # 首先通过长度筛选候选序列
            query_length = len(query_sequence)
            length_tolerance = 50  # 长度差异容忍度
            
            cursor.execute('''
                SELECT id, species_name, gene_name, protein_id, sequence
                FROM protein_sequences
                WHERE sequence_length BETWEEN ? AND ?
                ORDER BY ABS(sequence_length - ?)
                LIMIT 1000
            ''', (query_length - length_tolerance, query_length + length_tolerance, query_length))
            
            candidates = cursor.fetchall()
            results = []
            
            # 对候选序列进行详细比对
            for candidate in candidates:
                protein_id, species_name, gene_name, protein_id_name, sequence = candidate
                
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
                        "gene_name": gene_name,
                        "protein_id": protein_id_name,
                        "sequence": sequence,
                        "identity": round(identity, 2),
                        "evalue": evalue,
                        "alignment_length": alignment_length
                    })
            
            # 按相似度排序并限制结果数量
            results.sort(key=lambda x: (-x["identity"], x["evalue"]))
            results = results[:limit]
            
            conn.close()
            
            return {
                "status": "success",
                "query_sequence_length": len(query_sequence),
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询过程中出错: {str(e)}",
                "query_sequence_length": len(query_sequence) if query_sequence else 0
            }