#!/usr/bin/env python3
"""
测试工具修复 - 验证工具调用参数格式
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

def test_tool_call_fix():
    """测试工具调用修复"""
    print("=== 测试工具调用修复 ===")
    
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
    for i, tool in enumerate(agent.tools):
        print(f"  {i+1}. {tool.name}")
    
    user_requirement = "识别处理Alpha-hexachlorocyclohexane的工程微生物组"
    
    # 创建简化任务来测试工具调用
    task = Task(
        description=f"""
        请分析以下水质处理需求并识别相关的功能微生物：
        {user_requirement}
        
        请严格按照以下步骤执行：
        1. 首先使用强制本地数据查询工具查询必需数据
        2. 如果需要，使用本地数据读取工具查询具体的基因和微生物数据
        3. 评估数据完整性
        4. 生成结构化报告
        
        工具调用示例：
        - 强制本地数据查询：mandatory_query._run(operation="query_required_data", query_text="用户需求")
        - 本地数据读取（基因数据）：data_retriever._run(operation="get_gene_data", pollutant_name="Alpha-hexachlorocyclohexane")
        - 本地数据读取（微生物数据）：data_retriever._run(operation="get_organism_data", pollutant_name="Alpha-hexachlorocyclohexane")
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
    result = crew.kickoff()
    
    print("\n=== 工具使用测试结果 ===")
    print(result)
    
    return result

if __name__ == "__main__":
    test_tool_call_fix()