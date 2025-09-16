#!/usr/bin/env python3
"""
测试实施方案生成智能体
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.implementation_plan_generation_agent import ImplementationPlanGenerationAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_implementation_plan_generation_agent_creation():
    """测试实施方案生成智能体创建"""
    print("=== 测试实施方案生成智能体创建 ===")
    
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
    agent_instance = ImplementationPlanGenerationAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    
    # 验证Agent基本信息
    assert agent.role == "实施方案生成专家", f"Agent角色不正确: {agent.role}"
    assert "生成完整的微生物净化技术落地方案" in agent.goal, f"Agent目标不正确: {agent.goal}"
    
    print("✓ Agent创建成功")
    print("✓ Agent角色正确")
    print("✓ Agent目标正确")
    
    print("\n实施方案生成智能体创建测试完成。")

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
    agent_instance = ImplementationPlanGenerationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中是否包含关键内容
    backstory = agent.backstory
    
    required_content = [
        "工作依据",
        "方案内容要求",
        "生成原则"
    ]
    
    print("检查背景故事内容:")
    for content in required_content:
        if content in backstory:
            print(f"  ✓ 包含'{content}'")
        else:
            print(f"  ✗ 缺少'{content}'")
    
    print("\nAgent背景故事内容测试完成。")

def test_agent_plan_content_requirements():
    """测试Agent方案内容要求"""
    print("\n=== 测试Agent方案内容要求 ===")
    
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
    agent_instance = ImplementationPlanGenerationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查方案内容要求
    backstory = agent.backstory
    
    plan_requirements = [
        "菌剂获取",
        "制剂储运",
        "投加策略",
        "监测应急"
    ]
    
    print("检查方案内容要求:")
    for requirement in plan_requirements:
        if requirement in backstory:
            print(f"  ✓ 包含'{requirement}'")
        else:
            print(f"  ✗ 缺少'{requirement}'")
    
    # 检查具体细节
    specific_details = [
        "合法渠道（CGMCC/ATCC采购、实验室分离、合作授权）",
        "液体浓缩剂（10⁹ CFU/mL，2-8℃存1-3月）",
        "冻干粉（10¹⁰ CFU/g，常温存6-12月）",
        "启动期分阶段投加方案",
        "周期性水质和微生物群落监测计划"
    ]
    
    print("\n检查具体细节:")
    for detail in specific_details:
        if detail in backstory:
            print(f"  ✓ {detail}")
        else:
            print(f"  ✗ {detail}")
    
    print("\nAgent方案内容要求测试完成。")

def test_agent_generation_principles():
    """测试Agent生成原则"""
    print("\n=== 测试Agent生成原则 ===")
    
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
    agent_instance = ImplementationPlanGenerationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查生成原则
    backstory = agent.backstory
    
    generation_principles = [
        "方案必须具体可行，具有可操作性",
        "充分考虑实际应用场景的限制条件",
        "提供详细的操作指导和注意事项",
        "包含风险控制和应急预案"
    ]
    
    print("检查生成原则:")
    for principle in generation_principles:
        if principle in backstory:
            print(f"  ✓ {principle}")
        else:
            print(f"  ✗ {principle}")
    
    print("\nAgent生成原则测试完成。")

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
    agent_instance = ImplementationPlanGenerationAgent(llm)
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
    print("开始测试实施方案生成智能体...")
    test_implementation_plan_generation_agent_creation()
    test_agent_backstory_content()
    test_agent_plan_content_requirements()
    test_agent_generation_principles()
    test_agent_attributes()
    print("\n=== 所有测试完成 ===")