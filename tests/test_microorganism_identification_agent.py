#!/usr/bin/env python3
"""
功能微生物识别智能体单元测试脚本
专注于测试智能体的核心功能和工具调用
"""

import sys
import os

# 确保在项目根目录运行
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
from tasks.microorganism_identification_task import MicroorganismIdentificationTask

def test_agent_creation():
    """测试智能体创建功能"""
    print("测试1: 智能体创建测试")
    print("=" * 30)
    
    try:
        # 初始化LLM模型
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,
            model="openai/qwen3-30b-a3b-instruct-2507",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        
        # 创建工程微生物识别智能体
        agent_creator = EngineeringMicroorganismIdentificationAgent(llm)
        identification_agent = agent_creator.create_agent()
        
        # 验证智能体创建成功
        assert identification_agent is not None, "智能体创建失败"
        assert identification_agent.role == "功能微生物组识别专家", "智能体角色不正确"
        assert len(identification_agent.tools) > 0, "智能体工具未正确加载"
        
        print("✓ 智能体创建成功")
        print(f"✓ 智能体角色: {identification_agent.role}")
        print(f"✓ 工具数量: {len(identification_agent.tools)}")
        
        # 显示工具名称
        tool_names = [tool.name for tool in identification_agent.tools]
        print(f"✓ 工具列表: {', '.join(tool_names)}")
        
        return True
    except Exception as e:
        print(f"✗ 智能体创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_creation():
    """测试任务创建功能"""
    print("\n测试2: 任务创建测试")
    print("=" * 30)
    
    try:
        # 初始化LLM模型
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,
            model="openai/qwen3-30b-a3b-instruct-2507",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        
        # 创建任务
        task_creator = MicroorganismIdentificationTask(llm)
        
        # 创建一个模拟的智能体
        mock_agent = Agent(
            role="测试智能体",
            goal="测试任务创建",
            backstory="这是一个用于测试的模拟智能体"
        )
        
        # 创建任务
        task = task_creator.create_task(
            mock_agent,
            user_requirement="处理含有重金属镉的工业废水"
        )
        
        # 验证任务创建成功
        assert task is not None, "任务创建失败"
        assert "处理含有重金属镉的工业废水" in task.description, "任务描述未包含用户需求"
        assert "工程微生物组识别报告" in task.expected_output, "任务期望输出不正确"
        
        print("✓ 任务创建成功")
        print(f"✓ 任务描述长度: {len(task.description)} 字符")
        print(f"✓ 期望输出长度: {len(task.expected_output)} 字符")
        
        return True
    except Exception as e:
        print(f"✗ 任务创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_local_data_tools():
    """测试本地数据工具"""
    print("\n测试3: 本地数据工具测试")
    print("=" * 30)
    
    try:
        # 测试LocalDataRetriever
        from tools.local_data_retriever import LocalDataRetriever
        data_retriever = LocalDataRetriever(base_path=".")
        
        print("1. LocalDataRetriever工具测试:")
        # 列出可用污染物
        pollutants = data_retriever.list_available_pollutants()
        print(f"   ✓ 可用基因数据污染物数量: {len(pollutants['genes_pollutants'])}")
        print(f"   ✓ 可用微生物数据污染物数量: {len(pollutants['organism_pollutants'])}")
        
        # 测试读取特定污染物数据
        test_cases = [
            ("Alpha-hexachlorocyclohexane", "完整数据测试"),
            ("Endosulfan", "仅有基因数据测试"),
            ("Aldrin", "仅有微生物数据测试")
        ]
        
        for pollutant, description in test_cases:
            print(f"\n   {description} ({pollutant}):")
            
            # 测试基因数据
            try:
                gene_data = data_retriever.get_gene_data(pollutant)
                if gene_data is not None:
                    print(f"     ✓ 基因数据读取成功: {gene_data.shape}")
                else:
                    print("     - 基因数据不存在")
            except Exception as e:
                print(f"     - 基因数据读取异常: {e}")
            
            # 测试微生物数据
            try:
                organism_data = data_retriever.get_organism_data(pollutant)
                if organism_data is not None:
                    print(f"     ✓ 微生物数据读取成功: {organism_data.shape}")
                else:
                    print("     - 微生物数据不存在")
            except Exception as e:
                print(f"     - 微生物数据读取异常: {e}")
        
        # 测试智能数据查询工具
        print(f"\n2. SmartDataQueryTool工具测试:")
        from tools.smart_data_query_tool import SmartDataQueryTool
        smart_query = SmartDataQueryTool(base_path=".")
        
        test_queries = [
            ("我们需要处理Alpha-hexachlorocyclohexane污染问题", "完整数据查询"),
            ("请分析含有Endosulfan的农药废水", "基因数据查询"),
            ("处理含有Aldrin的有机氯农药废水", "微生物数据查询")
        ]
        
        for query, description in test_queries:
            print(f"\n   {description}:")
            print(f"     查询文本: {query}")
            result = smart_query.query_related_data(query)
            if result["status"] == "success":
                print(f"     ✓ 匹配污染物数量: {len(result['matched_pollutants'])}")
                print(f"     ✓ 成功查询基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
                print(f"     ✓ 成功查询微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            else:
                print(f"     - 查询结果: {result.get('message', '未知错误')}")
        
        print("\n✓ 本地数据工具测试完成!")
        return True
        
    except Exception as e:
        print(f"✗ 本地数据工具测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mandatory_local_data_query_tool():
    """测试强制本地数据查询工具"""
    print("\n测试4: 强制本地数据查询工具测试")
    print("=" * 30)
    
    try:
        from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool
        mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
        
        print("1. 工具初始化测试:")
        print("   ✓ 工具初始化成功")
        
        print("\n2. 可用污染物摘要测试:")
        summary_result = mandatory_query.get_available_pollutants_summary()
        print(f"   ✓ 基因污染物数量: {summary_result['genes_pollutants_count']}")
        print(f"   ✓ 微生物污染物数量: {summary_result['organism_pollutants_count']}")
        
        print("\n3. 强制数据查询测试:")
        test_queries = [
            "处理含有Alpha-hexachlorocyclohexane的有机污染物废水",
            "分析Endosulfan农药污染情况",
            "识别Aldrin降解微生物"
        ]
        
        for query in test_queries:
            print(f"\n   查询: {query}")
            result = mandatory_query.query_required_data(query)
            if result.get("status") == "success":
                print(f"     ✓ 查询成功")
                print(f"     ✓ 匹配污染物: {result.get('matched_pollutants', [])}")
            else:
                print(f"     - 查询结果: {result.get('message', '未知错误')}")
        
        print("\n✓ 强制本地数据查询工具测试完成!")
        return True
        
    except Exception as e:
        print(f"✗ 强制本地数据查询工具测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_integrity_handling():
    """测试数据完整性处理能力"""
    print("\n测试5: 数据完整性处理能力测试")
    print("=" * 30)
    
    try:
        # 测试SmartDataQueryTool的数据完整性处理
        from tools.smart_data_query_tool import SmartDataQueryTool
        smart_query = SmartDataQueryTool(base_path=".")
        
        print("1. 完整数据处理测试 (Alpha-hexachlorocyclohexane):")
        result = smart_query.query_related_data("处理含有Alpha-hexachlorocyclohexane的废水")
        if result["status"] == "success":
            pollutant = result["matched_pollutants"][0] if result["matched_pollutants"] else None
            if pollutant:
                gene_data = result["gene_data"].get(pollutant, {})
                organism_data = result["organism_data"].get(pollutant, {})
                
                print(f"   ✓ 匹配污染物: {pollutant}")
                if "error" not in gene_data:
                    print(f"   ✓ 基因数据可用: {gene_data.get('shape', 'N/A')}")
                else:
                    print(f"   - 基因数据不可用: {gene_data.get('error', '未知错误')}")
                
                if "error" not in organism_data:
                    print(f"   ✓ 微生物数据可用: {organism_data.get('shape', 'N/A')}")
                else:
                    print(f"   - 微生物数据不可用: {organism_data.get('error', '未知错误')}")
        
        print("\n2. 部分数据处理测试 (Aldrin - 仅有微生物数据):")
        result = smart_query.query_related_data("处理含有Aldrin的有机氯农药废水")
        if result["status"] == "success":
            pollutant = result["matched_pollutants"][0] if result["matched_pollutants"] else None
            if pollutant:
                gene_data = result["gene_data"].get(pollutant, {})
                organism_data = result["organism_data"].get(pollutant, {})
                
                print(f"   ✓ 匹配污染物: {pollutant}")
                if "error" not in gene_data:
                    print(f"   ✓ 基因数据可用: {gene_data.get('shape', 'N/A')}")
                else:
                    print(f"   - 基因数据不可用: {gene_data.get('error', '未知错误')}")
                
                if "error" not in organism_data:
                    print(f"   ✓ 微生物数据可用: {organism_data.get('shape', 'N/A')}")
                else:
                    print(f"   - 微生物数据不可用: {organism_data.get('error', '未知错误')}")
        
        print("\n3. 无本地数据处理测试 (模拟外部数据库查询):")
        result = smart_query.query_related_data("处理含有重金属镉的工业废水")
        print(f"   查询结果状态: {result.get('status', '未知')}")
        if result.get('matched_pollutants'):
            print(f"   匹配污染物: {result['matched_pollutants']}")
        else:
            print("   未匹配到本地数据，需要依赖外部数据库")
        
        print("\n✓ 数据完整性处理能力测试完成!")
        return True
        
    except Exception as e:
        print(f"✗ 数据完整性处理能力测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("功能微生物识别智能体单元测试")
    print("=" * 50)
    
    # 验证API密钥是否存在
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("警告：API密钥未正确设置，部分测试可能无法执行")
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 执行各项测试
    test_results = []
    
    # 测试智能体创建
    test_results.append(("智能体创建测试", test_agent_creation()))
    
    # 测试任务创建
    test_results.append(("任务创建测试", test_task_creation()))
    
    # 测试本地数据工具
    test_results.append(("本地数据工具测试", test_local_data_tools()))
    
    # 测试强制本地数据查询工具
    test_results.append(("强制本地数据查询工具测试", test_mandatory_local_data_query_tool()))
    
    # 测试数据完整性处理能力
    test_results.append(("数据完整性处理能力测试", test_data_integrity_handling()))
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print("=" * 50)
    passed = 0
    for test_name, result in test_results:
        status = "通过" if result else "失败"
        if result:
            passed += 1
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{len(test_results)} 个测试通过")
    
    if passed == len(test_results):
        print("🎉 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())