#!/usr/bin/env python3
"""
测试Agent是否能正确使用NCBI基因组查询工具
"""

import sys
import os
from dotenv import load_dotenv

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（当前目录的上级目录）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到Python路径中
sys.path.insert(0, project_root)

from config.config import Config
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
import dashscope

# 加载环境变量
load_dotenv()

def get_llm():
    """获取LLM实例"""
    dashscope.api_key = Config.QWEN_API_KEY
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    return llm

def test_agent_with_ncbi_tool():
    """测试Agent是否能正确使用NCBI基因组查询工具"""
    print("开始测试Agent是否能正确使用NCBI基因组查询工具...")
    
    # 初始化LLM
    try:
        llm = get_llm()
        print("✓ LLM模型初始化成功")
    except Exception as e:
        print(f"✗ LLM模型初始化失败: {e}")
        return
    
    # 创建Agent
    print("\n1. 创建EngineeringMicroorganismIdentificationAgent...")
    try:
        from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
        agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
        print("✓ 智能体创建成功")
        print(f"✓ 智能体角色: {agent.role}")
        print(f"✓ 工具数量: {len(agent.tools)}")
        for i, tool in enumerate(agent.tools, 1):
            print(f"  - 工具 {i}: {tool.name}")
    except Exception as e:
        print(f"✗ 智能体创建失败: {e}")
        return
    
    # 验证工具是否正确加载
    ncbi_tool_found = False
    for tool in agent.tools:
        if "NCBI" in tool.name:
            ncbi_tool_found = True
            break
    
    if not ncbi_tool_found:
        print("✗ NCBI基因组查询工具未正确加载")
        return
    else:
        print("✓ NCBI基因组查询工具已正确加载")
    
    # 创建任务
    print("  创建任务...")
    try:
        from tasks.microorganism_identification_task import MicroorganismIdentificationTask
        task_creator = MicroorganismIdentificationTask(llm)
        task = task_creator.create_task(
            agent=agent,
            user_requirement="识别可以降解dibutyl phthalate的微生物，并提供其NCBI基因组Assembly Accession信息"
        )
        print("✓ 任务创建成功")
    except Exception as e:
        print(f"✗ 任务创建失败: {e}")
        return
    
    # 创建Crew
    print("  创建Crew执行任务...")
    try:
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        print("✓ Crew创建成功")
    except Exception as e:
        print(f"✗ Crew创建失败: {e}")
        return
    
    # 执行任务
    print("  开始执行任务（真实调用工具）...")
    try:
        result = crew.kickoff()
        print("  === 任务执行完成 ===\n")
        print("  ✓ 任务执行成功\n")
        print("  === 执行结果 ===")
        if hasattr(result, 'raw') and result.raw:
            print(f"    {str(result.raw)}")
        else:
            print(f"    {str(result)}")
        print("  ✓ 结果验证完成")
        return result
    except Exception as e:
        print(f"✗ 任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_agent_with_ncbi_tool()