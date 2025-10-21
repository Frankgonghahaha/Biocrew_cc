#!/usr/bin/env python3
"""
测试MediumRecommendationTool工具
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入工具类
try:
    from core.tools.evaluation.medium_recommendation import MediumRecommendationTool
    print("成功导入MediumRecommendationTool")
except ImportError as e:
    print(f"无法导入MediumRecommendationTool: {e}")
    sys.exit(1)

def test_medium_recommendation():
    """测试MediumRecommendationTool"""
    print("开始测试MediumRecommendationTool...")
    
    # 创建工具实例
    tool = MediumRecommendationTool()
    
    # 设置参数
    models_path = str(project_root / "outputs" / "metabolic_models")
    output_path = str(project_root / "outputs" / "test_recommended_medium.csv")
    
    # 提供候选EX列表，使用模型中实际存在的交换反应ID
    candidate_ex = [
        "R_EX_glc__D_e=10.0",  # 葡萄糖交换反应
        "R_EX_ac_e=5.0",       # 乙酸交换反应
    ]
    
    print(f"模型路径: {models_path}")
    print(f"输出路径: {output_path}")
    print(f"候选EX列表: {candidate_ex}")
    
    # 执行工具
    result = tool._run(
        models_path=models_path,
        output_path=output_path,
        community_growth=0.2,
        min_growth=0.05,
        max_import=10.0,
        candidate_ex=candidate_ex
    )
    
    print(f"工具执行结果: {result}")
    
    # 检查结果
    if result.get("status") == "success":
        print("✅ MediumRecommendationTool执行成功")
        data = result.get("data", {})
        print(f"输出文件: {data.get('output_file')}")
        print(f"反应数量: {data.get('total_reactions')}")
        print(f"预览数据: {data.get('preview')}")
    else:
        print("❌ MediumRecommendationTool执行失败")
        print(f"错误信息: {result.get('message')}")

if __name__ == "__main__":
    test_medium_recommendation()