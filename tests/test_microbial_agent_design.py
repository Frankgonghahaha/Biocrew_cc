#!/usr/bin/env python3
"""
测试菌剂设计的简化测试文件
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

from crewai import Crew, Process
from config.config import Config
from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
from tasks.microbial_agent_design_task import MicrobialAgentDesignTask

def get_user_input():
    """获取用户输入的水质处理需求"""
    print("=== 菌剂设计测试系统 ===")
    print("请输入您的水质处理需求：")
    
    # 获取目标污染物
    target_pollutant = input("目标污染物（例如：苯酚、重金属等）: ").strip()
    
    # 获取处理目标
    treatment_goal = input("处理目标（例如：达到国家一级排放标准）: ").strip()
    
    # 获取环境条件
    environmental_conditions = input("环境条件（例如：温度、pH值、溶解氧等）: ").strip()
    
    return {
        'target_pollutant': target_pollutant,
        'treatment_goal': treatment_goal,
        'environmental_conditions': environmental_conditions
    }

def main():
    """主函数"""
    # 获取用户输入
    user_input = get_user_input()
    
    # 创建配置实例
    config = Config()
    
    # 获取LLM实例
    llm = config.get_llm()
    
    # 初始化智能体
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    # 构建用户需求描述
    user_requirement = f"""
    目标污染物: {user_input['target_pollutant']}
    处理目标: {user_input['treatment_goal']}
    环境条件: {user_input['environmental_conditions']}
    """
    
    # 初始化任务
    design_task_instance = MicrobialAgentDesignTask(llm)
    design_task = design_task_instance.create_task(
        agent=design_agent,
        user_requirement=user_requirement
    )
    
    # 创建Crew
    crew = Crew(
        agents=[design_agent],
        tasks=[design_task],
        process=Process.sequential,
        verbose=2
    )
    
    # 执行任务
    print("\n开始执行菌剂设计任务...")
    result = crew.kickoff()
    
    # 输出结果
    print("\n=== 任务执行结果 ===")
    print(result)

if __name__ == "__main__":
    main()