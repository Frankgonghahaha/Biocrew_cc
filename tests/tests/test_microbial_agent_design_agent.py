#!/usr/bin/env python3
"""
测试微生物菌剂设计智能体
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_microbial_agent_design_agent_creation():
    """测试微生物菌剂设计智能体创建"""
    print("=== 测试微生物菌剂设计智能体创建 ===")
    
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
    agent_instance = MicrobialAgentDesignAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    
    # 验证Agent基本信息
    assert agent.role == "微生物菌剂设计专家", f"Agent角色不正确: {agent.role}"
    assert "设计高性能微生物菌剂" in agent.goal, f"Agent目标不正确: {agent.goal}"
    
    print("✓ Agent创建成功")
    print("✓ Agent角色正确")
    print("✓ Agent目标正确")
    
    print("\n微生物菌剂设计智能体创建测试完成。")

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
    agent_instance = MicrobialAgentDesignAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中是否包含关键内容
    backstory = agent.backstory
    
    required_content = [
        "设计流程",
        "核心方法",
        "设计原则",
        "数据使用"
    ]
    
    print("检查背景故事内容:")
    for content in required_content:
        if content in backstory:
            print(f"  ✓ 包含'{content}'")
        else:
            print(f"  ✗ 缺少'{content}'")
    
    # 检查特定的关键方法和原则
    key_methods = [
        "ctFBA（协同权衡代谢通量平衡法）",
        "权衡系数：0-1范围",
        "代谢通量（F_take）"
    ]
    
    print("\n检查关键方法:")
    for method in key_methods:
        if method in backstory:
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method}")
    
    print("\nAgent背景故事内容测试完成。")

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
    agent_instance = MicrobialAgentDesignAgent(llm)
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

def test_agent_design_methodology():
    """测试Agent设计方法论"""
    print("\n=== 测试Agent设计方法论 ===")
    
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
    agent_instance = MicrobialAgentDesignAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查设计方法论相关内容
    backstory = agent.backstory
    
    design_principles = [
        "优先保证菌剂对目标污染物的降解能力",
        "确保菌剂群落的稳定性和鲁棒性",
        "考虑微生物间的协同作用和代谢互补性",
        "优化菌剂配比以实现最佳净化效果"
    ]
    
    print("检查设计原则:")
    for principle in design_principles:
        if principle in backstory:
            print(f"  ✓ {principle}")
        else:
            print(f"  ✗ {principle}")
    
    # 检查数据使用原则
    data_usage_principles = [
        "基于工程微生物识别智能体提供的微生物组数据",
        "参考本地基因数据和微生物数据",
        "必要时可调用KEGG工具查询代谢通路信息"
    ]
    
    print("\n检查数据使用原则:")
    for principle in data_usage_principles:
        if principle in backstory:
            print(f"  ✓ {principle}")
        else:
            print(f"  ✗ {principle}")
    
    print("\nAgent设计方法论测试完成。")

if __name__ == "__main__":
    print("开始测试微生物菌剂设计智能体...")
    test_microbial_agent_design_agent_creation()
    test_agent_backstory_content()
    test_agent_attributes()
    test_agent_design_methodology()
    print("\n=== 所有测试完成 ===")