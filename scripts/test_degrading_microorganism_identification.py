#!/usr/bin/env python3
"""
测试降解功能微生物识别工具
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.design.degrading_microorganism_identification_tool import DegradingMicroorganismIdentificationTool

def test_tool():
    """测试降解功能微生物识别工具"""
    # 创建工具实例
    tool = DegradingMicroorganismIdentificationTool()
    
    # 测试序列（示例）
    test_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGGDDDDD"
    
    print("测试降解功能微生物识别工具")
    print("=" * 50)
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
        print("\n互补微生物查询结果:")
        for microorganism, complementarity_result in result['complementary_microorganisms'].items():
            print(f"  {microorganism}:")
            print(f"    {complementarity_result}")

if __name__ == "__main__":
    test_tool()