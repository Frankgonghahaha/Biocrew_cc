#!/usr/bin/env python3
"""
功能菌剂设计智能体
负责设计和优化功能微生物菌剂配方
"""

class BioagentDesignAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='功能菌剂设计专家',
            goal='设计和优化针对特定污染物的功能微生物菌剂',
            backstory="""你是一位功能菌剂设计专家，专注于微生物菌剂的配方设计和优化。
            你了解不同微生物之间的协同作用、菌剂的稳定性、存活率等关键因素。
            你能够根据不同污染物的特点，设计出高效的复合菌剂配方。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )