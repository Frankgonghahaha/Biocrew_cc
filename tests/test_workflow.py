#!/usr/bin/env python3
"""
测试功能菌剂-菌剂设计-菌剂评估完整工作流
该测试文件完成功能菌剂识别、菌剂设计和菌剂评估三个流程的完整测试，
并记录最终结果和工具调用的详细结果，最后对所有结果进行分析。
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process
from langchain_openai import ChatOpenAI
from config.config import Config

# 智能体导入
from core.agents.identification_agent import EngineeringMicroorganismIdentificationAgent
from core.agents.design_agent import MicrobialAgentDesignAgent
from core.agents.evaluation_agent import MicrobialAgentEvaluationAgent

# 任务导入
from core.tasks.identification_task import MicroorganismIdentificationTask
from core.tasks.design_task import MicrobialAgentDesignTask
from core.tasks.evaluation_task import MicrobialAgentEvaluationTask

# 工具导入
from core.tools.evaluation.evaluation import EvaluationTool

def setup_logging():
    """设置日志记录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("test_results")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = log_dir / f"workflow_test_{timestamp}.log"
    result_file = log_dir / f"workflow_test_{timestamp}.txt"
    tool_call_file = log_dir / f"tool_call_log_{timestamp}.json"
    
    return str(log_file), str(result_file), str(tool_call_file)

def cleanup_previous_results():
    """清理之前的测试结果"""
    try:
        # 清理测试结果目录
        test_results_dir = Path("test_results")
        if test_results_dir.exists():
            import shutil
            shutil.rmtree(test_results_dir)
            test_results_dir.mkdir(exist_ok=True)
        
        # 清理代谢模型目录
        models_dir = Path("outputs/metabolic_models")
        if models_dir.exists():
            import shutil
            shutil.rmtree(models_dir)
            models_dir.mkdir(exist_ok=True)
            
        # 清理反应数据文件
        reactions_file = Path("data/reactions/phthalic_acid_degradation_reactions.csv")
        if reactions_file.exists():
            reactions_file.unlink()
            
        print("已清理之前的测试结果")
    except Exception as e:
        print(f"清理测试结果时出错: {e}")

def initialize_directories():
    """初始化必要的目录"""
    try:
        # 确保必要的目录存在
        directories = [
            "test_results",
            "outputs/metabolic_models",
            "data/reactions"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("已初始化必要的目录")
    except Exception as e:
        print(f"初始化目录时出错: {e}")

def log_message(message, log_file):
    """记录日志消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def log_tool_call(agent_name, tool_name, tool_call_file):
    """记录工具调用"""
    timestamp = datetime.now().isoformat()
    tool_call_entry = {
        "agent": agent_name,
        "tool": tool_name,
        "timestamp": timestamp
    }
    
    # 读取现有记录
    if os.path.exists(tool_call_file):
        with open(tool_call_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {"tool_calls": []}
    else:
        data = {"tool_calls": []}
    
    # 添加新记录
    data["tool_calls"].append(tool_call_entry)
    
    # 写入文件
    with open(tool_call_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def initialize_llm():
    """初始化LLM模型"""
    try:
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            openai_api_base=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,
            openai_api_key=Config.OPENAI_API_KEY,
            model="openai/qwen3-next-80b-a3b-thinking",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS,
            request_timeout=300  # 增加超时时间到5分钟
        )
        return llm
    except Exception as e:
        print(f"LLM模型初始化失败: {e}")
        return None

def run_identification_phase(llm, user_requirement, log_file, tool_call_file):
    """运行工程微生物组识别阶段"""
    log_message("开始工程微生物组识别阶段", log_file)
    
    try:
        # 创建智能体
        identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
        log_message("工程微生物识别智能体创建成功", log_file)
        log_tool_call("identification_agent", "Agent Creation", tool_call_file)
        
        # 创建任务
        identification_task = MicroorganismIdentificationTask(llm).create_task(
            identification_agent, 
            user_requirement=user_requirement
        )
        log_message("微生物识别任务创建成功", log_file)
        log_tool_call("identification_agent", "Task Creation", tool_call_file)
        
        # 使用Crew执行任务，增加重试机制
        log_message("开始执行微生物识别任务", log_file)
        crew = Crew(
            agents=[identification_agent],
            tasks=[identification_task],
            process=Process.sequential,
            verbose=True
        )
        
        # 执行任务，最多重试3次
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = crew.kickoff()
                log_message("微生物识别任务执行完成", log_file)
                log_tool_call("identification_agent", "Task Execution", tool_call_file)
                return result, identification_task
            except Exception as e:
                if attempt < max_retries - 1:
                    log_message(f"微生物识别任务执行失败 (尝试 {attempt + 1}/{max_retries}): {e}", log_file)
                    time.sleep(10)  # 等待10秒后重试，给网络更多时间
                else:
                    raise e  # 最后一次尝试失败，抛出异常
        
    except Exception as e:
        log_message(f"工程微生物组识别阶段执行失败: {e}", log_file)
        return None, None

def run_design_phase(llm, identification_result, identification_task, user_requirement, log_file, tool_call_file):
    """运行微生物菌剂设计阶段"""
    log_message("开始微生物菌剂设计阶段", log_file)
    
    try:
        # 创建智能体
        design_agent = MicrobialAgentDesignAgent(llm).create_agent()  # 传入LLM参数
        log_message("微生物菌剂设计智能体创建成功", log_file)
        log_tool_call("design_agent", "Agent Creation", tool_call_file)
        
        # 创建任务，使用识别阶段的结果作为上下文
        design_task = MicrobialAgentDesignTask(llm).create_task(
            design_agent, 
            context_task=identification_task,  # 使用识别阶段的任务作为上下文
            user_requirement=user_requirement
        )
        log_message("微生物菌剂设计任务创建成功", log_file)
        log_tool_call("design_agent", "Task Creation", tool_call_file)
        
        # 使用Crew执行任务，增加重试机制
        log_message("开始执行微生物菌剂设计任务", log_file)
        crew = Crew(
            agents=[design_agent],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True
        )
        
        # 执行任务，最多重试3次
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = crew.kickoff()
                log_message("微生物菌剂设计任务执行完成", log_file)
                log_tool_call("design_agent", "Task Execution", tool_call_file)
                return result, design_task
            except Exception as e:
                if attempt < max_retries - 1:
                    log_message(f"微生物菌剂设计任务执行失败 (尝试 {attempt + 1}/{max_retries}): {e}", log_file)
                    time.sleep(10)  # 等待10秒后重试，给网络更多时间
                else:
                    raise e  # 最后一次尝试失败，抛出异常
        
    except Exception as e:
        log_message(f"微生物菌剂设计阶段执行失败: {e}", log_file)
        return None, None

def run_evaluation_phase(llm, design_result, design_task, log_file, tool_call_file):
    """运行菌剂评估阶段"""
    log_message("开始菌剂评估阶段", log_file)
    
    try:
        # 创建智能体
        evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
        log_message("菌剂评估智能体创建成功", log_file)
        log_tool_call("evaluation_agent", "Agent Creation", tool_call_file)
        
        # 创建任务，使用设计阶段的结果作为上下文
        evaluation_task = MicrobialAgentEvaluationTask(llm).create_task(
            evaluation_agent, 
            context_task=design_task  # 使用设计阶段的任务作为上下文
        )
        log_message("菌剂评估任务创建成功", log_file)
        log_tool_call("evaluation_agent", "Task Creation", tool_call_file)
        
        # 使用Crew执行任务，增加重试机制
        log_message("开始执行菌剂评估任务", log_file)
        crew = Crew(
            agents=[evaluation_agent],
            tasks=[evaluation_task],
            process=Process.sequential,
            verbose=True
        )
        
        # 执行任务，最多重试3次
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = crew.kickoff()
                log_message("菌剂评估任务执行完成", log_file)
                log_tool_call("evaluation_agent", "Task Execution", tool_call_file)
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    log_message(f"菌剂评估任务执行失败 (尝试 {attempt + 1}/{max_retries}): {e}", log_file)
                    time.sleep(10)  # 等待10秒后重试，给网络更多时间
                else:
                    raise e  # 最后一次尝试失败，抛出异常
        
    except Exception as e:
        log_message(f"菌剂评估阶段执行失败: {e}", log_file)
        return None

def analyze_results(identification_result, design_result, evaluation_result, result_file, log_file):
    """分析所有阶段的结果"""
    log_message("开始分析所有阶段的结果", log_file)
    
    with open(result_file, "w", encoding="utf-8") as f:
        f.write("功能菌剂-菌剂设计-菌剂评估完整工作流测试结果分析\n")
        f.write("=" * 60 + "\n\n")
        
        # 工程微生物组识别结果
        f.write("## 1. 工程微生物组识别结果\n")
        f.write("-" * 30 + "\n")
        if identification_result:
            f.write(str(identification_result) + "\n\n")
        else:
            f.write("识别阶段执行失败或无结果\n\n")
        
        # 微生物菌剂设计结果
        f.write("## 2. 微生物菌剂设计结果\n")
        f.write("-" * 30 + "\n")
        if design_result:
            f.write(str(design_result) + "\n\n")
        else:
            f.write("设计阶段执行失败或无结果\n\n")
        
        # 菌剂评估结果
        f.write("## 3. 菌剂评估结果\n")
        f.write("-" * 30 + "\n")
        if evaluation_result:
            f.write(str(evaluation_result) + "\n\n")
        else:
            f.write("评估阶段执行失败或无结果\n\n")
        
        # 综合分析
        f.write("## 4. 综合分析\n")
        f.write("-" * 30 + "\n")
        f.write("工作流执行状态: ")
        if identification_result and design_result and evaluation_result:
            f.write("成功完成所有阶段\n")
        else:
            f.write("部分阶段执行失败\n")
        
        f.write("\n工具调用情况:\n")
        f.write("1. 工程微生物识别智能体工具: EnviPathTool, KeggTool, PollutantSummaryTool, NCBI基因组查询工具\n")
        f.write("2. 微生物菌剂设计智能体工具: EnviPathTool, KeggTool, PollutantSummaryTool, NCBI基因组查询工具, GenomeSPOTTool, DLkcatTool, CarvemeTool, IntegratedGenomeProcessingTool\n")
        f.write("3. 菌剂评估智能体工具: EvaluationTool, ReactionAdditionTool, MediumRecommendationTool, CtfbaTool\n")
    
    log_message(f"结果分析完成，详细报告已保存到: {result_file}", log_file)

def get_user_input():
    """获取用户输入的处理需求"""
    print("请输入您的水质处理需求:")
    print("例如: 处理含有邻苯二甲酸的工业废水")
    user_input = input("您的需求: ").strip()
    
    if not user_input:
        print("未输入有效需求，使用默认需求")
        return "处理含有邻苯二甲酸的工业废水"
    
    return user_input

def main():
    """主函数"""
    print("开始功能菌剂-菌剂设计-菌剂评估完整工作流测试")
    
    # 清理之前的测试结果
    cleanup_previous_results()
    
    # 初始化必要的目录
    initialize_directories()
    
    # 设置日志
    log_file, result_file, tool_call_file = setup_logging()
    log_message("测试开始", log_file)
    
    # 获取用户需求
    user_requirement = get_user_input()
    log_message(f"用户需求: {user_requirement}", log_file)
    
    # 初始化LLM
    log_message("初始化LLM模型", log_file)
    llm = initialize_llm()
    if not llm:
        log_message("LLM模型初始化失败，测试终止", log_file)
        return
    
    log_message("LLM模型初始化成功", log_file)
    
    # 执行工程微生物组识别阶段
    identification_result, identification_task = run_identification_phase(llm, user_requirement, log_file, tool_call_file)
    
    # 执行微生物菌剂设计阶段
    design_result, design_task = run_design_phase(llm, identification_result, identification_task, user_requirement, log_file, tool_call_file)
    
    # 执行菌剂评估阶段
    evaluation_result = run_evaluation_phase(llm, design_result, design_task, log_file, tool_call_file)
    
    # 分析结果
    analyze_results(identification_result, design_result, evaluation_result, result_file, log_file)
    
    log_message("测试完成", log_file)
    print(f"测试完成，详细日志请查看: {log_file}")
    print(f"结果分析报告请查看: {result_file}")
    print(f"工具调用记录请查看: {tool_call_file}")

if __name__ == "__main__":
    main()
