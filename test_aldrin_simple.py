#!/usr/bin/env python3
"""
简单的Aldrin数据查询测试脚本
直接测试工具调用功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool
from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool

def test_aldrin_data_query():
    """测试Aldrin数据查询功能"""
    print("=== 测试Aldrin数据查询功能 ===")
    
    # 创建工具实例
    local_retriever = LocalDataRetriever(".")
    smart_query = SmartDataQueryTool(".")
    mandatory_query = MandatoryLocalDataQueryTool(".")
    
    print("\n1. 测试本地数据读取工具:")
    try:
        # 直接调用获取Aldrin微生物数据
        result = local_retriever._run("get_organism_data", pollutant_name="Aldrin")
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n2. 测试智能数据查询工具:")
    try:
        # 调用查询相关数据
        result = smart_query._run("query_related_data", query_text="Aldrin")
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n3. 测试强制本地数据查询工具:")
    try:
        # 调用查询必需数据
        result = mandatory_query._run("query_required_data", query_text="Aldrin")
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n4. 测试数据完整性评估:")
    try:
        # 调用数据完整性评估
        result = mandatory_query._run("assess_data_integrity", query_text="Aldrin")
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    test_aldrin_data_query()