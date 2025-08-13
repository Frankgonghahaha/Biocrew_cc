#!/usr/bin/env python3
"""
工艺优化智能体
负责优化生物净化工艺参数
"""

class ProcessOptimizationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='工艺优化专家',
            goal='优化生物净化工艺参数以提高处理效率',
            backstory="""你是一位工艺优化专家，专注于水处理工艺的优化和改进。
            你熟悉各种生物处理工艺的操作参数优化，包括溶解氧、pH值、温度、水力停留时间等。
            你能够根据运行数据和出水水质要求，提出工艺调整方案。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )