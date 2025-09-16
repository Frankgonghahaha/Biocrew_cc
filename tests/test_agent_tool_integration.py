#!/usr/bin/env python3
"""
测试Agent和工具之间的协调
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool
from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool
from tools.data_output_coordinator import DataOutputCoordinator
from config.config import Config
from langchain_openai import ChatOpenAI

def test_agent_tool_integration():
    """测试Agent和工具之间的集成"""
    print("=== 测试Agent和工具之间的集成 ===")
    
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
    print(f"Agent工具数量: {len(agent.tools)}")
    
    # 验证所有工具都已正确集成
    tool_names = [tool.name for tool in agent.tools]
    expected_tools = [
        "本地数据读取工具",
        "智能数据查询工具",
        "强制本地数据查询工具",
        "数据输出协调器"
    ]
    
    print("\n工具集成检查:")
    all_tools_present = True
    for expected_tool in expected_tools:
        if expected_tool in tool_names:
            print(f"  ✓ {expected_tool}")
        else:
            print(f"  ✗ {expected_tool} (缺失)")
            all_tools_present = False
    
    if all_tools_present:
        print("\n✓ 所有工具都已正确集成到Agent中")
    else:
        print("\n✗ 某些工具缺失")
    
    print("\nAgent和工具集成测试完成。")

def test_tool_coordination_workflow():
    """测试工具协调工作流"""
    print("\n=== 测试工具协调工作流 ===")
    
    # 创建各个工具实例
    try:
        data_retriever = LocalDataRetriever(base_path=".")
        smart_query = SmartDataQueryTool(base_path=".")
        mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
        output_coordinator = DataOutputCoordinator()
        
        print("✓ 所有工具实例创建成功")
        
        # 测试工具链式调用
        print("\n测试工具链式调用:")
        
        # 1. 使用强制本地数据查询工具查询必需数据
        print("  1. 使用强制本地数据查询工具查询必需数据...")
        mandatory_result = mandatory_query._run("query_required_data", query_text="处理含有aldrin的废水")
        print(f"     状态: {mandatory_result.get('status', '未知')}")
        
        # 2. 使用智能数据查询工具获取补充信息
        print("  2. 使用智能数据查询工具获取补充信息...")
        smart_result = smart_query._run("query_related_data", query_text="aldrin降解微生物")
        print(f"     状态: {smart_result.get('status', '未知')}")
        
        # 3. 使用数据输出协调器整合数据
        print("  3. 使用数据输出协调器整合数据...")
        if mandatory_result.get('status') == 'success' and smart_result.get('status') == 'success':
            combined_result = output_coordinator._run(
                "combine_data", 
                local_data=mandatory_result, 
                external_data=smart_result
            )
            print(f"     状态: {combined_result.get('status', '未知')}")
            print(f"     数据源数量: {combined_result.get('sources_count', 0)}")
        else:
            print("     跳过数据整合（前序步骤失败）")
        
        # 4. 使用数据输出协调器生成报告
        print("  4. 使用数据输出协调器生成报告...")
        sections = [
            {"title": "本地数据查询结果", "content": str(mandatory_result)},
            {"title": "智能查询结果", "content": str(smart_result)}
        ]
        report_result = output_coordinator._run(
            "generate_report", 
            title="功能微生物识别综合报告", 
            sections=sections
        )
        print(f"     状态: {report_result.get('status', '未知')}")
        if report_result.get('status') == 'success':
            print(f"     报告章节数: {report_result.get('statistics', {}).get('section_count', 0)}")
        
        print("\n✓ 工具协调工作流测试完成")
        
    except Exception as e:
        print(f"✗ 工具实例创建或调用失败: {e}")
    
    print("\n工具协调工作流测试完成。")

def test_data_integrity_assessment():
    """测试数据完整性评估"""
    print("\n=== 测试数据完整性评估 ===")
    
    try:
        # 创建工具实例
        mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
        output_coordinator = DataOutputCoordinator()
        
        # 使用强制本地数据查询工具评估数据完整性
        print("使用强制本地数据查询工具评估数据完整性...")
        integrity_result = mandatory_query._run("assess_data_integrity", query_text="aldrin")
        print(f"  状态: {integrity_result.get('status', '未知')}")
        if integrity_result.get('status') == 'success':
            score = integrity_result.get('data_integrity_score', 0)
            print(f"  完整性评分: {score:.2f}")
            if 'recommendations' in integrity_result:
                print("  建议:")
                for rec in integrity_result['recommendations'][:2]:  # 只显示前2个建议
                    print(f"    {rec}")
        
        # 使用数据输出协调器评估数据完整性
        print("\n使用数据输出协调器评估数据完整性...")
        sample_data = {
            "microorganisms": ["Bacillus subtilis"],
            "genes": None,
            "complementarity_index": 0.85
        }
        required_fields = ["microorganisms", "genes", "complementarity_index"]
        completeness_result = output_coordinator._run(
            "assess_completeness", 
            data=sample_data, 
            required_fields=required_fields
        )
        print(f"  状态: {completeness_result.get('status', '未知')}")
        if completeness_result.get('status') == 'success':
            score = completeness_result.get('completeness_score', 0)
            print(f"  完整性评分: {score:.2f}%")
            print(f"  存在字段: {completeness_result.get('present_fields', [])}")
            print(f"  缺失字段: {completeness_result.get('missing_fields', [])}")
            if 'recommendations' in completeness_result:
                print("  建议:")
                for rec in completeness_result['recommendations']:
                    print(f"    {rec}")
        
        print("\n✓ 数据完整性评估测试完成")
        
    except Exception as e:
        print(f"✗ 数据完整性评估测试失败: {e}")
    
    print("\n数据完整性评估测试完成。")

def test_output_formatting():
    """测试输出格式化功能"""
    print("\n=== 测试输出格式化功能 ===")
    
    try:
        # 创建数据输出协调器实例
        output_coordinator = DataOutputCoordinator()
        
        # 测试数据
        sample_data = {
            "microorganisms": ["Bacillus subtilis", "Pseudomonas putida"],
            "genes": ["degA", "degB"],
            "complementarity_index": 0.85,
            "competition_index": 0.32
        }
        
        # 测试不同格式的输出
        formats = ["json", "table", "list"]
        for format_type in formats:
            print(f"\n测试{format_type.upper()}格式化:")
            result = output_coordinator._run(
                "format_output", 
                data=sample_data, 
                format_type=format_type
            )
            print(f"  状态: {result.get('status', '未知')}")
            if result.get('status') == 'success':
                print(f"  格式类型: {result.get('format_type', '未知')}")
                if format_type == "json":
                    print("  格式化数据 (前100字符):")
                    formatted_data = result.get('formatted_data', '')
                    print(f"    {formatted_data[:100]}{'...' if len(formatted_data) > 100 else ''}")
                elif format_type == "table":
                    print("  格式化数据:")
                    formatted_data = result.get('formatted_data', '')
                    lines = formatted_data.split('\n')
                    for line in lines[:5]:  # 只显示前5行
                        print(f"    {line}")
                else:  # list format
                    print("  格式化数据 (前3项):")
                    formatted_data = result.get('formatted_data', [])
                    for item in formatted_data[:3]:
                        print(f"    {item}")
        
        print("\n✓ 输出格式化功能测试完成")
        
    except Exception as e:
        print(f"✗ 输出格式化功能测试失败: {e}")
    
    print("\n输出格式化功能测试完成。")

if __name__ == "__main__":
    print("开始测试Agent和工具之间的协调...")
    test_agent_tool_integration()
    test_tool_coordination_workflow()
    test_data_integrity_assessment()
    test_output_formatting()
    print("\n=== 所有测试完成 ===")