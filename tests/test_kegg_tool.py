#!/usr/bin/env python3
"""
KEGG工具测试脚本
用于测试KEGG工具的各项功能
"""

import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.kegg_tool import KeggTool

def test_kegg_tool_basic_functions():
    """测试KEGG工具的基本功能"""
    print("开始测试KEGG工具基本功能...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    print("✓ KEGG工具实例创建成功")
    
    # 测试化合物搜索功能
    print("\n1. 测试化合物搜索功能...")
    try:
        result = kegg_tool.find_entries("compound", "phthalate", 3)
        if result.get("status") == "success":
            print("  ✓ 化合物搜索功能正常")
            print(f"  搜索结果数量: {result.get('count', 0)}")
            if result.get("data"):
                print(f"  第一个结果: {result['data'][0].get('description', 'N/A')}")
        else:
            print(f"  ✗ 化合物搜索失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"  ✗ 化合物搜索异常: {e}")
    
    # 测试pathway搜索功能
    print("\n2. 测试pathway搜索功能...")
    try:
        result = kegg_tool.find_entries("pathway", "degradation", 3)
        if result.get("status") == "success":
            print("  ✓ Pathway搜索功能正常")
            print(f"  搜索结果数量: {result.get('count', 0)}")
            if result.get("data"):
                print(f"  第一个结果: {result['data'][0].get('description', 'N/A')}")
        else:
            print(f"  ✗ Pathway搜索失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"  ✗ Pathway搜索异常: {e}")
    
    # 测试智能查询功能
    print("\n3. 测试智能查询功能...")
    try:
        result = kegg_tool.smart_query("phthalate")
        if result.get("status") == "success":
            print("  ✓ 智能查询功能正常")
            print(f"  查询类型: {result.get('query_type', 'N/A')}")
            if "compound" in result and result["compound"].get("status") == "success":
                print(f"  化合物信息: {result['compound'].get('data', {}).get('description', 'N/A')}")
            if "pathways" in result and result["pathways"].get("status") == "success":
                print(f"  路径信息数量: {len(result['pathways'].get('data', []))}")
        else:
            print(f"  ⚠ 智能查询返回警告: {result.get('message', '未知警告')}")
    except Exception as e:
        print(f"  ✗ 智能查询异常: {e}")

def test_kegg_tool_advanced_functions():
    """测试KEGG工具的高级功能"""
    print("\n开始测试KEGG工具高级功能...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    
    # 测试基因信息获取
    print("\n1. 测试基因信息获取...")
    try:
        # 先获取一个化合物的信息
        compound_result = kegg_tool.find_entries("compound", "phthalate", 1)
        if compound_result.get("status") == "success" and compound_result.get("data"):
            compound_id = compound_result["data"][0]["id"]
            print(f"  使用化合物: {compound_id}")
            
            # 获取相关pathway
            pathway_result = kegg_tool.search_pathway_by_compound(compound_id)
            if pathway_result.get("status") == "success" and pathway_result.get("data"):
                pathway_id = pathway_result["data"][0]["target"]
                print(f"  相关Pathway: {pathway_id}")
                
                # 获取基因信息
                gene_result = kegg_tool.search_genes_by_pathway(pathway_id)
                if gene_result.get("status") == "success":
                    print("  ✓ 基因信息获取功能正常")
                    print(f"  基因数量: {gene_result.get('count', 0)}")
                    if gene_result.get("data"):
                        print(f"  第一个基因: {gene_result['data'][0].get('target', 'N/A')}")
                else:
                    print(f"  ⚠ 基因信息获取返回警告: {gene_result.get('message', '未知警告')}")
            else:
                print("  ⚠ 未找到相关Pathway信息")
        else:
            print("  ⚠ 未找到化合物信息")
    except Exception as e:
        print(f"  ✗ 基因信息获取异常: {e}")

def test_specific_compounds():
    """测试特定化合物的查询"""
    print("\n开始测试特定化合物查询...")
    
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    
    # 测试几种常见的污染物
    test_compounds = ["phthalate", "dibutyl phthalate", "benzene", "toluene"]
    
    for compound in test_compounds:
        print(f"\n测试化合物: {compound}")
        try:
            result = kegg_tool.smart_query(compound)
            if result.get("status") == "success":
                print(f"  ✓ 查询成功")
                if "compound" in result and result["compound"].get("status") == "success":
                    print(f"    化合物: {result['compound']['data'].get('description', 'N/A')}")
                if "pathways" in result and result["pathways"].get("status") == "success":
                    pathway_count = len(result["pathways"].get("data", []))
                    print(f"    相关Pathway数量: {pathway_count}")
                if "genes" in result and result["genes"].get("status") == "success":
                    gene_count = len(result["genes"].get("genes", []))
                    print(f"    相关基因数量: {gene_count}")
                if "microbes" in result and result["microbes"].get("status") == "success":
                    microbe_count = len(result["microbes"].get("microbes", []))
                    print(f"    相关微生物数量: {microbe_count}")
            else:
                print(f"  ⚠ 查询返回警告: {result.get('message', '未知警告')}")
        except Exception as e:
            print(f"  ✗ 查询异常: {e}")

def main():
    """主函数"""
    print("KEGG工具测试脚本")
    print("=" * 50)
    
    # 测试基本功能
    test_kegg_tool_basic_functions()
    
    # 测试高级功能
    test_kegg_tool_advanced_functions()
    
    # 测试特定化合物
    test_specific_compounds()
    
    print("\n" + "=" * 50)
    print("KEGG工具测试完成")

if __name__ == "__main__":
    main()