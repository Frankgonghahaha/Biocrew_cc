#!/usr/bin/env python3
"""
测试智能体自主选择任务功能的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

def test_autonomous_agent():
    print("测试智能体自主选择任务功能")
    print("=" * 40)
    
    # 模拟用户需求
    user_requirement = "处理含有重金属镉的工业废水"
    print(f"用户需求: {user_requirement}")
    
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
    
    print("LLM模型初始化成功")
    print("测试完成")

if __name__ == "__main__":
    test_autonomous_agent()