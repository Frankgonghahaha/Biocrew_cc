#!/usr/bin/env python3
"""
测试所有工具的集成使用
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.database.factory import DatabaseToolFactory
from core.tools.design.protein_sequence_query_sql import ProteinSequenceQuerySQLTool
from scripts.update_carveme_for_sql import UpdatedCarvemeTool

def test_tool_integration():
    """
    测试工具集成
    """
    print("=== 测试工具集成 ===\n")
    
    # 1. 测试DatabaseToolFactory
    print("1. 测试DatabaseToolFactory")
    try:
        tools = DatabaseToolFactory.create_all_tools()
        print(f"   成功创建 {len(tools)} 个数据库工具")
        
        # 测试获取特定工具
        pollutant_tool = DatabaseToolFactory.create_pollutant_data_query_tool()
        if pollutant_tool:
            print("   成功创建PollutantDataQueryTool")
        else:
            print("   创建PollutantDataQueryTool失败")
    except Exception as e:
        print(f"   DatabaseToolFactory测试失败: {e}")
    
    # 2. 测试ProteinSequenceQuerySQLTool
    print("\n2. 测试ProteinSequenceQuerySQLTool")
    try:
        sql_tool = ProteinSequenceQuerySQLTool()
        query_sequence = "MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF"
        
        result = sql_tool._run(
            query_sequence=query_sequence,
            min_identity=40.0,
            max_evalue=1e-3,
            min_alignment_length=30,
            limit=5,
            database_path="protein_sequences.db"
        )
        
        if result['status'] == 'success':
            print(f"   SQL查询成功，找到 {result['total_results']} 个匹配结果")
        else:
            print(f"   SQL查询失败: {result['message']}")
    except Exception as e:
        print(f"   ProteinSequenceQuerySQLTool测试失败: {e}")
    
    # 3. 测试更新的CarvemeTool
    print("\n3. 测试更新的CarvemeTool")
    try:
        carveme_tool = UpdatedCarvemeTool()
        query_sequence = "MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF"
        
        result = carveme_tool._run_with_sql_query(
            query_sequence=query_sequence,
            min_identity=40.0,
            max_evalue=1e-3,
            min_alignment_length=30,
            limit=5,
            database_path="protein_sequences.db"
        )
        
        if result['status'] == 'success':
            print(f"   Carveme处理成功，生成 {result['data']['model_count']} 个模型")
        else:
            print(f"   Carveme处理失败: {result['message']}")
    except Exception as e:
        print(f"   UpdatedCarvemeTool测试失败: {e}")
    
    print("\n=== 集成测试完成 ===")

if __name__ == "__main__":
    test_tool_integration()