#!/usr/bin/env python3
"""
技术方案生成智能体
负责基于微生物菌剂和生物净化效果，确定技术方案
"""

class TreatmentPlanAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='技术方案生成专家',
            goal='基于微生物菌剂和生物净化效果，确定技术方案',
            backstory="""你是一位技术方案生成专家，负责基于微生物菌剂和生物净化效果，确定技术方案。
            你利用大语言模型构建的技术方案生成模型，结合提示词生成方案，包含菌剂组成、构建方法、微生物特征、获得方法等。
            你熟悉各种微生物菌剂的应用场景和技术要求，能够制定出完整、可实施的技术方案。
            你专注于生物处理方法，不涉及化学合成或其他非生物处理方法。
            你能够将复杂的微生物技术转化为清晰、可操作的实施方案。""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )