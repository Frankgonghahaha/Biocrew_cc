#!/usr/bin/env python3
"""
直接测试EnviPath工具的功能
用于验证工具是否能正确返回代谢路径信息
"""

import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from tools.envipath_tool import EnviPathTool

def test_envipath_tool():
    """测试EnviPath工具"""
    print("开始测试EnviPath工具...")
    
    # 创建EnviPath工具实例
    try:
        envipath_tool = EnviPathTool()
        print("✓ EnviPath工具初始化成功")
    except Exception as e:
        print(f"✗ EnviPath工具初始化失败: {e}")
        return
    
    # 测试化合物搜索
    print("\n1. 测试化合物搜索...")
    try:
        compound_name = "dibutyl phthalate"
        print(f"搜索化合物: {compound_name}")
        search_result = envipath_tool.search_compound(compound_name)
        print(f"搜索结果状态: {search_result['status']}")
        
        if search_result["status"] == "success" and search_result["data"]:
            print("✓ 化合物搜索成功")
            # 显示结果类型
            print(f"  结果类型: {type(search_result['data'])}")
            print(f"  结果内容: {search_result['data']}")
            
            # 检查是否有pathway数据
            if 'pathway' in search_result['data']:
                pathway_data = search_result['data']['pathway']
                print(f"  包含路径数据: {pathway_data}")
                if pathway_data:
                    # 获取第一个路径的ID
                    first_pathway = pathway_data[0]
                    print(f"  第一个路径: {first_pathway}")
                    if hasattr(first_pathway, 'id'):
                        pathway_id = getattr(first_pathway, 'id', None)
                        if pathway_id:
                            print(f"  路径ID: {pathway_id}")
                            # 尝试获取路径详细信息
                            print("  尝试获取路径详细信息...")
                            pathway_detail = envipath_tool.get_pathway_info_as_json(pathway_id)
                            print(f"  路径详细信息: {pathway_detail}")
        else:
            print("✗ 化合物搜索失败或无结果")
            print(f"  错误信息: {search_result.get('message', '无错误信息')}")
    except Exception as e:
        print(f"✗ 化合物搜索异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通过关键字搜索路径
    print("\n2. 测试通过关键字搜索路径...")
    try:
        keyword = "phthalate"
        print(f"搜索关键字: {keyword}")
        search_result = envipath_tool.search_pathways_by_keyword(keyword)
        print(f"搜索结果状态: {search_result['status']}")
        
        if search_result["status"] == "success":
            print("✓ 路径搜索成功")
            # 显示结果
            print(f"  结果内容: {search_result['data']}")
        else:
            print("✗ 路径搜索失败")
            print(f"  错误信息: {search_result.get('message', '无错误信息')}")
    except Exception as e:
        print(f"✗ 路径搜索异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试特定路径ID的详细信息
    print("\n3. 测试特定路径ID的详细信息...")
    try:
        # 使用已知的Phthalate Family路径ID
        pathway_id = "033f7ed7-d7c1-4bbc-83be-8d89617f76fe"
        print(f"获取路径详细信息: {pathway_id}")
        pathway_detail = envipath_tool.get_pathway_info_as_json(pathway_id)
        print(f"路径详细信息: {pathway_detail}")
    except Exception as e:
        print(f"✗ 获取路径详细信息异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_envipath_tool()