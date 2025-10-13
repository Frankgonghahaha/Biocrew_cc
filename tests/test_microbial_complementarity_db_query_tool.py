#!/usr/bin/env python3
"""
测试微生物互补性数据库查询工具
"""

import sys
import os
from dotenv import load_dotenv

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（当前目录的上级目录）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到Python路径中
sys.path.insert(0, project_root)

from tools.microbial_complementarity_db_query_tool import MicrobialComplementarityDBQueryTool

def test_microbial_complementarity_db_query_tool():
    """测试微生物互补性数据库查询工具"""
    print("开始测试微生物互补性数据库查询工具...")
    
    # 创建工具实例
    tool = MicrobialComplementarityDBQueryTool()
    print("✓ 工具实例创建成功")
    
    # 测试工具运行
    print("\n1. 测试工具运行...")
    try:
        # 查询特定微生物的互补性数据
        result = tool._run("Bacillus brevis")
        print("✓ 工具运行成功")
        print("结果:")
        print(result)
        
    except Exception as e:
        print(f"✗ 工具运行失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试查询两个微生物之间的互补性
    print("\n2. 测试查询两个微生物之间的互补性...")
    try:
        result = tool._run("Bacillus brevis", "Rhodococcus jostii")
        print("✓ 工具运行成功")
        print("结果:")
        print(result)
        
    except Exception as e:
        print(f"✗ 工具运行失败: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    test_microbial_complementarity_db_query_tool()
