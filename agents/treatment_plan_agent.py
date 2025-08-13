#!/usr/bin/env python3
"""
净化方案生成智能体
负责对评估后的群落组成进行可行性分析并提供购买渠道查询
"""

class TreatmentPlanAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='净化方案生成专家',
            goal='生成基于功能微生物的水质净化方案并提供实施建议',
            backstory="""你是一位净化方案生成专家，能够对微生物群落组成进行技术经济可行性分析。
            你熟悉市场上各类功能微生物产品的性能、价格和供应商信息。
            你能够根据微生物匹配和菌剂设计结果，制定完整的水质净化实施方案。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )