#!/usr/bin/env python3
"""
测试ctFBA工具的实现情况
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ctfba_implementation():
    """测试ctFBA工具的实现情况"""
    print("开始测试ctFBA工具的实现情况...")
    
    # 测试CtfbaTool
    print("\n1. 测试CtfbaTool实现...")
    try:
        from tools.microbial_agent_design.ctfba_tool.ctfba_tool import CtfbaTool
        tool = CtfbaTool()
        
        print("   工具名称:", tool.name)
        print("   工具描述:", tool.description)
        
        # 查看工具的_run方法实现
        import inspect
        run_method = inspect.getsource(tool._run)
        if "模拟ctFBA计算过程" in run_method:
            print("   ⚠️  工具使用模拟实现")
        else:
            print("   ✅ 工具使用真实实现")
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")

def main():
    print("BioCrew - ctFBA工具实现测试")
    print("=" * 50)
    
    try:
        test_ctfba_implementation()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
