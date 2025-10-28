#!/usr/bin/env python3
"""
测试蛋白质序列查询功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.design.protein_sequence_query_sql_updated import ProteinSequenceQuerySQLToolUpdated

def test_protein_sequence_query():
    """测试蛋白质序列查询功能"""
    # 创建工具实例
    tool = ProteinSequenceQuerySQLToolUpdated()
    
    # 测试序列（示例）
    test_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    
    print("测试蛋白质序列查询工具")
    print("=" * 50)
    print(f"查询序列长度: {len(test_sequence)}")
    print(f"查询序列: {test_sequence[:30]}...")
    print()
    
    # 执行查询
    result = tool._run(
        query_sequence=test_sequence,
        min_identity=30.0,
        max_evalue=1e-3,
        min_alignment_length=30,
        limit=10
    )
    
    print("查询结果:")
    print("-" * 30)
    
    if result["status"] == "error":
        print(f"错误: {result['message']}")
        return
    
    print(f"状态: {result['status']}")
    print(f"查询序列长度: {result['query_sequence_length']}")
    print(f"总结果数: {result['total_results']}")
    
    if "message" in result:
        print(f"消息: {result['message']}")
    
    if "degrading_microorganisms" in result:
        print(f"识别到的降解功能微生物数量: {len(result['degrading_microorganisms'])}")
        for i, microorganism in enumerate(result['degrading_microorganisms'], 1):
            print(f"  {i}. {microorganism}")
    
    if "results" in result and result["results"]:
        print(f"\n详细结果 (显示前5个):")
        for i, res in enumerate(result["results"][:5], 1):
            print(f"  {i}. 物种: {res['species_name']}")
            print(f"     序列ID: {res['sequence_id']}")
            print(f"     相似度: {res['identity']}%")
            print(f"     E-value: {res['evalue']}")
            print(f"     比对长度: {res['alignment_length']}")
            print()

if __name__ == "__main__":
    test_protein_sequence_query()