#!/usr/bin/env python3
"""
测试NCBI基因组查询工具
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

# 加载环境变量
load_dotenv()

def test_ncbi_genome_query_tool():
    """测试NCBI基因组查询工具"""
    print("开始测试NCBI基因组查询工具...")
    
    try:
        # 导入工具
        from tools.ncbi_genome_query_tool import NCBIGenomeQueryTool
        
        # 创建工具实例
        tool = NCBIGenomeQueryTool()
        print("✓ 工具创建成功")
        
        # 测试查询特定微生物
        test_organisms = [
            "Rhodococcus jostii RHA1",
            "Brevibacillus brevis",
            "Pseudomonas pseudoalcaligene",
            "Ralstonia eutropha H85"
        ]
        
        for organism in test_organisms:
            print(f"\n测试查询: {organism}")
            try:
                result = tool._run(organism, max_results=3)
                print(f"查询结果:\n{result}")
            except Exception as e:
                print(f"查询 {organism} 时出错: {e}")
                
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ncbi_genome_query_tool()