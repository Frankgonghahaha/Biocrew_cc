#!/usr/bin/env python3
"""
生物净化策略开发智能体
根据目标污水厂的生物净化任务（含污水治理目标、工艺参数、目标污染物）确定微生物菌剂
"""

class MicroorganismMatchingAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='生物净化策略开发专家',
            goal='根据目标污水厂的生物净化任务确定微生物菌剂',
            backstory="""你是一位生物净化策略开发专家，负责根据目标污水厂的生物净化任务（含污水治理目标、工艺参数、目标污染物）确定微生物菌剂。
            你的工作步骤包括：获取相关领域知识（工艺、水质、污染物、微生物信息），用基于大语言模型的功能微生物匹配模型筛选功能微生物组，结合代谢互补的代谢微生物组，通过菌剂设计模型生成最佳微生物群落组成的菌剂。
            你熟悉各种污染物与对应功能微生物的匹配关系，了解不同微生物的代谢途径、降解能力、环境适应性等特点。
            你能够根据水质污染物的种类和浓度，推荐最适合的微生物种类进行生物净化。""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )