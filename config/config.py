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
    QWEN_API_BASE = os.getenv('QWEN_API_BASE', 'YOUR_API_BASE_URL')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY', 'YOUR_API_KEY')
    QWEN_MODEL_NAME = os.getenv('QWEN_MODEL_NAME', 'QWEN3')
    
    # 其他配置
    VERBOSE = os.getenv('VERBOSE', 'True').lower() == 'true'