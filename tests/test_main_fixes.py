#!/usr/bin/env python3
"""
测试main.py修复后的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from crewai import Process
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

def test_main_imports():
    """测试main.py的导入是否正常"""
    print("测试main.py导入...")
    
    try:
        # 测试导入
        from main import (
            get_user_input,
            get_processing_mode,
            analyze_evaluation_result,
            run_autonomous_workflow,
            run_dynamic_workflow,
            main
        )
        print("✓ 所有函数导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_crew_configuration():
    """测试Crew配置是否正确"""
    print("\n测试Crew配置...")
    
    try:
        # 模拟LLM初始化
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,
            model="openai/qwen3-30b-a3b-instruct-2507",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        
        # 测试自主工作流的Crew配置
        from main import run_autonomous_workflow
        import inspect
        
        # 获取函数源代码
        source = inspect.getsource(run_autonomous_workflow)
        
        # 检查关键配置
        if "manager_agent=coordination_agent" in source:
            print("✓ 分层处理模式配置正确")
        else:
            print("✗ 缺少manager_agent配置")
            return False
            
        if "Process.hierarchical" in source:
            print("✓ 使用了分层处理模式")
        else:
            print("✗ 未使用分层处理模式")
            return False
            
        # 检查管理器智能体是否不在agents列表中
        lines = source.split('\n')
        in_agents_list = False
        coordination_agent_in_list = False
        
        for line in lines:
            if "agents=[" in line:
                in_agents_list = True
            if in_agents_list and "coordination_agent" in line:
                coordination_agent_in_list = True
            if in_agents_list and "]" in line and "[" in line:
                in_agents_list = False
            elif in_agents_list and "]" in line:
                in_agents_list = False
                
        if not coordination_agent_in_list:
            print("✓ 管理器智能体未包含在agents列表中")
        else:
            print("✗ 管理器智能体错误地包含在agents列表中")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Crew配置测试失败: {e}")
        return False

def test_evaluation_analysis():
    """测试评估结果分析功能"""
    print("\n测试评估结果分析...")
    
    try:
        from main import analyze_evaluation_result
        from tools.evaluation_tool import EvaluationTool
        
        # 测试评估工具的可用性
        eval_tool = EvaluationTool()
        
        # 检查是否有analyze_evaluation_result方法
        if hasattr(eval_tool, 'analyze_evaluation_result'):
            print("✓ EvaluationTool包含analyze_evaluation_result方法")
        else:
            print("✗ EvaluationTool缺少analyze_evaluation_result方法")
            return False
            
        return True
    except Exception as e:
        print(f"✗ 评估结果分析测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试main.py修复后的功能")
    print("=" * 40)
    
    tests = [
        test_main_imports,
        test_crew_configuration,
        test_evaluation_analysis
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！main.py修复成功。")
    else:
        print("❌ 部分测试失败，请检查上述错误信息。")