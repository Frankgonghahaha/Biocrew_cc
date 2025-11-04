#!/usr/bin/env python3
"""
配置文件，用于设置模型URL和Token
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量（确保无论当前工作目录在哪，都能找到项目根目录的 .env）
_project_root_env = Path(__file__).resolve().parent.parent / ".env"
if _project_root_env.exists():
    load_dotenv(dotenv_path=_project_root_env)
else:
    load_dotenv()

class Config:
    # QWEN3模型配置
    QWEN_API_BASE = os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY', 'YOUR_API_KEY')
    QWEN_MODEL_NAME = os.getenv('QWEN_MODEL_NAME', 'qwen3-next-80b-a3b-thinking')
    
    # OpenAI兼容配置（CrewAI需要）
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_API_KEY')
    
    # 其他配置
    VERBOSE = os.getenv('VERBOSE', 'True').lower() == 'true'
    
    # 模型参数配置
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
    MODEL_MAX_TOKENS = int(os.getenv('MODEL_MAX_TOKENS', '2048'))
    
    # 系统配置
    PROJECT_NAME = "BioCrew"
    VERSION = "1.0.0"
    
    # 数据库配置
    DB_TYPE = os.getenv('DB_TYPE', 'postgresql')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'Bio_data')
    DB_USER = os.getenv('DB_USER', 'nju_bio')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '980605Hyz')
    
    @classmethod
    def resolve_model_name(cls) -> str:
        """
        Resolve model name with optional provider prefix when using DashScope.
        """
        model_name = (cls.QWEN_MODEL_NAME or "").strip()
        if not model_name:
            model_name = "qwen3-next-80b-a3b-thinking"

        needs_provider_prefix = (
            "/" not in model_name
            and isinstance(cls.OPENAI_API_BASE, str)
            and "dashscope" in cls.OPENAI_API_BASE.lower()
        )
        if needs_provider_prefix:
            model_name = f"openai/{model_name}"

        return model_name

    def get_llm(self):
        """
        获取LLM实例
        """
        return ChatOpenAI(
            base_url=self.OPENAI_API_BASE,
            openai_api_base=self.OPENAI_API_BASE,
            api_key=self.OPENAI_API_KEY,
            openai_api_key=self.OPENAI_API_KEY,
            model=self.resolve_model_name(),
            temperature=self.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=self.MODEL_MAX_TOKENS
        )
