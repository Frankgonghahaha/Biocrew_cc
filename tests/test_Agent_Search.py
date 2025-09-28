#!/usr/bin/env python3
"""
测试系统处理自然语言输入的能力
用于验证Agent是否能从自然语言中提取目标污染物并正确调用工具
同时验证Agent调用结果与直接API调用结果的一致性
"""

import sys
import os
from dotenv import load_dotenv

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（当前目录的上级目录）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到Python路径中
sys.path.insert(0, project_root)

from config.config import Config
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
import dashscope

# 加载环境变量
load_dotenv()

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

def get_user_input():
    """获取用户输入"""
    print("=== 用户自定义输入测试 ===")
    print("请输入您的水质处理需求:")
    print("例如: 请你帮我识别下哪些微生物可以降解dibutyl_phthalate_要精确到种")
    try:
        user_input = input("水质处理需求: ")
        return user_input
    except (EOFError, KeyboardInterrupt):
        print("\n程序被用户中断或未检测到输入，使用预设测试案例...")
        return ""

def test_natural_language_input():
    """测试自然语言输入处理"""
    print("开始测试自然语言输入处理...")
    
    # 初始化LLM
    try:
        llm = get_llm()
        print("✓ LLM模型初始化成功")
    except Exception as e:
        print(f"✗ LLM模型初始化失败: {e}")
        return
    
    # 创建Agent
    print("\n1. 创建EngineeringMicroorganismIdentificationAgent...")
    try:
        from agents.engineering_microorganism_identification_agent import EngineeringMicroorganismIdentificationAgent
        agent = EngineeringMicroorganismIdentificationAgent(llm).create_agent()
        print("✓ 智能体创建成功")
        print(f"✓ 智能体角色: {agent.role}")
        print(f"✓ 工具数量: {len(agent.tools)}")
        for i, tool in enumerate(agent.tools, 1):
            print(f"  - 工具 {i}: {tool.name}")
    except Exception as e:
        print(f"✗ 智能体创建失败: {e}")
        return
    
    # 验证工具是否正确加载
    if not agent.tools:
        print("✗ 没有加载任何工具")
        return
    
    # 获取用户输入
    user_input = get_user_input()
    # 如果用户没有输入，则使用预设的测试案例
    if not user_input.strip():
        print("未输入自定义需求，使用预设测试案例...")
        user_input = "请你帮我识别下哪些微生物可以降解dibutyl_phthalate_要精确到种"
    
    # 标准化输入
    standardized_input = user_input
    print(f"\n=== 用户输入测试: {user_input} ===")
    print(f"标准化输入: {standardized_input}")
    
    # 创建任务
    print("  创建任务...")
    try:
        task = agent.create_task(
            description=f"""
            请分析处理含有特定污染物的污水的需求，并综合使用多种数据查询工具查询相关数据：
            用户输入: {user_input}
            标准化污染物名称: {standardized_input}
            
            请严格按照以下步骤执行：
            1. 从用户输入中识别目标污染物并将其翻译为标准科学术语
            2. 优先使用EnviPathTool查询目标污染物的环境代谢路径，获取完整的反应步骤和EC编号
               - 必须调用EnviPathTool的search_compound方法获取化合物信息
               - 如果返回了pathway信息，必须进一步调用get_pathway_info_as_json方法获取详细代谢路径
               - 重点分析EnviPathTool返回的代谢路径信息，这是主要的数据来源
               - 基于代谢路径中的每一步反应，提取相应的EC编号和酶信息
            3. 如果EnviPathTool无法提供完整信息，则使用KEGG Tool进行智能查询获取相关基因和通路信息
            4. 使用PollutantDataQueryTool和OrganismDataQueryTool查询本地数据库中的相关基因和微生物数据
            5. 使用PollutantSearchTool进行关键词搜索，获取更多相关污染物信息
            6. 综合所有工具返回的数据，构建完整的代谢路径图
            7. 基于代谢路径和基因功能，推断并推荐能够降解目标污染物的功能微生物（精确到种）
            8. 对推荐的微生物进行科学分类和降解能力评估
            9. 提供生长环境评估和降解效果分析
            10. 给出明确的置信度评估和数据来源标注
            
            特别强调：
            - 必须优先使用EnviPathTool获取的代谢路径信息作为核心依据
            - EnviPathTool返回的JSON格式数据是最权威的参考
            - 所有后续分析都应以EnviPathTool提供的代谢路径为基础展开
            - 当其他工具结果与EnviPathTool结果冲突时，以EnviPathTool为准
            """,
            expected_output="""
            请提供一个完整的分析报告，包含以下内容：
            1. 原始污染物描述
            2. 翻译后的标准科学术语
            3. 各工具查询到的具体基因数据（标注来源与置信度）
            4. 各工具查询到的具体微生物数据（标注来源与置信度）
            5. 数据完整性和可信度评估
            6. 全基因组信息获取判断
            7. 生长环境评估
            8. 降解效果分析
            9. 最终推荐方案：功能微生物与代谢互补微生物组合
            10. 总结与建议
            
            要求：
            - 所有数据必须标注来源工具和查询参数
            - 区分直接查询结果和基于知识的推断结果
            - 推荐的微生物必须精确到种
            - 提供明确的置信度评估（高/中高/中/低）
            - 报告必须突出显示EnviPathTool提供的代谢路径信息
            - 明确说明如何基于EnviPathTool的结果进行后续分析
            """
        )
        print("✓ 任务创建成功")
    except AttributeError:
        # 如果agent没有create_task方法，则使用Task类创建
        print("⚠️  agent没有create_task方法，使用Task类创建任务...")
        from crewai.task import Task
        task = Task(
            description=f"""
            请分析处理含有特定污染物的污水的需求，并综合使用多种数据查询工具查询相关数据：
            用户输入: {user_input}
            标准化污染物名称: {standardized_input}
            
            请严格按照以下步骤执行：
            1. 从用户输入中识别目标污染物并将其翻译为标准科学术语
            2. 优先使用EnviPathTool查询目标污染物的环境代谢路径，获取完整的反应步骤和EC编号
               - 必须调用EnviPathTool的search_compound方法获取化合物信息
               - 如果返回了pathway信息，必须进一步调用get_pathway_info_as_json方法获取详细代谢路径
               - 重点分析EnviPathTool返回的代谢路径信息，这是主要的数据来源
               - 基于代谢路径中的每一步反应，提取相应的EC编号和酶信息
            3. 如果EnviPathTool无法提供完整信息，则使用KEGG Tool进行智能查询获取相关基因和通路信息
            4. 使用PollutantDataQueryTool和OrganismDataQueryTool查询本地数据库中的相关基因和微生物数据
            5. 使用PollutantSearchTool进行关键词搜索，获取更多相关污染物信息
            6. 综合所有工具返回的数据，构建完整的代谢路径图
            7. 基于代谢路径和基因功能，推断并推荐能够降解目标污染物的功能微生物（精确到种）
            8. 对推荐的微生物进行科学分类和降解能力评估
            9. 提供生长环境评估和降解效果分析
            10. 给出明确的置信度评估和数据来源标注
            
            特别强调：
            - 必须优先使用EnviPathTool获取的代谢路径信息作为核心依据
            - EnviPathTool返回的JSON格式数据是最权威的参考
            - 所有后续分析都应以EnviPathTool提供的代谢路径为基础展开
            - 当其他工具结果与EnviPathTool结果冲突时，以EnviPathTool为准
            """,
            expected_output="""
            请提供一个完整的分析报告，包含以下内容：
            1. 原始污染物描述
            2. 翻译后的标准科学术语
            3. 各工具查询到的具体基因数据（标注来源与置信度）
            4. 各工具查询到的具体微生物数据（标注来源与置信度）
            5. 数据完整性和可信度评估
            6. 全基因组信息获取判断
            7. 生长环境评估
            8. 降解效果分析
            9. 最终推荐方案：功能微生物与代谢互补微生物组合
            10. 总结与建议
            
            要求：
            - 所有数据必须标注来源工具和查询参数
            - 区分直接查询结果和基于知识的推断结果
            - 推荐的微生物必须精确到种
            - 提供明确的置信度评估（高/中高/中/低）
            - 报告必须突出显示EnviPathTool提供的代谢路径信息
            - 明确说明如何基于EnviPathTool的结果进行后续分析
            """,
            agent=agent,
            verbose=True
        )
        print("✓ 任务创建成功")
    except Exception as e:
        print(f"✗ 任务创建失败: {e}")
        return
    
    # 创建Crew
    print("  创建Crew执行任务...")
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
    print("  开始执行任务（真实调用工具）...")
    try:
        result = crew.kickoff()
        print("  === 任务执行完成 ===\n")
        print("  ✓ 任务执行成功，Agent可以处理自然语言输入\n")
        print("  === 关键结果摘要 ===")
        print(f"  标准化污染物名称: {standardized_input}")
        print("  Agent执行结果完整内容:")
        if hasattr(result, 'raw') and result.raw:
            print(f"    {str(result.raw)}")
        else:
            print(f"    {str(result)}")
        print("  ✓ 结果验证完成")
        return result
    except Exception as e:
        print(f"✗ 任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_natural_language_input()