#!/usr/bin/env python3
"""
测试菌剂评估智能体工具调用能力

该脚本测试微生物菌剂评估智能体是否能够根据任务需求，
自主调用所需的各类工具，包括：
1. 代谢反应填充工具 (ReactionAdditionTool)
2. 培养基推荐工具 (MediumRecommendationTool)
3. ctFBA工具 (CtfbaTool)
4. 核心评估工具 (EvaluationTool)
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

def test_microbial_agent_evaluation_tools():
    """
    测试微生物菌剂评估智能体的工具调用能力
    """
    print("开始测试微生物菌剂评估智能体的工具调用能力...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入菌剂评估智能体
    from agents.microbial_agent_evaluation_agent import MicrobialAgentEvaluationAgent
    
    # 创建菌剂评估智能体
    evaluation_agent = MicrobialAgentEvaluationAgent(llm).create_agent()
    
    # 显示智能体信息和可用工具
    print(f"智能体角色: {evaluation_agent.role}")
    print(f"智能体目标: {evaluation_agent.goal}")
    print(f"智能体可用工具数量: {len(evaluation_agent.tools)}")
    
    # 列出所有可用工具
    print("\n智能体可用工具列表:")
    for i, tool in enumerate(evaluation_agent.tools):
        print(f"{i+1}. {tool.name}: {tool.description}")
    
    # 检查必需的工具是否都已加载
    tool_names = [tool.name for tool in evaluation_agent.tools]
    required_tools = ["ReactionAdditionTool", "MediumRecommendationTool", "CtfbaTool", "EvaluationTool"]
    
    print("\n必需工具检查:")
    missing_tools = []
    for tool in required_tools:
        if tool in tool_names:
            print(f"✓ {tool} 已正确加载")
        else:
            print(f"✗ {tool} 未加载")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n警告: 以下必需工具未加载: {missing_tools}")
    else:
        print("\n✓ 所有必需工具均已正确加载")
    
    # 创建测试任务
    from crewai import Task
    
    test_task = Task(
        description="""
        请根据以下微生物菌剂设计方案进行综合评估：
        
        菌剂设计方案：
        1. 功能微生物: Pseudomonas putida (占比40%)
        2. 代谢互补微生物: Bacillus subtilis (占比30%)
        3. 代谢互补微生物: Rhodococcus erythropolis (占比30%)
        
        目标污染物：苯酚 (phenol)
        水质净化目标：苯酚浓度从100mg/L降至10mg/L以下
        污水厂背景：常规市政污水处理厂，温度25°C，pH 7.0
        
        请完成以下评估任务：
        1. 使用代谢反应填充工具为模型添加必要的代谢反应
        2. 使用培养基推荐工具生成推荐培养基
        3. 使用ctFBA工具计算菌剂的实际代谢通量和生长率
        4. 分析菌剂在生物净化效果和群落生态特性方面的表现
        5. 重点关注群落稳定性和结构稳定性是否达到标准
        6. 提供详细的评估报告
        """,
        expected_output="""
        完整的菌剂评估报告，包括：
        1. 各维度评分（满分10分）
        2. 核心标准评估结果（群落稳定性和结构稳定性）
        3. 培养基推荐结果
        4. ctFBA计算结果（生长率、代谢通量、稳定性指标等）
        5. 明确的决策建议（通过或回退重新识别）
        6. 如果需要回退，提供具体的改进建议
        7. 降解速率计算结果
        8. 代谢性能详细分析
        9. 代谢反应添加结果
        """,
        agent=evaluation_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    evaluation_crew = Crew(
        agents=[evaluation_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行菌剂评估任务...")
    result = evaluation_crew.kickoff()
    
    print("\n任务执行完成，结果如下:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return result

def main():
    print("BioCrew - 微生物菌剂评估智能体工具调用能力测试")
    print("=" * 50)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        test_microbial_agent_evaluation_tools()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()