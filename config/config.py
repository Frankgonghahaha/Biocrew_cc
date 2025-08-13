#!/usr/bin/env python3
"""
配置文件，用于设置模型URL和Token
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # QWEN3模型配置
    QWEN_API_BASE = os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY', 'YOUR_API_KEY')
    QWEN_MODEL_NAME = os.getenv('QWEN_MODEL_NAME', 'qwen3-30b-a3b-instruct-2507')
    
    # 兼容OpenAI的配置（CrewAI需要）
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_API_KEY')
    
    # 其他配置
    VERBOSE = os.getenv('VERBOSE', 'True').lower() == 'true'