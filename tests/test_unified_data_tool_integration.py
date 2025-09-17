#!/usr/bin/env python3
"""
测试功能微生物组识别智能体 - 统一数据工具集成测试
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from config.config import Config
from langchain_openai import ChatOpenAI
from crewai import Task, Crew
from tools.unified_data_tool import UnifiedDataTool

def test_agent_with_unified_tool():
    """测试智能体使用统一数据工具"""
    print("=== 测试智能体使用统一数据工具 ===")
    
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
    print(f"Agent工具数量: {len(agent.tools)}")
    
    # 显示工具列表
    if agent.tools:
        print("\nAgent工具列表:")
        for i, tool in enumerate(agent.tools):
            print(f"  {i+1}. {tool.name} - {tool.description}")
    
    # 创建测试任务
    task = Task(
        description="""
        请分析处理含有Aldrin的污水的需求，并使用统一数据工具查询相关数据：
        1. 识别Aldrin污染物
        2. 查询相关的基因和微生物数据
        3. 评估数据完整性
        4. 生成结构化报告
        """,
        expected_output="""
        提供一个分析报告，包括：
        1. 识别的污染物名称
        2. 相关的微生物信息（如果有数据）
        3. 数据查询结果摘要
        """,
        agent=agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=Config.VERBOSE
    )
    
    # 执行任务
    print("\n开始执行任务...")
    result = crew.kickoff()
    
    print("\n=== 任务执行结果 ===")
    print(result)
    
    return result

def test_direct_tool_call():
    """测试直接工具调用"""
    print("\n=== 测试直接工具调用 ===")
    
    tool = UnifiedDataTool()
    print(f"工具名称: {tool.name}")
    
    # 测试1: 直接调用
    print("\n1. 测试直接调用:")
    try:
        result1 = tool._run("query_pollutant_data", pollutant_name="Aldrin")
        print(f"   结果: {result1}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试2: JSON字符串调用
    print("\n2. 测试JSON字符串调用:")
    try:
        json_input = "{\"operation\": \"query_pollutant_data\", \"pollutant_name\": \"Aldrin\"}"
        result2 = tool._run(json_input)
        print(f"   结果: {result2}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试3: 模拟智能体调用方式
    print("\n3. 模拟智能体调用方式:")
    try:
        # 模拟智能体可能的调用方式
        result3 = tool._run("{\"operation\": \"query_pollutant_data\", \"pollutant_name\": \"Aldrin\"}")
        print(f"   结果: {result3}")
    except Exception as e:
        print(f"   错误: {e}")

def main():
    """主函数"""
    print("功能微生物组识别智能体 - 统一数据工具集成测试")
    print("=" * 50)
    
    # 直接运行测试，不使用交互式输入
    print("运行智能体使用统一数据工具测试...")
    try:
        test_agent_with_unified_tool()
    except Exception as e:
        print(f"智能体测试执行出错: {e}")
    
    print("\n运行直接工具调用测试...")
    try:
        test_direct_tool_call()
    except Exception as e:
        print(f"直接工具调用测试执行出错: {e}")

if __name__ == "__main__":
    main()