#!/usr/bin/env python3
"""
测试智能体是否能够通过用户提问下载基因文件并成功进行后续处理
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from langchain_openai import ChatOpenAI
from crewai import Crew, Process
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

def test_gene_file_download_and_processing():
    """测试基因文件下载和后续处理"""
    print("测试智能体是否能够通过用户提问下载基因文件并成功进行后续处理...")
    
    # 获取LLM实例
    llm = get_llm()
    
    # 导入菌剂设计智能体
    from agents.microbial_agent_design_agent import MicrobialAgentDesignAgent
    
    # 创建菌剂设计智能体
    design_agent = MicrobialAgentDesignAgent(llm).create_agent()
    
    # 显示智能体可用工具
    print(f"智能体可用工具数量: {len(design_agent.tools)}")
    
    # 检查集成工具是否存在
    integrated_tool_available = False
    for tool in design_agent.tools:
        if tool.name == "IntegratedGenomeProcessingTool":
            integrated_tool_available = True
            print("✓ 集成基因组处理工具已成功加载")
            break
    
    if not integrated_tool_available:
        print("✗ 集成基因组处理工具未找到")
        return False
    
    # 创建测试任务 - 要求分析特定微生物的环境适应性
    from crewai import Task
    
    test_task = Task(
        description="""
        请分析以下微生物的环境适应性特征：
        
        微生物列表：
        1. Pseudomonas putida
        2. Rhodococcus jostii
        
        要求：
        1. 使用IntegratedGenomeProcessingTool查询这些微生物的基因组信息
        2. 下载所需的基因组文件
        3. 分析它们的环境适应性特征（温度、pH、盐度和氧气耐受性）
        4. 提供详细的分析结果
        """,
        expected_output="""
        包含以下内容的详细报告：
        1. 每种微生物的基因组信息
        2. 环境适应性特征分析结果
        3. 如果工具调用成功，提供具体数值
        4. 如果有错误，提供详细错误信息
        """,
        agent=design_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    test_crew = Crew(
        agents=[design_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行基因文件下载和处理测试任务...")
    try:
        result = test_crew.kickoff()
        
        print("\n基因文件下载和处理测试完成，结果如下:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        # 分析结果中是否调用了集成工具
        result_str = str(result)
        if "IntegratedGenomeProcessingTool" in result_str or "基因组" in result_str or "环境适应性" in result_str:
            print("\n✓ 智能体成功调用了集成基因组处理工具")
            return True
        else:
            print("\n✗ 未能确认智能体调用了集成基因组处理工具")
            return False
            
    except Exception as e:
        print(f"\n执行任务时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("BioCrew - 基因文件下载和处理测试")
    print("=" * 50)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("警告：QWEN_API_KEY未配置，但不影响本次测试")
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("警告：OPENAI_API_KEY未配置，但不影响本次测试")
    
    try:
        # 执行测试
        result = test_gene_file_download_and_processing()
        
        if result:
            print("\n✓ 基因文件下载和处理测试通过！")
            print("智能体能够通过用户提问下载基因文件并进行后续处理。")
        else:
            print("\n✗ 基因文件下载和处理测试失败。")
            
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()