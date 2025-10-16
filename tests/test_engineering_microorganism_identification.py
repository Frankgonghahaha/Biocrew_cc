#!/usr/bin/env python3
"""
测试脚本 - 测试工程微生物识别智能体

该测试验证：
1. 工程微生物识别智能体能否正确识别功能微生物
2. 智能体是否能正确调用相关工具
3. 输出内容是否合理且完整
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

def test_engineering_microorganism_identification():
    """
    测试工程微生物识别智能体
    """
    print("开始测试工程微生物识别智能体...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入必要的智能体
    from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
    from agents.knowledge_management_agent import KnowledgeManagementAgent
    
    # 创建智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    print("创建的智能体:")
    print(f"1. 识别智能体: {identification_agent.role}")
    print(f"2. 知识管理智能体: {knowledge_agent.role}")
    
    # 显示各智能体可用工具数量
    print(f"\n各智能体可用工具数量:")
    print(f"识别智能体工具数: {len(identification_agent.tools)}")
    print(f"知识管理智能体工具数: {len(knowledge_agent.tools)}")
    
    # 创建任务
    from crewai import Task
    
    identification_task = Task(
        description="""
        识别适用于处理含苯酚工业废水的功能微生物和代谢互补微生物。
        
        要求：
        1. 使用数据库工具查询苯酚相关的微生物和基因数据
        2. 使用EnviPath工具查询苯酚的代谢路径信息
        3. 使用KEGG工具获取相关代谢信息
        4. 使用NCBI工具查询目标微生物的基因组信息
        5. 提供至少3种功能微生物及其特性说明
        6. 明确指出每种微生物的降解能力和环境适应性
        
        输入污染物：苯酚 (phenol)
        """,
        expected_output="""
        包含以下内容的详细报告：
        1. 查询到的功能微生物列表（至少3种）
        2. 每种微生物的关键特性（包括降解能力、环境适应性等）
        3. 苯酚的代谢路径信息
        4. 相关基因和酶信息
        5. 数据来源说明
        6. 微生物之间的代谢互补性分析
        """,
        agent=identification_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    test_crew = Crew(
        agents=[identification_agent, knowledge_agent],
        tasks=[identification_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行任务...")
    result = test_crew.kickoff()
    
    print("\n任务执行完成，最终结果如下:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    # 验证结果
    result_str = str(result)
    
    # 检查是否包含关键信息
    required_elements = [
        "微生物",
        "苯酚",
        "代谢",
        "基因",
        "酶"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in result_str:
            missing_elements.append(element)
    
    print("\n测试结果分析:")
    if missing_elements:
        print(f"✗ 结果中缺少以下关键元素: {missing_elements}")
    else:
        print("✓ 结果包含所有关键元素")
    
    # 检查工具调用
    print("\n工具调用检查:")
    if len(identification_agent.tools) > 0:
        print(f"✓ 识别智能体成功加载 {len(identification_agent.tools)} 个工具")
        for tool in identification_agent.tools:
            print(f"  - {tool.name}: {tool.description}")
    else:
        print("✗ 识别智能体未加载任何工具")
    
    # 检查输出完整性
    print("\n输出完整性检查:")
    if len(result_str) > 200:  # 简单检查输出长度
        print("✓ 输出内容较为完整")
    else:
        print("✗ 输出内容可能不完整")
    
    return result

def main():
    print("BioCrew - 工程微生物识别智能体测试")
    print("=" * 60)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        result = test_engineering_microorganism_identification()
        print("\n测试完成!")
        return result
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()