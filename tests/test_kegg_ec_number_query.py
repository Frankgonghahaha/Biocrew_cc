#!/usr/bin/env python3
"""
测试KEGG工具根据EC编号查询基因名称的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from core.tools.database.kegg import KeggTool


def test_kegg_ec_number_query():
    """测试KEGG工具根据EC编号查询基因名称的功能"""
    print("=== 开始测试KEGG工具EC编号查询功能 ===")
    
    # 创建KEGG工具实例
    print("1. 创建KEGG工具实例...")
    try:
        tool = KeggTool()
        print("   ✓ KEGG工具实例创建成功")
    except Exception as e:
        print(f"   ✗ KEGG工具实例创建失败: {e}")
        return
    
    # 测试通过EC编号查询基因
    print("\n2. 测试通过EC编号查询基因...")
    try:
        # 使用一个已知的EC编号进行测试
        ec_number = "1.14.12.7"  # 邻苯二甲酸酯酶
        print(f"   查询EC编号: {ec_number}")
        result = tool.search_genes_by_ec_number(ec_number)
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            print(f"   查询到 {result['count']} 个基因")
            if result['data']:
                print(f"   第一个基因ID: {result['data'][0].get('gene_id', 'N/A')}")
                print(f"   第一个基因名称: {result['data'][0].get('gene_name', 'N/A')}")
                print(f"   查询方法: {result['method']}")
            else:
                print("   未查询到基因信息")
        elif result['status'] == 'warning':
            print(f"   警告: {result.get('message', '未知警告')}")
            print("   尝试推断结果...")
            # 这里可以添加推断逻辑的测试
        else:
            print(f"   错误: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ EC编号查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试另一个EC编号
    print("\n3. 测试另一个EC编号...")
    try:
        # 使用另一个EC编号进行测试
        ec_number = "3.1.1.4"  # 脂肪酶
        print(f"   查询EC编号: {ec_number}")
        result = tool.search_genes_by_ec_number(ec_number)
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            print(f"   查询到 {result['count']} 个基因")
            if result['data']:
                print(f"   第一个基因ID: {result['data'][0].get('gene_id', 'N/A')}")
                print(f"   第一个基因名称: {result['data'][0].get('gene_name', 'N/A')}")
                print(f"   查询方法: {result['method']}")
        elif result['status'] == 'warning':
            print(f"   警告: {result.get('message', '未知警告')}")
            print("   尝试推断结果...")
        else:
            print(f"   错误: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ EC编号查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试工具调用接口
    print("\n4. 测试工具调用接口...")
    try:
        result = tool._run(ec_number="1.14.12.7")
        print(f"   工具调用结果状态: {result['status']}")
        if result['status'] == 'success':
            print(f"   查询到 {result['count']} 个基因")
            if result['data']:
                print(f"   第一个基因ID: {result['data'][0].get('gene_id', 'N/A')}")
                print(f"   第一个基因名称: {result['data'][0].get('gene_name', 'N/A')}")
        elif result['status'] == 'warning':
            print(f"   警告: {result.get('message', '未知警告')}")
        else:
            print(f"   错误: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 工具调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== KEGG工具EC编号查询测试完成 ===")


if __name__ == "__main__":
    test_kegg_ec_number_query()