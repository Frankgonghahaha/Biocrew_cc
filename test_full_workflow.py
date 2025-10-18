#!/usr/bin/env python3
"""
测试从菌剂设计到菌剂评估的完整流程
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
from tools.microbial_agent_evaluation.reaction_addition_tool.reaction_addition_tool import ReactionAdditionTool
from tools.microbial_agent_evaluation.medium_recommendation_tool.medium_recommendation_tool import MediumRecommendationTool
from tools.microbial_agent_design.ctfba_tool.ctfba_tool import CtfbaTool
from tools.microbial_agent_evaluation.evaluation_tool import EvaluationTool

def test_full_workflow():
    """测试完整的工作流程"""
    print("开始测试从菌剂设计到菌剂评估的完整流程...")
    
    # 1. 使用CarveMe工具生成代谢模型
    print("\n1. 使用CarveMe工具生成代谢模型...")
    carveme_tool = CarvemeTool()
    input_path = str(project_root / "test_data")
    output_path = str(project_root / "outputs" / "metabolic_models")
    
    carveme_result = carveme_tool._run(
        input_path=input_path,
        output_path=output_path,
        threads=1,
        overwrite=True
    )
    
    print(f"CarveMe工具执行结果: {carveme_result}")
    
    if carveme_result.get("status") != "success":
        print("CarveMe工具执行失败，流程终止")
        return
    
    # 2. 使用ReactionAdditionTool为模型添加反应
    print("\n2. 使用ReactionAdditionTool为模型添加反应...")
    reaction_tool = ReactionAdditionTool()
    reaction_result = reaction_tool._run(
        models_path=output_path,
        pollutant_name="phthalic acid"
    )
    
    print(f"ReactionAdditionTool工具执行结果: {reaction_result}")
    
    if reaction_result.get("status") != "success":
        print("ReactionAdditionTool工具执行失败，流程终止")
        return
    
    # 3. 使用MediumRecommendationTool生成推荐培养基
    print("\n3. 使用MediumRecommendationTool生成推荐培养基...")
    medium_tool = MediumRecommendationTool()
    medium_output = str(project_root / "outputs" / "test_medium.csv")
    medium_result = medium_tool._run(
        models_path=output_path,
        output_path=medium_output,
        community_growth=0.2,
        min_growth=0.05,
        max_import=10.0
    )
    
    print(f"MediumRecommendationTool工具执行结果: {medium_result}")
    
    # 4. 使用CtfbaTool计算代谢通量
    print("\n4. 使用CtfbaTool计算代谢通量...")
    ctfba_tool = CtfbaTool()
    
    # 构造社区组成（使用模拟数据）
    community_composition = {
        "GCF_000014565_1_protein": 0.6,
        "GCF_039596375_1_protein": 0.4
    }
    
    ctfba_result = ctfba_tool._run(
        models_path=output_path,
        target_compound="phthalic acid",
        community_composition=community_composition,
        tradeoff_coefficient=0.7
    )
    
    print(f"CtfbaTool工具执行结果: {ctfba_result}")
    
    # 5. 使用EvaluationTool评估结果
    print("\n5. 使用EvaluationTool评估结果...")
    eval_tool = EvaluationTool()
    eval_result = eval_tool._run(
        ctfba_results=ctfba_result,
        target_compound="phthalic acid"
    )
    
    print(f"EvaluationTool工具执行结果: {eval_result}")
    
    print("\n完整流程测试完成！")
    
    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    print(f"CarveMe工具: {'✅ 成功' if carveme_result.get('status') == 'success' else '❌ 失败'}")
    print(f"ReactionAdditionTool工具: {'✅ 成功' if reaction_result.get('status') == 'success' else '❌ 失败'}")
    print(f"MediumRecommendationTool工具: {'✅ 成功' if medium_result.get('status') == 'success' else '❌ 失败'}")
    print(f"CtfbaTool工具: {'✅ 成功' if ctfba_result.get('status') == 'success' else '❌ 失败'}")
    print(f"EvaluationTool工具: {'✅ 成功' if eval_result.get('status') == 'success' else '❌ 失败'}")

if __name__ == "__main__":
    test_full_workflow()