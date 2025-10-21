"""
核心工具模块初始化文件
"""

# 确保outputs目录存在
import os
from pathlib import Path

# 创建必要的目录
directories = [
    "outputs",
    "outputs/logs",
    "outputs/metabolic_models",
    "outputs/genome_features",
    "outputs/reactions"
]

for directory in directories:
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)