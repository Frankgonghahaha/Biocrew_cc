#!/usr/bin/env python3
"""
测试基于SQL的蛋白质序列查询工具
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.design.protein_sequence_query_sql import ProteinSequenceQuerySQLTool

def test_protein_sequence_query():
    """
    测试蛋白质序列查询工具
    """
    print("=== 测试基于SQL的蛋白质序列查询工具 ===\n")
    
    # 创建工具实例
    tool = ProteinSequenceQuerySQLTool()
    
    # 测试1: 查询相似序列
    print("[测试1] 查询与Pseudomonas putida alkB基因相似的序列")
    query_sequence = "MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF"
    
    result = tool._run(
        query_sequence=query_sequence,
        min_identity=40.0,
        max_evalue=1e-3,
        min_alignment_length=30,
        limit=5,
        database_path="protein_sequences.db"
    )
    
    print(f"查询状态: {result['status']}")
    if result['status'] == 'success':
        print(f"查询序列长度: {result['query_sequence_length']}")
        print(f"找到结果数量: {result['total_results']}")
        print("\n匹配结果:")
        for i, match in enumerate(result['results'], 1):
            print(f"  {i}. 物种: {match['species_name']}")
            print(f"     基因: {match['gene_name']}")
            print(f"     蛋白质ID: {match['protein_id']}")
            print(f"     相似度: {match['identity']}%")
            print(f"     E-value: {match['evalue']}")
            print(f"     比对长度: {match['alignment_length']}")
            print(f"     序列: {match['sequence'][:50]}...")
            print()
    else:
        print(f"错误信息: {result['message']}")
    
    # 测试2: 查询不匹配的序列
    print("\n[测试2] 查询不匹配的序列")
    query_sequence2 = "MKKTFGRALAVLALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALALAL"
    
    result2 = tool._run(
        query_sequence=query_sequence2,
        min_identity=50.0,
        max_evalue=1e-5,
        min_alignment_length=50,
        limit=5,
        database_path="protein_sequences.db"
    )
    
    print(f"查询状态: {result2['status']}")
    if result2['status'] == 'success':
        print(f"查询序列长度: {result2['query_sequence_length']}")
        print(f"找到结果数量: {result2['total_results']}")
        if result2['total_results'] > 0:
            print("\n匹配结果:")
            for i, match in enumerate(result2['results'], 1):
                print(f"  {i}. 物种: {match['species_name']}")
                print(f"     基因: {match['gene_name']}")
                print(f"     蛋白质ID: {match['protein_id']}")
                print(f"     相似度: {match['identity']}%")
                print(f"     E-value: {match['evalue']}")
                print(f"     比对长度: {match['alignment_length']}")
                print()
        else:
            print("未找到匹配的序列")
    else:
        print(f"错误信息: {result2['message']}")
    
    # 测试3: 数据库文件不存在的情况
    print("\n[测试3] 测试数据库文件不存在的情况")
    result3 = tool._run(
        query_sequence=query_sequence,
        database_path="nonexistent.db"
    )
    
    print(f"查询状态: {result3['status']}")
    print(f"错误信息: {result3['message']}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_protein_sequence_query()