#!/usr/bin/env python3
"""
工具集成测试脚本
用于测试BioCrew项目中各工具的集成情况
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入工具
from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
from tools.microbial_agent_design.genome_spot_tool.genome_spot_tool import GenomeSPOTTool
from tools.microbial_agent_evaluation.reaction_addition_tool.reaction_addition_tool import ReactionAdditionTool
from tools.microbial_agent_evaluation.medium_recommendation_tool.medium_recommendation_tool import MediumRecommendationTool
from tools.microbial_agent_design.ctfba_tool.ctfba_tool import CtfbaTool
from tools.microbial_agent_evaluation.evaluation_tool import EvaluationTool

# 定义测试数据目录
test_data_dir = project_root / "data" / "test"
test_outputs_dir = project_root / "tests" / "test_results"

def test_carveme_tool():
    """测试CarvemeTool工具"""
    print("=" * 50)
    print("测试 CarveMe 工具")
    print("=" * 50)
    
    try:
        # 初始化工具
        tool = CarvemeTool()
        
        # 调用工具
        result = tool._run(
            input_path=str(test_data_dir),
            output_path="test_model.xml",
            threads=1,
            overwrite=True
        )
        
        print(f"CarveMe工具调用结果: {result}")
        return result
        
    except Exception as e:
        print(f"CarveMe工具测试失败: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_genome_spot_tool():
    """测试GenomeSPOTTool工具"""
    print("=" * 50)
    print("测试 GenomeSPOT 工具")
    print("=" * 50)
    
    try:
        # 初始化工具
        tool = GenomeSPOTTool()
        
        # 调用工具
        result = tool._run(
            fna_path=str(test_data_dir / "test.fna"),
            faa_path="",  # 暂时不需要蛋白质序列文件
            models_path=""  # 使用默认模型路径
        )
        
        print(f"GenomeSPOT工具调用结果: {result}")
        return result
        
    except Exception as e:
        print(f"GenomeSPOT工具测试失败: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_reaction_addition_tool():
    """测试ReactionAdditionTool工具"""
    print("=" * 50)
    print("测试 ReactionAdditionTool 工具")
    print("=" * 50)
    
    try:
        # 初始化工具
        tool = ReactionAdditionTool()
        
        # 调用工具
        result = tool._run(
            models_path=os.path.join(project_root, "tools", "outputs", "metabolic_models"), # 使用CarveMe生成模型的目录
            pollutant_name="phthalic acid"
        )
        
        print(f"ReactionAdditionTool工具调用结果: {result}")
        return result
        
    except Exception as e:
        print(f"ReactionAdditionTool工具测试失败: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_medium_recommendation_tool():
    """测试MediumRecommendationTool工具"""
    print("=" * 50)
    print("测试 MediumRecommendationTool 工具")
    print("=" * 50)
    
    try:
        # 初始化工具
        tool = MediumRecommendationTool()
        
        # 调用工具
        result = tool._run(
            models_path=os.path.join(project_root, "tools", "outputs", "metabolic_models"), # 使用CarveMe生成模型的目录
            output_path=str(project_root / "outputs" / "test_medium.csv"),
            community_growth=0.2,
            min_growth=0.05,
            max_import=10.0
        )
        
        print(f"MediumRecommendationTool工具调用结果: {result}")
        return result
        
    except Exception as e:
        print(f"MediumRecommendationTool工具测试失败: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_ctfba_tool():
    """测试CtfbaTool工具"""
    print("=" * 50)
    print("测试 CtfbaTool 工具")
    print("=" * 50)
    
    try:
        # 初始化工具
        tool = CtfbaTool()
        
        # 调用工具，使用实际生成的模型文件名
        result = tool._run(
            models_path=os.path.join(project_root, "tools", "outputs", "metabolic_models"),
            target_compound="phthalic acid",
            community_composition={
                "GCF_000014565.1_protein": 0.6, 
                "GCF_039596375.1_protein": 0.4
            },
            tradeoff_coefficient=0.7
        )
        
        print(f"CtfbaTool工具调用结果: {result}")
        return result
        
    except Exception as e:
        print(f"CtfbaTool工具测试失败: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_evaluation_tool():
    """测试EvaluationTool工具"""
    print("=" * 50)
    print("测试 EvaluationTool 工具")
    print("=" * 50)
    
    try:
        # 初始化工具
        tool = EvaluationTool()
        
        # 调用工具（使用模拟模式）
        result = tool._run(
            operation="analyze_evaluation_result",
            evaluation_report="这是一个模拟的评估报告内容"
        )
        
        print(f"EvaluationTool工具调用结果: {result}")
        return result
        
    except Exception as e:
        print(f"EvaluationTool工具测试失败: {str(e)}")
        return {"status": "error", "message": str(e)}

def main():
    """主函数"""
    print("开始工具集成测试")
    
    # 记录测试开始时间
    start_time = datetime.now()
    print(f"测试开始时间: {start_time}")
    
    # 创建输出目录
    test_outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # 存储测试结果
    results = {}
    
    # 依次测试各工具
    results["carveme"] = test_carveme_tool()
    results["genome_spot"] = test_genome_spot_tool()
    results["reaction_addition"] = test_reaction_addition_tool()
    results["medium_recommendation"] = test_medium_recommendation_tool()
    results["ctfba"] = test_ctfba_tool()
    results["evaluation"] = test_evaluation_tool()
    
    # 记录测试结束时间
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"测试结束时间: {end_time}")
    print(f"总测试耗时: {duration}")
    
    # 保存测试结果到文件
    result_file = test_outputs_dir / f"tool_integration_test_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"测试结果已保存到: {result_file}")
    
    # 打印测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for tool_name, result in results.items():
        status = "✅ 通过" if result.get("status", "").startswith("success") else "❌ 失败"
        print(f"{tool_name:<20} {status}")
    
    return results

if __name__ == "__main__":
    main()