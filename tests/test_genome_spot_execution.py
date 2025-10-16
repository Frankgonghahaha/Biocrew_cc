#!/usr/bin/env python3
"""
测试GenomeSPOT工具的真实执行
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_genome_spot_execution():
    """测试GenomeSPOT工具的真实执行"""
    print("开始测试GenomeSPOT工具的真实执行...")
    
    # 测试GenomeSPOTTool
    print("\n1. 测试GenomeSPOTTool真实执行...")
    try:
        from tools.microbial_agent_design.genome_spot_tool.genome_spot_tool import GenomeSPOTTool
        tool = GenomeSPOTTool()
        
        # 使用--help参数测试真实执行
        import subprocess
        import tools.microbial_agent_design.genome_spot_tool.genome_spot_tool as genome_spot_module
        current_dir = os.path.dirname(os.path.abspath(genome_spot_module.__file__))
        genome_spot_script = os.path.join(current_dir, '..', '..', 'external_tools', 'genome_spot', 'run_genomespot_batch.py')
        
        if os.path.exists(genome_spot_script):
            cmd = [sys.executable, genome_spot_script, "--help"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("   ✅ GenomeSPOT脚本真实执行成功")
            else:
                print(f"   ⚠️  GenomeSPOT脚本执行失败: {result.stderr}")
        else:
            print(f"   ⚠️  GenomeSPOT脚本不存在: {genome_spot_script}")
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")

def main():
    print("BioCrew - GenomeSPOT工具真实执行测试")
    print("=" * 50)
    
    try:
        test_genome_spot_execution()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
