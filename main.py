#!/usr/bin/env python3
"""
基于CrewAI的水质生物净化技术开发多智能体系统框架

该系统支持两种任务处理模式：
1. 链式处理模式（Process.sequential）- 按固定顺序执行智能体
2. 自主选择模式（Process.hierarchical）- 智能体根据情况自主选择需要调度的智能体

在自主选择模式中，任务协调智能体作为管理者，根据工作流程状态和评估结果，
智能地决定下一步应该执行哪个智能体，实现动态任务调度。
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
from core.agents.identification_agent import EngineeringMicroorganismIdentificationAgent
from core.agents.design_agent import MicrobialAgentDesignAgent
from core.agents.evaluation_agent import MicrobialAgentEvaluationAgent
from core.agents.implementation_agent import ImplementationPlanGenerationAgent
from core.agents.knowledge_agent import KnowledgeManagementAgent
from core.agents.coordination_agent import TaskCoordinationAgent

# 任务导入
from core.tasks.identification_task import MicroorganismIdentificationTask
from core.tasks.design_task import MicrobialAgentDesignTask
from core.tasks.evaluation_task import MicrobialAgentEvaluationTask
from core.tasks.implementation_task import ImplementationPlanGenerationTask
from core.tasks.coordination_task import TaskCoordinationTask

# 工具导入
from core.tools.evaluation.evaluation import EvaluationTool

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
    try:
        # 使用EvaluationTool来分析评估结果
        eval_tool = EvaluationTool()
        # 使用更详细的分析方法
        analysis = eval_tool._run(evaluation_report=str(evaluation_result))
        if analysis.get("status") == "success":
            return analysis.get("data", {})
        else:
            # 如果工具调用失败，尝试解析评估结果文本
            return _parse_evaluation_text(str(evaluation_result))
    except Exception as e:
        print(f"评估结果分析出错: {str(e)}")
        # 如果分析失败，返回默认结果
        return {"core_standards_met": True}

def _parse_evaluation_text(evaluation_text):
    """
    解析评估结果文本，提取关键指标
    
    Args:
        evaluation_text: 评估结果文本
        
    Returns:
        dict: 解析结果
    """
    try:
        # 检查是否包含核心标准达标信息
        if "群落稳定性和结构稳定性均达标" in evaluation_text:
            return {
                "core_standards_met": True,
                "need_redesign": False
            }
        elif "群落稳定性和结构稳定性不达标" in evaluation_text:
            return {
                "core_standards_met": False,
                "need_redesign": True,
                "suggestions": "建议重新进行微生物识别和设计"
            }
        
        # 检查是否包含具体的评分信息
        import re
        stability_score_match = re.search(r'群落稳定性.*?(\d+(\.\d+)?)', evaluation_text)
        structure_score_match = re.search(r'结构稳定性.*?(\d+(\.\d+)?)', evaluation_text)
        
        stability_score = float(stability_score_match.group(1)) if stability_score_match else None
        structure_score = float(structure_score_match.group(1)) if structure_score_match else None
        
        # 如果评分都大于等于8分，认为达标
        if stability_score is not None and structure_score is not None:
            if stability_score >= 8.0 and structure_score >= 8.0:
                return {
                    "core_standards_met": True,
                    "need_redesign": False,
                    "stability_score": stability_score,
                    "structure_score": structure_score
                }
            else:
                return {
                    "core_standards_met": False,
                    "need_redesign": True,
                    "stability_score": stability_score,
                    "structure_score": structure_score,
                    "suggestions": "建议重新进行微生物识别和设计"
                }
        
        # 默认返回通过
        return {"core_standards_met": True}
    except Exception as e:
        print(f"评估文本解析出错: {str(e)}")
        # 如果解析失败，返回默认结果
        return {"core_standards_met": True}

def run_sequential_workflow(user_requirement, llm):
    """
    链式执行工作流，按照固定顺序执行所有任务
    
    使用CrewAI的顺序处理模式（Process.sequential）执行任务：
    - 按照预定顺序依次执行微生物识别、菌剂设计、效果评估和方案生成任务
    - 每个任务的输出作为下一个任务的输入
    """
    print("开始链式任务执行流程...")
    
    # 创建智能体（不包含知识管理智能体）
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
    plan_agent = ImplementationPlanGenerationAgent(llm).create_agent()
    
    # 创建不包含知识管理智能体的Crew配置
    crew_agents = [identification_agent, design_agent, evaluation_agent, plan_agent]
    
    # 创建任务
    identification_task = MicroorganismIdentificationTask(llm).create_task(
        identification_agent, 
        user_requirement=f"{user_requirement}\n\n重要数据处理指导：\n1. 必须优先使用专门的数据查询工具(PollutantDataQueryTool、GeneDataQueryTool等)获取具体数据\n2. 当某些类型的数据缺失时（如只有微生物数据而无基因数据），应基于现有数据继续分析并明确指出数据缺失情况\n3. 利用外部数据库工具(EnviPath、KEGG等)获取补充信息以完善分析\n4. 在最终报告中明确体现查询到的微生物名称、基因数据等具体内容，不能仅依赖预训练知识"
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
    
    # 使用顺序处理模式执行任务
    sequential_crew = Crew(
        agents=crew_agents,
        tasks=[identification_task, design_task, evaluation_task, plan_task],
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    result = sequential_crew.kickoff()
    return result

def run_autonomous_workflow(user_requirement, llm):
    """
    自主执行工作流，智能体根据情况自主选择需要调度的智能体
    
    使用CrewAI的分层处理模式（Process.hierarchical）实现智能体自主调度：
    - 任务协调智能体作为管理者，负责根据任务执行情况和评估结果决定下一步执行哪个智能体
    - 其他智能体作为执行者，负责执行具体的任务
    - 管理者可以将任务委托给适当的执行者智能体
    """
    print("开始自主任务执行流程...")
    
    # 创建智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
    plan_agent = ImplementationPlanGenerationAgent(llm).create_agent()
    coordination_agent = TaskCoordinationAgent(llm).create_agent()
    
    # 创建任务协调任务
    coordination_task = TaskCoordinationTask(llm).create_task(coordination_agent)
    
    # 创建其他任务
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
    # 注意：在分层处理模式中，管理器智能体不应包含在agents列表中
    autonomous_crew = Crew(
        agents=[
            identification_agent, 
            design_agent, 
            evaluation_agent, 
            plan_agent
        ],
        tasks=[
            coordination_task,
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
    
    # 创建不包含知识管理智能体的Crew配置
    crew_agents = [identification_agent, design_agent, evaluation_agent, plan_agent]
    
    # 初始化任务结果
    identification_result = None
    design_result = None
    evaluation_result = None
    plan_result = None
    
    # 最大循环次数，防止无限循环
    max_iterations = 3
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"执行第 {iteration} 轮任务流程...")
        
        # 创建识别任务，添加数据完整性处理指导
        identification_task = MicroorganismIdentificationTask(llm).create_task(
            identification_agent, 
            user_requirement=f"{user_requirement}\n\n重要数据处理指导：\n1. 必须优先使用专门的数据查询工具(PollutantDataQueryTool、GeneDataQueryTool等)获取具体数据\n2. 当某些类型的数据缺失时（如只有微生物数据而无基因数据），应基于现有数据继续分析并明确指出数据缺失情况\n3. 利用外部数据库工具(EnviPath、KEGG等)获取补充信息以完善分析\n4. 在最终报告中明确体现查询到的微生物名称、基因数据等具体内容，不能仅依赖预训练知识"
        )
        
        # 如果不是第一轮，添加反馈信息和数据完整性处理指导
        if identification_result:
            identification_task = MicroorganismIdentificationTask(llm).create_task(
                identification_agent, 
                user_requirement=user_requirement,
                feedback=f"根据上一轮评估结果，需要重新进行微生物识别。之前的识别结果: {identification_result}\n\n重要数据处理指导：\n1. 必须优先使用专门的数据查询工具(PollutantDataQueryTool、GeneDataQueryTool等)获取具体数据\n2. 当某些类型的数据缺失时（如只有微生物数据而无基因数据），应基于现有数据继续分析并明确指出数据缺失情况\n3. 利用外部数据库工具(EnviPath、KEGG等)获取补充信息以完善分析\n4. 在最终报告中明确体现查询到的微生物名称、基因数据等具体内容，不能仅依赖预训练知识"
            )
        
        # 执行识别任务
        identification_crew = Crew(
            agents=crew_agents,
            tasks=[identification_task],
            process=Process.sequential,
            verbose=Config.VERBOSE
        )
        identification_result = identification_crew.kickoff()
        print(f"识别任务完成: {identification_result}")
        
        # 创建设计任务，确保依赖于识别任务
        design_task = MicrobialAgentDesignTask(llm).create_task(
            design_agent, 
            identification_task, 
            user_requirement=user_requirement
        )
        
        # 执行设计任务
        design_crew = Crew(
            agents=crew_agents,
            tasks=[design_task],
            process=Process.sequential,
            verbose=Config.VERBOSE
        )
        design_result = design_crew.kickoff()
        print(f"设计任务完成: {design_result}")
        
        # 创建评估任务，确保依赖于设计任务
        evaluation_task = MicrobialAgentEvaluationTask(llm).create_task(
            evaluation_agent, 
            design_task
        )
        
        # 执行评估任务
        evaluation_crew = Crew(
            agents=crew_agents,
            tasks=[evaluation_task],
            process=Process.sequential,
            verbose=Config.VERBOSE
        )
        evaluation_result = evaluation_crew.kickoff()
        print(f"评估任务完成: {evaluation_result}")
        
        # 分析评估结果
        analysis_result = analyze_evaluation_result(str(evaluation_result))
        core_standards_met = analysis_result.get("core_standards_met", False) if isinstance(analysis_result, dict) else analysis_result
        
        if core_standards_met:
            print("评估结果达标，进入方案生成阶段...")
            # 创建方案生成任务，确保依赖于评估任务
            plan_task = ImplementationPlanGenerationTask(llm).create_task(
                plan_agent, 
                evaluation_task
            )
            
            # 执行方案生成任务
            plan_crew = Crew(
                agents=crew_agents,
                tasks=[plan_task],
                process=Process.sequential,
                verbose=Config.VERBOSE
            )
            plan_result = plan_crew.kickoff()
            print(f"方案生成任务完成: {plan_result}")
            break  # 退出循环
        else:
            print("评估结果不达标，需要重新进行微生物识别和设计...")
            # 获取具体的改进建议
            if isinstance(analysis_result, dict) and "suggestions" in analysis_result:
                print(f"改进建议: {analysis_result['suggestions']}")
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
    
    # 验证OPENAI_API_KEY是否存在
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：OPENAI_API_KEY未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，使用DashScope专用方式
    # 注意：必须正确指定提供商（openai/前缀）以避免"LLM Provider NOT provided"错误
    try:
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,  # 使用原始API密钥
            model="openai/qwen3-30b-a3b-instruct-2507",  # 指定openai提供商
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        print("   ✓ LLM模型初始化成功")
    except Exception as e:
        print(f"   ✗ LLM模型初始化失败: {e}")
        return
    
    # 根据用户选择的模式执行相应的工作流
    if processing_mode == 1:
        print("使用链式处理模式...")
        result = run_sequential_workflow(user_requirement, llm)
    else:
        print("使用自主选择模式...")
        result = run_autonomous_workflow(user_requirement, llm)
    
    print("最终结果:")
    print(result)

if __name__ == "__main__":
    main()