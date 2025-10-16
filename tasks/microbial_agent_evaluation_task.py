#!/usr/bin/env python3
"""
菌剂评估任务
负责评估微生物菌剂的净化效果和生态特性
"""

class MicrobialAgentEvaluationTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None):
        from crewai import Task
        
        description = """
        根据微生物菌剂、水质净化目标、污水厂水质背景评估菌剂性能。
        
        # 评估维度：
        # 1. 生物净化效果：
        #    - 降解速率：Degradation_rate=F_take×X（X=菌剂投加量）
        #    - 达标判断：满足水质目标则定效果，不满足则更新匹配提示词回退筛选
        # 2. 群落生态特性：
        #    - 稳定性：Pianka生态位重叠指数（互补度C=1-O，C越高越稳）
        #    - 鲁棒性：物种敲除指数（I_KO越近1越稳）、通路阻断恢复（R高/T_rec短越稳）
        # 3. 代谢性能：
        #    - 使用ctFBA工具计算实际代谢通量
        #    - 群落生长率分析
        #    - 代谢通量分布评估
        #    - 稳定性指标计算（多样性指数、鲁棒性评分）
        
        # 评估步骤：
        # 1. 使用代谢反应填充工具为模型添加必要的代谢反应
        # 2. 使用培养基推荐工具生成推荐培养基
        # 3. 使用ctFBA工具计算菌剂的实际代谢性能
        # 4. 分析菌剂在上述维度的表现
        # 5. 重点关注群落稳定性和结构稳定性是否达到标准
        # 6. 如果群落稳定性和结构稳定性不符合标准，请明确指出问题并建议回退到工程微生物组识别阶段
        # 7. 如果这两项核心标准达标，再综合评估其他维度
        
        # 评估结果输出格式：
        # 1. 各维度评分（满分10分）
        # 2. 核心标准评估结果
        # 3. 培养基推荐结果
        # 4. ctFBA计算结果（生长率、代谢通量、稳定性指标等）
        # 5. 综合评价和建议
        """
        
        expected_output = """
        提供详细的菌剂评价报告，包括：
        # 1. 各维度评分和分析
        # 2. 核心标准评估结果
        # 3. 培养基推荐结果
        # 4. ctFBA计算结果（生长率、代谢通量、稳定性指标等）
        # 5. 明确的决策建议（通过或回退重新识别）
        # 6. 如果需要回退，提供具体的改进建议
        # 7. 降解速率计算结果
        # 8. 代谢性能详细分析
        # 9. 代谢反应添加结果（如适用）
        """
        
        # 如果有上下文任务，设置依赖关系
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent,
            'verbose': True
        }
        
        if context_task:
            task_params['context'] = [context_task]
            
        return Task(**task_params)