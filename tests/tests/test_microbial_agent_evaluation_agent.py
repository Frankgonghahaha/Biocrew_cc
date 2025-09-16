#!/usr/bin/env python3
"""
测试菌剂评估智能体
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.microbial_agent_evaluation_agent import MicrobialAgentEvaluationAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_microbial_agent_evaluation_agent_creation():
    """测试菌剂评估智能体创建"""
    print("=== 测试菌剂评估智能体创建 ===")
    
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
    agent_instance = MicrobialAgentEvaluationAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    print(f"Agent工具数量: {len(agent.tools)}")
    
    # 验证Agent基本信息
    assert agent.role == "菌剂评估专家", f"Agent角色不正确: {agent.role}"
    assert "评估微生物菌剂的生物净化效果和生态特性" in agent.goal, f"Agent目标不正确: {agent.goal}"
    
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
    
    print("\n菌剂评估智能体创建测试完成。")

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
    agent_instance = MicrobialAgentEvaluationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中是否包含关键内容
    backstory = agent.backstory
    
    required_content = [
        "核心评估维度",
        "评估流程",
        "决策规则",
        "报告要求"
    ]
    
    print("检查背景故事内容:")
    for content in required_content:
        if content in backstory:
            print(f"  ✓ 包含'{content}'")
        else:
            print(f"  ✗ 缺少'{content}'")
    
    print("\nAgent背景故事内容测试完成。")

def test_agent_evaluation_dimensions():
    """测试Agent评估维度"""
    print("\n=== 测试Agent评估维度 ===")
    
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
    agent_instance = MicrobialAgentEvaluationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查评估维度相关内容
    backstory = agent.backstory
    
    evaluation_dimensions = [
        "生物净化效果",
        "群落生态特性",
        "降解速率：Degradation_rate=F_take×X",
        "群落稳定性：Pianka生态位重叠指数",
        "结构稳定性：物种敲除指数"
    ]
    
    print("检查评估维度:")
    for dimension in evaluation_dimensions:
        if dimension in backstory:
            print(f"  ✓ {dimension}")
        else:
            print(f"  ✗ {dimension}")
    
    print("\nAgent评估维度测试完成。")

def test_agent_decision_rules():
    """测试Agent决策规则"""
    print("\n=== 测试Agent决策规则 ===")
    
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
    agent_instance = MicrobialAgentEvaluationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查决策规则相关内容
    backstory = agent.backstory
    
    decision_rules = [
        "群落稳定性和结构稳定性是必须达标的两个核心标准",
        "如果任一核心标准不达标，整个菌剂方案需要重新设计",
        "使用EvaluationTool工具来判断核心标准是否达标",
        "评估结果将直接影响是否需要重新进行微生物识别和设计"
    ]
    
    print("检查决策规则:")
    for rule in decision_rules:
        if rule in backstory:
            print(f"  ✓ {rule}")
        else:
            print(f"  ✗ {rule}")
    
    print("\nAgent决策规则测试完成。")

def test_agent_tool_integration():
    """测试Agent工具集成"""
    print("\n=== 测试Agent工具集成 ===")
    
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
    agent_instance = MicrobialAgentEvaluationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查工具集成
    if agent.tools:
        tool_names = [tool.name for tool in agent.tools]
        print(f"Agent工具: {tool_names}")
        
        # 检查是否包含评估工具
        if "EvaluationTool" in str(agent.tools):
            print("  ✓ 包含EvaluationTool")
        else:
            print("  - 未明确包含EvaluationTool")
    else:
        print("  Agent没有工具")
    
    print("\nAgent工具集成测试完成。")

if __name__ == "__main__":
    print("开始测试菌剂评估智能体...")
    test_microbial_agent_evaluation_agent_creation()
    test_agent_backstory_content()
    test_agent_evaluation_dimensions()
    test_agent_decision_rules()
    test_agent_tool_integration()
    print("\n=== 所有测试完成 ===")