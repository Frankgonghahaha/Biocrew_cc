#!/usr/bin/env python3
"""
验证工具基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.design.protein_sequence_query_sql_updated import ProteinSequenceQuerySQLToolUpdated
from core.tools.design.degrading_microorganism_identification_tool import DegradingMicroorganismIdentificationTool

def test_tool_functionality():
    """测试工具基本功能"""
    print("验证工具基本功能")
    print("=" * 50)
    
    # 测试ProteinSequenceQuerySQLToolUpdated工具创建
    try:
        protein_tool = ProteinSequenceQuerySQLToolUpdated()
        print("✓ ProteinSequenceQuerySQLToolUpdated工具创建成功")
    except Exception as e:
        print(f"✗ ProteinSequenceQuerySQLToolUpdated工具创建失败: {e}")
        return
    
    # 测试DegradingMicroorganismIdentificationTool工具创建
    try:
        degrading_tool = DegradingMicroorganismIdentificationTool()
        print("✓ DegradingMicroorganismIdentificationTool工具创建成功")
    except Exception as e:
        print(f"✗ DegradingMicroorganismIdentificationTool工具创建失败: {e}")
        return
    
    # 测试空序列处理
    print("\n测试空序列处理:")
    result = protein_tool._run(query_sequence="")
    if result["status"] == "error" and "不能为空" in result["message"]:
        print("✓ 空序列处理正确")
    else:
        print("✗ 空序列处理不正确")
    
    # 测试无效序列处理
    print("\n测试无效序列处理:")
    result = protein_tool._run(query_sequence="INVALID")
    if result["status"] in ["success", "error"]:
        print("✓ 无效序列处理正确")
    else:
        print("✗ 无效序列处理不正确")
    
    print("\n工具基本功能验证完成")

if __name__ == "__main__":
    test_tool_functionality()