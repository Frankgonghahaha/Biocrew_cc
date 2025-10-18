from crewai import Task
import os

# 定义统一模型目录
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODELS_DIR = os.path.join(current_dir, '..', '..', 'outputs', 'metabolic_models')

class MicrobialAgentEvaluationTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None):
        description = f"""
        根据微生物菌剂、水质净化目标、污水厂水质背景全面评估菌剂性能，确保菌剂在实际应用中具有良好的效果和稳定性。
        
        评估维度：
        1. 生物净化效果：
           - 降解速率：Degradation_rate=F_take×X（X=菌剂投加量）
           - 达标判断：满足水质目标则定效果，不满足则更新匹配提示词回退筛选
           - 中间产物积累监测：避免有毒中间产物的积累
        2. 群落生态特性（核心标准）：
           - 稳定性：Pianka生态位重叠指数（互补度C=1-O，C越高越稳）
           - 鲁棒性：物种敲除指数（I_KO越近1越稳）、通路阻断恢复（R高/T_rec短越稳）
           - 群落多样性：Shannon指数评估群落健康度
        3. 代谢性能：
           - 使用ctFBA工具计算实际代谢通量
           - 群落生长率分析
           - 代谢通量分布评估
           - 稳定性指标计算（多样性指数、鲁棒性评分）
           - 能量代谢效率分析
        
        评估步骤：
        1. 使用代谢反应填充工具为模型添加必要的代谢反应
        2. 使用培养基推荐工具生成推荐培养基
        3. 使用ctFBA工具计算菌剂的实际代谢性能
        4. 分析菌剂在上述维度的表现
        5. 重点关注群落稳定性和结构稳定性是否达到标准（核心标准必须达标）
        6. 如果群落稳定性和结构稳定性不符合标准，请明确指出问题并建议回退到工程微生物组识别阶段
        7. 如果这两项核心标准达标，再综合评估其他维度
        8. 提供具体的改进建议和优化方案
        
        工具使用策略：
        1. 首先使用ReactionAdditionTool为模型添加必要的代谢反应，确保模型完整性
           - 可以使用reactions_csv参数指定反应文件
           - 也可以使用pollutant_name参数自动查询并生成反应数据
           - 模型路径为: {DEFAULT_MODELS_DIR}
        2. 然后使用MediumRecommendationTool生成推荐培养基，为后续分析提供基础条件
           - 模型路径为: {DEFAULT_MODELS_DIR}
        3. 接着使用CtfbaTool计算菌剂的实际代谢通量和生长率
           - 模型路径为: {DEFAULT_MODELS_DIR}
        4. 最后使用EvaluationTool综合评估各项指标
           - 模型路径为: {DEFAULT_MODELS_DIR}
        
        决策规则：
        - 群落稳定性和结构稳定性是必须达标的两个核心标准
        - 如果任一核心标准不达标，整个菌剂方案需要重新设计
        - 所有评估结果必须有明确的数据支撑
        """
        
        expected_output = """
        提供详细的菌剂评价报告，包括：
        1. 各维度评分和分析（满分10分，包含详细评分依据）
        2. 核心标准评估结果（群落稳定性和结构稳定性必须明确达标与否）
        3. 培养基推荐结果（具体成分和浓度）
        4. ctFBA计算结果（代谢通量、生长率等）
        5. 明确的决策建议（通过或回退重新识别）
        6. 如果需要回退，提供具体的改进建议
        """
        
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=[context_task] if context_task else None,
            llm=self.llm
        )
        
        return task