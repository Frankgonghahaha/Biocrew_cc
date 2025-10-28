"""
测试工程微生物组识别阶段
该测试文件专门测试工程微生物组识别阶段的功能，
包括工具调用、数据查询和结果生成等。
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

# 任务导入
from core.tasks.identification_task import MicroorganismIdentificationTask

# 工具导入
from core.tools.database.uniprot import UniProtTool
from core.tools.database.complementarity_query import MicrobialComplementarityDBQueryTool
from core.tools.design.degrading_microorganism_identification_tool import DegradingMicroorganismIdentificationTool
from core.tools.design.protein_sequence_query_sql_updated import ProteinSequenceQuerySQLToolUpdated

def setup_logging():
    """设置日志记录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("test_results")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = log_dir / f"identification_test_{timestamp}.log"
    result_file = log_dir / f"identification_test_{timestamp}.txt"
    tool_call_file = log_dir / f"tool_call_log_identification_{timestamp}.json"
    
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


def test_protein_sequence_query(user_requirement, log_file, tool_call_file):
    """验证UniProt工具可创建性"""
    log_message("验证UniProt工具可创建性", log_file)
    
    try:
        # 创建UniProt工具实例（仅验证工具可创建）
        log_message("创建UniProt工具实例", log_file)
        uniprot_tool = UniProtTool()
        log_message("UniProt工具实例创建成功", log_file)
        log_tool_call("uniprot_tool", "Tool Creation", tool_call_file)
            
    except Exception as e:
        log_message(f"UniProt工具创建过程中发生错误: {e}", log_file)
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}", log_file)


def test_protein_sequence_query_sql(user_requirement, log_file, tool_call_file):
    """验证基于SQL的蛋白质序列查询工具可创建性"""
    log_message("验证基于SQL的蛋白质序列查询工具可创建性", log_file)
    
    try:
        # 创建基于SQL的蛋白质序列查询工具实例（仅验证工具可创建）
        log_message("创建基于SQL的蛋白质序列查询工具实例", log_file)
        protein_sequence_tool = ProteinSequenceQuerySQLToolUpdated()
        log_message("基于SQL的蛋白质序列查询工具实例创建成功", log_file)
        log_tool_call("protein_sequence_tool", "Tool Creation", tool_call_file)
            
    except Exception as e:
        log_message(f"基于SQL的蛋白质序列查询工具创建过程中发生错误: {e}", log_file)
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}", log_file)

def test_complementarity_query(user_requirement, log_file, tool_call_file):
    """验证微生物互补性查询工具可创建性"""
    log_message("验证微生物互补性查询工具可创建性", log_file)
    
    try:
        # 创建微生物互补性查询工具实例（仅验证工具可创建）
        log_message("创建微生物互补性查询工具实例", log_file)
        complementarity_tool = MicrobialComplementarityDBQueryTool()
        log_message("微生物互补性查询工具实例创建成功", log_file)
        log_tool_call("complementarity_tool", "Tool Creation", tool_call_file)
            
    except Exception as e:
        log_message(f"微生物互补性查询工具创建过程中发生错误: {e}", log_file)
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}", log_file)

def test_degrading_microorganism_identification(user_requirement, log_file, tool_call_file):
    """验证降解功能微生物识别工具可创建性"""
    log_message("验证降解功能微生物识别工具可创建性", log_file)
    
    try:
        # 创建降解功能微生物识别工具实例（仅验证工具可创建）
        log_message("创建降解功能微生物识别工具实例", log_file)
        degrading_tool = DegradingMicroorganismIdentificationTool()
        log_message("降解功能微生物识别工具实例创建成功", log_file)
        log_tool_call("degrading_tool", "Tool Creation", tool_call_file)
            
    except Exception as e:
        log_message(f"降解功能微生物识别工具创建过程中发生错误: {e}", log_file)
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}", log_file)

def initialize_llm():
    """初始化LLM模型"""
    try:
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
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

def run_identification_test():
    """运行工程微生物组识别测试"""
    print("开始工程微生物组识别阶段测试")
    
    # 设置日志
    log_file, result_file, tool_call_file = setup_logging()
    log_message("测试开始", log_file)
    
    # 用户需求
    user_requirement = "请你告诉我有哪些邻苯二甲二丁酯水解酶"
    log_message(f"用户需求: {user_requirement}", log_file)
    
    # 初始化LLM
    log_message("初始化LLM模型", log_file)
    llm = initialize_llm()
    if not llm:
        log_message("LLM模型初始化失败，测试终止", log_file)
        return
    
    log_message("LLM模型初始化成功", log_file)
    
    try:
        # 首先测试蛋白质序列查询功能（模拟测试，避免实际调用UniProt API）
        test_protein_sequence_query(user_requirement, log_file, tool_call_file)
        
        # 测试基于SQL的蛋白质序列查询工具
        test_protein_sequence_query_sql(user_requirement, log_file, tool_call_file)
        
        # 测试微生物互补性查询工具
        test_complementarity_query(user_requirement, log_file, tool_call_file)
        
        # 测试降解功能微生物识别工具
        test_degrading_microorganism_identification(user_requirement, log_file, tool_call_file)
        
        # 创建智能体
        log_message("创建工程微生物识别智能体", log_file)
        identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
        log_message("工程微生物识别智能体创建成功", log_file)
        log_tool_call("identification_agent", "Agent Creation", tool_call_file)
        
        # 创建任务
        log_message("创建微生物识别任务", log_file)
        identification_task = MicroorganismIdentificationTask(llm).create_task(
            identification_agent, 
            user_requirement=user_requirement
        )
        log_message("微生物识别任务创建成功", log_file)
        log_tool_call("identification_agent", "Task Creation", tool_call_file)
        
        # 使用Crew执行任务
        log_message("开始执行微生物识别任务", log_file)
        crew = Crew(
            agents=[identification_agent],
            tasks=[identification_task],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff()
        log_message("微生物识别任务执行完成", log_file)
        log_tool_call("identification_agent", "Task Execution", tool_call_file)
        
        # 保存结果
        with open(result_file, "w", encoding="utf-8") as f:
            f.write("工程微生物组识别测试结果\n")
            f.write("=" * 30 + "\n")
            f.write(str(result))
        
        log_message(f"测试结果已保存到: {result_file}", log_file)
        log_message("测试完成", log_file)
        
        return result
        
    except Exception as e:
        log_message(f"测试过程中发生错误: {e}", log_file)
        return None

if __name__ == "__main__":
    run_identification_test()