#!/usr/bin/env python3
"""
统一路径配置文件
用于管理项目中所有工具使用的路径
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 统一的模型文件保存目录
MODELS_DIR = PROJECT_ROOT / "outputs" / "metabolic_models"

# 统一的反应数据目录
REACTIONS_DIR = PROJECT_ROOT / "data" / "reactions"

# 统一的测试数据目录
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

# 统一的输出目录
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# 确保所有目录都存在
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REACTIONS_DIR.mkdir(parents=True, exist_ok=True)
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# 外部工具目录
EXTERNAL_TOOLS_DIR = PROJECT_ROOT / "core" / "tools" / "external"