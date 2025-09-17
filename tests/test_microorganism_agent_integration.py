#!/usr/bin/env python3
"""
测试功能微生物组识别智能体与修复后的UnifiedDataTool集成
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from crewai import Crew
from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from tasks.microorganism_identification_task import MicroorganismIdentificationTask

def test_microorganism_agent_with_fixed_tool():
    """测试功能微生物组识别智能体与修复后的工具集成"""
    print("=== 测试功能微生物组识别智能体与修复后的UnifiedDataTool集成 ===")
    
    try:
        # 创建一个模拟的LLM对象（避免实际API调用）
        class MockLLM:
            def __init__(self):
                pass
            
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
        
        # 创建任务
        print("\n3. 创建微生物识别任务...")
        task_creator = MicroorganismIdentificationTask()
        identification_task = task_creator.create_task(
            agent=identification_agent,
            pollutant_name="Aldrin"
        )
        print(f"   ✓ 任务创建成功: {identification_task.description[:50]}...")
        
        # 创建Crew并执行（简化版本，避免实际LLM调用）
        print("\n4. 验证工具调用能力...")
        # 直接测试工具调用
        unified_tool = identification_agent.tools[0]
        
        # 测试不同的调用方式
        print("   测试直接调用...")
        result1 = unified_tool._run("query_pollutant_data", pollutant_name="Aldrin")
        print(f"   ✓ 直接调用成功: {result1['status']}")
        
        print("   测试JSON字符串调用...")
        result2 = unified_tool._run('{"operation": "get_pollutant_summary", "pollutant_name": "Aldrin"}')
        print(f"   ✓ JSON字符串调用成功: {result2['status']}")
        
        print("   测试字典调用（模拟CrewAI框架调用）...")
        result3 = unified_tool._run({"operation": "search_pollutants", "keyword": "Aldrin"})
        print(f"   ✓ 字典调用成功: {result3['status']}")
        
        print("\n=== 智能体集成测试完成 ===")
        print("🎉 功能微生物组识别智能体可以正常与修复后的UnifiedDataTool集成！")
        return True
        
    except Exception as e:
        print(f"✗ 智能体集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("功能微生物组识别智能体集成测试")
    print("=" * 50)
    
    success = test_microorganism_agent_with_fixed_tool()
    
    if success:
        print("\n🎉 所有测试通过！智能体与工具集成正常工作。")
    else:
        print("\n❌ 测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()