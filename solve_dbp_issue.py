#!/usr/bin/env python3
"""
邻苯二甲酸二丁酯(DBP)污染问题处理脚本
使用hierarchical模式处理DBP含量超标问题
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

def create_dbp_crew():
    """创建针对DBP污染处理的Crew"""
    # 初始化LLM模型
    llm = ChatOpenAI(
        base_url=Config.QWEN_API_BASE,
        api_key=Config.QWEN_API_KEY,
        model=f"openai/{Config.QWEN_MODEL_NAME}"
    )
    
    # 创建智能体
    coordinator_agent = TaskCoordinationAgent(llm).create_agent()
    microorganism_agent = MicroorganismMatchingAgent(llm).create_agent()
    bioagent_agent = BioagentDesignAgent(llm).create_agent()
    plan_agent = TreatmentPlanAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    # 创建DBP处理任务，使用原始问题描述
    dbp_treatment_task = Task(
        description="你好，我现在想解决一下邻苯二甲酸二丁酯含量超标的问题，我现在邻苯二甲酸二丁酯的含量是1 mg/L。",
        expected_output="完整的DBP污染处理方案，包括菌剂设计、预期效果和实施建议",
        agent=coordinator_agent,
        verbose=True
    )
    
    # 创建Crew，使用hierarchical流程让模型自行挑选智能体进行调用
    dbp_crew = Crew(
        agents=[coordinator_agent, microorganism_agent, bioagent_agent, plan_agent, knowledge_agent],
        tasks=[dbp_treatment_task],
        process=Process.hierarchical,
        manager_llm=llm,
        verbose=Config.VERBOSE
    )
    
    return dbp_crew

def solve_dbp_issue():
    """解决DBP污染问题"""
    print("开始处理邻苯二甲酸二丁酯(DBP)污染问题...")
    print("=" * 60)
    print("污染物: 邻苯二甲酸二丁酯(DBP)")
    print("当前浓度: 1mg/L")
    print("处理目标: 降至0.005mg/L以下(符合《地表水环境质量标准》GB3838-2002 III类标准)")
    print("=" * 60)
    
    try:
        # 创建DBP处理Crew
        dbp_crew = create_dbp_crew()
        
        # 运行处理任务
        print("正在处理DBP污染问题...")
        result = dbp_crew.kickoff()
        
        print("\nDBP污染问题处理完成！结果如下：")
        print("=" * 60)
        print(result)
        
    except Exception as e:
        print(f"DBP污染问题处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve_dbp_issue()