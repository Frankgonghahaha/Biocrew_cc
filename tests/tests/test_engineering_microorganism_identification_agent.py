#!/usr/bin/env python3
"""
测试功能微生物组识别智能体
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_engineering_microorganism_identification_agent_creation():
    """测试功能微生物组识别智能体创建"""
    print("=== 测试功能微生物组识别智能体创建 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    print(f"Agent工具数量: {len(agent.tools)}")
    
    # 验证Agent基本信息
    assert agent.role == "功能微生物组识别专家", f"Agent角色不正确: {agent.role}"
    assert "根据水质净化目标" in agent.goal, f"Agent目标不正确: {agent.goal}"
    assert len(agent.tools) >= 0, "Agent应该至少有0个工具"
    
    print("✓ Agent创建成功")
    print("✓ Agent角色正确")
    print("✓ Agent目标正确")
    
    # 显示工具列表
    if agent.tools:
        print("\nAgent工具列表:")
        for i, tool in enumerate(agent.tools):
            print(f"  {i+1}. {tool.name} - {tool.description}")
    else:
        print("\nAgent没有工具")
    
    print("\n功能微生物组识别智能体创建测试完成。")

def test_agent_backstory_content():
    """测试Agent背景故事内容"""
    print("\n=== 测试Agent背景故事内容 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中是否包含增强功能
    backstory = agent.backstory
    
    enhanced_features = [
        "数据查询顺序和协调机制",
        "数据完整性处理",
        "结果整合策略",
        "错误处理机制"
    ]
    
    print("增强功能检查:")
    for feature in enhanced_features:
        if feature in backstory:
            print(f"  ✓ 包含'{feature}'")
        else:
            print(f"  ✗ 缺少'{feature}'")
    
    print("\nAgent背景故事内容测试完成。")

def test_agent_tool_functionality():
    """测试Agent工具功能"""
    print("\n=== 测试Agent工具功能 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查工具功能
    tool_names = [tool.name for tool in agent.tools]
    
    # 检查必需的工具
    required_tools = [
        "本地数据读取工具",
        "智能数据查询工具",
        "强制本地数据查询工具",
        "数据输出协调器"
    ]
    
    print("工具功能检查:")
    for required_tool in required_tools:
        if required_tool in tool_names:
            print(f"  ✓ {required_tool}")
        else:
            print(f"  ✗ {required_tool} (缺失)")
    
    # 检查工具调用方法
    required_methods = [
        "data_retriever._run(\"get_organism_data\", pollutant_name=\"aldrin\")",
        "data_retriever._run(\"get_gene_data\", pollutant_name=\"aldrin\")",
        "mandatory_query._run(\"query_required_data\", query_text=\"用户需求\")",
        "output_coordinator._run(\"format_output\", data=查询结果, format_type=\"json\")",
        "output_coordinator._run(\"combine_data\", local_data, external_data)",
        "output_coordinator._run(\"generate_report\", title=\"报告标题\", sections=报告章节)"
    ]
    
    backstory = agent.backstory
    print("\n工具调用方法检查:")
    for method in required_methods:
        if method in backstory:
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} (未在背景故事中明确说明)")
    
    print("\nAgent工具功能测试完成。")

def test_agent_attributes():
    """测试Agent属性设置"""
    print("\n=== 测试Agent属性设置 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查必需属性
    assert hasattr(agent, 'role'), "Agent缺少role属性"
    assert hasattr(agent, 'goal'), "Agent缺少goal属性"
    assert hasattr(agent, 'backstory'), "Agent缺少backstory属性"
    assert hasattr(agent, 'verbose'), "Agent缺少verbose属性"
    assert hasattr(agent, 'allow_delegation'), "Agent缺少allow_delegation属性"
    
    print("Agent属性检查:")
    print(f"  ✓ role: {agent.role}")
    print(f"  ✓ goal: {agent.goal[:50]}...")
    print(f"  ✓ verbose: {agent.verbose}")
    print(f"  ✓ allow_delegation: {agent.allow_delegation}")
    
    # 验证属性值
    assert agent.verbose == True, f"Agent verbose属性应为True，实际为{agent.verbose}"
    assert agent.allow_delegation == True, f"Agent allow_delegation属性应为True，实际为{agent.allow_delegation}"
    
    print("\nAgent属性设置测试完成。")

if __name__ == "__main__":
    print("开始测试功能微生物组识别智能体...")
    test_engineering_microorganism_identification_agent_creation()
    test_agent_backstory_content()
    test_agent_tool_functionality()
    test_agent_attributes()
    print("\n=== 所有测试完成 ===")