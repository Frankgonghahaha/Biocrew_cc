#!/usr/bin/env python3
"""
测试本地数据查询功能，验证是否能遍历所有数据文件
"""

import sys
import os
# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool

def test_full_data_traversal():
    """测试遍历所有数据文件"""
    print("测试遍历所有数据文件")
    print("=" * 50)
    
    try:
        # 测试LocalDataRetriever
        print("1. 测试LocalDataRetriever工具:")
        data_retriever = LocalDataRetriever()
        
        # 列出所有可用污染物
        pollutants = data_retriever.list_available_pollutants()
        print(f"   可用基因数据污染物数量: {len(pollutants['genes_pollutants'])}")
        print(f"   可用微生物数据污染物数量: {len(pollutants['organism_pollutants'])}")
        
        # 显示所有基因数据污染物名称
        print("\n   基因数据污染物列表:")
        for i, pollutant in enumerate(pollutants['genes_pollutants'], 1):
            print(f"     {i:2d}. {pollutant}")
            
        # 显示所有微生物数据污染物名称
        print("\n   微生物数据污染物列表:")
        for i, pollutant in enumerate(pollutants['organism_pollutants'], 1):
            print(f"     {i:2d}. {pollutant}")
        
        # 测试读取每个基因数据文件
        print(f"\n2. 测试读取所有基因数据文件:")
        successful_genes = 0
        failed_genes = 0
        for pollutant in pollutants['genes_pollutants']:
            try:
                gene_data = data_retriever.get_gene_data(pollutant)
                if gene_data is not None:
                    print(f"   ✓ {pollutant}: 成功 ({gene_data.shape})")
                    successful_genes += 1
                else:
                    print(f"   ✗ {pollutant}: 读取失败")
                    failed_genes += 1
            except Exception as e:
                print(f"   ✗ {pollutant}: 错误 - {e}")
                failed_genes += 1
                
        # 测试读取每个微生物数据文件
        print(f"\n3. 测试读取所有微生物数据文件:")
        successful_organisms = 0
        failed_organisms = 0
        for pollutant in pollutants['organism_pollutants']:
            try:
                organism_data = data_retriever.get_organism_data(pollutant)
                if organism_data is not None:
                    print(f"   ✓ {pollutant}: 成功 ({organism_data.shape})")
                    successful_organisms += 1
                else:
                    print(f"   ✗ {pollutant}: 读取失败")
                    failed_organisms += 1
            except Exception as e:
                print(f"   ✗ {pollutant}: 错误 - {e}")
                failed_organisms += 1
        
        # 总结
        print(f"\n4. 测试总结:")
        print(f"   基因数据文件: 成功 {successful_genes}, 失败 {failed_genes}")
        print(f"   微生物数据文件: 成功 {successful_organisms}, 失败 {failed_organisms}")
        print(f"   总计: 成功 {successful_genes + successful_organisms}, 失败 {failed_genes + failed_organisms}")
        
        # 测试SmartDataQueryTool
        print("\n5. 测试SmartDataQueryTool工具:")
        smart_query = SmartDataQueryTool()
        
        # 测试查询一些常见的污染物
        test_queries = [
            "处理含有重金属镉的工业废水",
            "分析含有DDT的污染土壤",
            "降解多氯联苯污染物"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   测试查询 {i}: {query}")
            result = smart_query.query_related_data(query)
            
            if result["status"] == "success":
                print(f"     查询成功，匹配污染物数量: {len(result['matched_pollutants'])}")
                print(f"     成功查询基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
                print(f"     成功查询微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            else:
                print(f"     查询失败: {result.get('message', '未知错误')}")
        
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_data_traversal()