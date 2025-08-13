#!/usr/bin/env python3
"""
任务协调智能体
负责识别用户需求并调用架构内的其他智能体
"""

class TaskCoordinationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='任务协调专家',
            goal='识别用户需求并协调调用其他智能体完成任务',
            backstory="""你是一位专业的任务协调专家，负责理解用户需求并合理分配任务给系统内的其他智能体。
            你拥有全局视野，能够分析用户需求的复杂性并制定合适的执行策略。
            你擅长判断何时需要调用哪个智能体，确保任务能够高效完成。""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )