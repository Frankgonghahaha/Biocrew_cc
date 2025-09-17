#!/usr/bin/env python3
"""
修复后的工具调用测试 - 验证Agent中的工具调用参数格式
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

def test_agent_with_correct_tool_calls():
    """测试Agent使用正确的工具调用参数格式"""
    print("=== 测试Agent使用正确的工具调用参数格式 ===")
    
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
    
    print(f"Agent创建成功")
    print(f"工具数量: {len(agent.tools)}")
    
    user_requirement = "识别处理Alpha-hexachlorocyclohexane的工程微生物组"
    
    # 创建任务，提供明确的工具调用指导
    task = Task(
        description=f"""
        请分析以下水质处理需求并识别相关的功能微生物：
        {user_requirement}
        
        请严格按照以下步骤执行，并确保正确提供工具调用参数：
        
        步骤1: 使用强制本地数据查询工具查询必需数据
        工具调用格式: 
        Action: 强制本地数据查询工具
        Action Input: {{"operation": "query_required_data", "query_text": "识别处理Alpha-hexachlorocyclohexane的工程微生物组"}}
        
        步骤2: 如果步骤1返回了匹配的污染物，使用本地数据读取工具查询具体的基因和微生物数据
        工具调用格式:
        Action: 本地数据读取工具
        Action Input: {{"operation": "get_gene_data", "pollutant_name": "Alpha-hexachlorocyclohexane"}}
        
        Action: 本地数据读取工具
        Action Input: {{"operation": "get_organism_data", "pollutant_name": "Alpha-hexachlorocyclohexane"}}
        
        步骤3: 评估数据完整性并生成报告
        """,
        expected_output="""
        提供一个完整的分析报告，包括：
        1. 识别的污染物名称
        2. 相关的基因数据（如果有）
        3. 相关的微生物数据（如果有）
        4. 数据完整性评估
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
    result = crew.kickoff()
    
    print("\n=== 工具使用测试结果 ===")
    print(result)
    
    return result

if __name__ == "__main__":
    test_agent_with_correct_tool_calls()