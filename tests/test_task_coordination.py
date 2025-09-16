#!/usr/bin/env python3
"""
测试任务协调专家的修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

# 智能体导入
from agents.task_coordination_agent import TaskCoordinationAgent

# 任务导入
from tasks.task_coordination_task import TaskCoordinationTask

def test_task_coordination_agent():
    """测试任务协调专家"""
    print("测试任务协调专家...")
    
    # 验证API密钥是否存在
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建任务协调智能体
    coordination_agent = TaskCoordinationAgent(llm).create_agent()
    
    # 创建任务协调任务
    coordination_task = TaskCoordinationTask(llm).create_task(coordination_agent)
    
    # 创建测试Crew
    test_crew = Crew(
        agents=[coordination_agent],
        tasks=[coordination_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行测试
    print("开始执行任务协调测试...")
    try:
        result = test_crew.kickoff()
        print("\n任务协调结果:")
        print(result)
        print("\n✓ 任务协调专家测试通过!")
        return True
    except Exception as e:
        print(f"\n✗ 任务协调专家测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_task_coordination_agent()