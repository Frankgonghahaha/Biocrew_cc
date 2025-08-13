#!/usr/bin/env python3
"""
研发智能体
负责新技术和新方法的研究与开发
"""

class ResearchDevelopmentAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='研发专家',
            goal='研究和开发新型生物净化技术',
            backstory="""你是一位水处理技术的研发专家，专注于前沿生物净化技术的开发。
            你熟悉新型生物载体材料、高效菌种筛选、生物强化技术等前沿领域。
            你能根据现有技术的不足，提出创新性的改进方案。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )