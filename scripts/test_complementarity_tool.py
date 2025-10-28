#!/usr/bin/env python3
"""
测试微生物互补性查询工具
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.database.complementarity_query import MicrobialComplementarityDBQueryTool

def test_complementarity_tool():
    """测试微生物互补性查询工具"""
    # 创建工具实例
    tool = MicrobialComplementarityDBQueryTool()
    
    print("测试微生物互补性查询工具")
    print("=" * 50)
    
    # 测试查询
    result = tool._run(
        microorganism_a="Pseudomonas putida",
        filter_by_complementarity=True
    )
    
    print("查询结果:")
    print("-" * 30)
    print(result)

if __name__ == "__main__":
    test_complementarity_tool()