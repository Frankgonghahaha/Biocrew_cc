#!/usr/bin/env python3
"""
测试修复后的SmartDataQueryTool
"""

import sys
import os
# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

from tools.smart_data_query_tool import SmartDataQueryTool

def test_smart_data_query_tool():
    print("测试修复后的SmartDataQueryTool")
    print("=" * 40)
    
    smart_query = SmartDataQueryTool()
    
    test_queries = [
        "我们需要处理Alpha-hexachlorocyclohexane污染问题",
        "请分析含有Pentachlorophenol的污水"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试查询 {i}: {query}")
        result = smart_query.query_related_data(query)
        if result["status"] == "success":
            print(f"  匹配污染物数量: {len(result['matched_pollutants'])}")
            successful_genes = len([k for k, v in result["gene_data"].items() if "error" not in v])
            successful_organisms = len([k for k, v in result["organism_data"].items() if "error" not in v])
            print(f"  成功查询基因数据项数: {successful_genes}")
            print(f"  成功查询微生物数据项数: {successful_organisms}")
            
            # 显示一些成功查询的示例
            if successful_genes > 0:
                print("  成功的基因数据查询示例:")
                count = 0
                for pollutant, data in result["gene_data"].items():
                    if "error" not in data and count < 3:
                        print(f"    {pollutant}: {data['shape']}")
                        count += 1
                        
            if successful_organisms > 0:
                print("  成功的微生物数据查询示例:")
                count = 0
                for pollutant, data in result["organism_data"].items():
                    if "error" not in data and count < 3:
                        print(f"    {pollutant}: {data['shape']}")
                        count += 1
        else:
            print(f"  查询失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    test_smart_data_query_tool()