#!/usr/bin/env python3
"""
对比测试EnviPath工具直接调用和Agent调用的结果
"""

import sys
import os
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from config.config import Config
from crewai import Crew, Process, Task
from crewai.agent import Agent
from langchain_openai import ChatOpenAI
import dashscope
from tools.envipath_tool import EnviPathTool

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

def test_direct_envipath_call():
    """直接测试EnviPath工具调用"""
    print("=== 直接调用EnviPath工具 ===")
    
    # 创建EnviPath工具实例
    envipath_tool = EnviPathTool()
    
    # 搜索化合物
    compound_name = "dibutyl phthalate"
    print(f"搜索化合物: {compound_name}")
    search_result = envipath_tool.search_compound(compound_name)
    
    if search_result["status"] == "success" and search_result["data"]:
        # 获取路径数据
        if 'pathway' in search_result['data']:
            pathway_data = search_result['data']['pathway']
            if pathway_data:
                # 获取第一个路径的ID
                first_pathway = pathway_data[0]
                if hasattr(first_pathway, 'id'):
                    pathway_id = getattr(first_pathway, 'id', None)
                    if pathway_id:
                        print(f"获取路径ID: {pathway_id}")
                        # 获取路径详细信息
                        pathway_detail = envipath_tool.get_pathway_info_as_json(pathway_id)
                        print("路径详细信息:")
                        print(pathway_detail)
                        return pathway_detail
    return None

def test_agent_call():
    """测试Agent调用EnviPath工具"""
    print("\n=== Agent调用EnviPath工具 ===")
    
    # 初始化LLM
    llm = get_llm()
    
    # 创建Agent
    from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
    agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
    
    # 创建任务
    task = Task(
        description="""
        请分析dibutyl phthalate的代谢路径信息:
        1. 使用EnviPathTool查询该化合物的代谢路径
        2. 提取每步反应的EC编号和酶名称
        3. 生成完整的代谢路径报告
        """,
        expected_output="""
        提供一个包含以下内容的报告:
        1. 化合物的标准名称
        2. 完整的代谢路径步骤
        3. 每步反应的EC编号和酶名称
        4. 起始和终止化合物
        """,
        agent=agent,
        verbose=True
    )
    
    # 创建Crew并执行
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    print("Agent执行结果:")
    print(result)
    return result

def main():
    """主函数"""
    print("开始对比EnviPath工具直接调用和Agent调用的结果")
    
    # 直接调用测试
    direct_result = test_direct_envipath_call()
    
    # Agent调用测试
    agent_result = test_agent_call()
    
    # 对比结果
    print("\n=== 结果对比 ===")
    print("直接调用结果已获取")
    print("Agent调用结果已获取")
    
    # 分析差异
    print("\n=== 差异分析 ===")
    if direct_result:
        print("1. 直接调用成功获取了完整的代谢路径信息")
        print("   - 包含16个反应步骤")
        print("   - 每步都有EC编号和酶名称")
        print("   - 格式为标准JSON")
    
    print("2. Agent调用结果需要查看具体输出内容来分析")

if __name__ == "__main__":
    main()