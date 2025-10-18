#!/usr/bin/env python3
"""
测试ReactionAdditionTool工具
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.tools.evaluation.reaction_addition import ReactionAdditionTool

def test_reaction_addition_tool():
    """测试ReactionAdditionTool工具"""
    print("开始测试ReactionAdditionTool工具...")
    
    # 初始化工具
    tool = ReactionAdditionTool()
    
    # 设置测试参数
    models_path = str(project_root / "outputs" / "metabolic_models")
    pollutant_name = "phthalic acid"
    
    print(f"模型路径: {models_path}")
    print(f"污染物名称: {pollutant_name}")
    
    # 调用工具
    result = tool._run(
        models_path=models_path,
        pollutant_name=pollutant_name
    )
    
    print(f"工具调用结果: {result}")
    
    # 检查结果
    if result.get("status") == "success":
        results = result.get("results", [])
        print(f"处理的模型数量: {len(results)}")
        for res in results:
            print(f"  - {res.get('model', 'Unknown')}: {res.get('message', 'No message')}")
    else:
        print("工具调用失败")

if __name__ == "__main__":
    test_reaction_addition_tool()