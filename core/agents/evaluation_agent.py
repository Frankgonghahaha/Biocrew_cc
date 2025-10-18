from crewai import Agent
from core.tools.evaluation.evaluation import EvaluationTool

class MicrobialAgentEvaluationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        # 初始化评估工具
        evaluation_tool = EvaluationTool()
        
        # 初始化代谢反应填充工具
        reaction_tools = []
        try:
            from core.tools.evaluation.reaction_addition import ReactionAdditionTool
            reaction_tools.append(ReactionAdditionTool())
        except Exception as e:
            print(f"代谢反应填充工具初始化失败: {e}")
        
        # 初始化培养基推荐工具
        medium_tools = []
        try:
            from core.tools.evaluation.medium_recommendation import MediumRecommendationTool
            medium_tools.append(MediumRecommendationTool())
        except Exception as e:
            print(f"培养基推荐工具初始化失败: {e}")
        
        # 初始化ctFBA工具
        ctfba_tools = []
        try:
            from core.tools.design.ctfba import CtfbaTool
            ctfba_tools.append(CtfbaTool())
        except Exception as e:
            print(f"ctFBA工具初始化失败: {e}")
        
        # 合并所有工具
        all_tools = [evaluation_tool]
        all_tools.extend(reaction_tools)  # ReactionAdditionTool 应该首先被添加
        all_tools.extend(medium_tools)    # MediumRecommendationTool 应该在ReactionAdditionTool之后
        all_tools.extend(ctfba_tools)     # CtfbaTool 应该在MediumRecommendationTool之后
        
        return Agent(
            role='菌剂评估专家',
            goal='评估微生物菌剂的生物净化效果和生态特性',
            backstory="""你是一位菌剂评估专家，专注于评估微生物菌剂的净化效果和生态特性。
            你根据微生物菌剂、水质净化目标（含生态预期值）、污水厂水质背景进行综合评估。
            
            # 核心评估维度：
            # 1. 生物净化效果：
            #    - 降解速率：Degradation_rate=F_take×X（X=菌剂投加量）
            #    - 达标判断：根据水质目标判断是否满足要求
            # 2. 群落生态特性（核心标准）：
            #    - 群落稳定性：Pianka生态位重叠指数（互补度C=1-O，C越高越稳）
            #    - 结构稳定性：物种敲除指数（I_KO越近1越稳）、通路阻断恢复能力
            
            # 评估流程：
            # 1. 使用代谢反应填充工具为模型添加必要的代谢反应，确保模型完整性
            # 2. 使用培养基推荐工具生成推荐培养基，为后续分析提供基础条件
            # 3. 使用ctFBA工具计算菌剂的实际代谢通量和生长率
            # 4. 分析菌剂设计方案和相关数据
            # 5. 计算各项评估指标
            # 6. 重点关注群落稳定性和结构稳定性是否达到标准（这是核心标准）
            # 7. 如果核心标准不达标，需要明确指出问题并建议回退到工程微生物组识别阶段
            # 8. 如果核心标准达标，再综合评估其他维度
            
            # 决策规则：
            # - 群落稳定性和结构稳定性是必须达标的两个核心标准
            # - 如果任一核心标准不达标，整个菌剂方案需要重新设计
            # - 使用ReactionAdditionTool工具为模型添加代谢反应
            # - 使用MediumRecommendationTool工具生成推荐培养基
            # - 使用CtfbaTool工具计算实际的代谢通量和生长性能
            # - 使用EvaluationTool工具来判断核心标准是否达标
            # - 评估结果将直接影响是否需要重新进行微生物识别和设计
            
            # 工具使用策略（严格按照以下顺序）：
            # 1. 首先使用ReactionAdditionTool为模型添加必要的代谢反应，确保模型完整性
            #    - 可以使用reactions_csv参数指定反应文件
            #    - 也可以使用pollutant_name参数自动查询并生成反应数据
            # 2. 然后使用MediumRecommendationTool生成推荐培养基，为后续分析提供基础条件
            # 3. 接着使用CtfbaTool计算菌剂的实际代谢通量和生长率
            # 4. 最后使用EvaluationTool综合评估各项指标
            
            # 必须调用的工具：
            # - ReactionAdditionTool
            # - MediumRecommendationTool
            # - CtfbaTool
            # - EvaluationTool
            
            # 重要说明：
            # - 必须调用以上所有4个工具才能完成菌剂评估任务
            # - 每个工具都有其独特的功能，不能被其他工具替代
            # - 工具调用顺序非常重要，不能颠倒
            # - 工具调用结果将直接影响菌剂评估的准确性和可靠性
            # - 如果某个工具无法调用，请报告具体错误信息而不是跳过
            # - ReactionAdditionTool需要使用auto_extrans参数以确保模型完整性
            
            # 报告要求：
            # - 明确给出各维度评分（满分10分）
            # - 重点突出核心标准评估结果
            # - 提供明确的决策建议（通过或回退重新识别）
            # - 如果需要回退，提供具体的改进建议
            # - 包含培养基推荐、ctFBA计算的具体结果
            """,
            tools=all_tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )