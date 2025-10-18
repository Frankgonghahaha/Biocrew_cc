#!/usr/bin/env python3
"""
测试中间产物检查工具
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from tools.intermediate_product_check_tool import IntermediateProductCheckTool

def test_intermediate_product_check():
    """测试中间产物检查工具"""
    print("开始测试中间产物检查工具")
    
    # 创建工具实例
    tool = IntermediateProductCheckTool()
    
    # 测试检查所有中间产物
    print("\n1. 测试检查所有中间产物:")
    result = tool._run(check_type="all", output_dir="./outputs")
    print(f"检查结果: {result}")
    
    # 测试检查基因组特征文件
    print("\n2. 测试检查基因组特征文件:")
    result = tool._run(check_type="genome_features", output_dir="./outputs")
    print(f"检查结果: {result}")
    
    # 测试检查代谢模型文件
    print("\n3. 测试检查代谢模型文件:")
    result = tool._run(check_type="metabolic_models", output_dir="./outputs")
    print(f"检查结果: {result}")
    
    # 测试检查反应数据文件
    print("\n4. 测试检查反应数据文件:")
    result = tool._run(check_type="reactions", output_dir="./outputs")
    print(f"检查结果: {result}")

if __name__ == "__main__":
    test_intermediate_product_check()