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

from crewai import Crew, Process
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

# 智能体导入
from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
from agents.microbial_agent_evaluation_agent import MicrobialAgentEvaluationAgent
from agents.implementation_plan_generation_agent import ImplementationPlanGenerationAgent
from agents.knowledge_management_agent import KnowledgeManagementAgent
from agents.task_coordination_agent import TaskCoordinationAgent

# 任务导入
from tasks.microorganism_identification_task import MicroorganismIdentificationTask
from tasks.microbial_agent_design_task import MicrobialAgentDesignTask
from tasks.microbial_agent_evaluation_task import MicrobialAgentEvaluationTask
from tasks.implementation_plan_generation_task import ImplementationPlanGenerationTask
from tasks.task_coordination_task import TaskCoordinationTask

# 工具导入
from tools.evaluation_tool import EvaluationTool

def get_user_input():
    """获取用户自定义的水质处理需求"""
    print("请输入您的水质处理需求:")
    print("例如: 处理含有重金属镉的工业废水")
    user_input = input("水质处理需求: ")
    return user_input

def get_processing_mode():
    """获取用户选择的处理模式"""
    print("\n请选择处理模式:")
    print("1. 链式处理模式（按固定顺序执行）")
    print("2. 自主选择模式（智能体根据情况自主选择）")
    while True:
        choice = input("请输入模式选择 (1 或 2): ")
        if choice in ['1', '2']:
            return int(choice)
        print("无效输入，请输入 1 或 2")

def analyze_evaluation_result(evaluation_result):
    """
    分析评估结果，判断是否需要重新执行任务
    """
    # 使用EvaluationTool来分析评估结果
    eval_tool = EvaluationTool()
    analysis = eval_tool.check_core_standards(evaluation_result)
    return analysis

def run_autonomous_workflow(user_requirement, llm):
    """
    自主执行工作流，智能体根据情况自主选择需要调度的智能体
    """
    print("开始自主任务执行流程...")
    
    # 创建智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
    plan_agent = ImplementationPlanGenerationAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    coordination_agent = TaskCoordinationAgent(llm).create_agent()
    
    # 创建任务
    identification_task = MicroorganismIdentificationTask(llm).create_task(
        identification_agent, 
        user_requirement=user_requirement
    )
    
    design_task = MicrobialAgentDesignTask(llm).create_task(
        design_agent, 
        identification_task, 
        user_requirement=user_requirement
    )
    
    evaluation_task = MicrobialAgentEvaluationTask(llm).create_task(
        evaluation_agent, 
        design_task
    )
    
    plan_task = ImplementationPlanGenerationTask(llm).create_task(
        plan_agent, 
        evaluation_task
    )
    
    # 使用分层处理模式执行任务
    # 任务协调智能体作为管理器来控制其他智能体的执行
    autonomous_crew = Crew(
        agents=[
            coordination_agent,
            identification_agent, 
            design_agent, 
            evaluation_agent, 
            plan_agent, 
            knowledge_agent
        ],
        tasks=[
            identification_task,
            design_task,
            evaluation_task,
            plan_task
        ],
        process=Process.hierarchical,
        manager_agent=coordination_agent,
        verbose=Config.VERBOSE
    )
    
    result = autonomous_crew.kickoff()
    return result

def run_dynamic_workflow(user_requirement, llm):
    """
    动态执行工作流，根据评估结果决定是否需要重新执行任务
    """
    print("开始动态任务执行流程...")
    
    # 创建智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
    plan_agent = ImplementationPlanGenerationAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    # 初始化任务结果
    identification_result = None
    evaluation_result = None
    plan_result = None
    
    # 最大循环次数，防止无限循环
    max_iterations = 3
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"执行第 {iteration} 轮任务流程...")
        
        # 创建识别任务
        identification_task = MicroorganismIdentificationTask(llm).create_task(
            identification_agent, 
            user_requirement=user_requirement
        )
        
        # 如果不是第一轮，添加反馈信息
        if identification_result:
            identification_task = MicroorganismIdentificationTask(llm).create_task(
                identification_agent, 
                user_requirement=user_requirement,
                feedback=f"根据上一轮评估结果，需要重新进行微生物识别。之前的识别结果: {identification_result}"
            )
        
        # 执行识别任务
        identification_crew = Crew(
            agents=[identification_agent, knowledge_agent],
            tasks=[identification_task],
            process=Process.sequential,
            verbose=Config.VERBOSE
        )
        identification_result = identification_crew.kickoff()
        print(f"识别任务完成: {identification_result}")
        
        # 创建设计任务
        design_task = MicrobialAgentDesignTask(llm).create_task(
            design_agent, 
            identification_task, 
            user_requirement=user_requirement
        )
        
        # 执行设计任务
        design_crew = Crew(
            agents=[design_agent, knowledge_agent],
            tasks=[design_task],
            process=Process.sequential,
            verbose=Config.VERBOSE
        )
        design_result = design_crew.kickoff()
        print(f"设计任务完成: {design_result}")
        
        # 创建评估任务
        evaluation_task = MicrobialAgentEvaluationTask(llm).create_task(
            evaluation_agent, 
            design_task
        )
        
        # 执行评估任务
        evaluation_crew = Crew(
            agents=[evaluation_agent, knowledge_agent],
            tasks=[evaluation_task],
            process=Process.sequential,
            verbose=Config.VERBOSE
        )
        evaluation_result = evaluation_crew.kickoff()
        print(f"评估任务完成: {evaluation_result}")
        
        # 分析评估结果
        core_standards_met = analyze_evaluation_result(str(evaluation_result))
        
        if core_standards_met:
            print("评估结果达标，进入方案生成阶段...")
            # 创建方案生成任务
            plan_task = ImplementationPlanGenerationTask(llm).create_task(
                plan_agent, 
                evaluation_task
            )
            
            # 执行方案生成任务
            plan_crew = Crew(
                agents=[plan_agent, knowledge_agent],
                tasks=[plan_task],
                process=Process.sequential,
                verbose=Config.VERBOSE
            )
            plan_result = plan_crew.kickoff()
            print(f"方案生成任务完成: {plan_result}")
            break  # 退出循环
        else:
            print("评估结果不达标，需要重新进行微生物识别和设计...")
            if iteration >= max_iterations:
                print(f"已达到最大迭代次数 ({max_iterations})，停止循环。")
                break
    
    # 返回最终结果
    if plan_result:
        return plan_result
    elif evaluation_result:
        return f"最终评估结果: {evaluation_result}"
    else:
        return "任务执行失败"

def main():
    print("基于CrewAI的水质生物净化技术开发多智能体系统")
    print("=" * 50)
    
    # 获取用户自定义输入
    user_requirement = get_user_input()
    
    # 获取处理模式选择
    processing_mode = get_processing_mode()
    
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
    
    # 根据用户选择的模式执行相应的工作流
    if processing_mode == 1:
        print("使用链式处理模式...")
        result = run_dynamic_workflow(user_requirement, llm)
    else:
        print("使用自主选择模式...")
        result = run_autonomous_workflow(user_requirement, llm)
    
    print("最终结果:")
    print(result)

if __name__ == "__main__":
    main()