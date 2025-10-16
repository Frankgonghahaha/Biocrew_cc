#!/usr/bin/env python3
"""
测试脚本 - 测试从功能微生物识别到菌剂设计的完整流程
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

def test_complete_workflow():
    """
    测试从功能微生物识别到菌剂设计的完整流程
    """
    print("开始测试从功能微生物识别到菌剂设计的完整流程...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入必要的智能体
    from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    from agents.knowledge_management_agent import KnowledgeManagementAgent
    
    # 创建智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    knowledge_agent = KnowledgeManagementAgent(llm).create_agent()
    
    print("创建的智能体:")
    print(f"1. 识别智能体: {identification_agent.role}")
    print(f"2. 设计智能体: {design_agent.role}")
    print(f"3. 知识管理智能体: {knowledge_agent.role}")
    
    # 显示各智能体可用工具数量
    print(f"\n各智能体可用工具数量:")
    print(f"识别智能体工具数: {len(identification_agent.tools)}")
    print(f"设计智能体工具数: {len(design_agent.tools)}")
    print(f"知识管理智能体工具数: {len(knowledge_agent.tools)}")
    
    # 创建任务
    from tasks.microorganism_identification_task import MicroorganismIdentificationTask
    from tasks.microbial_agent_design_task import MicrobialAgentDesignTask
    
    # 创建功能微生物识别任务
    identification_task = MicroorganismIdentificationTask(llm).create_task(
        identification_agent, 
        user_requirement="处理含有苯酚的工业废水"
    )
    
    # 创建菌剂设计任务，依赖于识别任务
    design_task = MicrobialAgentDesignTask(llm).create_task(
        design_agent, 
        identification_task, 
        user_requirement="处理含有苯酚的工业废水"
    )
    
    # 创建Crew执行任务
    test_crew = Crew(
        agents=[identification_agent, design_agent, knowledge_agent],
        tasks=[identification_task, design_task],
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
    
    # 分析结果
    result_str = str(result)
    
    # 检查是否包含关键信息
    required_elements = [
        "微生物",
        "苯酚",
        "代谢",
        "菌剂",
        "设计"
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
    else:
        print("✗ 识别智能体未加载任何工具")
        
    if len(design_agent.tools) > 0:
        print(f"✓ 设计智能体成功加载 {len(design_agent.tools)} 个工具")
        # 检查专业设计工具是否加载
        tool_names = [tool.name for tool in design_agent.tools]
        required_tools = ["CtfbaTool", "GenomeSPOTTool", "DLkcatTool", "CarvemeTool", "PhylomintTool"]
        loaded_tools = [tool for tool in required_tools if tool in tool_names]
        print(f"  已加载的专业设计工具: {loaded_tools}")
    else:
        print("✗ 设计智能体未加载任何工具")
    
    # 检查输出完整性
    print("\n输出完整性检查:")
    if len(result_str) > 200:  # 简单检查输出长度
        print("✓ 输出内容较为完整")
    else:
        print("✗ 输出内容可能不完整")
    
    return result

def main():
    print("BioCrew - 完整工作流测试")
    print("=" * 60)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        result = test_complete_workflow()
        print("\n测试完成!")
        return result
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()