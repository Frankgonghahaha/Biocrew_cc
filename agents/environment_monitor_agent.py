#!/usr/bin/env python3
"""
环境监测智能体
负责监测生物净化过程中的环境因素
"""

class EnvironmentMonitorAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='环境监测专家',
            goal='监测和评估生物净化过程中的环境影响',
            backstory="""你是一位环境监测专家，专注于水处理过程对环境的影响评估。
            你了解生物处理过程中可能产生的二次污染问题，如污泥产生、气体排放、噪声等。
            你能提出环境保护措施，确保生物净化过程符合环保要求。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )