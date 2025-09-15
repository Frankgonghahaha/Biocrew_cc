#!/usr/bin/env python3
"""
任务协调任务
负责根据当前任务执行情况动态选择下一个要执行的智能体
"""

class TaskCoordinationTask:
    def __init__(self, llm):
        self.llm = llm
    
    def create_task(self, task_coordination_agent, context=None):
        from crewai import Task
        
        description = """作为任务协调专家，你需要根据当前的工作流程状态和评估结果，决定下一步应该执行哪个智能体。
        分析当前情况并做出决策：
        1. 如果是初始状态，应该启动微生物识别任务
        2. 如果微生物识别已完成，应该启动菌剂设计任务
        3. 如果菌剂设计已完成，应该启动评估任务
        4. 如果评估结果不达标，应该重新启动微生物识别任务
        5. 如果评估结果达标，应该启动方案生成任务
        
        请根据上下文信息做出决策，并明确指出下一步应该执行的任务。"""
        
        expected_output = """明确指出下一步应该执行的任务名称，以及简要说明选择该任务的原因。
        例如："下一步应该执行微生物识别任务，因为这是工作流程的开始阶段。"
        或："下一步应该重新执行微生物识别任务，因为评估结果不达标，需要重新筛选微生物。" """
        
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=task_coordination_agent,
            context=context or []
        )
        
        return task