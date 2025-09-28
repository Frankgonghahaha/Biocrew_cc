#!/usr/bin/env python3
"""
测试代谢互补性分析工具
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

from tools.metabolic_complementarity_tool import MetabolicComplementarityTool

def test_metabolic_complementarity_tool():
    """测试代谢互补性分析工具"""
    print("开始测试代谢互补性分析工具...")
    
    # 创建工具实例
    tool = MetabolicComplementarityTool()
    print("✓ 工具实例创建成功")
    
    # 测试工具运行
    print("\n1. 测试工具运行...")
    try:
        # 创建一些模拟的模型文件路径（即使文件不存在，工具也会模拟处理）
        model_paths = [
            "./models/GCF_000001405_40.xml",
            "./models/GCF_000002406_50.xml"
        ]
        
        # 创建模拟的环境代谢物
        exchange_metabolites = ["glucose", "oxygen", "ammonia"]
        
        # 运行工具
        result = tool._run(model_paths, exchange_metabolites)
        print("✓ 工具运行成功")
        print("结果:")
        print(result)
        
    except Exception as e:
        print(f"✗ 工具运行失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试另一种情况：文件存在的情况
    print("\n2. 测试模拟文件存在的情况...")
    try:
        # 创建临时目录和文件
        os.makedirs("./models", exist_ok=True)
        with open("./models/GCF_000001405_40.xml", "w") as f:
            f.write("<model>This is a mock model file</model>")
        with open("./models/GCF_000002406_50.xml", "w") as f:
            f.write("<model>This is another mock model file</model>")
        
        # 运行工具
        result = tool._run(model_paths, exchange_metabolites)
        print("✓ 工具运行成功")
        print("结果:")
        print(result)
        
        # 清理临时文件
        os.remove("./models/GCF_000001405_40.xml")
        os.remove("./models/GCF_000002406_50.xml")
        
    except Exception as e:
        print(f"✗ 工具运行失败: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    test_metabolic_complementarity_tool()
