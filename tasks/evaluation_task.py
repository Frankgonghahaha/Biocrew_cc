#!/usr/bin/env python3
"""
功能菌剂评价任务
基于物种多样性、群落稳定性、结构稳定性、代谢相互作用、污染物降解性能五个维度进行评价
"""

class EvaluationTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None):
        from crewai import Task
        
        description = """
        请根据以下五个维度评估功能菌剂的性能：
        1. 物种多样性
        2. 群落稳定性
        3. 结构稳定性
        4. 代谢相互作用
        5. 污染物降解性能
        
        其中，群落稳定性和结构稳定性是核心标准。
        
        评估步骤：
        1. 分析菌剂在上述五个维度的表现
        2. 重点关注群落稳定性和结构稳定性是否达到标准
        3. 如果群落稳定性和结构稳定性不符合标准，请明确指出问题并建议返回功能菌剂设计阶段重新设计
        4. 如果这两项核心标准达标，再综合评估其他维度
        
        评估结果输出格式：
        1. 各维度评分（满分10分）：
           - 物种多样性: [评分]
           - 群落稳定性: [评分] (核心标准)
           - 结构稳定性: [评分] (核心标准)
           - 代谢相互作用: [评分]
           - 污染物降解性能: [评分]
        
        2. 核心标准评估：
           - 群落稳定性: [达标/不达标]
           - 结构稳定性: [达标/不达标]
        
        3. 综合评价：
           - 如果核心标准不达标: 返回重新设计，并说明原因
           - 如果核心标准达标: 继续进行其他维度评估并给出总体建议
        """
        
        expected_output = """
        提供详细的菌剂评价报告，包括：
        1. 各维度评分和分析
        2. 核心标准评估结果
        3. 明确的决策建议（通过或返回重新设计）
        4. 如果需要重新设计，提供具体的改进建议
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