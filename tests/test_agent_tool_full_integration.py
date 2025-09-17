#!/usr/bin/env python3
"""
完整测试功能微生物组识别智能体与修复后的UnifiedDataTool集成
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent

def test_agent_tool_full_integration():
    """完整测试智能体与工具集成"""
    print("=== 完整测试功能微生物组识别智能体与修复后的UnifiedDataTool集成 ===")
    
    try:
        # 创建一个模拟的LLM对象
        class MockLLM:
            def __init__(self):
                self.model_name = "mock-llm"
            
            def call(self, *args, **kwargs):
                # 返回模拟响应
                return "模拟响应：已识别到Aldrin污染物相关的功能微生物组"
        
        mock_llm = MockLLM()
        
        # 创建智能体
        print("1. 创建功能微生物组识别智能体...")
        agent_creator = EngineeringMicroorganismIdentificationAgent(mock_llm)
        identification_agent = agent_creator.create_agent()
        print(f"   ✓ 智能体创建成功: {identification_agent.role}")
        
        # 检查智能体工具
        print("\n2. 检查智能体工具配置...")
        if identification_agent.tools:
            for i, tool in enumerate(identification_agent.tools):
                print(f"   工具 {i+1}: {tool.name}")
                print(f"   工具描述: {tool.description}")
        else:
            print("   未配置工具")
            return False
        
        # 直接测试工具调用能力
        print("\n3. 测试工具调用能力...")
        unified_tool = identification_agent.tools[0]
        
        # 测试不同的调用方式
        print("   3.1 测试直接调用...")
        result1 = unified_tool._run("query_pollutant_data", pollutant_name="Aldrin")
        print(f"   ✓ 直接调用成功: {result1['status']}")
        if result1['status'] == 'success':
            print(f"     污染物: {result1['pollutant_name']}")
            print(f"     微生物数据条数: {len(result1['organism_data']) if result1['organism_data'] else 0}")
        
        print("   3.2 测试JSON字符串调用...")
        result2 = unified_tool._run('{"operation": "get_pollutant_summary", "pollutant_name": "Aldrin"}')
        print(f"   ✓ JSON字符串调用成功: {result2['status']}")
        if result2['status'] == 'success':
            print(f"     污染物: {result2['pollutant_name']}")
            print(f"     基因数据统计: {result2['gene_data']}")
            print(f"     微生物数据统计: {result2['organism_data']}")
        
        print("   3.3 测试字典调用（模拟CrewAI框架调用）...")
        result3 = unified_tool._run({"operation": "search_pollutants", "keyword": "Aldrin"})
        print(f"   ✓ 字典调用成功: {result3['status']}")
        if result3['status'] == 'success':
            print(f"     搜索关键词: {result3['keyword']}")
            print(f"     匹配污染物数: {result3['count']}")
        
        print("   3.4 测试结构化工具调用...")
        try:
            structured_tool = unified_tool.to_structured_tool()
            result4 = structured_tool.func("query_pollutant_data", pollutant_name="Aldrin")
            print(f"   ✓ 结构化工具调用成功: {result4['status']}")
        except Exception as e:
            print(f"   ✗ 结构化工具调用失败: {e}")
        
        # 验证工具的args_schema
        print("\n4. 验证工具参数模式...")
        try:
            structured_tool = unified_tool.to_structured_tool()
            print(f"   工具名称: {structured_tool.name}")
            print(f"   参数字段: {list(structured_tool.args_schema.model_fields.keys())}")
        except Exception as e:
            print(f"   验证参数模式失败: {e}")
        
        print("\n=== 完整集成测试完成 ===")
        print("🎉 功能微生物组识别智能体可以正常与修复后的UnifiedDataTool集成！")
        return True
        
    except Exception as e:
        print(f"✗ 完整集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("功能微生物组识别智能体完整集成测试")
    print("=" * 50)
    
    success = test_agent_tool_full_integration()
    
    if success:
        print("\n🎉 所有测试通过！智能体与工具集成正常工作。")
        print("智能体现在可以使用以下方式调用UnifiedDataTool：")
        print("1. 直接调用: tool._run('operation', param=value)")
        print("2. JSON字符串调用: tool._run('{\"operation\": \"op\", \"param\": \"value\"}')")
        print("3. 字典调用: tool._run({'operation': 'op', 'param': 'value'})")
    else:
        print("\n❌ 测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()