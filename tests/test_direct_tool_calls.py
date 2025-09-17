#!/usr/bin/env python3
"""
简单测试工具修复 - 直接调用工具验证参数解析
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool
from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool

def test_direct_tool_calls():
    """直接测试工具调用"""
    print("=== 直接测试工具调用 ===")
    
    # 创建工具实例
    mandatory_query = MandatoryLocalDataQueryTool(".")
    data_retriever = LocalDataRetriever(".")
    smart_query = SmartDataQueryTool(".")
    
    print("工具初始化成功")
    
    # 测试强制本地数据查询工具
    print("\n1. 测试强制本地数据查询工具:")
    try:
        result = mandatory_query._run(
            operation="query_required_data", 
            query_text="处理Alpha-hexachlorocyclohexane的工程微生物组"
        )
        print("强制本地数据查询工具调用成功:")
        print(f"  状态: {result.get('status')}")
        print(f"  匹配的污染物: {result.get('matched_pollutants', [])}")
    except Exception as e:
        print(f"强制本地数据查询工具调用失败: {e}")
    
    # 测试本地数据读取工具 - 基因数据
    print("\n2. 测试本地数据读取工具 - 基因数据:")
    try:
        result = data_retriever._run(
            operation="get_gene_data", 
            pollutant_name="Alpha-hexachlorocyclohexane"
        )
        print("本地数据读取工具(基因数据)调用成功:")
        print(f"  状态: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"  数据形状: {result.get('data', {}).get('shape')}")
    except Exception as e:
        print(f"本地数据读取工具(基因数据)调用失败: {e}")
    
    # 测试本地数据读取工具 - 微生物数据
    print("\n3. 测试本地数据读取工具 - 微生物数据:")
    try:
        result = data_retriever._run(
            operation="get_organism_data", 
            pollutant_name="Alpha-hexachlorocyclohexane"
        )
        print("本地数据读取工具(微生物数据)调用成功:")
        print(f"  状态: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"  数据形状: {result.get('data', {}).get('shape')}")
    except Exception as e:
        print(f"本地数据读取工具(微生物数据)调用失败: {e}")

if __name__ == "__main__":
    test_direct_tool_calls()