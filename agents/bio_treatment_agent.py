#!/usr/bin/env python3
"""
生物处理专家智能体
负责生物净化技术的核心处理过程
"""

class BioTreatmentAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='生物处理专家',
            goal='开发和优化水质生物净化技术方案',
            backstory="""你是一位资深的生物处理专家，专注于利用微生物和生物技术进行水质净化。
            你拥有丰富的生物膜技术、活性污泥法、生物滤池等生物处理工艺经验。
            你能够根据不同的水质情况设计合适的生物处理方案。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )