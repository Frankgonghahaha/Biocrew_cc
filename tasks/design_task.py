#!/usr/bin/env python3
"""
功能菌剂设计任务
负责设计和优化功能微生物菌剂配方
"""

class DesignTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None, feedback=None):
        from crewai import Task
        
        description = """
        根据生物净化策略和评估反馈设计功能微生物菌剂配方。
        
        设计步骤：
        1. 分析目标污染物特性和处理要求
        2. 选择合适的功能微生物组（考虑代谢互补性）
        3. 优化菌剂配比以确保群落稳定性和结构稳定性
        4. 考虑物种多样性、代谢相互作用和降解性能的平衡
        
        设计要点：
        - 确保菌剂具有良好的群落稳定性和结构稳定性
        - 优化微生物间的协同作用
        - 满足目标污染物的降解需求
        """
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        提供完整的菌剂设计方案，包括：
        1. 菌剂组成（微生物种类和比例）
        2. 设计原理说明
        3. 稳定性保障措施
        4. 预期的净化效果
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