#!/usr/bin/env python3
"""
质量控制智能体
负责出水水质的检测和质量保证
"""

class QualityControlAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='质量控制专家',
            goal='确保出水水质达标并符合相关标准',
            backstory="""你是一位质量控制专家，专注于出水水质的检测和质量保证。
            你熟悉国家和地方的水污染物排放标准，了解各种水质指标的检测方法。
            你能根据出水水质数据判断处理效果，并提出质量改进措施。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )