#!/usr/bin/env python3
"""
测试脚本：支持用户输入的数据库查询测试
用户可以输入污染物名称，系统将查询相关的基因和微生物数据
"""

import sys
import os
import pandas as pd

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def get_user_input():
    """获取用户输入的污染物名称"""
    print("请输入要查询的污染物名称:")
    print("例如: Alpha-hexachlorocyclohexane, Lindane, Benzene 等")
    pollutant_name = input("污染物名称: ").strip()
    return pollutant_name

def check_pollutant_data(pollutant_name):
    """检查指定污染物相关的基因和微生物数据"""
    print(f"检查 {pollutant_name} 相关数据...")
    print("=" * 50)
    
    # 构建文件路径
    gene_file_path = f"/home/axlhuang/BioCrew/data/Genes/{pollutant_name}_Genes.xlsx"
    organism_file_path = f"/home/axlhuang/BioCrew/data/Organism/{pollutant_name}_organisms.xlsx"
    
    # 检查基因数据
    print("1. 检查基因数据文件...")
    if os.path.exists(gene_file_path):
        print(f"   ✓ 基因数据文件存在: {gene_file_path}")
        try:
            # 读取Excel文件
            gene_df = pd.read_excel(gene_file_path)
            print(f"   ✓ 基因数据读取成功，共有 {len(gene_df)} 行数据")
            
            # 显示前几行数据
            print("   前5行基因数据:")
            print(gene_df.head())
            
            # 显示列名
            print(f"   列名: {list(gene_df.columns)}")
        except Exception as e:
            print(f"   ✗ 读取基因数据文件时出错: {e}")
    else:
        print(f"   ✗ 基因数据文件不存在: {gene_file_path}")
    
    print("\n" + "-" * 30 + "\n")
    
    # 检查微生物数据
    print("2. 检查微生物数据文件...")
    if os.path.exists(organism_file_path):
        print(f"   ✓ 微生物数据文件存在: {organism_file_path}")
        try:
            # 读取Excel文件
            organism_df = pd.read_excel(organism_file_path)
            print(f"   ✓ 微生物数据读取成功，共有 {len(organism_df)} 行数据")
            
            # 显示前几行数据
            print("   前5行微生物数据:")
            print(organism_df.head())
            
            # 显示列名
            print(f"   列名: {list(organism_df.columns)}")
        except Exception as e:
            print(f"   ✗ 读取微生物数据文件时出错: {e}")
    else:
        print(f"   ✗ 微生物数据文件不存在: {organism_file_path}")

def search_similar_pollutants(pollutant_name):
    """搜索相似污染物的数据文件"""
    print("\n" + "=" * 50)
    print("搜索相似污染物的数据文件...")
    
    # 搜索基因数据目录中包含输入名称的文件
    genes_dir = "/home/axlhuang/BioCrew/data/Genes/"
    organism_dir = "/home/axlhuang/BioCrew/data/Organism/"
    
    print(f"1. 基因数据目录中包含'{pollutant_name}'的文件:")
    found_genes = False
    for file in os.listdir(genes_dir):
        if pollutant_name.lower() in file.lower():
            print(f"   - {file}")
            found_genes = True
    if not found_genes:
        print("   未找到相关文件")
    
    print(f"\n2. 微生物数据目录中包含'{pollutant_name}'的文件:")
    found_organisms = False
    for file in os.listdir(organism_dir):
        if pollutant_name.lower() in file.lower():
            print(f"   - {file}")
            found_organisms = True
    if not found_organisms:
        print("   未找到相关文件")

def list_available_pollutants():
    """列出所有可用的污染物数据"""
    print("\n" + "=" * 50)
    print("所有可用的污染物数据:")
    
    # 列出基因数据目录中的所有污染物
    genes_dir = "/home/axlhuang/BioCrew/data/Genes/"
    organism_dir = "/home/axlhuang/BioCrew/data/Organism/"
    
    # 获取所有污染物名称
    pollutants = set()
    
    # 从基因数据目录获取
    for file in os.listdir(genes_dir):
        if file.endswith("_Genes.xlsx"):
            pollutant = file.replace("_Genes.xlsx", "")
            pollutants.add(pollutant)
    
    # 从微生物数据目录获取
    for file in os.listdir(organism_dir):
        if file.endswith("_organisms.xlsx"):
            pollutant = file.replace("_organisms.xlsx", "")
            pollutants.add(pollutant)
    
    print("可用的污染物:")
    for i, pollutant in enumerate(sorted(pollutants), 1):
        print(f"   {i}. {pollutant}")

if __name__ == "__main__":
    print("数据库查询测试脚本（支持用户输入）")
    print("=" * 50)
    
    # 列出所有可用的污染物
    list_available_pollutants()
    
    # 获取用户输入
    print("\n" + "=" * 50)
    pollutant_name = get_user_input()
    
    # 如果用户没有输入，则使用默认值
    if not pollutant_name:
        print("未输入污染物名称，使用默认值: Alpha-hexachlorocyclohexane")
        pollutant_name = "Alpha-hexachlorocyclohexane"
    
    # 检查数据
    check_pollutant_data(pollutant_name)
    search_similar_pollutants(pollutant_name)
    
    print("\n" + "=" * 50)
    print("查询完成")