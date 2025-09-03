#!/usr/bin/env python3
"""
基于CrewAI的水质生物净化技术开发多智能体系统框架
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

# 智能体导入
from agents.task_coordination_agent import TaskCoordinationAgent
from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
from agents.microbial_agent_evaluation_agent import MicrobialAgentEvaluationAgent
from agents.implementation_plan_generation_agent import ImplementationPlanGenerationAgent
from agents.knowledge_management_agent import KnowledgeManagementAgent

# 任务导入
from tasks.microorganism_identification_task import MicroorganismIdentificationTask
from tasks.microbial_agent_design_task import MicrobialAgentDesignTask
from tasks.microbial_agent_evaluation_task import MicrobialAgentEvaluationTask
from tasks.implementation_plan_generation_task import ImplementationPlanGenerationTask

def get_user_input():
    """获取用户自定义的水质处理需求"""
    print("请输入您的水质处理需求:")
    print("例如: 处理含有重金属镉的工业废水")
    user_input = input("水质处理需求: ")
    return user_input

def main():
    print("基于CrewAI的水质生物净化技术开发多智能体系统")
    print("=" * 50)
    
    # 获取用户自定义输入
    user_requirement = get_user_input()
    
    # 打印配置信息用于调试
    print(f"QWEN_API_BASE: {Config.QWEN_API_BASE}")
    print(f"QWEN_API_KEY: {Config.QWEN_API_KEY}")
    print(f"QWEN_MODEL_NAME: {Config.QWEN_MODEL_NAME}")
    print(f"OPENAI_API_BASE: {Config.OPENAI_API_BASE}")
    print(f"OPENAI_API_KEY: {Config.OPENAI_API_KEY}")
    
    # 验证API密钥是否存在
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，使用DashScope专用方式
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,  # 使用原始API密钥
        model="openai/qwen3-30b-a3b-instruct-2507",  # 指定openai提供商
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建智能体
    coordinator_agent = TaskCoordinationAgent(llm).create_agent()
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
    plan_agent = ImplementationPlanGenerationAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    # 创建任务
    identification_task = MicroorganismIdentificationTask(llm).create_task(identification_agent, user_requirement=user_requirement)
    design_task = MicrobialAgentDesignTask(llm).create_task(design_agent, identification_task, user_requirement=user_requirement)
    evaluation_task = MicrobialAgentEvaluationTask(llm).create_task(evaluation_agent, design_task)
    plan_task = ImplementationPlanGenerationTask(llm).create_task(plan_agent, evaluation_task)
    
    # 创建Crew
    water_treatment_crew = Crew(
        agents=[coordinator_agent, identification_agent, design_agent, evaluation_agent, plan_agent, knowledge_agent],
        tasks=[identification_task, design_task, evaluation_task, plan_task],
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    # 执行
    result = water_treatment_crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()