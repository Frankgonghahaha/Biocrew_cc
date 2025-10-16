#!/usr/bin/env python3
"""
实际测试脚本 - 验证工具是否能真实执行
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_actual_tool_execution():
    """测试工具的真实执行"""
    print("开始测试工具的真实执行...")
    
    # 测试DLkcatTool
    print("\n1. 测试DLkcatTool真实执行...")
    try:
        from tools.microbial_agent_design.dlkcat_tool.dlkcat_tool import DLkcatTool
        tool = DLkcatTool()
        
        # 使用--help参数测试真实执行
        result = tool._run(
            script_path="--help",
            file_path="--help"
        )
        print(f"   结果状态: {result['status']}")
        if "simulated" in str(result):
            print("   ⚠️  仍然使用模拟执行")
        else:
            print("   ✅ 真实执行")
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
    
    # 测试CarvemeTool
    print("\n2. 测试CarvemeTool真实执行...")
    try:
        from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
        tool = CarvemeTool()
        
        # 使用--help参数测试真实执行
        result = tool._run(
            input_path="--help",
            output_path="/tmp"
        )
        print(f"   结果状态: {result['status']}")
        if "simulated" in str(result):
            print("   ⚠️  仍然使用模拟执行")
        else:
            print("   ✅ 真实执行")
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
    
    # 测试PhylomintTool
    print("\n3. 测试PhylomintTool真实执行...")
    try:
        from tools.microbial_agent_design.phylomint_tool.phylomint_tool import PhylomintTool
        tool = PhylomintTool()
        
        # 使用--help参数测试真实执行（不检查输出文件）
        import subprocess
        import tools.microbial_agent_design.phylomint_tool.phylomint_tool as phylomint_module
        current_dir = os.path.dirname(os.path.abspath(phylomint_module.__file__))
        phylomint_script = os.path.join(current_dir, '..', '..', 'external_tools', 'phylomint', 'run_phylomint.py')
        
        cmd = [sys.executable, phylomint_script, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Phylomint脚本真实执行成功")
        else:
            print(f"   ⚠️  Phylomint脚本执行失败: {result.stderr}")
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")

def main():
    print("BioCrew - 工具真实执行测试")
    print("=" * 50)
    
    try:
        test_actual_tool_execution()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()