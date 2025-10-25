#!/usr/bin/env python3
"""
单独测试UniProt工具的蛋白质序列查询功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from core.tools.database.uniprot import UniProtTool


def test_protein_sequence_query():
    """测试UniProt工具的蛋白质序列查询功能"""
    print("=== 开始测试UniProt工具蛋白质序列查询功能 ===")
    
    # 创建UniProt工具实例
    print("1. 创建UniProt工具实例...")
    try:
        tool = UniProtTool()
        print("   ✓ UniProt工具实例创建成功")
    except Exception as e:
        print(f"   ✗ UniProt工具实例创建失败: {e}")
        return
    
    # 测试获取已知蛋白质的序列
    print("\n2. 测试获取β-半乳糖苷酶蛋白质序列...")
    try:
        # 使用已知的UniProt ID P00722 (β-galactosidase from E. coli)
        result = tool.get_protein_sequence("P00722")
        print(f"   查询结果状态: {result['status']}")
        if result['status'] == 'success':
            sequence = result['sequence']
            print(f"   序列长度: {len(sequence)}")
            if len(sequence) > 100:
                print(f"   序列前100个字符: {sequence[:100]}...")
            else:
                print(f"   完整序列: {sequence}")
            
            # 验证是否是FASTA格式
            if sequence.startswith('>'):
                print("   ✓ 序列格式正确 (FASTA格式)")
            else:
                print("   ✗ 序列格式不正确，应为FASTA格式")
        else:
            print(f"   错误信息: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 获取蛋白质序列失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通过蛋白质名称查询并获取序列
    print("\n3. 测试通过蛋白质名称查询并获取序列...")
    try:
        # 首先通过蛋白质名称查询
        search_result = tool.search_by_protein_name("lacZ", limit=1)
        print(f"   查询结果状态: {search_result['status']}")
        if search_result['status'] == 'success' and search_result['results']:
            # 获取第一个结果的UniProt ID
            uniprot_id = search_result['results'][0].get('primaryAccession')
            if uniprot_id:
                print(f"   找到蛋白质ID: {uniprot_id}")
                # 获取该蛋白质的序列
                sequence_result = tool.get_protein_sequence(uniprot_id)
                print(f"   序列查询结果状态: {sequence_result['status']}")
                if sequence_result['status'] == 'success':
                    sequence = sequence_result['sequence']
                    print(f"   序列长度: {len(sequence)}")
                    if len(sequence) > 100:
                        print(f"   序列前100个字符: {sequence[:100]}...")
                    else:
                        print(f"   完整序列: {sequence}")
                else:
                    print(f"   错误信息: {sequence_result.get('message', '未知错误')}")
            else:
                print("   未找到有效的UniProt ID")
        else:
            print(f"   查询失败或未找到结果: {search_result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 通过蛋白质名称查询并获取序列失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通过基因名称查询并获取序列
    print("\n4. 测试通过基因名称查询并获取序列...")
    try:
        # 首先通过基因名称查询
        search_result = tool.search_by_gene_name("lacZ", limit=1)
        print(f"   查询结果状态: {search_result['status']}")
        if search_result['status'] == 'success' and search_result['results']:
            # 获取第一个结果的UniProt ID
            uniprot_id = search_result['results'][0].get('primaryAccession')
            if uniprot_id:
                print(f"   找到蛋白质ID: {uniprot_id}")
                # 获取该蛋白质的序列
                sequence_result = tool.get_protein_sequence(uniprot_id)
                print(f"   序列查询结果状态: {sequence_result['status']}")
                if sequence_result['status'] == 'success':
                    sequence = sequence_result['sequence']
                    print(f"   序列长度: {len(sequence)}")
                    if len(sequence) > 100:
                        print(f"   序列前100个字符: {sequence[:100]}...")
                    else:
                        print(f"   完整序列: {sequence}")
                else:
                    print(f"   错误信息: {sequence_result.get('message', '未知错误')}")
            else:
                print("   未找到有效的UniProt ID")
        else:
            print(f"   查询失败或未找到结果: {search_result.get('message', '未知错误')}")
    except Exception as e:
        print(f"   ✗ 通过基因名称查询并获取序列失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== UniProt工具蛋白质序列查询测试完成 ===")


if __name__ == "__main__":
    test_protein_sequence_query()