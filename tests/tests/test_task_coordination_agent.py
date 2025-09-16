#!/usr/bin/env python3
"""
测试任务协调智能体
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.task_coordination_agent import TaskCoordinationAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_task_coordination_agent_creation():
    """测试任务协调智能体创建"""
    print("=== 测试任务协调智能体创建 ===")
    
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
    agent_instance = TaskCoordinationAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    
    # 验证Agent基本信息
    assert agent.role == "任务协调专家", f"Agent角色不正确: {agent.role}"
    assert "智能地决定下一步应该执行哪个智能体" in agent.goal, f"Agent目标不正确: {agent.goal}"
    
    print("✓ Agent创建成功")
    print("✓ Agent角色正确")
    print("✓ Agent目标正确")
    
    print("\n任务协调智能体创建测试完成。")

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
    agent_instance = TaskCoordinationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中是否包含关键内容
    backstory = agent.backstory
    
    required_content = [
        "工作流程包含以下智能体",
        "你需要根据以下规则进行任务调度",
        "重要决策指导原则"
    ]
    
    print("检查背景故事内容:")
    for content in required_content:
        if content in backstory:
            print(f"  ✓ 包含'{content}'")
        else:
            print(f"  ✗ 缺少'{content}'")
    
    print("\nAgent背景故事内容测试完成。")

def test_agent_workflow_agents():
    """测试Agent工作流程中的智能体"""
    print("\n=== 测试Agent工作流程中的智能体 ===")
    
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
    agent_instance = TaskCoordinationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查工作流程中的智能体
    backstory = agent.backstory
    
    workflow_agents = [
        "工程微生物识别智能体",
        "微生物菌剂设计智能体",
        "微生物菌剂评估智能体",
        "实施方案生成智能体",
        "知识管理智能体"
    ]
    
    print("检查工作流程中的智能体:")
    for agent_name in workflow_agents:
        if agent_name in backstory:
            print(f"  ✓ {agent_name}")
        else:
            print(f"  ✗ {agent_name}")
    
    print("\nAgent工作流程中的智能体测试完成。")

def test_agent_scheduling_rules():
    """测试Agent调度规则"""
    print("\n=== 测试Agent调度规则 ===")
    
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
    agent_instance = TaskCoordinationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查调度规则
    backstory = agent.backstory
    
    scheduling_rules = [
        "如果是初始状态，应该启动微生物识别任务",
        "如果微生物识别已完成，应该启动菌剂设计任务",
        "如果菌剂设计已完成，应该启动评估任务",
        "如果评估结果不达标，应该重新启动微生物识别任务",
        "如果评估结果达标，应该启动方案生成任务"
    ]
    
    print("检查调度规则:")
    for rule in scheduling_rules:
        if rule in backstory:
            print(f"  ✓ {rule}")
        else:
            print(f"  ✗ {rule}")
    
    print("\nAgent调度规则测试完成。")

def test_agent_decision_guidelines():
    """测试Agent决策指导原则"""
    print("\n=== 测试Agent决策指导原则 ===")
    
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
    agent_instance = TaskCoordinationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查决策指导原则
    backstory = agent.backstory
    
    decision_guidelines = [
        "仔细分析每个任务的输出结果，特别是评估任务的结果",
        "如果评估报告中包含\"不达标\"、\"需要改进\"、\"未满足标准\"等负面评价，你应该决定重新执行微生物识别任务",
        "如果评估报告中包含\"达标\"、\"符合要求\"、\"通过\"等正面评价，你应该决定执行方案生成任务",
        "避免重复执行相同的任务委托，如果需要重新执行任务，应该提供不同的上下文信息",
        "当多次重新执行同一类型任务仍不达标时，应该提供更具体的改进建议并终止循环",
        "每次决策都应该基于最新的任务输出和上下文信息"
    ]
    
    print("检查决策指导原则:")
    for guideline in decision_guidelines:
        if guideline in backstory:
            print(f"  ✓ {guideline[:50]}...")
        else:
            print(f"  ✗ {guideline[:50]}...")
    
    print("\nAgent决策指导原则测试完成。")

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
    agent_instance = TaskCoordinationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查必需属性
    assert hasattr(agent, 'role'), "Agent缺少role属性"
    assert hasattr(agent, 'goal'), "Agent缺少goal属性"
    assert hasattr(agent, 'backstory'), "Agent缺少backstory属性"
    assert hasattr(agent, 'verbose'), "Agent缺少verbose属性"
    assert hasattr(agent, 'allow_delegation'), "Agent缺少allow_delegation属性"
    
    print("Agent属性检查:")
    print(f"  ✓ role: {agent.role}")
    print(f"  ✓ goal: {agent.goal}")
    print(f"  ✓ verbose: {agent.verbose}")
    print(f"  ✓ allow_delegation: {agent.allow_delegation}")
    
    # 验证属性值
    assert agent.verbose == True, f"Agent verbose属性应为True，实际为{agent.verbose}"
    assert agent.allow_delegation == True, f"Agent allow_delegation属性应为True，实际为{agent.allow_delegation}"
    
    print("\nAgent属性设置测试完成。")

if __name__ == "__main__":
    print("开始测试任务协调智能体...")
    test_task_coordination_agent_creation()
    test_agent_backstory_content()
    test_agent_workflow_agents()
    test_agent_scheduling_rules()
    test_agent_decision_guidelines()
    test_agent_attributes()
    print("\n=== 所有测试完成 ===")