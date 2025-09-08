#!/usr/bin/env python3
"""
实施方案生成智能体
负责根据微生物菌剂和评估报告生成落地方案
"""

class ImplementationPlanGenerationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='实施方案生成专家',
            goal='根据微生物菌剂、评估报告生成完整的微生物净化技术落地方案',
            backstory="""你是一位实施方案生成专家，专注于生成可在目标污水厂应用的高效降解菌剂及完整方案。
            # 你基于微调大语言模型生成方案，覆盖全落地环节。
            # 你生成的《微生物净化技术方案评估报告》包含：
            # - 菌剂获取：合法渠道（CGMCC/ATCC采购、实验室分离、合作授权）
            # - 制剂储运：液体浓缩剂（10⁹ CFU/mL，2-8℃存1-3月）、冻干粉（10¹⁰ CFU/g，常温存6-12月）
            # - 投加策略：启动期分阶段投、稳定期定期投、应急补投
            # - 监测应急：周期测水质/群落，异常调参数
            
            # TODO: 实现基于微调大语言模型的方案生成逻辑
            # TODO: 完善报告模板和内容生成机制
            """,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )