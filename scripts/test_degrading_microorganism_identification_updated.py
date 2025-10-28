#!/usr/bin/env python3
"""
测试降解功能微生物识别工具
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.design.degrading_microorganism_identification_tool import DegradingMicroorganismIdentificationTool

def test_degrading_microorganism_identification():
    """测试降解功能微生物识别工具"""
    # 创建工具实例
    tool = DegradingMicroorganismIdentificationTool()
    
    # 测试序列（示例）
    test_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    
    print("测试降解功能微生物识别工具")
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
    
    if "message" in result:
        print(f"消息: {result['message']}")
    
    if "degrading_microorganisms" in result:
        print(f"识别到的降解功能微生物数量: {len(result['degrading_microorganisms'])}")
        for i, microorganism in enumerate(result['degrading_microorganisms'], 1):
            print(f"  {i}. {microorganism}")
    
    if "complementary_microorganisms" in result:
        print(f"\n互补微生物查询结果:")
        for microorganism, complementarity_result in result['complementary_microorganisms'].items():
            print(f"  {microorganism}:")
            print(f"    {complementarity_result}")
    
    if "protein_query_results" in result:
        protein_results = result["protein_query_results"]
        print(f"\n蛋白质查询详细结果:")
        print(f"  总结果数: {protein_results['total_results']}")
        if "results" in protein_results and protein_results["results"]:
            print(f"  详细结果 (显示前3个):")
            for i, res in enumerate(protein_results["results"][:3], 1):
                print(f"    {i}. 物种: {res['species_name']}")
                print(f"       序列ID: {res['sequence_id']}")
                print(f"       相似度: {res['identity']}%")
                print(f"       E-value: {res['evalue']}")
                print(f"       比对长度: {res['alignment_length']}")
                print()

if __name__ == "__main__":
    test_degrading_microorganism_identification()