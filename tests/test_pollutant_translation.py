#!/usr/bin/env python3
"""
测试修改后的Agent是否能正确识别和翻译污染物名称
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
from crewai import Crew, Process, Agent, Task
from langchain_openai import ChatOpenAI
import dashscope

def test_pollutant_translation():
    """测试污染物识别和翻译能力"""
    print("开始测试污染物识别和翻译能力...")
    
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
    
    # 测试自然语言输入
    natural_language_inputs = [
        "处理含有重金属镉的工业废水",
        "治理被苯系化合物污染的河水",
        "去除生活污水中的有机磷农药",
        "降解海洋中的塑料垃圾微粒",
        "处理含有多氯联苯的电子废弃物废水"
    ]
    
    for i, user_input in enumerate(natural_language_inputs, 1):
        print(f"\n=== 测试案例 {i}: {user_input} ===")
        
        # 创建任务
        print("  创建任务...")
        try:
            task = Task(
                description=f"""
                请分析处理含有特定污染物的污水的需求，并使用数据查询工具查询相关数据：
                用户输入: {user_input}
                
                请严格按照以下步骤执行：
                1. 从用户输入中识别目标污染物并将其翻译为标准科学术语
                2. 使用PollutantDataQueryTool查询相关数据
                3. 分析查询到的数据
                4. 生成包含具体数据的报告
                5. 在报告中明确说明原始污染物描述和翻译后的标准科学术语
                """,
                expected_output="""
                提供一个分析报告，必须包含以下内容：
                1. 识别的原始污染物描述
                2. 翻译后的标准科学术语
                3. 查询到的具体基因数据（如果有）
                4. 查询到的具体微生物数据（如果有）
                5. 数据完整性和可信度评估
                """,
                agent=agent,
                verbose=True
            )
            print("  ✓ 任务创建成功")
        except Exception as e:
            print(f"  ✗ 任务创建失败: {e}")
            continue
        
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
            continue
        
        # 执行任务
        print("  开始执行任务（真实调用工具）...")
        try:
            result = crew.kickoff()
            print(f"\n  === 任务执行结果 ===")
            print(f"  {result}")
            print("  === 任务执行完成 ===")
            
            # 分析结果
            if result:
                print(f"\n  ✓ 任务执行成功，Agent可以处理自然语言输入并正确翻译污染物名称")
            else:
                print(f"\n  ✗ 任务执行失败，Agent无法正确处理自然语言输入")
                
        except Exception as e:
            print(f"  ✗ 任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n  ✗ 任务执行过程中出现异常，Agent可能无法正确处理自然语言输入")

if __name__ == "__main__":
    test_pollutant_translation()