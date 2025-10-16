#!/usr/bin/env python3
"""
测试集成基因组处理工具是否已正确添加到微生物菌剂设计智能体中
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

def test_integrated_tool_inclusion():
    """测试集成工具是否已正确添加到微生物菌剂设计智能体中"""
    print("测试集成基因组处理工具是否已正确添加到微生物菌剂设计智能体中...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入菌剂设计智能体
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    
    # 创建菌剂设计智能体
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    # 显示智能体可用工具
    print(f"智能体可用工具数量: {len(design_agent.tools)}")
    
    # 列出所有可用工具
    print("\n智能体可用工具列表:")
    tool_names = []
    for i, tool in enumerate(design_agent.tools):
        print(f"{i+1}. {tool.name}: {tool.description}")
        tool_names.append(tool.name)
    
    # 检查新工具是否存在
    integrated_tool_name = "IntegratedGenomeProcessingTool"
    if integrated_tool_name in tool_names:
        print(f"\n✓ {integrated_tool_name} 已成功添加到智能体工具列表中")
        return True
    else:
        print(f"\n✗ {integrated_tool_name} 未找到在智能体工具列表中")
        return False

def test_integrated_tool_functionality():
    """测试集成工具的功能"""
    print("\n测试集成基因组处理工具的功能...")
    
    try:
        # 导入工具
        from tools.microbial_agent_design.integrated_genome_processing_tool import IntegratedGenomeProcessingTool
        
        # 创建工具实例
        tool = IntegratedGenomeProcessingTool()
        
        # 检查工具属性
        print(f"工具名称: {tool.name}")
        print(f"工具描述: {tool.description}")
        
        # 检查工具输入模式
        print(f"工具输入模式: {tool.args_schema}")
        
        if tool.name == "IntegratedGenomeProcessingTool" and "集成" in tool.description:
            print("✓ 工具属性正确")
            return True
        else:
            print("✗ 工具属性不正确")
            return False
            
    except Exception as e:
        print(f"✗ 测试集成工具功能时出错: {e}")
        return False

def main():
    print("BioCrew - 集成基因组处理工具测试")
    print("=" * 50)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("警告：QWEN_API_KEY未配置，但不影响本次测试")
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("警告：OPENAI_API_KEY未配置，但不影响本次测试")
    
    try:
        # 执行测试
        tool_inclusion_result = test_integrated_tool_inclusion()
        tool_functionality_result = test_integrated_tool_functionality()
        
        print("\n" + "=" * 50)
        print("测试结果汇总:")
        print(f"工具集成测试: {'通过' if tool_inclusion_result else '失败'}")
        print(f"工具功能测试: {'通过' if tool_functionality_result else '失败'}")
        
        if tool_inclusion_result and tool_functionality_result:
            print("\n✓ 所有测试通过！集成基因组处理工具已成功添加到系统中。")
        else:
            print("\n✗ 部分测试失败，请检查实现。")
            
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()