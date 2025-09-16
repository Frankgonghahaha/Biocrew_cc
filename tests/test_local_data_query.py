#!/usr/bin/env python3
"""
测试本地数据查询功能的脚本
"""

import sys
import os
# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool

def test_local_data_query():
    """测试本地数据查询功能"""
    print("测试本地数据查询功能")
    print("=" * 30)
    
    try:
        # 测试LocalDataRetriever
        print("1. 测试LocalDataRetriever工具:")
        data_retriever = LocalDataRetriever()
        
        # 列出可用污染物
        pollutants = data_retriever.list_available_pollutants()
        print(f"   可用基因数据污染物数量: {len(pollutants['genes_pollutants'])}")
        print(f"   可用微生物数据污染物数量: {len(pollutants['organism_pollutants'])}")
        
        # 测试含硫化合物相关数据查询（使用实际存在的数据）
        print("\n2. 测试含硫化合物相关数据查询:")
        # 尝试查找与含硫化合物相关的数据（如Perfluorooctane_Sulfonate）
        sulfur_related_genes = []
        sulfur_related_organisms = []
        
        for pollutant in pollutants['genes_pollutants']:
            if 'sulf' in pollutant.lower() or 'sulfonate' in pollutant.lower():
                sulfur_related_genes.append(pollutant)
        
        for pollutant in pollutants['organism_pollutants']:
            if 'sulf' in pollutant.lower() or 'sulfonate' in pollutant.lower():
                sulfur_related_organisms.append(pollutant)
        
        print(f"   与含硫化合物相关的基因数据文件: {sulfur_related_genes}")
        print(f"   与含硫化合物相关的微生物数据文件: {sulfur_related_organisms}")
        
        # 如果找到了相关数据，尝试读取
        if sulfur_related_genes:
            print(f"\n3. 尝试读取{sulfur_related_genes[0]}的基因数据:")
            gene_data = data_retriever.get_gene_data(sulfur_related_genes[0])
            if gene_data is not None:
                print(f"   成功读取数据，形状: {gene_data.shape}")
                print(f"   列名: {list(gene_data.columns)[:5]}...")
            else:
                print("   读取数据失败")
        else:
            print("   未找到含硫化合物相关的基因数据文件")
        
        # 测试SmartDataQueryTool
        print("\n4. 测试SmartDataQueryTool工具:")
        smart_query = SmartDataQueryTool()
        
        # 测试查询含硫化合物相关数据（使用实际存在的数据）
        test_query = "处理含有全氟辛烷磺酸盐的废水"
        result = smart_query.query_related_data(test_query)
        
        if result["status"] == "success":
            print(f"   查询成功，匹配污染物数量: {len(result['matched_pollutants'])}")
            print(f"   成功查询基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
            print(f"   成功查询微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            
            # 显示匹配的污染物
            print(f"   匹配的污染物: {result['matched_pollutants'][:5]}...")
        else:
            print(f"   查询失败: {result.get('message', '未知错误')}")
        
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_data_query()
