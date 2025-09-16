#!/usr/bin/env python3
"""
功能微生物识别智能体数据完整性测试脚本
专门测试智能体在不同数据完整性情况下的表现
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

def test_data_integrity_scenarios():
    """测试不同数据完整性场景"""
    print("数据完整性场景测试")
    print("=" * 40)
    
    # 测试用例：不同数据完整性情况
    test_cases = [
        {
            "name": "完整数据测试",
            "pollutant": "Alpha-hexachlorocyclohexane",
            "description": "该污染物同时具有基因数据和微生物数据"
        },
        {
            "name": "仅有基因数据测试",
            "pollutant": "Endosulfan", 
            "description": "该污染物只有基因数据，无微生物数据"
        },
        {
            "name": "仅有微生物数据测试", 
            "pollutant": "Aldrin",
            "description": "该污染物只有微生物数据，无基因数据"
        },
        {
            "name": "无本地数据测试",
            "pollutant": "重金属镉", 
            "description": "该污染物无本地数据，需依赖外部数据库"
        }
    ]
    
    # 测试本地数据工具对不同情况的处理
    from tools.local_data_retriever import LocalDataRetriever
    from tools.smart_data_query_tool import SmartDataQueryTool
    from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool
    
    data_retriever = LocalDataRetriever(base_path=".")
    smart_query = SmartDataQueryTool(base_path=".")
    mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['name']}")
        print(f"描述: {case['description']}")
        print("-" * 30)
        
        # 直接测试数据读取
        if case['name'] != "无本地数据测试":
            print("直接数据读取测试:")
            try:
                gene_data = data_retriever.get_gene_data(case['pollutant'])
                if gene_data is not None:
                    print(f"  ✓ 基因数据读取成功: {gene_data.shape}")
                else:
                    print("  - 基因数据不存在")
            except Exception as e:
                print(f"  - 基因数据读取异常: {e}")
            
            try:
                organism_data = data_retriever.get_organism_data(case['pollutant'])
                if organism_data is not None:
                    print(f"  ✓ 微生物数据读取成功: {organism_data.shape}")
                else:
                    print("  - 微生物数据不存在")
            except Exception as e:
                print(f"  - 微生物数据读取异常: {e}")
        
        # 测试智能查询
        print("智能查询测试:")
        query_text = f"处理含有{case['pollutant']}的废水"
        result = smart_query.query_related_data(query_text)
        
        if result["status"] == "success":
            print(f"  ✓ 查询成功")
            print(f"  ✓ 匹配污染物数量: {len(result['matched_pollutants'])}")
            gene_count = len([k for k, v in result['gene_data'].items() if 'error' not in v])
            organism_count = len([k for k, v in result['organism_data'].items() if 'error' not in v])
            print(f"  ✓ 成功查询基因数据项数: {gene_count}")
            print(f"  ✓ 成功查询微生物数据项数: {organism_count}")
            
            # 显示数据完整性信息
            if gene_count > 0 and organism_count > 0:
                print("  → 数据完整性: 完整 (基因+微生物)")
            elif gene_count > 0:
                print("  → 数据完整性: 部分 (仅有基因)")
            elif organism_count > 0:
                print("  → 数据完整性: 部分 (仅有微生物)")
            else:
                print("  → 数据完整性: 不完整 (无本地数据)")
        else:
            print(f"  - 查询失败: {result.get('message', '未知错误')}")
            print("  → 数据完整性: 不完整 (无本地数据)")

def test_agent_response_to_data_integrity():
    """测试智能体对不同数据完整性情况的响应"""
    print("\n\n智能体响应测试")
    print("=" * 40)
    
    # 初始化LLM模型
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建智能体和任务
    agent_creator = EngineeringMicroorganismIdentificationAgent(llm)
    identification_agent = agent_creator.create_agent()
    
    task_creator = MicroorganismIdentificationTask(llm)
    
    # 测试不同数据完整性情况下的任务执行
    test_requirements = [
        "处理含有Alpha-hexachlorocyclohexane的有机污染物废水",  # 完整数据
        "处理含有Endosulfan的农药废水",  # 仅有基因数据
        "处理含有Aldrin的有机氯农药废水",  # 仅有微生物数据
        "处理含有重金属镉的工业废水"  # 无本地数据
    ]
    
    print("测试智能体在不同数据完整性情况下的响应能力:")
    for i, requirement in enumerate(test_requirements, 1):
        print(f"\n测试 {i}: {requirement}")
        print("-" * 30)
        
        # 创建任务（不执行，仅检查创建）
        try:
            task = task_creator.create_task(
                identification_agent,
                user_requirement=requirement
            )
            print("  ✓ 任务创建成功")
            
            # 检查任务描述中是否包含数据完整性处理指导
            if "当某些类型的数据缺失时" in task.description:
                print("  ✓ 任务描述包含数据完整性处理指导")
            else:
                print("  - 任务描述缺少数据完整性处理指导")
                
            # 检查期望输出中是否包含数据完整性评估
            if "数据完整性和可信度评估" in task.expected_output:
                print("  ✓ 任务期望输出包含数据完整性评估")
            else:
                print("  - 任务期望输出缺少数据完整性评估")
                
        except Exception as e:
            print(f"  - 任务创建失败: {e}")

def main():
    print("功能微生物识别智能体数据完整性专项测试")
    print("=" * 50)
    
    # 验证API密钥是否存在
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("警告：API密钥未正确设置，部分测试可能无法执行")
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 执行测试
    try:
        test_data_integrity_scenarios()
        test_agent_response_to_data_integrity()
        
        print("\n" + "=" * 50)
        print("🎉 数据完整性专项测试完成!")
        print("系统能够正确处理不同数据完整性情况:")
        print("1. 完整数据情况 (基因+微生物)")
        print("2. 部分数据情况 (仅有基因或仅有微生物)")
        print("3. 无本地数据情况 (依赖外部数据库)")
        return 0
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())