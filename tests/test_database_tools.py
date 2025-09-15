#!/usr/bin/env python3
"""
数据库工具测试脚本
用于测试EnviPath和KEGG工具的功能
"""

import sys
import os

# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

def test_envipath_tool():
    """测试EnviPath工具"""
    print("开始测试EnviPath工具...")
    print("=" * 30)
    
    try:
        # 测试EnviPathTool
        from tools.envipath_tool import EnviPathTool
        envipath_tool = EnviPathTool()
        
        print("1. 测试化合物搜索功能:")
        result = envipath_tool.search_compound("cadmium")
        if result["status"] == "success":
            print("   化合物搜索成功")
            print(f"   返回数据类型: {type(result['data'])}")
        else:
            print(f"   化合物搜索失败: {result.get('message', '未知错误')}")
            if 'suggestion' in result:
                print(f"   建议: {result['suggestion']}")
        
        print("\n2. 测试pathway关键词搜索功能:")
        result = envipath_tool.search_pathways_by_keyword("heavy metal")
        if result["status"] == "success":
            print("   pathway关键词搜索成功")
            print(f"   返回数据类型: {type(result['data'])}")
        else:
            print(f"   pathway关键词搜索失败: {result.get('message', '未知错误')}")
            if 'suggestion' in result:
                print(f"   建议: {result['suggestion']}")
        
        print("\nEnviPath工具测试完成!")
        
    except Exception as e:
        print(f"EnviPath工具测试出错: {e}")
        import traceback
        traceback.print_exc()

def test_kegg_tool():
    """测试KEGG工具"""
    print("\n开始测试KEGG工具...")
    print("=" * 30)
    
    try:
        # 测试KeggTool
        from tools.kegg_tool import KeggTool
        kegg_tool = KeggTool()
        
        print("1. 测试数据库信息获取:")
        result = kegg_tool.get_database_info("pathway")
        if result["status"] == "success":
            print("   数据库信息获取成功")
            print(f"   返回数据长度: {len(result['data']) if result['data'] else 0}")
        else:
            print(f"   数据库信息获取失败: {result.get('message', '未知错误')}")
        
        print("\n2. 测试基因搜索功能:")
        result = kegg_tool.find_entries("genes", "cadmium")
        if result["status"] == "success":
            print("   基因搜索成功")
            print(f"   找到条目数量: {result.get('count', 0)}")
            if result.get('data'):
                print(f"   前3个结果: {result['data'][:3]}")
        else:
            print(f"   基因搜索失败: {result.get('message', '未知错误')}")
        
        print("\n3. 测试pathway搜索功能:")
        result = kegg_tool.find_entries("pathway", "heavy metal")
        if result["status"] == "success":
            print("   pathway搜索成功")
            print(f"   找到条目数量: {result.get('count', 0)}")
            if result.get('data'):
                print(f"   前3个结果: {result['data'][:3]}")
        else:
            print(f"   pathway搜索失败: {result.get('message', '未知错误')}")
        
        print("\nKEGG工具测试完成!")
        
    except Exception as e:
        print(f"KEGG工具测试出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("数据库工具测试")
    print("=" * 30)
    
    # 测试EnviPath工具
    test_envipath_tool()
    
    # 测试KEGG工具
    test_kegg_tool()
    
    print("\n所有工具测试完成!")

if __name__ == "__main__":
    main()