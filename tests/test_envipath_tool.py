#!/usr/bin/env python3
"""
测试EnviPath工具的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.envipath_tool import EnviPathTool
import json

def test_envipath_tool():
    print("开始测试EnviPath工具...")
    
    # 创建EnviPath工具实例
    envipath_tool = EnviPathTool()
    
    # 检查客户端是否初始化成功
    if not envipath_tool.client:
        print("错误: EnviPath客户端初始化失败")
        return False
    
    print("1. 测试化合物搜索功能...")
    try:
        result = envipath_tool.search_compound("cadmium")
        print(f"   搜索'cadmium'结果: {result['status']}")
        if result['status'] == 'success':
            print("   ✓ 化合物搜索功能正常")
        else:
            print(f"   ✗ 化合物搜索失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 化合物搜索异常: {e}")
    
    print("2. 测试关键词搜索pathway功能...")
    try:
        result = envipath_tool.search_pathways_by_keyword("heavy metal")
        print(f"   搜索'heavy metal'结果: {result['status']}")
        if result['status'] == 'success':
            print("   ✓ 关键词搜索pathway功能正常")
        else:
            print(f"   ✗ 关键词搜索失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 关键词搜索异常: {e}")
    
    print("3. 测试获取pathway信息功能...")
    try:
        # 使用一个实际存在的pathway URL进行测试
        pathway_url = "https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1/pathway/f0da2abe-81be-4903-8868-cf7ca311e7de"
        result = envipath_tool.get_pathway_info(pathway_url)
        print(f"   获取pathway信息结果: {result['status']}")
        if result['status'] == 'success':
            print("   ✓ 获取pathway信息功能正常")
        else:
            print(f"   ✗ 获取pathway信息失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 获取pathway信息异常: {e}")
    
    print("4. 测试获取化合物路径信息功能...")
    try:
        # 使用一个实际存在的化合物URL进行测试
        compound_url = "https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1/compound/51f35ac0-e104-4698-8a4b-e5e01da33af6"
        result = envipath_tool.get_compound_pathways(compound_url)
        print(f"   获取化合物路径信息结果: {result['status']}")
        if result['status'] == 'success':
            print("   ✓ 获取化合物路径信息功能正常")
        else:
            print(f"   ✗ 获取化合物路径信息失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 获取化合物路径信息异常: {e}")
    
    print("\n测试完成。")
    return True

if __name__ == "__main__":
    test_envipath_tool()