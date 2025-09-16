#!/usr/bin/env python3
"""
测试 Aldrin 污染物数据查询功能的脚本
"""

import sys
import os
# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool
from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool

def test_aldrin_data_query():
    """测试 Aldrin 污染物数据查询功能"""
    print("测试 Aldrin 污染物数据查询功能")
    print("=" * 40)
    
    try:
        # 测试LocalDataRetriever
        print("1. 测试LocalDataRetriever工具:")
        data_retriever = LocalDataRetriever()
        
        # 列出可用污染物
        pollutants = data_retriever.list_available_pollutants()
        print(f"   可用基因数据污染物数量: {len(pollutants['genes_pollutants'])}")
        print(f"   可用微生物数据污染物数量: {len(pollutants['organism_pollutants'])}")
        
        # 查找 Aldrin 相关数据
        print("\n2. 查找 Aldrin 相关数据:")
        aldrin_related_genes = []
        aldrin_related_organisms = []
        
        for pollutant in pollutants['genes_pollutants']:
            if 'aldrin' in pollutant.lower() or 'Aldrin' in pollutant:
                aldrin_related_genes.append(pollutant)
        
        for pollutant in pollutants['organism_pollutants']:
            if 'aldrin' in pollutant.lower() or 'Aldrin' in pollutant:
                aldrin_related_organisms.append(pollutant)
        
        print(f"   与 Aldrin 相关的基因数据文件: {aldrin_related_genes}")
        print(f"   与 Aldrin 相关的微生物数据文件: {aldrin_related_organisms}")
        
        # 测试查询 Aldrin 微生物数据
        if aldrin_related_organisms:
            print(f"\n3. 尝试读取{aldrin_related_organisms[0]}的微生物数据:")
            organism_data = data_retriever.get_organism_data(aldrin_related_organisms[0])
            if organism_data is not None:
                print(f"   成功读取数据，形状: {organism_data.shape}")
                print(f"   列名: {list(organism_data.columns)[:5]}...")
                print(f"   前几行数据:")
                print(organism_data.head(3))
            else:
                print("   读取数据失败")
        else:
            print("   未找到 Aldrin 相关的微生物数据文件")
        
        # 测试SmartDataQueryTool
        print("\n4. 测试SmartDataQueryTool工具:")
        smart_query = SmartDataQueryTool()
        
        # 测试查询 Aldrin 相关数据
        test_query = "处理含有 Aldrin 的污水"
        result = smart_query.query_related_data(test_query)
        
        if result["status"] == "success":
            print(f"   查询成功，匹配污染物数量: {len(result['matched_pollutants'])}")
            print(f"   成功查询基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
            print(f"   成功查询微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            
            # 显示匹配的污染物
            print(f"   匹配的污染物: {result['matched_pollutants']}")
            
            # 显示查询到的数据
            if result['gene_data']:
                print("   基因数据:")
                for pollutant, data in result['gene_data'].items():
                    print(f"     {pollutant}: {data.get('shape', 'N/A')}")
            
            if result['organism_data']:
                print("   微生物数据:")
                for pollutant, data in result['organism_data'].items():
                    print(f"     {pollutant}: {data.get('shape', 'N/A')}")
        else:
            print(f"   查询失败: {result.get('message', '未知错误')}")
        
        # 测试MandatoryLocalDataQueryTool
        print("\n5. 测试MandatoryLocalDataQueryTool工具:")
        mandatory_query = MandatoryLocalDataQueryTool()
        
        # 测试查询 Aldrin 相关数据
        test_query = "处理含有 Aldrin 的污水"
        result = mandatory_query.query_required_data(test_query)
        
        if result["status"] == "success":
            print(f"   强制查询成功，匹配污染物数量: {len(result['matched_pollutants'])}")
            print(f"   成功查询基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
            print(f"   成功查询微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            
            # 显示匹配的污染物
            print(f"   匹配的污染物: {result['matched_pollutants']}")
        else:
            print(f"   强制查询失败: {result.get('message', '未知错误')}")
        
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_aldrin_data_query()