#!/usr/bin/env python3
"""
系统测试脚本
用于测试整个多智能体系统的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 在导入其他模块前先设置环境变量
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from config.config import Config

# 智能体导入
from agents.task_coordination_agent import TaskCoordinationAgent
from agents.microorganism_matching_agent import MicroorganismMatchingAgent
from agents.bioagent_design_agent import BioagentDesignAgent
from agents.treatment_plan_agent import TreatmentPlanAgent
from agents.knowledge_management_agent import KnowledgeManagementAgent

# 任务导入
from tasks.design_task import DesignTask
from tasks.evaluation_task import EvaluationTask

def check_config():
    """检查配置是否完整"""
    print("检查环境配置...")
    if 'your-qwen-api-endpoint' in Config.QWEN_API_BASE:
        print("警告: 请在.env文件中配置QWEN_API_BASE")
        return False
    if 'your-api-key' in Config.QWEN_API_KEY or Config.QWEN_API_KEY == 'YOUR_API_KEY':
        print("警告: 请在.env文件中配置QWEN_API_KEY")
        return False
    print("配置检查完成")
    return True

def create_test_crew():
    """创建测试用的Crew"""
    # 初始化LLM模型
    llm = ChatOpenAI(
        base_url=Config.QWEN_API_BASE,
        api_key=Config.QWEN_API_KEY,
        model=f"openai/{Config.QWEN_MODEL_NAME}"  # 添加提供者前缀
    )
    
    # 创建智能体
    coordinator_agent = TaskCoordinationAgent(llm).create_agent()
    microorganism_agent = MicroorganismMatchingAgent(llm).create_agent()
    bioagent_agent = BioagentDesignAgent(llm).create_agent()
    plan_agent = TreatmentPlanAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    # 创建测试任务
    # 1. 创建菌剂设计任务，提供测试用的背景信息
    design_description = """
    请为以下污水处理场景设计功能微生物菌剂：
    
    污水处理厂信息：
    - 处理规模：日处理量10000吨
    - 目标污染物：印染废水中的偶氮染料
    - 污染物浓度：偶氮染料约200mg/L
    - 工艺参数：好氧-缺氧工艺，水温25-35°C，pH 7.0-8.5
    
    请根据以上信息设计合适的微生物菌剂配方。
    """
    
    design_task = Task(
        description=design_description,
        expected_output="详细的微生物菌剂设计方案，包括菌剂组成、设计原理和预期效果",
        agent=bioagent_agent,
        verbose=True
    )
    
    # 2. 创建评价任务
    evaluation_task = Task(
        description="""
        请根据以下五个维度评估提供的功能菌剂方案：
        1. 物种多样性
        2. 群落稳定性（核心标准）
        3. 结构稳定性（核心标准）
        4. 代谢相互作用
        5. 污染物降解性能
        
        重点关注群落稳定性和结构稳定性这两个核心标准。
        如果这两项核心标准不达标，请明确指出问题并建议改进方向。
        """,
        expected_output="菌剂评价报告，包含各维度评分、核心标准评估结果和改进建议",
        agent=bioagent_agent,
        context=[design_task],
        verbose=True
    )
    
    # 创建Crew
    test_crew = Crew(
        agents=[coordinator_agent, microorganism_agent, bioagent_agent, plan_agent, knowledge_agent],
        tasks=[design_task, evaluation_task],
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    return test_crew

def run_test():
    """运行测试"""
    print("开始测试BioCrew系统...")
    print("=" * 50)
    
    # 检查配置
    if not check_config():
        print("\n请按以下步骤配置环境:")
        print("1. 编辑.env文件，设置正确的API地址和密钥")
        print("2. 确保可以访问配置的Qwen模型API")
        return
    
    try:
        # 创建测试Crew
        test_crew = create_test_crew()
        
        # 运行测试
        print("正在执行测试任务...")
        result = test_crew.kickoff()
        
        print("\n测试完成！结果如下：")
        print("=" * 50)
        print(result)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        print("\n常见问题及解决方案:")
        print("1. 如果是API配置错误，请检查.env文件中的配置")
        print("2. 如果是网络连接问题，请确保可以访问配置的API地址")
        print("3. 如果是认证问题，请检查API密钥是否正确")
        import traceback
        traceback.print_exc()

def print_system_info():
    """打印系统信息"""
    print("BioCrew系统信息:")
    print("-" * 30)
    print(f"模型地址: {Config.QWEN_API_BASE}")
    print(f"模型名称: {Config.QWEN_MODEL_NAME}")
    print(f"详细输出: {Config.VERBOSE}")
    print()

if __name__ == "__main__":
    print_system_info()
    run_test()