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

from agents.task_coordination_agent import TaskCoordinationAgent
from agents.microorganism_matching_agent import MicroorganismMatchingAgent
from agents.bioagent_design_agent import BioagentDesignAgent
from agents.treatment_plan_agent import TreatmentPlanAgent

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
    
    # 定义任务（示例）
    # 后续需要根据用户提供的具体工作流程链路进行配置
    
    # 创建Crew
    water_treatment_crew = Crew(
        agents=[coordinator_agent, microorganism_agent, bioagent_agent, plan_agent],
        tasks=[],  # 后续填充具体任务
        process=Process.sequential,  # 或使用Process.hierarchical
        verbose=Config.VERBOSE
    )
    
    # 执行（示例）
    # result = water_treatment_crew.kickoff()
    # print(result)

if __name__ == "__main__":
    main()