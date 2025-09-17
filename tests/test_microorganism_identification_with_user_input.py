#!/usr/bin/env python3
"""
测试功能微生物组识别智能体 - 支持用户输入处理
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

def get_user_input():
    """获取用户输入的水质处理需求"""
    print("请输入您的水质处理需求:")
    print("例如: 处理含有重金属镉的工业废水")
    print("例如: 需要降解水中的Aldrin污染物")
    print("例如: 处理含有机磷农药的农业废水")
    
    user_input = input("水质处理需求: ")
    return user_input

def test_agent_with_user_input():
    """测试Agent处理用户输入的能力"""
    print("=== 测试Agent处理用户输入 ===")
    
    # 获取用户输入
    user_requirement = get_user_input()
    
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
    
    print(f"\nAgent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    print(f"用户需求: {user_requirement}")
    
    # 创建任务
    task = Task(
        description=f"""
        根据以下水质净化目标识别工程微生物组：
        {user_requirement}
        
        请严格按照以下步骤执行：
        1. 分析水质净化目标（水质治理指标+目标污染物）
        2. 首先从本地数据目录(data/Genes和data/Organism)查询相关基因和微生物数据
        3. 从公开数据库获取补充领域知识
        4. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
        
        重要数据处理指导：
        1. 必须优先使用本地数据查询工具(LocalDataRetriever和SmartDataQueryTool)获取具体数据
        2. 当某些类型的数据缺失时（如只有微生物数据而无基因数据），应基于现有数据继续分析并明确指出数据缺失情况
        3. 对于Aldrin等特定污染物，可能只有微生物数据而没有基因数据，这是正常情况，应基于现有微生物数据继续分析
        4. 利用外部数据库工具(EnviPath、KEGG等)获取补充信息以完善分析
        5. 在最终报告中明确体现查询到的微生物名称、基因数据等具体内容，不能仅依赖预训练知识
        """,
        expected_output="""
        提供完整的工程微生物组识别报告，包括：
        1. 识别的功能微生物列表（优先基于本地数据查询到的具体微生物名称，若数据缺失则说明情况）
        2. 代谢互补微生物列表（优先基于本地数据查询到的具体微生物名称，若数据缺失则说明情况）
        3. 竞争指数和互补指数计算结果（基于可用的本地数据，数据缺失时应说明）
        4. 微生物组选择的科学依据（结合本地数据和外部数据库信息）
        5. 本地数据查询的具体结果（包括查询到的基因数据、微生物数据等详细信息，对于部分数据缺失的情况要明确说明）
        6. 数据完整性和可信度评估（明确指出哪些数据可用，哪些数据缺失，对于Aldrin等只有微生物数据的污染物要特别说明）
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

def test_agent_tool_usage_with_user_input():
    """测试Agent工具使用与用户输入的结合"""
    print("\n=== 测试Agent工具使用与用户输入的结合 ===")
    
    # 获取用户输入
    user_requirement = get_user_input()
    
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
    
    print(f"用户需求: {user_requirement}")
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
        2. 查询相关的基因和微生物数据（注意某些污染物可能只有微生物数据而没有基因数据，如Aldrin）
        3. 评估数据完整性
        4. 生成结构化报告
        5. 对于数据缺失的情况要明确说明，不能因为部分数据缺失而停止分析
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

def main():
    """主函数"""
    print("功能微生物组识别智能体 - 用户输入测试")
    print("=" * 50)
    
    while True:
        print("\n请选择测试模式:")
        print("1. 完整任务执行测试")
        print("2. 工具使用测试")
        print("3. 退出")
        
        choice = input("请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            try:
                test_agent_with_user_input()
            except Exception as e:
                print(f"测试执行出错: {e}")
        elif choice == "2":
            try:
                test_agent_tool_usage_with_user_input()
            except Exception as e:
                print(f"测试执行出错: {e}")
        elif choice == "3":
            print("退出测试程序")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()