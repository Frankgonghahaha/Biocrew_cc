#!/usr/bin/env python3
"""
KEGG工具完整功能测试脚本
用于测试KEGG工具的所有功能，包括改进的基因和微生物信息获取
"""

import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.kegg_tool import KeggTool

def test_compound_to_pathway_workflow():
    """测试化合物到路径的完整工作流"""
    print("开始测试化合物到路径的完整工作流...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    
    # 测试几种常见的污染物
    test_compounds = ["phthalate", "dibutyl phthalate"]
    
    for compound in test_compounds:
        print(f"\n测试化合物: {compound}")
        try:
            result = kegg_tool.compound_to_pathway_workflow(compound, 3)
            if result.get("status") == "success":
                print(f"  ✓ 工作流执行成功")
                print(f"    查询类型: {result.get('query_type', 'N/A')}")
                if "compound" in result:
                    compound_info = result["compound"]
                    print(f"    化合物ID: {compound_info.get('id', 'N/A')}")
                    print(f"    化合物名称: {compound_info.get('name', 'N/A')}")
                if "pathways" in result:
                    pathway_count = len(result["pathways"])
                    print(f"    相关Pathway数量: {pathway_count}")
                    if pathway_count > 0:
                        print(f"    第一个Pathway: {result['pathways'][0].get('name', 'N/A')}")
                if "genes" in result:
                    gene_count = len(result["genes"])
                    print(f"    相关基因数量: {gene_count}")
                if "enzymes" in result:
                    enzyme_count = len(result["enzymes"])
                    print(f"    相关酶数量: {enzyme_count}")
                if "reactions" in result:
                    reaction_count = len(result["reactions"])
                    print(f"    相关反应数量: {reaction_count}")
            else:
                print(f"  ⚠ 工作流返回: {result.get('message', '未知状态')}")
        except Exception as e:
            print(f"  ✗ 工作流执行异常: {e}")

def test_smart_query_function():
    """测试智能查询功能"""
    print("\n开始测试智能查询功能...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    
    # 测试智能查询
    test_compounds = ["phthalate", "benzene"]
    
    for compound in test_compounds:
        print(f"\n测试智能查询: {compound}")
        try:
            result = kegg_tool.smart_query(compound)
            if result.get("status") == "success":
                print(f"  ✓ 智能查询成功")
                print(f"    查询类型: {result.get('query_type', 'N/A')}")
                if "compound" in result and result["compound"].get("status") == "success":
                    compound_data = result["compound"].get("data", {})
                    print(f"    化合物: {compound_data.get('description', 'N/A')}")
                if "pathways" in result and result["pathways"].get("status") == "success":
                    pathway_count = len(result["pathways"].get("data", []))
                    print(f"    Pathway数量: {pathway_count}")
                if "genes" in result and result["genes"].get("status") == "success":
                    gene_count = len(result["genes"].get("genes", []))
                    print(f"    基因数量: {gene_count}")
                if "microbes" in result and result["microbes"].get("status") == "success":
                    microbe_count = len(result["microbes"].get("microbes", []))
                    print(f"    微生物数量: {microbe_count}")
                    if microbe_count > 0:
                        first_microbe = result["microbes"]["microbes"][0]
                        print(f"    第一个微生物: {first_microbe.get('microbe', 'N/A')}")
                        print(f"    来源: {first_microbe.get('source', 'N/A')}")
            else:
                print(f"  ⚠ 智能查询返回: {result.get('message', '未知状态')}")
        except Exception as e:
            print(f"  ✗ 智能查询异常: {e}")

def test_gene_and_microbe_extraction():
    """测试基因和微生物信息提取功能"""
    print("\n开始测试基因和微生物信息提取功能...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    
    # 测试基因信息获取
    print("\n1. 测试基因信息获取...")
    try:
        # 先获取一个pathway
        pathway_result = kegg_tool.find_entries("pathway", "degradation", 1)
        if pathway_result.get("status") == "success" and pathway_result.get("data"):
            pathway_id = pathway_result["data"][0]["id"]
            print(f"  使用Pathway: {pathway_id}")
            
            # 获取基因信息
            gene_result = kegg_tool.search_genes_by_pathway(pathway_id)
            if gene_result.get("status") == "success":
                print("  ✓ 基因信息获取成功")
                print(f"    基因数量: {gene_result.get('count', 0)}")
                if gene_result.get("data"):
                    print(f"    第一个基因: {gene_result['data'][0].get('target', 'N/A')}")
            else:
                print(f"  ⚠ 基因信息获取返回: {gene_result.get('message', '未知状态')}")
        else:
            print("  ⚠ 未找到Pathway信息")
    except Exception as e:
        print(f"  ✗ 基因信息获取异常: {e}")
    
    # 测试酶信息获取
    print("\n2. 测试酶信息获取...")
    try:
        # 先获取一个化合物
        compound_result = kegg_tool.find_entries("compound", "phthalate", 1)
        if compound_result.get("status") == "success" and compound_result.get("data"):
            compound_id = compound_result["data"][0]["id"]
            print(f"  使用化合物: {compound_id}")
            
            # 获取酶信息
            enzyme_result = kegg_tool.search_enzymes_by_compound(compound_id)
            if enzyme_result.get("status") == "success":
                print("  ✓ 酶信息获取成功")
                print(f"    酶数量: {enzyme_result.get('count', 0)}")
                if enzyme_result.get("data"):
                    print(f"    第一个酶: {enzyme_result['data'][0].get('target', 'N/A')}")
            else:
                print(f"  ⚠ 酶信息获取返回: {enzyme_result.get('message', '未知状态')}")
        else:
            print("  ⚠ 未找到化合物信息")
    except Exception as e:
        print(f"  ✗ 酶信息获取异常: {e}")

def main():
    """主函数"""
    print("KEGG工具完整功能测试脚本")
    print("=" * 50)
    
    # 测试化合物到路径的完整工作流
    test_compound_to_pathway_workflow()
    
    # 测试智能查询功能
    test_smart_query_function()
    
    # 测试基因和微生物信息提取功能
    test_gene_and_microbe_extraction()
    
    print("\n" + "=" * 50)
    print("KEGG工具完整功能测试完成")

if __name__ == "__main__":
    main()