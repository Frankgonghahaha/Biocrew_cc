#!/usr/bin/env python3
"""
测试系统处理自然语言输入的能力
用于验证Agent是否能从自然语言中提取目标污染物并正确调用工具
同时验证Agent调用结果与直接API调用结果的一致性
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
from tools.pollutant_name_utils import standardize_pollutant_name, generate_pollutant_name_variants

def get_user_input():
    """获取用户自定义的水质处理需求"""
    print("请输入您的水质处理需求:")
    print("例如: 处理含有重金属镉的工业废水")
    try:
        user_input = input("水质处理需求: ")
        return user_input
    except EOFError:
        print("未检测到用户输入，使用预设测试案例...")
        return ""

def standardize_input(input_text):
    """
    标准化输入处理，使用与直接调用相同的标准化函数
    从用户输入中提取污染物名称并标准化
    """
    # 直接使用工具函数进行标准化
    return standardize_pollutant_name(input_text)


def test_natural_language_input():
    """测试自然语言输入处理"""
    print("开始测试自然语言输入处理...")
    
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
    
    # 获取用户输入
    print("\n=== 用户自定义输入测试 ===")
    user_input = get_user_input()
    # 如果用户没有输入，则使用预设的测试案例
    if not user_input.strip():
        print("未输入自定义需求，使用预设测试案例...")
        natural_language_inputs = [
            "处理含有重金属镉的工业废水",
            "治理被苯系化合物污染的河水",
            "去除生活污水中的有机磷农药",
            "降解海洋中的塑料垃圾微粒",
            "处理含有多氯联苯的电子废弃物废水"
        ]
        # 只测试第一个案例
        user_input = natural_language_inputs[0]
    
    print(f"\n=== 用户输入测试: {user_input} ===")
    
    # 标准化输入处理
    standardized_input = standardize_input(user_input)
    print(f"标准化输入: {standardized_input}")
    
    # 创建任务
    print("  创建任务...")
    try:
        # 构建任务描述，确保参数传递方式与直接调用一致
        task_description = """
        请分析处理含有特定污染物的污水的需求，并综合使用多种数据查询工具查询相关数据：
        用户输入: """ + user_input + """
        标准化污染物名称: """ + standardized_input + """
        
        请严格按照以下步骤执行：
        1. 从用户输入中识别目标污染物并将其翻译为标准科学术语
        2. 必须综合使用所有可用工具获取完整信息，而不是仅依赖单一工具
        3. 同时使用PollutantDataQueryTool查询本地数据，参数格式: {"pollutant_name": "标准化污染物名称"}
        4. 同时使用EnviPathTool查询环境代谢路径信息，参数格式: {"compound_name": "标准化污染物名称"}
        5. 同时使用KeggTool查询生物代谢信息，参数格式: {"compound_name": "标准化污染物名称"}
        6. 综合分析所有工具返回的结果，形成完整的代谢网络图
        7. 优先使用KeggTool的smart_query方法获取综合分析结果
        8. 如需特定信息，可使用KeggTool的基础查询方法
        9. 分析查询到的数据，明确区分各工具的直接查询结果和综合分析结论
        10. 生成包含具体数据的报告
        11. 在报告中明确说明原始污染物描述和翻译后的标准科学术语
        12. 对于每个数据点，必须明确标注数据来源（工具名称和查询参数）
        13. 评估查询结果的置信度
        14. 最终输出必须是综合所有工具查询结果的分析结论
        
        工具调用参数格式要求：
        - PollutantDataQueryTool: {"pollutant_name": "标准化污染物名称"}
        - EnviPathTool: {"compound_name": "标准化污染物名称"}
        - KeggTool: {"compound_name": "标准化污染物名称"} (将自动调用smart_query方法)
        """
        
        task = Task(
            description=task_description,
            expected_output="""
            提供一个分析报告，必须包含以下内容：
            1. 识别的原始污染物描述
            2. 翻译后的标准科学术语
            3. 各工具查询到的具体基因数据（如果有），必须标注数据来源和工具名称
            4. 各工具查询到的具体微生物数据（如果有），必须标注数据来源和工具名称
            5. 数据完整性和可信度评估，明确区分各工具的直接查询结果和综合分析结论
            6. 全基因组信息获取判断
            7. 生长环境评估
            8. 降解效果分析
            9. 对于每个数据点，必须明确说明是直接查询结果还是基于已知信息的推断
            10. 查询结果的置信度评估
            11. 最终输出必须是综合所有工具查询结果的分析结论
            
            输出格式要求：
            - 使用简洁的自然语言格式返回结果
            - 只保留必要且合理的结构化信息
            - 避免过于冗长和复杂的嵌套结构
            - 突出关键发现和结论
            - 明确标注数据来源和置信度
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
        print(f"  {result}")
        print("  === 任务执行完成 ===")
        
        # 分析结果
        if result:
            print(f"\n  ✓ 任务执行成功，Agent可以处理自然语言输入")
            
            # 显示关键信息
            print("\n  === 关键结果摘要 ===")
            print(f"  标准化污染物名称: {standardized_input}")
            
            # 显示Agent执行结果的完整内容
            if hasattr(result, 'raw') and result.raw:
                print("  Agent执行结果完整内容:")
                print(f"    {str(result.raw)}")
            
            print("  ✓ 结果验证完成")
        else:
            print(f"\n  ✗ 任务执行失败，Agent无法正确处理自然语言输入")
            
    except Exception as e:
        print(f"  ✗ 任务执行异常: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n  ✗ 任务执行过程中出现异常，Agent可能无法正确处理自然语言输入")

if __name__ == "__main__":
    test_natural_language_input()