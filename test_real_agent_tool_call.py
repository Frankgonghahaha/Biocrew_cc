#!/usr/bin/env python3
"""
真实测试Agent调用工具示例
用于验证Agent是否可以正确调用工具，不使用模拟数据和模拟流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from config.config import Config
from crewai import Crew, Process, Agent, Task
from langchain_openai import ChatOpenAI
import dashscope

def test_real_agent_tool_call():
    """测试真实Agent工具调用"""
    print("开始测试真实Agent工具调用...")
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型
    try:
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,
            model="openai/qwen3-30b-a3b-instruct-2507",
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        print("✓ LLM模型初始化成功")
    except Exception as e:
        print(f"✗ LLM模型初始化失败: {e}")
        return
    
    # 创建智能体
    print("\n1. 创建EngineeringMicroorganismIdentificationAgent...")
    try:
        from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
        agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
        print(f"✓ 智能体创建成功")
        print(f"✓ 智能体角色: {agent.role}")
        print(f"✓ 工具数量: {len(agent.tools)}")
        for i, tool in enumerate(agent.tools):
            print(f"  - 工具 {i+1}: {tool.name}")
    except Exception as e:
        print(f"✗ 智能体创建失败: {e}")
        return
    
    # 验证工具是否正确加载
    if not agent.tools:
        print("✗ 没有加载任何工具")
        return
    
    # 测试直接调用工具
    print("\n2. 测试直接调用工具...")
    try:
        # 获取第一个工具（PollutantDataQueryTool）
        tool = agent.tools[0]
        print(f"  工具名称: {tool.name}")
        print(f"  工具描述: {tool.description}")
        
        # 直接调用工具
        print("  直接调用工具查询 'endrin' 的数据...")
        result = tool._run(pollutant_name="endrin", data_type="both")
        print(f"  工具调用结果: {result}")
        
        if result.get('status') == 'success':
            print("  ✓ 工具直接调用成功")
            if result.get('gene_data'):
                print(f"    基因数据条数: {len(result['gene_data'])}")
            if result.get('organism_data'):
                print(f"    微生物数据条数: {len(result['organism_data'])}")
        else:
            print(f"  ✗ 工具直接调用失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"✗ 工具直接调用异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 创建任务
    print("\n3. 创建任务...")
    try:
        task = Task(
            description="""
            请分析处理含有endrin的污水的需求，并使用数据查询工具查询相关数据：
            1. 识别endrin污染物
            2. 查询相关的基因和微生物数据
            3. 评估数据完整性
            4. 生成结构化报告
            
            请严格按照以下步骤执行：
            1. 首先使用PollutantDataQueryTool查询endrin的相关数据
            2. 分析查询到的数据
            3. 生成包含具体数据的报告
            """,
            expected_output="""
            提供一个分析报告，必须包含以下内容：
            1. 识别的污染物名称
            2. 查询到的具体基因数据（如果有）
            3. 查询到的具体微生物数据（如果有）
            4. 数据完整性和可信度评估
            """,
            agent=agent,
            verbose=True
        )
        print("✓ 任务创建成功")
    except Exception as e:
        print(f"✗ 任务创建失败: {e}")
        return
    
    # 创建Crew执行任务
    print("\n4. 创建Crew执行任务...")
    try:
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        print("✓ Crew创建成功")
    except Exception as e:
        print(f"✗ Crew创建失败: {e}")
        return
    
    # 执行任务
    print("\n5. 开始执行任务（真实调用工具）...")
    try:
        result = crew.kickoff()
        print("\n=== 任务执行结果 ===")
        print(result)
        print("=== 任务执行完成 ===")
        
        # 分析结果
        if result:
            print("\n✓ 任务执行成功，Agent可以正确调用工具")
        else:
            print("\n✗ 任务执行失败，Agent无法正确调用工具")
            
    except Exception as e:
        print(f"✗ 任务执行异常: {e}")
        import traceback
        traceback.print_exc()
        print("\n✗ 任务执行过程中出现异常，Agent可能无法正确调用工具")

if __name__ == "__main__":
    test_real_agent_tool_call()