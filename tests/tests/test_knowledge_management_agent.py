#!/usr/bin/env python3
"""
测试知识管理智能体
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.knowledge_management_agent import KnowledgeManagementAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_knowledge_management_agent_creation():
    """测试知识管理智能体创建"""
    print("=== 测试知识管理智能体创建 ===")
    
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
    agent_instance = KnowledgeManagementAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    
    # 验证Agent基本信息
    assert agent.role == "知识管理专家", f"Agent角色不正确: {agent.role}"
    assert "确定与生物净化任务相关的领域知识" in agent.goal, f"Agent目标不正确: {agent.goal}"
    
    print("✓ Agent创建成功")
    print("✓ Agent角色正确")
    print("✓ Agent目标正确")
    
    print("\n知识管理智能体创建测试完成。")

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
    agent_instance = KnowledgeManagementAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中是否包含关键内容
    backstory = agent.backstory
    
    required_content = [
        "核心职责",
        "知识来源",
        "工作原则"
    ]
    
    print("检查背景故事内容:")
    for content in required_content:
        if content in backstory:
            print(f"  ✓ 包含'{content}'")
        else:
            print(f"  ✗ 缺少'{content}'")
    
    print("\nAgent背景故事内容测试完成。")

def test_agent_core_responsibilities():
    """测试Agent核心职责"""
    print("\n=== 测试Agent核心职责 ===")
    
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
    agent_instance = KnowledgeManagementAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查核心职责
    backstory = agent.backstory
    
    core_responsibilities = [
        "领域知识提供",
        "数据库补充",
        "工具协调"
    ]
    
    print("检查核心职责:")
    for responsibility in core_responsibilities:
        if responsibility in backstory:
            print(f"  ✓ {responsibility}")
        else:
            print(f"  ✗ {responsibility}")
    
    # 检查具体职责内容
    specific_duties = [
        "为其他智能体提供水质治理、污染物特性、微生物代谢途径等相关领域的背景知识",
        "识别当前知识库中的不足",
        "协助其他智能体正确使用本地数据查询工具"
    ]
    
    print("\n检查具体职责内容:")
    for duty in specific_duties:
        if duty in backstory:
            print(f"  ✓ {duty}")
        else:
            print(f"  ✗ {duty}")
    
    print("\nAgent核心职责测试完成。")

def test_agent_knowledge_sources():
    """测试Agent知识来源"""
    print("\n=== 测试Agent知识来源 ===")
    
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
    agent_instance = KnowledgeManagementAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查知识来源
    backstory = agent.backstory
    
    knowledge_sources = [
        "本地数据目录(data/Genes和data/Organism)中的基因和微生物数据",
        "EnviPath数据库中的环境化合物代谢路径信息",
        "KEGG数据库中的生物代谢信息",
        "预训练模型中的领域知识"
    ]
    
    print("检查知识来源:")
    for source in knowledge_sources:
        if source in backstory:
            print(f"  ✓ {source}")
        else:
            print(f"  ✗ {source}")
    
    print("\nAgent知识来源测试完成。")

def test_agent_working_principles():
    """测试Agent工作原则"""
    print("\n=== 测试Agent工作原则 ===")
    
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
    agent_instance = KnowledgeManagementAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查工作原则
    backstory = agent.backstory
    
    working_principles = [
        "专注于生物处理方法，不涉及化学合成或其他非生物处理方法",
        "确保提供的知识准确、全面、及时",
        "根据具体任务需求提供针对性的知识支持",
        "优先使用本地数据，外部数据库作为补充"
    ]
    
    print("检查工作原则:")
    for principle in working_principles:
        if principle in backstory:
            print(f"  ✓ {principle}")
        else:
            print(f"  ✗ {principle}")
    
    print("\nAgent工作原则测试完成。")

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
    agent_instance = KnowledgeManagementAgent(llm)
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
    print("开始测试知识管理智能体...")
    test_knowledge_management_agent_creation()
    test_agent_backstory_content()
    test_agent_core_responsibilities()
    test_agent_knowledge_sources()
    test_agent_working_principles()
    test_agent_attributes()
    print("\n=== 所有测试完成 ===")