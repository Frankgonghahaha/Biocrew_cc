#!/usr/bin/env python3
"""
功能菌剂识别到菌剂设计的融合测试脚本

该脚本测试从工程微生物识别到微生物菌剂设计的完整流程，
验证两个智能体之间的协作和数据传递能力。
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

def test_identification_to_design_workflow():
    """
    测试从微生物识别到菌剂设计的完整工作流程
    """
    print("开始测试从工程微生物识别到菌剂设计的完整工作流程...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入相关智能体
    from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    
    # 创建智能体
    identification_agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    print(f"工程微生物识别智能体创建成功，可用工具数量: {len(identification_agent.tools)}")
    print(f"微生物菌剂设计智能体创建成功，可用工具数量: {len(design_agent.tools)}")
    
    # 导入相关任务
    from tasks.microorganism_identification_task import MicroorganismIdentificationTask
    from tasks.microbial_agent_design_task import MicrobialAgentDesignTask
    
    # 创建测试任务
    # 首先创建微生物识别任务
    identification_task = MicroorganismIdentificationTask(llm).create_task(
        agent=identification_agent,
        user_requirement="处理含有邻苯二甲酸二丁酯(DBP)的工业废水，要求在48小时内降解率达到90%以上"
    )
    
    print(f"微生物识别任务创建成功")
    
    # 然后创建菌剂设计任务，依赖于识别任务的输出
    design_task = MicrobialAgentDesignTask(llm).create_task(
        agent=design_agent,
        context_task=identification_task,
        user_requirement="处理含有邻苯二甲酸二丁酯(DBP)的工业废水，要求在48小时内降解率达到90%以上"
    )
    
    print(f"菌剂设计任务创建成功")
    
    # 创建Crew执行任务
    workflow_crew = Crew(
        agents=[identification_agent, design_agent],
        tasks=[identification_task, design_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行从微生物识别到菌剂设计的完整工作流程...")
    result = workflow_crew.kickoff()
    
    print("\n工作流程执行完成，最终结果如下:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    return result

def main():
    print("BioCrew - 从功能菌剂识别到菌剂设计的融合测试")
    print("=" * 60)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        test_identification_to_design_workflow()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()