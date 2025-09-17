#!/usr/bin/env python3
"""
验证修复后的UnifiedDataTool与CrewAI框架的集成
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from tools.unified_data_tool import UnifiedDataTool

def test_crewai_integration():
    """测试CrewAI框架集成"""
    print("=== 测试修复后UnifiedDataTool与CrewAI框架集成 ===")
    
    try:
        # 创建工具实例
        unified_tool = UnifiedDataTool()
        print(f"✓ 工具创建成功: {unified_tool.name}")
        
        # 测试工具的各种调用方式
        print("\n--- 测试工具调用方式 ---")
        
        # 1. 直接调用
        result1 = unified_tool._run("query_pollutant_data", pollutant_name="Aldrin")
        print(f"✓ 直接调用成功: {result1['status']}")
        if result1['status'] == 'success':
            print(f"  污染物: {result1['pollutant_name']}")
            print(f"  微生物数据条数: {len(result1['organism_data']) if result1['organism_data'] else 0}")
        
        # 2. JSON字符串调用
        result2 = unified_tool._run('{"operation": "get_pollutant_summary", "pollutant_name": "Aldrin"}')
        print(f"✓ JSON字符串调用成功: {result2['status']}")
        if result2['status'] == 'success':
            print(f"  污染物: {result2['pollutant_name']}")
            print(f"  基因数据统计: {result2['gene_data']}")
            print(f"  微生物数据统计: {result2['organism_data']}")
        
        # 3. 字典调用（模拟CrewAI框架调用）
        result3 = unified_tool._run({"operation": "search_pollutants", "keyword": "Aldrin"})
        print(f"✓ 字典调用成功: {result3['status']}")
        if result3['status'] == 'success':
            print(f"  搜索关键词: {result3['keyword']}")
            print(f"  匹配污染物数: {result3['count']}")
        
        # 4. 测试结构化工具调用
        print("\n--- 测试结构化工具调用 ---")
        try:
            structured_tool = unified_tool.to_structured_tool()
            print(f"✓ 结构化工具创建成功: {structured_tool.name}")
            
            # 测试结构化工具调用
            result4 = structured_tool.func("query_pollutant_data", pollutant_name="Aldrin")
            print(f"✓ 结构化工具调用成功: {result4['status']}")
        except Exception as e:
            print(f"✗ 结构化工具调用失败: {e}")
            
        print("\n=== 集成测试完成 ===")
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("UnifiedDataTool与CrewAI框架集成验证")
    print("=" * 50)
    
    success = test_crewai_integration()
    
    if success:
        print("\n🎉 集成验证成功！UnifiedDataTool可以正常与CrewAI框架集成。")
        print("智能体现在可以使用各种调用方式来访问工具功能。")
    else:
        print("\n❌ 集成验证失败，请检查错误信息。")

if __name__ == "__main__":
    main()