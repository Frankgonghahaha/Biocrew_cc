#!/usr/bin/env python3
"""
测试微生物菌剂设计智能体
验证工具是否正确加载和调用
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
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

def test_microbial_agent_design():
    """
    测试微生物菌剂设计智能体
    """
    print("开始测试微生物菌剂设计智能体...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入菌剂设计智能体
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    
    # 创建菌剂设计智能体
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    # 显示智能体信息
    print(f"智能体角色: {design_agent.role}")
    print(f"智能体目标: {design_agent.goal}")
    print(f"智能体可用工具数量: {len(design_agent.tools)}")
    
    # 检查结果完整性
    result_elements = str(design_agent.backstory)
    key_elements = ["微生物", "菌剂", "代谢", "基因", "酶"]
    missing_elements = []
    
    for element in key_elements:
        if element not in result_elements:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"✗ 结果中缺少以下关键元素: {missing_elements}")
    else:
        print("✓ 结果包含所有关键元素")
    
    # 检查工具调用
    print("\n工具调用检查:")
    if len(design_agent.tools) > 0:
        print(f"✓ 设计智能体成功加载 {len(design_agent.tools)} 个工具")
        tool_names = [tool.name for tool in design_agent.tools]
        required_tools = ["GenomeSPOTTool", "DLkcatTool", "CarvemeTool", "PhylomintTool", "CtfbaTool"]
        
        missing_tools = []
        for tool in required_tools:
            if tool not in tool_names:
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"✗ 以下必需工具未加载: {missing_tools}")
        else:
            print("✓ 所有必需工具均已正确加载")
            
        # 显示加载的工具
        print("\n已加载的工具:")
        for i, tool in enumerate(design_agent.tools):
            print(f"{i+1}. {tool.name}")
    else:
        print("✗ 设计智能体未加载任何工具")

if __name__ == "__main__":
    test_microbial_agent_design()