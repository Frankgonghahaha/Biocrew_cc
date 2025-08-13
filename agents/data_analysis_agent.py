#!/usr/bin/env python3
"""
数据分析智能体
负责水质数据的分析和处理
"""

class DataAnalysisAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='数据分析专家',
            goal='分析水质数据并提供技术洞察',
            backstory="""你是一位专业的数据分析师，擅长水质参数分析和趋势预测。
            你能够处理各种水质数据，包括COD、BOD、氨氮、总磷、重金属含量等指标。
            你能从数据中发现水质变化规律，并为生物净化过程提供数据支持。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )