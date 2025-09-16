#!/usr/bin/env python3
"""
直接查询功能微生物数据（无需API密钥）
支持用户输入不同的污染物名称
"""

import sys
import os

# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool

def get_user_input():
    """获取用户输入的污染物名称"""
    print("请输入要查询的污染物名称:")
    print("示例: Aldrin, DDT, PFOS, Endosulfan 等")
    pollutant_name = input("污染物名称: ").strip()
    return pollutant_name

def analyze_microorganisms(pollutant_name):
    """分析指定污染物的降解功能微生物"""
    print(f"分析{pollutant_name}降解功能微生物")
    print("=" * 40)
    
    # 初始化本地数据读取工具
    data_retriever = LocalDataRetriever(base_path=".")
    
    # 直接查询指定污染物的微生物数据
    print(f"1. 直接查询{pollutant_name}微生物数据:")
    try:
        organism_data = data_retriever.get_organism_data(pollutant_name)
        if organism_data is not None:
            print(f"   数据形状: {organism_data.shape}")
            print(f"   列名: {list(organism_data.columns)}")
            print("\n   前5行数据:")
            for index, row in organism_data.head().iterrows():
                print(f"   - 微生物: {row.get('Strain ID/Microorganism', 'N/A')}")
                print(f"     有机体: {row.get('Organism', 'N/A')}")
                print(f"     研究链接: {row.get('Research link', 'N/A')}")
                print()
        else:
            print(f"   未找到{pollutant_name}的微生物数据")
    except Exception as e:
        print(f"   读取{pollutant_name}微生物数据时出错: {e}")
    
    # 使用智能查询工具
    print(f"2. 使用智能查询工具:")
    smart_query = SmartDataQueryTool(base_path=".")
    query_text = f"识别能降解{pollutant_name}污染物的功能微生物"
    result = smart_query.query_related_data(query_text)
    
    if result.get('status') == 'success':
        print(f"   匹配的污染物: {result.get('matched_pollutants', [])}")
        # 查找与用户输入最匹配的污染物
        matched_pollutant = None
        for p in result.get('matched_pollutants', []):
            if pollutant_name.lower() in p.lower() or p.lower() in pollutant_name.lower():
                matched_pollutant = p
                break
        
        if matched_pollutant:
            organism_data = result['organism_data'].get(matched_pollutant, {})
            if organism_data and 'error' not in organism_data:
                print(f"   {matched_pollutant}微生物数据形状: {organism_data.get('shape')}")
                print("   具体数据:")
                sample_data = organism_data.get('sample_data', [])
                for i, item in enumerate(sample_data):
                    print(f"   {i+1}. 微生物: {item.get('Strain ID/Microorganism', 'N/A')}")
                    print(f"      有机体: {item.get('Organism', 'N/A')}")
                    print(f"      代谢产物: {item.get('Primary Intermediate/s', 'N/A')}")
                    print(f"      研究参考: {item.get('Reference', 'N/A')}")
                    print()
        else:
            print(f"   未找到与'{pollutant_name}'精确匹配的污染物数据")
    else:
        print(f"   查询失败: {result.get('message', '未知错误')}")

def main():
    # 获取用户输入
    pollutant_name = get_user_input()
    
    # 如果用户没有输入，使用默认值Aldrin
    if not pollutant_name:
        pollutant_name = "Aldrin"
        print("未输入污染物名称，使用默认值'Aldrin'")
    
    # 分析指定污染物的功能微生物
    analyze_microorganisms(pollutant_name)

if __name__ == "__main__":
    main()