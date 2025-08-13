#!/usr/bin/env python3
"""
基于CrewAI的水质生物净化技术开发多智能体系统框架
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def main():
    print("基于CrewAI的水质生物净化技术开发多智能体系统")
    print("=" * 50)
    
    # 初始化LLM模型
    # 后续需要根据用户提供的URL和Token配置
    llm = ChatOpenAI(
        openai_api_base=Config.QWEN_API_BASE,  # 用户提供的URL
        openai_api_key=Config.QWEN_API_KEY,        # 用户提供的Token
        model_name=Config.QWEN_MODEL_NAME                    # QWEN3系列模型
    )
    
    # 创建智能体
    coordinator_agent = TaskCoordinationAgent(llm).create_agent()
    microorganism_agent = MicroorganismMatchingAgent(llm).create_agent()
    bioagent_agent = BioagentDesignAgent(llm).create_agent()
    plan_agent = TreatmentPlanAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    # 创建任务
    # 首先创建菌剂设计任务
    design_task = DesignTask(llm).create_task(bioagent_agent)
    
    # 创建评价任务，依赖于设计任务
    evaluation_task = EvaluationTask(llm).create_task(bioagent_agent, design_task)
    
    # 定义基于评价结果的条件处理逻辑说明
    """
    实现评价流程的条件判断逻辑：
    1. 系统会自动执行设计任务和评价任务
    2. 评价专家会基于五个维度评估菌剂性能
    3. 如果群落稳定性和结构稳定性不达标，任务会标记为需要重新设计
    4. 协调专家会根据评价结果决定是否需要重新设计
    
    在实际应用中，可以通过以下方式实现循环优化：
    - 使用CrewAI的hierarchical流程，让协调专家动态决定下一步
    - 或者通过自定义工具实现评价结果的解析和条件判断
    """
    
    # 创建Crew
    water_treatment_crew = Crew(
        agents=[coordinator_agent, microorganism_agent, bioagent_agent, plan_agent, knowledge_agent],
        tasks=[design_task, evaluation_task],  # 任务按顺序执行
        process=Process.sequential,  # 使用顺序流程执行任务
        verbose=Config.VERBOSE
    )
    
    # 执行
    # result = water_treatment_crew.kickoff()
    # print(result)

if __name__ == "__main__":
    main()