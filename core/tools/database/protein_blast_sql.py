#!/usr/bin/env python3
"""
SQL-based BLAST-like蛋白质序列比对工具
用于在SQL数据库中查询蛋白质序列，模拟BLAST的三个关键阈值：
- EVALUE_THRESHOLD = 1e-5
- IDENTITY_THRESHOLD = 50.0
- MIN_ALIGNMENT_LENGTH = 50
"""

import sqlite3
import math
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ProteinBlastSQLInput(BaseModel):
    """蛋白质BLAST SQL查询输入参数"""
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


class ProteinBlastSQLTool(BaseTool):
    """SQL-based BLAST-like蛋白质序列比对工具"""
    
    name: str = "ProteinBLASTSQL工具"
    description: str = """用于在SQL数据库中查询蛋白质序列，模拟BLAST的三个关键阈值。
    可以通过蛋白质序列查询相似的蛋白质，并返回满足阈值条件的结果。
    """
    args_schema: type[BaseModel] = ProteinBlastSQLInput
    
    def __init__(self, db_path: str = "protein_sequences.db"):
        super().__init__()
        object.__setattr__(self, 'db_path', db_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建蛋白质序列表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS protein_sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                species_name VARCHAR(255),
                gene_name VARCHAR(255),
                protein_id VARCHAR(100),
                sequence TEXT,
                sequence_length INTEGER
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_species ON protein_sequences(species_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gene ON protein_sequences(gene_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_protein_id ON protein_sequences(protein_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sequence_length ON protein_sequences(sequence_length)')
        
        # 创建k-mer索引表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kmer_index (
                kmer VARCHAR(7),
                protein_id INTEGER,
                position INTEGER,
                FOREIGN KEY (protein_id) REFERENCES protein_sequences(id)
            )
        ''')
        
        # 创建k-mer索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kmer ON kmer_index(kmer)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_protein_position ON kmer_index(protein_id, position)')
        
        conn.commit()
        conn.close()
    
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
    
    def _precompute_kmers(self, protein_id: int, sequence: str, k: int = 7):
        """
        为蛋白质序列预计算k-mer
        
        Args:
            protein_id: 蛋白质ID
            sequence: 蛋白质序列
            k: k-mer长度
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 清除旧的k-mer
        cursor.execute("DELETE FROM kmer_index WHERE protein_id = ?", (protein_id,))
        
        # 计算并插入新的k-mer
        for i in range(len(sequence) - k + 1):
            kmer = sequence[i:i+k]
            cursor.execute(
                "INSERT INTO kmer_index (kmer, protein_id, position) VALUES (?, ?, ?)",
                (kmer, protein_id, i)
            )
        
        conn.commit()
        conn.close()
    
    def add_protein_sequence(self, species_name: str, gene_name: str, 
                           protein_id: str, sequence: str) -> bool:
        """
        添加蛋白质序列到数据库
        
        Args:
            species_name: 物种名称
            gene_name: 基因名称
            protein_id: 蛋白质ID
            sequence: 蛋白质序列
            
        Returns:
            bool: 是否添加成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入蛋白质序列
            cursor.execute('''
                INSERT INTO protein_sequences 
                (species_name, gene_name, protein_id, sequence, sequence_length)
                VALUES (?, ?, ?, ?, ?)
            ''', (species_name, gene_name, protein_id, sequence, len(sequence)))
            
            protein_id_db = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # 预计算k-mer
            self._precompute_kmers(protein_id_db, sequence)
            
            return True
        except Exception as e:
            print(f"添加蛋白质序列时出错: {e}")
            return False
    
    def _run(self, query_sequence: str, min_identity: float = 50.0,
             max_evalue: float = 1e-5, min_alignment_length: int = 50,
             limit: int = 100) -> Dict[str, any]:
        """
        执行SQL-based BLAST-like查询
        
        Args:
            query_sequence: 查询蛋白质序列
            min_identity: 最小序列相似度百分比
            max_evalue: 最大E-value阈值
            min_alignment_length: 最小比对长度
            limit: 返回结果数量限制
            
        Returns:
            dict: 查询结果
        """
        try:
            conn = sqlite3.connect(self.db_path)
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


# 使用示例
if __name__ == "__main__":
    # 创建工具实例
    tool = ProteinBlastSQLTool("protein_sequences.db")
    
    # 添加示例数据
    tool.add_protein_sequence(
        "Escherichia coli", 
        "lacZ", 
        "P00722", 
        "MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK"
    )
    
    # 执行查询
    result = tool._run(
        "MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK",
        min_identity=50.0,
        max_evalue=1e-5,
        min_alignment_length=50,
        limit=10
    )
    
    print("查询结果:")
    print(result)