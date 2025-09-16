#!/usr/bin/env python3
"""
调试模式2功能的测试脚本
专门测试工具使用功能，针对Aldrin污染物识别需求
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from config.config import Config
from langchain_openai import ChatOpenAI
from crewai import Task, Crew

def test_mode2_functionality():
    """测试模式2功能，针对Aldrin污染物识别需求"""
    print("=== 测试模式2功能 - Aldrin污染物识别 ===")
    
    # 模拟用户输入
    user_requirement = "帮我识别出一下能降解Aldrin污染物的功能微生物"
    print(f"用户需求: {user_requirement}")
    
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
    
    print(f"Agent工具数量: {len(agent.tools)}")
    
    # 显示工具列表
    if agent.tools:
        print("\nAgent工具列表:")
        for i, tool in enumerate(agent.tools):
            print(f"  {i+1}. {tool.name}")
    
    # 创建简化任务来测试工具调用
    task = Task(
        description=f"""
        请分析以下水质处理需求并识别相关的功能微生物：
        {user_requirement}
        
        请使用适当的工具来查询相关数据，特别是：
        1. 使用智能数据查询工具识别需求中的污染物名称
        2. 查询相关的基因和微生物数据
        3. 评估数据完整性
        4. 生成结构化报告
        """,
        expected_output="""
        提供一个简要的分析报告，包括：
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
    print("\n开始执行工具使用测试...")
    try:
        result = crew.kickoff()
        print("\n=== 工具使用测试结果 ===")
        print(result)
        return result
    except Exception as e:
        print(f"测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_mode2_functionality()