#!/usr/bin/env python3
"""
工程微生物识别智能体单独测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from tasks.microorganism_identification_task import MicroorganismIdentificationTask

def test_local_data_tools():
    """测试本地数据工具"""
    print("开始测试本地数据工具...")
    print("=" * 30)
    
    try:
        # 测试LocalDataRetriever
        from tools.local_data_retriever import LocalDataRetriever
        data_retriever = LocalDataRetriever()
        
        print("1. 测试LocalDataRetriever工具:")
        # 列出可用污染物
        pollutants = data_retriever.list_available_pollutants()
        print(f"   可用基因数据污染物数量: {len(pollutants['genes_pollutants'])}")
        print(f"   可用微生物数据污染物数量: {len(pollutants['organism_pollutants'])}")
        
        # 测试读取特定污染物数据
        test_pollutant = "Alpha-hexachlorocyclohexane"
        print(f"\n2. 测试读取{test_pollutant}数据:")
        
        gene_data = data_retriever.get_gene_data(test_pollutant)
        if gene_data is not None:
            print(f"   基因数据读取成功: {gene_data.shape}")
        else:
            print("   基因数据读取失败")
        
        organism_data = data_retriever.get_organism_data(test_pollutant)
        if organism_data is not None:
            print(f"   微生物数据读取成功: {organism_data.shape}")
        else:
            print("   微生物数据读取失败")
        
        # 测试多工作表功能
        print(f"\n3. 测试多工作表功能:")
        sheet_names = data_retriever.list_sheet_names(test_pollutant, "gene")
        if sheet_names:
            print(f"   {test_pollutant}基因数据工作表数量: {len(sheet_names)}")
            print(f"   工作表名称: {sheet_names[:3]}...")  # 显示前3个
        
        # 测试读取所有工作表
        all_gene_sheets = data_retriever.get_gene_data_all_sheets(test_pollutant)
        if all_gene_sheets:
            print(f"   成功读取所有工作表，数量: {len(all_gene_sheets)}")
        
        print("\nLocalDataRetriever工具测试完成!")
        
    except Exception as e:
        print(f"LocalDataRetriever工具测试出错: {e}")
        import traceback
        traceback.print_exc()

def test_smart_data_query_tool():
    """测试智能数据查询工具"""
    print("\n开始测试智能数据查询工具...")
    print("=" * 30)
    
    try:
        # 测试SmartDataQueryTool
        from tools.smart_data_query_tool import SmartDataQueryTool
        smart_query = SmartDataQueryTool()
        
        print("1. 测试SmartDataQueryTool工具:")
        
        # 测试查询相关数据
        test_queries = [
            "我们需要处理Alpha-hexachlorocyclohexane污染问题",
            "请分析含有Pentachlorophenol的污水"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   测试查询 {i}: {query}")
            result = smart_query.query_related_data(query)
            if result["status"] == "success":
                print(f"     匹配污染物数量: {len(result['matched_pollutants'])}")
                print(f"     成功查询基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
                print(f"     成功查询微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            else:
                print(f"     查询失败: {result.get('message', '未知错误')}")
        
        # 测试数据摘要功能
        print(f"\n2. 测试数据摘要功能:")
        summary = smart_query.get_data_summary("Alpha-hexachlorocyclohexane")
        if summary["gene_summary"] and "error" not in summary["gene_summary"]:
            print(f"   基因数据摘要: {summary['gene_summary']['shape']}")
        if summary["organism_summary"] and "error" not in summary["organism_summary"]:
            print(f"   微生物数据摘要: {summary['organism_summary']['shape']}")
        
        print("\nSmartDataQueryTool工具测试完成!")
        
    except Exception as e:
        print(f"SmartDataQueryTool工具测试出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("工程微生物识别智能体单独测试")
    print("=" * 30)
    
    # 首先测试本地数据工具
    test_local_data_tools()
    
    # 测试智能数据查询工具
    test_smart_data_query_tool()
    
    # 设置默认测试需求
    default_requirement = "处理含有重金属镉的工业废水"
    
    # 尝试获取用户输入，如果失败则使用默认值
    try:
        user_requirement = input("\n请输入测试用的水质处理需求 (例如: 处理含有重金属镉的工业废水): ") or default_requirement
    except EOFError:
        print("未检测到输入，使用默认测试需求")
        user_requirement = default_requirement
    
    # 验证API密钥是否存在
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，使用DashScope专用方式
    try:
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,  # 使用原始API密钥
            model="openai/qwen3-30b-a3b-instruct-2507",  # 指定openai提供商
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        print("模型连接配置完成")
    except Exception as e:
        print(f"模型初始化失败: {e}")
        return
    
    # 创建工程微生物识别智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    
    # 创建识别任务
    identification_task = MicroorganismIdentificationTask(llm).create_task(
        identification_agent, 
        user_requirement=user_requirement
    )
    
    # 创建测试Crew
    test_crew = Crew(
        agents=[identification_agent],
        tasks=[identification_task],
        verbose=True
    )
    
    # 执行测试
    print("\n开始执行工程微生物识别任务...")
    try:
        result = test_crew.kickoff()
        print("\n识别结果:")
        print(result)
    except Exception as e:
        print(f"执行任务时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

