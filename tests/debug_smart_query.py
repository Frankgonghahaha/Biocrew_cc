#!/usr/bin/env python3
"""
调试SmartDataQueryTool中的文件查找问题
"""

import sys
import os
# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool

def debug_file_matching():
    """调试文件匹配问题"""
    print("调试文件匹配问题")
    print("=" * 50)
    
    # 创建LocalDataRetriever实例
    data_retriever = LocalDataRetriever()
    
    # 获取所有可用污染物
    pollutants = data_retriever.list_available_pollutants()
    print(f"基因数据污染物数量: {len(pollutants['genes_pollutants'])}")
    print(f"微生物数据污染物数量: {len(pollutants['organism_pollutants'])}")
    
    # 测试一些有问题的污染物名称
    test_pollutants = [
        'Hexachlorobutadiene',
        'Chlordane',
        'Heptachlor',
        'Polychlorinated_Biphenyls_Organisms',
        'Chlordecone _organismsxlsx',
        'Delta-hexachlorocyclohexane',
        'Perfluorooctane Sulfonate (PFOS)',
        'Beta-Hexachlorocyclohexane Genes',
        'Perfluorooctane_Sulfonate',
        'Dichlorodiphenyltrichloroethane(DDT)',
        'Polychlorinated_Dibenzo-p-Dioxin',
        'Hexabromodiphenyl_ether ',
        'Polychlorinated_Dibenzofuran',
        'PolyChlorinatedBiphenyls'
    ]
    
    print("\n测试文件查找:")
    for pollutant in test_pollutants:
        print(f"\n测试污染物: {pollutant}")
        
        # 测试基因数据查找
        try:
            gene_file = data_retriever._find_file_by_pollutant(data_retriever.genes_path, pollutant)
            if gene_file:
                print(f"  基因数据文件: {gene_file.name}")
            else:
                print(f"  基因数据文件: 未找到")
        except Exception as e:
            print(f"  基因数据查找错误: {e}")
            
        # 测试微生物数据查找
        try:
            organism_file = data_retriever._find_file_by_pollutant(data_retriever.organism_path, pollutant)
            if organism_file:
                print(f"  微生物数据文件: {organism_file.name}")
            else:
                print(f"  微生物数据文件: 未找到")
        except Exception as e:
            print(f"  微生物数据查找错误: {e}")

def debug_smart_query():
    """调试智能查询工具"""
    print("\n\n调试智能查询工具")
    print("=" * 50)
    
    # 创建SmartDataQueryTool实例
    smart_query = SmartDataQueryTool()
    
    # 测试提取污染物名称
    test_texts = [
        "我们需要处理Alpha-hexachlorocyclohexane污染问题",
        "请分析含有Pentachlorophenol的污水"
    ]
    
    for text in test_texts:
        print(f"\n测试文本: {text}")
        pollutant_names = smart_query._extract_pollutant_names(text)
        print(f"提取到的污染物名称: {pollutant_names}")

if __name__ == "__main__":
    debug_file_matching()
    debug_smart_query()