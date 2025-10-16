#!/usr/bin/env python3
"""
验证工具是否真正被调用的测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from langchain_openai import ChatOpenAI
from crewai import Crew, Process
import dashscope

def get_llm():
    """获取LLM实例"""
    dashscope.api_key = Config.QWEN_API_KEY
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    return llm

def test_tool_call_verification():
    """
    验证工具是否真正被调用的测试
    """
    print("开始验证微生物菌剂设计智能体工具的真实调用...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入菌剂设计智能体
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    
    # 创建菌剂设计智能体
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    # 显示智能体可用工具
    print(f"智能体可用工具数量: {len(design_agent.tools)}")
    
    # 列出所有可用工具
    print("\n智能体可用工具列表:")
    tool_names = []
    for i, tool in enumerate(design_agent.tools):
        print(f"{i+1}. {tool.name}: {tool.description}")
        tool_names.append(tool.name)
    
    # 验证特定工具是否存在
    required_tools = ["CtfbaTool", "GenomeSPOTTool", "DLkcatTool", "CarvemeTool", "PhylomintTool"]
    missing_tools = []
    for tool_name in required_tools:
        if tool_name not in tool_names:
            missing_tools.append(tool_name)
    
    if missing_tools:
        print(f"\n警告：以下必需工具缺失: {missing_tools}")
    else:
        print(f"\n所有必需工具均已正确加载")
    
    # 创建验证任务 - 使用一个非常具体的任务，需要真实工具调用才能完成
    from crewai import Task
    
    verification_task = Task(
        description="""
        请使用ctFBA工具计算以下微生物群落对苯酚的代谢通量：
        
        微生物群落组成：
        1. Pseudomonas putida (占比40%)
        2. Bacillus subtilis (占比30%)
        3. Rhodococcus erythropolis (占比30%)
        
        目标污染物：苯酚 (phenol)
        权衡系数：0.7
        
        要求：
        1. 必须真实调用ctFBA工具进行计算
        2. 返回具体的代谢通量数值结果
        3. 提供计算过程说明
        4. 如果工具调用失败，请明确指出错误信息
        """,
        expected_output="""
        包含以下内容的详细报告：
        1. 工具调用确认（是否真实调用了ctFBA工具）
        2. 代谢通量计算结果（具体数值）
        3. 计算过程说明
        4. 如果有错误，提供详细错误信息
        """,
        agent=design_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    verification_crew = Crew(
        agents=[design_agent],
        tasks=[verification_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行工具调用验证任务...")
    result = verification_crew.kickoff()
    
    print("\n工具调用验证完成，结果如下:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # 分析结果中调用的工具
    result_str = str(result)
    called_tools = []
    
    for tool_name in required_tools:
        if tool_name.lower() in result_str.lower():
            called_tools.append(tool_name)
    
    print(f"\n检测到调用的工具: {called_tools}")
    print(f"未检测到的工具: {list(set(required_tools) - set(called_tools))}")
    
    return result

def main():
    print("BioCrew - 工具调用验证测试")
    print("=" * 50)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        # 执行测试
        test_tool_call_verification()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()