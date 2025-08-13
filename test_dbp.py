#!/usr/bin/env python3
"""
邻苯二甲酸二丁酯(DBP)污染处理测试脚本
用于测试系统对特定污染物的处理能力
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
    
    # 创建DBP处理任务
    dbp_treatment_task = Task(
        description="邻苯二甲酸二丁酯含量超标的问题，邻苯二甲酸二丁酯的含量是1 mg/L",
        expected_output="详细的微生物菌剂设计方案，包括菌剂组成、设计原理和预期效果，以及菌剂评价报告",
        agent=coordinator_agent,
        verbose=True
    )
    
    # 创建Crew，使用hierarchical流程让模型自行挑选智能体进行调用
    dbp_crew = Crew(
        agents=[coordinator_agent, microorganism_agent, bioagent_agent, plan_agent, knowledge_agent],
        tasks=[dbp_treatment_task],
        process=Process.hierarchical,
        verbose=Config.VERBOSE
    )
    
    return dbp_crew

def run_dbp_test():
    """运行DBP处理测试"""
    print("开始测试邻苯二甲酸二丁酯(DBP)污染处理...")
    print("=" * 60)
    print("污染物: 邻苯二甲酸二丁酯(DBP)")
    print("当前浓度: 1mg/L")
    print("处理目标: 降至0.005mg/L以下(符合《地表水环境质量标准》GB3838-2002 III类标准)")
    print("=" * 60)
    
    try:
        # 创建DBP处理Crew
        dbp_crew = create_dbp_crew()
        
        # 运行测试
        print("正在执行DBP处理任务...")
        result = dbp_crew.kickoff()
        
        print("\nDBP处理完成！结果如下：")
        print("=" * 60)
        print(result)
        
    except Exception as e:
        print(f"DBP处理过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_dbp_test()