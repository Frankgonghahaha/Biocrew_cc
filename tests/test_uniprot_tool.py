#!/usr/bin/env python3
"""
测试UniProt工具的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from core.tools.database.uniprot import UniProtTool


def test_uniprot_tool():
    """测试UniProt工具"""
    print("=== 开始测试UniProt工具 ===")
    
    # 创建UniProt工具实例
    print("1. 创建UniProt工具实例...")
    try:
        tool = UniProtTool()
        print("   ✓ UniProt工具实例创建成功")
    except Exception as e:
        print(f"   ✗ UniProt工具实例创建失败: {e}")
        return
    
    # 测试通过蛋白质名称查询
    print("\n2. 测试通过蛋白质名称查询...")
    try:
        result = tool.search_by_protein_name("lacZ", limit=5)
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            print(f"   查询到的结果数量: {len(result['results'])}")
            if result['results']:
                print(f"   第一个结果的ID: {result['results'][0].get('primaryAccession', 'N/A')}")
                print(f"   第一个结果的基因名: {result['results'][0].get('genes', [{}])[0].get('geneName', {}).get('value', 'N/A')}")
        else:
            print(f"   错误信息: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 通过蛋白质名称查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通过基因名称查询
    print("\n3. 测试通过基因名称查询...")
    try:
        result = tool.search_by_gene_name("lacZ", limit=5)
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            print(f"   查询到的结果数量: {len(result['results'])}")
            if result['results']:
                print(f"   第一个结果的ID: {result['results'][0].get('primaryAccession', 'N/A')}")
        else:
            print(f"   错误信息: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 通过基因名称查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通过UniProt ID查询
    print("\n4. 测试通过UniProt ID查询...")
    try:
        result = tool.search_by_id("P00722")  # β-半乳糖苷酶
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            print(f"   查询到的结果数量: {len(result['results'])}")
            if result['results']:
                print(f"   蛋白质名称: {result['results'][0].get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', 'N/A')}")
        else:
            print(f"   错误信息: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 通过UniProt ID查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试获取蛋白质序列
    print("\n5. 测试获取蛋白质序列...")
    try:
        result = tool.get_protein_sequence("P00722")  # β-半乳糖苷酶
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            sequence = result['sequence']
            print(f"   序列长度: {len(sequence)}")
            if len(sequence) > 20:
                print(f"   序列前20个字符: {sequence[:20]}...")
            else:
                print(f"   序列: {sequence}")
        else:
            print(f"   错误信息: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 获取蛋白质序列失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== UniProt工具测试完成 ===")


if __name__ == "__main__":
    test_uniprot_tool()