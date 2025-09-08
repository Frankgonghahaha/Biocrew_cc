#!/usr/bin/env python3
"""
任务协调智能体
负责调控生物净化技术开发智能体、技术评估智能体、技术方案生成智能体的执行顺序
"""

class TaskCoordinationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='任务协调专家',
            goal='调控生物净化技术开发智能体、技术评估智能体、技术方案生成智能体的执行顺序',
            backstory="""你是一位专业的任务协调专家，负责调控生物净化技术开发智能体、技术评估智能体、技术方案生成智能体的执行顺序。
            # 你拥有全局视野，能够分析用户需求的复杂性并制定合适的执行策略。
            # 你擅长判断何时需要调用哪个智能体，确保任务能够高效完成。
            # 你专注于生物方法处理污染物，不考虑化学合成或其他非生物处理方法。
            # 你可以协调知识管理专家提供必要的背景知识，然后让生物净化策略开发专家设计菌剂，
            # 再由技术评估专家评估效果，最后由技术方案生成专家形成完整方案。
            
            # TODO: 实现任务协调的具体功能
            """,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )