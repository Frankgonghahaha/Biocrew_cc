#!/usr/bin/env python3
"""
测试菌剂设计智能体对其所需工具的自主调用能力

该脚本测试微生物菌剂设计智能体是否能够根据任务需求，
自主调用所需的各类工具，包括：
1. 数据库查询工具（污染物、基因、微生物数据）
2. 专业设计工具（GenomeSPOT、DLkcat、Carveme、Phylomint、ctFBA）
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 加载环境变量
load_dotenv()

from config.config import Config
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
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

def test_microbial_agent_design_tool_usage():
    """
    测试微生物菌剂设计智能体的工具调用能力
    """
    print("开始测试微生物菌剂设计智能体的工具调用能力...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入菌剂设计智能体
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    
    # 创建菌剂设计智能体
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    # 显示智能体信息和可用工具
    print(f"智能体角色: {design_agent.role}")
    print(f"智能体目标: {design_agent.goal}")
    print(f"智能体可用工具数量: {len(design_agent.tools)}")
    
    # 列出所有可用工具
    print("\n智能体可用工具列表:")
    for i, tool in enumerate(design_agent.tools):
        print(f"{i+1}. {tool.name}: {tool.description}")
    
    # 创建测试任务
    from crewai import Task
    
    test_task = Task(
        description="""
        请根据以下工程微生物组设计功能微生物菌剂配方：
        
        工程微生物组信息：
        1. 功能微生物: Pseudomonas putida (占比40%)
        2. 代谢互补微生物: Bacillus subtilis (占比30%)
        3. 代谢互补微生物: Rhodococcus erythropolis (占比30%)
        
        目标污染物：苯酚 (phenol)
        
        请完成以下任务：
        1. 分析这些微生物的降解能力
        2. 使用ctFBA工具计算代谢通量
        3. 使用GenomeSPOT工具分析环境适应性
        4. 使用DLkcat工具预测酶催化速率
        5. 使用Carveme工具构建代谢模型
        6. 使用Phylomint工具分析微生物互作关系
        7. 提供最优菌剂设计方案
        """,
        expected_output="""
        完整的菌剂设计方案，包括：
        1. 菌剂组成（微生物种类和比例）
        2. 各工具的分析结果
        3. 设计原理说明
        4. 稳定性保障措施
        5. 预期的净化效果
        6. 代谢通量计算结果
        """,
        agent=design_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    design_crew = Crew(
        agents=[design_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行菌剂设计任务...")
    result = design_crew.kickoff()
    
    print("\n任务执行完成，结果如下:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return result

def main():
    print("BioCrew - 微生物菌剂设计智能体工具调用能力测试")
    print("=" * 50)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        test_microbial_agent_design_tool_usage()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()