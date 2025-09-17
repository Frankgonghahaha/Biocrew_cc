#!/usr/bin/env python3
"""
测试增强版UnifiedDataTool，修复CrewAI框架参数传递问题
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from tools.unified_data_tool import UnifiedDataTool

def test_current_tool():
    """测试当前工具的各种调用方式"""
    print("=== 测试当前工具 ===")
    tool = UnifiedDataTool()
    
    # 测试1: 直接调用
    print("\n1. 测试直接调用:")
    try:
        result1 = tool._run("query_pollutant_data", pollutant_name="Aldrin")
        print(f"   结果: {result1}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试2: JSON字符串调用
    print("\n2. 测试JSON字符串调用:")
    try:
        json_input = "{\"operation\": \"query_pollutant_data\", \"pollutant_name\": \"Aldrin\"}"
        result2 = tool._run(json_input)
        print(f"   结果: {result2}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试3: 字典调用（模拟CrewAI框架调用）
    print("\n3. 测试字典调用（模拟CrewAI框架调用）:")
    try:
        # 这是CrewAI框架可能的调用方式
        result3 = tool._run({"operation": "query_pollutant_data", "pollutant_name": "Aldrin"})
        print(f"   结果: {result3}")
    except Exception as e:
        print(f"   错误: {e}")

def main():
    """主函数"""
    print("增强版UnifiedDataTool测试")
    print("=" * 30)
    
    try:
        test_current_tool()
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
