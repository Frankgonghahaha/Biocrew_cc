#!/usr/bin/env python3
"""
测试微生物菌剂设计阶段
该测试文件专门验证菌剂设计阶段是否正确加载评分工具，并确保智能体提示词包含最新的环境/功能评分逻辑（ScoreEnvironment → Norm1(kcat) → Norm1(enzyme_diversity)）。
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
from core.agents.design_agent import MicrobialAgentDesignAgent

# 任务导入
from core.tasks.design_task import MicrobialAgentDesignTask


REQUIRED_TOOL_NAMES = [
    "ParseDegradationJSONTool",
    "ParseEnvironmentJSONTool",
    "ScoreEnzymeDegradationTool",
    "ScoreEnvironmentTool",
    "ScoreSingleSpeciesTool",
    "微生物互补性数据库查询工具",
]

def setup_logging():
    """设置日志记录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("test_results")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = log_dir / f"design_test_{timestamp}.log"
    result_file = log_dir / f"design_test_{timestamp}.txt"
    tool_call_file = log_dir / f"tool_call_log_design_{timestamp}.json"
    
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
            model="openai/qwen3-30b-a3b-instruct-2507",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        return llm
    except Exception as e:
        print(f"LLM模型初始化失败: {e}")
        return None

def run_design_test():
    """运行微生物菌剂设计测试"""
    print("开始微生物菌剂设计阶段测试")
    
    # 设置日志
    log_file, result_file, tool_call_file = setup_logging()
    log_message("测试开始", log_file)
    
    # 用户需求
    user_requirement = "please help to design a microbial consortium for degrading Dibutyl phthalate effectively."
    log_message(f"用户需求: {user_requirement}", log_file)
    
    # 初始化LLM
    log_message("初始化LLM模型", log_file)
    llm = initialize_llm()
    if not llm:
        log_message("LLM模型初始化失败，测试终止", log_file)
        return
    
    log_message("LLM模型初始化成功", log_file)
    
    try:
        # 创建智能体
        log_message("创建微生物菌剂设计智能体", log_file)
        design_agent = MicrobialAgentDesignAgent(llm).create_agent()
        log_message("微生物菌剂设计智能体创建成功", log_file)
        log_tool_call("design_agent", "Agent Creation", tool_call_file)

        tool_names = [getattr(tool, "name", "") for tool in getattr(design_agent, "tools", [])]
        missing_tools = [name for name in REQUIRED_TOOL_NAMES if name not in tool_names]
        log_message(
            "必备设计工具检测: " + ("全部就绪" if not missing_tools else f"缺失 {missing_tools}"),
            log_file,
        )
        assert not missing_tools, f"Design agent 缺少必要工具: {missing_tools}"

        backstory_text = getattr(design_agent, "backstory", "")
        for required_phrase in [
            "ScoreEnvironmentTool",
            "Norm1(kcat)",
            "互补微生物不承担降解任务",
            "Norm1(enzyme_diversity)",
        ]:
            assert required_phrase in backstory_text, f"Design agent 提示词缺少关键说明: {required_phrase}"
        log_message("智能体提示词包含环境与功能评分要求", log_file)
        
        # 创建任务
        log_message("创建微生物菌剂设计任务（需生成环境/功能评分与组合设计文件）", log_file)
        design_task = MicrobialAgentDesignTask(llm).create_task(
            design_agent, 
            context_task=None,
            user_requirement=user_requirement
        )
        log_message("微生物菌剂设计任务创建成功", log_file)
        log_tool_call("design_agent", "Task Creation", tool_call_file)
        
        # 使用Crew执行任务
        log_message("开始执行微生物菌剂设计任务", log_file)
        crew = Crew(
            agents=[design_agent],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff()
        log_message("微生物菌剂设计任务执行完成", log_file)
        log_tool_call("design_agent", "Task Execution", tool_call_file)
        
        # 保存结果
        with open(result_file, "w", encoding="utf-8") as f:
            f.write("微生物菌剂设计测试结果\n")
            f.write("=" * 30 + "\n")
            f.write(str(result))
        
        log_message(f"测试结果已保存到: {result_file}", log_file)
        log_message("测试完成", log_file)
        
        return result
        
    except Exception as e:
        log_message(f"测试过程中发生错误: {e}", log_file)
        return None

if __name__ == "__main__":
    run_design_test()
