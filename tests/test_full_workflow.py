#!/usr/bin/env python3
"""
测试从菌剂设计到菌剂评估的完整流程
"""

import os
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入工具类
try:
    from core.tools.design.carveme import CarvemeTool
    from core.tools.evaluation.reaction_addition import ReactionAdditionTool
    from core.tools.evaluation.medium_recommendation import MediumRecommendationTool
    from core.tools.design.ctfba import CtfbaTool
    from core.tools.evaluation.evaluation import EvaluationTool
except ImportError as e:
    logger.error(f"无法导入核心工具模块: {e}")
    sys.exit(1)

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
    # 使用改进的反应数据文件
    reactions_csv = str(project_root / "data" / "reactions" / "phthalic_acid_reactions.csv")
    reaction_result = reaction_tool._run(
        models_path=output_path,
        pollutant_name="phthalic acid",
        reactions_csv=reactions_csv
    )
    
    print(f"ReactionAdditionTool工具执行结果: {reaction_result}")
    
    if reaction_result.get("status") != "success":
        print("ReactionAdditionTool工具执行失败，流程终止")
        return
    
    # 3. 使用MediumRecommendationTool生成推荐培养基
    print("\n3. 使用MediumRecommendationTool生成推荐培养基...")
    medium_tool = MediumRecommendationTool()
    medium_output = str(project_root / "outputs" / "test_medium.csv")
    # 提供更丰富的碳源候选
    candidate_ex = [
        "EX_glc__D_e=10.0",  # 葡萄糖
        "EX_ac_e=5.0",       # 乙酸
        "EX_pyr_e=5.0",      # 丙酮酸
        "EX_lac__D_e=5.0",   # 乳酸
        "EX_succ_e=5.0"      # 琥珀酸
    ]
    
    medium_result = medium_tool._run(
        models_path=output_path,
        output_path=medium_output,
        community_growth=0.2,
        min_growth=0.05,
        max_import=10.0,
        candidate_ex=candidate_ex
    )
    
    print(f"MediumRecommendationTool工具执行结果: {medium_result}")
    
    # 4. 使用CtfbaTool计算代谢通量
    logger.info("4. 使用CtfbaTool计算代谢通量...")
    ctfba_tool = CtfbaTool()
    
    # 构造社区组成（使用模拟数据）
    community_composition = {
        "GCF_000014565_1_protein": 0.6,
        "GCF_039596375_1_protein": 0.4
    }
    
    # 使用更平衡的权衡系数
    ctfba_result = ctfba_tool._run(
        models_path=output_path,
        target_compound="phthalic acid",
        community_composition=community_composition,
        tradeoff_coefficient=0.3  # 降低权衡系数，更注重群落稳定性
    )
    
    print(f"CtfbaTool工具执行结果: {ctfba_result}")
    
    # 5. 使用EvaluationTool评估结果
    logger.info("5. 使用EvaluationTool评估结果...")
    eval_tool = EvaluationTool()
    eval_result = eval_tool._run(
        ctfba_results=ctfba_result,
        target_compound="phthalic acid"
    )
    
    print(f"EvaluationTool工具执行结果: {eval_result}")
    
    logger.info("完整流程测试完成！")
    
    # 汇总结果
    logger.info("=== 测试结果汇总 ===")
    logger.info(f"CarveMe工具: {'✅ 成功' if carveme_result.get('status') == 'success' else '❌ 失败'}")
    logger.info(f"ReactionAdditionTool工具: {'✅ 成功' if reaction_result.get('status') == 'success' else '❌ 失败'}")
    logger.info(f"MediumRecommendationTool工具: {'✅ 成功' if medium_result.get('status') == 'success' else '❌ 失败'}")
    logger.info(f"CtfbaTool工具: {'✅ 成功' if ctfba_result.get('status') == 'success' else '❌ 失败'}")
    logger.info(f"EvaluationTool工具: {'✅ 成功' if eval_result.get('status') == 'success' else '❌ 失败'}")

if __name__ == "__main__":
    test_full_workflow()