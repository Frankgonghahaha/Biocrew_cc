#!/usr/bin/env python3
"""
测试功能微生物识别智能体的工具调用和内容完善功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from config.config import Config
from langchain_openai import ChatOpenAI

def test_tool_integration_and_content_enhancement():
    """测试工具集成和内容完善功能"""
    print("=== 测试工具集成和内容完善功能 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    print(f"Agent角色: {agent.role}")
    print(f"Agent目标: {agent.goal}")
    print(f"Agent工具数量: {len(agent.tools)}")
    
    # 显示工具列表
    if agent.tools:
        print("\nAgent工具列表:")
        for i, tool in enumerate(agent.tools):
            print(f"  {i+1}. {tool.name} - {tool.description}")
    else:
        print("\nAgent没有工具")
    
    # 检查工具功能
    tool_names = [tool.name for tool in agent.tools]
    
    # 检查必需的工具
    required_tools = [
        "本地数据读取工具",
        "智能数据查询工具",
        "强制本地数据查询工具"
    ]
    
    print("\n必需工具检查:")
    all_required_tools_present = True
    for required_tool in required_tools:
        if required_tool in tool_names:
            print(f"  ✓ {required_tool}")
        else:
            print(f"  ✗ {required_tool} (缺失)")
            all_required_tools_present = False
    
    if not all_required_tools_present:
        print("  警告: 某些必需工具缺失，可能影响Agent功能")
    
    # 检查Agent背景故事中的工具使用规范
    backstory = agent.backstory
    
    print("\n工具使用规范检查:")
    tool_usage_patterns = [
        'mandatory_query._run("query_required_data", query_text="用户需求")',
        'data_retriever._run("get_organism_data", pollutant_name="aldrin")',
        'data_retriever._run("get_gene_data", pollutant_name="aldrin")',
        'smart_query._run("query_related_data", query_text="如何降解含有aldrin的废水？")',
        'mandatory_query._run("assess_data_integrity", query_text="用户需求")',
        'smart_query._run("query_external_databases", query_text="aldrin")'
    ]
    
    for pattern in tool_usage_patterns:
        if pattern in backstory:
            print(f"  ✓ {pattern}")
        else:
            print(f"  - {pattern} (未在背景故事中明确说明)")
    
    # 检查数据完整性评估相关内容
    print("\n数据完整性评估检查:")
    integrity_patterns = [
        "数据完整性评估",
        "完整性评分低于70",
        "评估结果的推荐"
    ]
    
    for pattern in integrity_patterns:
        if pattern in backstory:
            print(f"  ✓ 包含'{pattern}'")
        else:
            print(f"  ✗ 缺少'{pattern}'")
    
    # 检查筛选原则
    print("\n筛选原则检查:")
    screening_principles = [
        "互补指数＞竞争指数",
        "重点关注微生物对目标污染物的降解能力",
        "当基因数据缺失时",
        "数据完整性和可信度的评估"
    ]
    
    for principle in screening_principles:
        if principle in backstory:
            print(f"  ✓ 包含'{principle}'")
        else:
            print(f"  ✗ 缺少'{principle}'")
    
    print("\n工具集成和内容完善功能测试完成。")

def test_agent_data_query_capabilities():
    """测试Agent数据查询能力"""
    print("\n=== 测试Agent数据查询能力 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 检查背景故事中的数据查询策略
    backstory = agent.backstory
    
    data_query_strategies = [
        "优先使用本地数据目录",
        "本地数据情况",
        "数据文件支持多工作表结构",
        "系统支持的污染物数据",
        "智能数据查询能力"
    ]
    
    print("数据查询策略检查:")
    for strategy in data_query_strategies:
        if strategy in backstory:
            print(f"  ✓ 包含'{strategy}'")
        else:
            print(f"  ✗ 缺少'{strategy}'")
    
    # 检查外部数据库工具信息
    print("\n外部数据库工具检查:")
    database_tools_info = [
        "EnviPath和KEGG数据库访问工具",
        "外部数据库访问工具",
        "数据查询协调器",
        "工具协调器"
    ]
    
    for info in database_tools_info:
        if info in backstory:
            print(f"  ✓ 包含'{info}'")
        else:
            print(f"  ✗ 缺少'{info}'")
    
    print("\nAgent数据查询能力测试完成。")

def analyze_agent_tool_coordination():
    """分析Agent工具协调"""
    print("\n=== 分析Agent工具协调 ===")
    
    # 创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建Agent实例
    agent_instance = EngineeringMicroorganismIdentificationAgent(llm)
    agent = agent_instance.create_agent()
    
    # 分析工具协调逻辑
    backstory = agent.backstory
    
    coordination_aspects = [
        "工具使用规范",
        "数据查询顺序",
        "数据完整性处理",
        "错误处理机制",
        "结果整合策略"
    ]
    
    print("工具协调方面分析:")
    for aspect in coordination_aspects:
        if aspect in backstory:
            print(f"  ✓ 包含'{aspect}'相关说明")
        else:
            print(f"  - 缺少'{aspect}'相关说明")
    
    # 检查工具调用的依赖关系
    print("\n工具调用依赖关系检查:")
    dependency_patterns = [
        "必须使用MandatoryLocalDataQueryTool来确保查询本地数据",
        "当本地数据不足时，可以使用智能数据查询工具获取补充信息",
        "在分析和回复过程中，必须明确体现查询到的具体数据"
    ]
    
    for pattern in dependency_patterns:
        if pattern in backstory:
            print(f"  ✓ {pattern}")
        else:
            print(f"  - {pattern}")
    
    print("\nAgent工具协调分析完成。")

if __name__ == "__main__":
    print("开始测试功能微生物识别智能体的工具调用和内容完善功能...")
    test_tool_integration_and_content_enhancement()
    test_agent_data_query_capabilities()
    analyze_agent_tool_coordination()
    print("\n=== 所有测试完成 ===")