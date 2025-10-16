#!/usr/bin/env python3
"""
测试所有菌剂设计工具的调用
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

def test_all_design_tools():
    """
    测试所有菌剂设计工具的调用
    """
    print("开始测试所有菌剂设计工具的调用...")
    
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
    required_tools = [
        "GenomeSPOTTool", 
        "DLkcatTool", 
        "CarvemeTool", 
        "PhylomintTool", 
        "CtfbaTool"
    ]
    
    missing_tools = []
    for tool_name in required_tools:
        if tool_name not in tool_names:
            missing_tools.append(tool_name)
    
    if missing_tools:
        print(f"\n警告：以下必需工具缺失: {missing_tools}")
    else:
        print(f"\n所有必需工具均已正确加载")
    
    # 创建测试任务 - 测试所有工具的调用
    from crewai import Task
    
    test_task = Task(
        description="""
        请分析以下微生物对目标污染物的降解能力，并使用所有可用的专业工具：
        
        微生物列表：
        1. Pseudomonas putida
        2. Bacillus subtilis
        
        目标污染物：苯酚 (phenol)
        
        请完成以下任务：
        1. 使用GenomeSPOT工具分析这些微生物的环境适应性
        2. 使用DLkcat工具预测酶催化速率
        3. 使用Carveme工具构建代谢模型
        4. 使用Phylomint工具分析微生物互作关系
        5. 使用ctFBA工具计算代谢通量
        6. 综合所有工具的分析结果，提供详细报告
        """,
        expected_output="""
        包含以下内容的详细报告：
        1. 每个工具的调用确认
        2. 各工具的分析结果摘要
        3. 综合评估结论
        """,
        agent=design_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    test_crew = Crew(
        agents=[design_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行工具调用测试任务...")
    result = test_crew.kickoff()
    
    print("\n工具调用测试完成，结果如下:")
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

def test_individual_tools():
    """
    单独测试每个工具的基本功能
    """
    print("\n开始单独测试每个工具的基本功能...")
    
    # 测试GenomeSPOT工具
    try:
        from tools.microbial_agent_design.genome_spot_tool.genome_spot_tool import GenomeSPOTTool
        genome_spot_tool = GenomeSPOTTool()
        print("✓ GenomeSPOT工具加载成功")
    except Exception as e:
        print(f"✗ GenomeSPOT工具加载失败: {e}")
    
    # 测试DLkcat工具
    try:
        from tools.microbial_agent_design.dlkcat_tool.dlkcat_tool import DLkcatTool
        dlkcat_tool = DLkcatTool()
        print("✓ DLkcat工具加载成功")
    except Exception as e:
        print(f"✗ DLkcat工具加载失败: {e}")
    
    # 测试Carveme工具
    try:
        from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
        carveme_tool = CarvemeTool()
        print("✓ Carveme工具加载成功")
    except Exception as e:
        print(f"✗ Carveme工具加载失败: {e}")
    
    # 测试Phylomint工具
    try:
        from tools.microbial_agent_design.phylomint_tool.phylomint_tool import PhylomintTool
        phylomint_tool = PhylomintTool()
        print("✓ Phylomint工具加载成功")
    except Exception as e:
        print(f"✗ Phylomint工具加载失败: {e}")
    
    # 测试Ctfba工具
    try:
        from tools.microbial_agent_design.ctfba_tool.ctfba_tool import CtfbaTool
        ctfba_tool = CtfbaTool()
        print("✓ Ctfba工具加载成功")
    except Exception as e:
        print(f"✗ Ctfba工具加载失败: {e}")

def main():
    print("BioCrew - 所有菌剂设计工具调用测试")
    print("=" * 50)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        # 单独测试工具加载
        test_individual_tools()
        
        # 测试工具调用
        test_all_design_tools()
        print("\n综合测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()