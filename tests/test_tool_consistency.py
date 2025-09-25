#!/usr/bin/env python3
"""
Agent工具调用一致性测试脚本
用于验证Agent调用工具与直接调用工具结果的一致性
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
from langchain_openai import ChatOpenAI
import dashscope

def test_tool_consistency():
    """测试Agent工具调用一致性"""
    print("开始测试Agent工具调用一致性...")
    
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
    
    # 测试用例：使用标准化的污染物名称
    pollutant_name = "dibutyl_phthalate"
    print(f"\n=== 测试用例: {pollutant_name} ===")
    
    # 创建任务
    print("  创建任务...")
    try:
        task_description = f"""
        请分析处理含有特定污染物的污水的需求，并综合使用多种数据查询工具查询相关数据：
        标准化污染物名称: {pollutant_name}
        
        请严格按照以下步骤执行：
        1. 使用PollutantDataQueryTool查询本地数据，参数格式: {{"pollutant_name": "{pollutant_name}"}}
        2. 使用EnviPathTool查询环境代谢路径信息，参数格式: {{"compound_name": "{pollutant_name}"}}
        3. 使用KeggTool查询生物代谢信息，参数格式: {{"compound_name": "{pollutant_name}"}}
        4. 综合分析所有工具返回的结果
        5. 生成包含具体数据的报告
        """
        
        task = Task(
            description=task_description,
            expected_output=f"""
            提供一个分析报告，必须包含以下内容：
            1. 各工具查询到的具体基因数据（如果有），必须标注数据来源和工具名称
            2. 各工具查询到的具体微生物数据（如果有），必须标注数据来源和工具名称
            3. 数据完整性和可信度评估
            4. 最终输出必须是综合所有工具查询结果的分析结论
            """,
            agent=agent,
            verbose=True
        )
        print("  ✓ 任务创建成功")
    except Exception as e:
        print(f"  ✗ 任务创建失败: {e}")
        return
    
    # 创建Crew执行任务
    print("  创建Crew执行任务...")
    try:
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        print("  ✓ Crew创建成功")
    except Exception as e:
        print(f"  ✗ Crew创建失败: {e}")
        return
    
    # 执行任务
    print("  开始执行任务（真实调用工具）...")
    try:
        result = crew.kickoff()
        print(f"\n  === 任务执行结果 ===")
        # 只打印关键信息，避免输出过多内容
        if hasattr(result, 'raw') and result.raw:
            print(f"  任务执行完成，结果长度: {len(str(result.raw))} 字符")
        else:
            print(f"  任务执行完成: {result}")
        print("  === 任务执行完成 ===")
        
        # 分析结果
        if result:
            print(f"\n  ✓ 任务执行成功，Agent可以处理工具调用")
            
            # 执行直接API调用以进行一致性验证
            print("\n  === 直接API调用验证 ===")
            
            # 直接调用PollutantDataQueryTool
            try:
                from tools.pollutant_data_query_tool import PollutantDataQueryTool
                pollutant_tool = PollutantDataQueryTool()
                direct_pollutant_result = pollutant_tool._run(pollutant_name)
                print("  ✓ PollutantDataQueryTool直接调用成功")
                print(f"    状态: {direct_pollutant_result.get('status', 'unknown')}")
            except Exception as e:
                print(f"  ✗ PollutantDataQueryTool直接调用失败: {e}")
                direct_pollutant_result = {"status": "error", "message": str(e)}
            
            # 直接调用KeggTool
            try:
                from tools.kegg_tool import KeggTool
                kegg_tool = KeggTool()
                direct_kegg_result = kegg_tool._run(compound_name=pollutant_name)
                print("  ✓ KeggTool直接调用成功")
                print(f"    状态: {direct_kegg_result.get('status', 'unknown')}")
            except Exception as e:
                print(f"  ✗ KeggTool直接调用失败: {e}")
                direct_kegg_result = {"status": "error", "message": str(e)}
            
            # 直接调用EnviPathTool
            try:
                from tools.envipath_tool import EnviPathTool
                envipath_tool = EnviPathTool()
                direct_envipath_result = envipath_tool._run(compound_name=pollutant_name)
                print("  ✓ EnviPathTool直接调用成功")
                print(f"    状态: {direct_envipath_result.get('status', 'unknown')}")
            except Exception as e:
                print(f"  ✗ EnviPathTool直接调用失败: {e}")
                direct_envipath_result = {"status": "error", "message": str(e)}
            
            # 比较结果状态
            print("\n  === 结果状态对比 ===")
            print(f"  PollutantDataQueryTool - 直接调用: {direct_pollutant_result.get('status', 'unknown')}")
            print(f"  KeggTool - 直接调用: {direct_kegg_result.get('status', 'unknown')}")
            print(f"  EnviPathTool - 直接调用: {direct_envipath_result.get('status', 'unknown')}")
            
            print("  ✓ 工具调用一致性测试完成")
        else:
            print(f"\n  ✗ 任务执行失败，Agent无法正确处理工具调用")
            
    except Exception as e:
        print(f"  ✗ 任务执行异常: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n  ✗ 任务执行过程中出现异常，Agent可能无法正确处理工具调用")

if __name__ == "__main__":
    test_tool_consistency()