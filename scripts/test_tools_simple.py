#!/usr/bin/env python3
"""
测试降解功能微生物识别工具（简化版）
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接导入需要的工具
from core.tools.design.protein_sequence_query_sql_updated import ProteinSequenceQuerySQLToolUpdated
from core.tools.database.complementarity_query import MicrobialComplementarityDBQueryTool

def test_protein_query():
    """测试蛋白质序列查询工具"""
    print("测试蛋白质序列查询工具")
    print("=" * 30)
    
    # 创建工具实例
    tool = ProteinSequenceQuerySQLToolUpdated()
    
    # 检查是否有数据库连接信息
    if not hasattr(tool, 'database_url'):
        print("未找到数据库配置信息")
        return
    
    print(f"数据库URL: {tool.database_url[:50]}...")
    print("工具初始化成功")

def test_complementarity_query():
    """测试互补性查询工具"""
    print("\n测试微生物互补性查询工具")
    print("=" * 30)
    
    # 创建工具实例
    tool = MicrobialComplementarityDBQueryTool()
    
    # 检查是否有数据库连接信息
    if not tool.__dict__.get('Session'):
        print("数据库连接未初始化")
        return
    
    print("工具初始化成功")

if __name__ == "__main__":
    test_protein_query()
    test_complementarity_query()
    print("\n工具测试完成")