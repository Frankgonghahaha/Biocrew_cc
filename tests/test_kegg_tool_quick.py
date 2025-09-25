#!/usr/bin/env python3
"""
KEGG工具快速测试脚本
用于快速测试KEGG工具的基本功能
"""

import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.kegg_tool import KeggTool

def test_kegg_tool_quick():
    """快速测试KEGG工具功能"""
    print("开始快速测试KEGG工具功能...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    print("✓ KEGG工具实例创建成功")
    
    # 测试化合物搜索功能（限制结果数量和超时）
    print("\n1. 测试化合物搜索功能...")
    try:
        result = kegg_tool.find_entries("compound", "phthalate", 2)
        if result.get("status") == "success":
            print("  ✓ 化合物搜索功能正常")
            print(f"  搜索结果数量: {result.get('count', 0)}")
            if result.get("data"):
                print(f"  第一个结果: {result['data'][0].get('id', 'N/A')} - {result['data'][0].get('description', 'N/A')}")
        else:
            print(f"  ⚠ 化合物搜索返回: {result.get('message', '未知状态')}")
    except Exception as e:
        print(f"  ✗ 化合物搜索异常: {e}")
    
    # 测试pathway搜索功能
    print("\n2. 测试pathway搜索功能...")
    try:
        result = kegg_tool.find_entries("pathway", "degradation", 2)
        if result.get("status") == "success":
            print("  ✓ Pathway搜索功能正常")
            print(f"  搜索结果数量: {result.get('count', 0)}")
            if result.get("data"):
                print(f"  第一个结果: {result['data'][0].get('id', 'N/A')} - {result['data'][0].get('description', 'N/A')}")
        else:
            print(f"  ⚠ Pathway搜索返回: {result.get('message', '未知状态')}")
    except Exception as e:
        print(f"  ✗ Pathway搜索异常: {e}")
    
    print("\n快速测试完成")

if __name__ == "__main__":
    test_kegg_tool_quick()