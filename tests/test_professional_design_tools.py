#!/usr/bin/env python3
"""
测试脚本 - 单独检测菌剂设计中使用的五个专业工具
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_individual_tools():
    """
    单独测试每个专业工具
    """
    print("开始测试菌剂设计专业工具...")
    
    # 测试CtfbaTool
    print("\n1. 测试CtfbaTool (代谢通量计算)...")
    try:
        from tools.microbial_agent_design.ctfba_tool.ctfba_tool import CtfbaTool
        ctfba_tool = CtfbaTool()
        print("   ✓ CtfbaTool加载成功")
        
        # 测试工具调用
        result = ctfba_tool._run(
            models_path="/path/to/models",
            target_compound="phenol",
            community_composition={"Pseudomonas putida": 0.4, "Bacillus subtilis": 0.3, "Rhodococcus erythropolis": 0.3},
            tradeoff_coefficient=0.7
        )
        print(f"   ✓ CtfbaTool调用成功: {result['status']}")
        if "simulated" in result['status']:
            print("   ⚠️  工具使用模拟执行")
        else:
            print("   ✅ 工具真实执行")
    except Exception as e:
        print(f"   ✗ CtfbaTool测试失败: {e}")
    
    # 测试GenomeSPOTTool
    print("\n2. 测试GenomeSPOTTool (环境适应性预测)...")
    try:
        from tools.microbial_agent_design.genome_spot_tool.genome_spot_tool import GenomeSPOTTool
        genome_spot_tool = GenomeSPOTTool()
        print("   ✓ GenomeSPOTTool加载成功")
        
        # 检查工具路径
        import tools.microbial_agent_design.genome_spot_tool.genome_spot_tool as genome_spot_module
        current_dir = os.path.dirname(os.path.abspath(genome_spot_module.__file__))
        genome_spot_path = os.path.join(current_dir, '..', '..', 'external_tools', 'genome_spot')
        genome_spot_main_path = os.path.join(genome_spot_path, 'genome_spot', 'genome_spot.py')
        
        if os.path.exists(genome_spot_path) and os.path.exists(genome_spot_main_path):
            # 检查是否可以导入GenomeSPOT模块
            try:
                sys.path.append(genome_spot_path)
                from genome_spot.genome_spot import run_genome_spot
                print("   ✅ GenomeSPOT外部工具存在且可导入")
            except ImportError as e:
                print(f"   ⚠️  GenomeSPOT外部工具存在但无法导入: {e}")
                print("   ⚠️  将使用模拟执行")
        else:
            print("   ⚠️  GenomeSPOT外部工具不存在，将使用模拟执行")
            
    except Exception as e:
        print(f"   ✗ GenomeSPOTTool测试失败: {e}")
    
    # 测试DLkcatTool
    print("\n3. 测试DLkcatTool (酶催化速率预测)...")
    try:
        from tools.microbial_agent_design.dlkcat_tool.dlkcat_tool import DLkcatTool
        dlkcat_tool = DLkcatTool()
        print("   ✓ DLkcatTool加载成功")
        
        # 检查工具路径
        import tools.microbial_agent_design.dlkcat_tool.dlkcat_tool as dlkcat_module
        current_dir = os.path.dirname(os.path.abspath(dlkcat_module.__file__))
        dlkcat_script = os.path.join(current_dir, '..', '..', 'external_tools', 'dlkcat', 'run_DLkcat.py')
        
        if os.path.exists(dlkcat_script):
            print("   ✅ DLkcat外部工具存在")
        else:
            print("   ⚠️  DLkcat外部工具不存在，将使用模拟执行")
            
    except Exception as e:
        print(f"   ✗ DLkcatTool测试失败: {e}")
    
    # 测试CarvemeTool
    print("\n4. 测试CarvemeTool (代谢模型构建)...")
    try:
        from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
        carveme_tool = CarvemeTool()
        print("   ✓ CarvemeTool加载成功")
        
        # 检查工具路径
        import tools.microbial_agent_design.carveme_tool.carveme_tool as carveme_module
        current_dir = os.path.dirname(os.path.abspath(carveme_module.__file__))
        carveme_script = os.path.join(current_dir, '..', '..', 'external_tools', 'carveme', 'build_GSMM_from_aa.py')
        
        if os.path.exists(carveme_script):
            print("   ✅ Carveme外部工具存在")
        else:
            print("   ⚠️  Carveme外部工具不存在，将使用模拟执行")
            
    except Exception as e:
        print(f"   ✗ CarvemeTool测试失败: {e}")
    
    # 测试PhylomintTool
    print("\n5. 测试PhylomintTool (微生物互作分析)...")
    try:
        from tools.microbial_agent_design.phylomint_tool.phylomint_tool import PhylomintTool
        phylomint_tool = PhylomintTool()
        print("   ✓ PhylomintTool加载成功")
        
        # 检查工具路径
        import tools.microbial_agent_design.phylomint_tool.phylomint_tool as phylomint_module
        current_dir = os.path.dirname(os.path.abspath(phylomint_module.__file__))
        phylomint_script = os.path.join(current_dir, '..', '..', 'external_tools', 'phylomint', 'run_phylomint.py')
        
        if os.path.exists(phylomint_script):
            print("   ✅ Phylomint外部工具存在")
        else:
            print("   ⚠️  Phylomint外部工具不存在，将使用模拟执行")
            
    except Exception as e:
        print(f"   ✗ PhylomintTool测试失败: {e}")

def main():
    print("BioCrew - 专业设计工具测试")
    print("=" * 50)
    
    try:
        test_individual_tools()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()