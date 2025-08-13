#!/usr/bin/env python3
"""
功能微生物匹配智能体
负责根据污染物类型匹配相应的功能微生物
"""

class MicroorganismMatchingAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='功能微生物匹配专家',
            goal='根据污染物类型和处理要求匹配最适宜的功能微生物',
            backstory="""你是一位功能微生物匹配专家，熟悉各种污染物与对应功能微生物的匹配关系。
            你了解不同微生物的代谢途径、降解能力、环境适应性等特点。
            你能够根据水质污染物的种类和浓度，推荐最适合的微生物种类进行生物净化。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )