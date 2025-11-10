#!/usr/bin/env python3
"""
测试菌剂评估阶段
该测试文件专门测试菌剂评估阶段的功能，
包括代谢反应填充、培养基推荐和ctFBA计算等。
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
from core.agents.evaluation_agent import MicrobialAgentEvaluationAgent

# 任务导入
from core.tasks.evaluation_task import MicrobialAgentEvaluationTask

def setup_logging():
    """设置日志记录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("test_results")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = log_dir / f"evaluation_test_{timestamp}.log"
    result_file = log_dir / f"evaluation_test_{timestamp}.txt"
    tool_call_file = log_dir / f"tool_call_log_evaluation_{timestamp}.json"
    
    return str(log_file), str(result_file), str(tool_call_file)

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
            model="openai/qwen3-30b-a3b-instruct-2507",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        return llm
    except Exception as e:
        print(f"LLM模型初始化失败: {e}")
        return None

def run_evaluation_test():
    """运行菌剂评估测试"""
    print("开始菌剂评估阶段测试")
    
    # 设置日志
    log_file, result_file, tool_call_file = setup_logging()
    log_message("测试开始", log_file)
    
    # 初始化LLM
    log_message("初始化LLM模型", log_file)
    llm = initialize_llm()
    if not llm:
        log_message("LLM模型初始化失败，测试终止", log_file)
        return
    
    log_message("LLM模型初始化成功", log_file)
    
    try:
        # 创建智能体
        log_message("创建菌剂评估智能体", log_file)
        evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
        log_message("菌剂评估智能体创建成功", log_file)
        log_tool_call("evaluation_agent", "Agent Creation", tool_call_file)

        # 确认核心工具已加载
        tool_names = [getattr(tool, "name", "") for tool in getattr(evaluation_agent, "tools", [])]
        has_parse_tool = "ParseDesignConsortiaTool" in tool_names
        has_faa_tool = "FaaBuildTool" in tool_names
        has_carveme_tool = "CarvemeModelBuildTool" in tool_names
        has_medium_tool = "MediumBuildTool" in tool_names
        has_pathway_tool = "AddPathwayTool" in tool_names
        has_micom_tool = "MicomSimulationTool" in tool_names
        log_message(f"检测 ParseDesignConsortiaTool 可用: {'yes' if has_parse_tool else 'missing'}", log_file)
        log_message(f"检测 FaaBuildTool 可用: {'yes' if has_faa_tool else 'missing'}", log_file)
        log_message(f"检测 CarvemeModelBuildTool 可用: {'yes' if has_carveme_tool else 'missing'}", log_file)
        log_message(f"检测 MediumBuildTool 可用: {'yes' if has_medium_tool else 'missing'}", log_file)
        log_message(f"检测 AddPathwayTool 可用: {'yes' if has_pathway_tool else 'missing'}", log_file)
        log_message(f"检测 MicomSimulationTool 可用: {'yes' if has_micom_tool else 'missing'}", log_file)
        assert has_parse_tool, "菌剂评估智能体应包含 ParseDesignConsortiaTool"
        assert has_faa_tool, "菌剂评估智能体应包含 FaaBuildTool"
        assert has_carveme_tool, "菌剂评估智能体应包含 CarvemeModelBuildTool"
        assert has_medium_tool, "菌剂评估智能体应包含 MediumBuildTool"
        assert has_pathway_tool, "菌剂评估智能体应包含 AddPathwayTool"
        assert has_micom_tool, "菌剂评估智能体应包含 MicomSimulationTool"
        
        # 创建任务
        log_message("创建菌剂评估任务（解析设计结果 + 构建 FAA）", log_file)
        evaluation_task = MicrobialAgentEvaluationTask(llm).create_task(
            evaluation_agent,
            context_task=None,
        )
        log_message("菌剂评估任务创建成功", log_file)
        log_tool_call("evaluation_agent", "Task Creation", tool_call_file)
        
        # 使用Crew执行任务
        log_message("开始执行菌剂评估任务", log_file)
        crew = Crew(
            agents=[evaluation_agent],
            tasks=[evaluation_task],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff()
        log_message("菌剂评估任务执行完成", log_file)
        log_tool_call("evaluation_agent", "Task Execution", tool_call_file)
        
        # 保存结果
        with open(result_file, "w", encoding="utf-8") as f:
            f.write("菌剂评估测试结果\n")
            f.write("=" * 30 + "\n")
            f.write(str(result))
        
        log_message(f"测试结果已保存到: {result_file}", log_file)
        log_message("测试完成", log_file)
        
        return result
        
    except Exception as e:
        log_message(f"测试过程中发生错误: {e}", log_file)
        raise

if __name__ == "__main__":
    run_evaluation_test()
