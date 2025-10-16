#!/usr/bin/env python3
"""
测试脚本 - 查看菌剂设计工具在完整运行时的具体调用结果
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

def test_detailed_tool_calls():
    """
    测试并详细记录菌剂设计工具的具体调用结果
    """
    print("开始测试菌剂设计工具的具体调用结果...")
    
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
    
    # 验证特定工具是否存在
    required_tools = ["CtfbaTool", "GenomeSPOTTool", "DLkcatTool", "CarvemeTool", "PhylomintTool"]
    missing_tools = []
    for tool_name in required_tools:
        if tool_name not in tool_names:
            missing_tools.append(tool_name)
    
    if missing_tools:
        print(f"\n警告：以下必需工具缺失: {missing_tools}")
    else:
        print(f"\n所有必需工具均已正确加载")
    
    # 创建详细测试任务 - 要求详细说明每个工具的调用和结果
    from crewai import Task
    
    detailed_test_task = Task(
        description="""
        请分析以下微生物对苯酚的降解能力，并详细记录每个专业工具的调用过程和具体结果：
        
        微生物列表：
        1. Pseudomonas putida
        2. Rhodococcus jostii RHA1
        
        目标污染物：苯酚 (phenol)
        
        要求：
        1. 详细记录GenomeSPOT工具的调用过程和环境适应性预测结果
        2. 详细记录DLkcat工具的调用过程和酶催化速率预测结果
        3. 详细记录Carveme工具的调用过程和代谢模型构建结果
        4. 详细记录Phylomint工具的调用过程和微生物互作分析结果
        5. 详细记录ctFBA工具的调用过程和代谢通量计算结果
        6. 对每个工具的调用都要说明是真实执行还是模拟执行
        7. 提供每个工具返回的具体数值和数据
        
        请按照以下格式输出：
        # 工具调用详细报告
        
        ## 1. GenomeSPOT工具调用详情
        - 调用状态：[真实执行/模拟执行]
        - 输入参数：[具体参数]
        - 输出结果：[具体数值]
        - 详细说明：[过程描述]
        
        ## 2. DLkcat工具调用详情
        - 调用状态：[真实执行/模拟执行]
        - 输入参数：[具体参数]
        - 输出结果：[具体数值]
        - 详细说明：[过程描述]
        
        ## 3. Carveme工具调用详情
        - 调用状态：[真实执行/模拟执行]
        - 输入参数：[具体参数]
        - 输出结果：[具体数值]
        - 详细说明：[过程描述]
        
        ## 4. Phylomint工具调用详情
        - 调用状态：[真实执行/模拟执行]
        - 输入参数：[具体参数]
        - 输出结果：[具体数值]
        - 详细说明：[过程描述]
        
        ## 5. ctFBA工具调用详情
        - 调用状态：[真实执行/模拟执行]
        - 输入参数：[具体参数]
        - 输出结果：[具体数值]
        - 详细说明：[过程描述]
        """,
        expected_output="""
        包含每个工具详细调用信息的完整报告，按照指定格式输出
        """,
        agent=design_agent,
        verbose=True
    )
    
    # 创建Crew执行任务
    detailed_test_crew = Crew(
        agents=[design_agent],
        tasks=[detailed_test_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 执行任务
    print("\n开始执行详细工具调用测试任务...")
    result = detailed_test_crew.kickoff()
    
    print("\n详细工具调用测试完成，结果如下:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    
    # 分析结果中调用的工具
    result_str = str(result)
    called_tools = []
    
    for tool_name in required_tools:
        if tool_name.lower() in result_str.lower():
            called_tools.append(tool_name)
    
    print(f"\n检测到调用的工具: {called_tools}")
    print(f"未检测到的工具: {list(set(required_tools) - set(called_tools))}")
    
    return result

def main():
    print("BioCrew - 菌剂设计工具详细调用结果测试")
    print("=" * 60)
    
    # 检查API密钥
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置QWEN_API_KEY")
        return
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "YOUR_API_KEY":
        print("错误：请在.env文件中配置OPENAI_API_KEY")
        return
    
    try:
        # 执行详细工具调用测试
        result = test_detailed_tool_calls()
        print("\n测试完成!")
        return result
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()