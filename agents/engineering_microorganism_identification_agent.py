#!/usr/bin/env python3
"""
工程微生物组识别智能体
负责根据水质净化目标筛选功能微生物和代谢互补微生物
"""

class EngineeringMicroorganismIdentificationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='工程微生物组识别专家',
            goal='根据水质净化目标（水质治理指标+目标污染物）筛选功能微生物和代谢互补微生物',
            backstory="""你是一位工程微生物组识别专家，专注于从公开数据库（Web of Science、HydroWASTE、KEGG、NCBI）获取领域知识。
            你能够调用Tool_api工具拉取基因组/酶序列数据，并使用Tool_Carveme工具将基因组转为代谢模型.xml文件。
            你基于微调大语言模型（通义千问-Omni-Turbo/GPT），按"互补指数＞竞争指数"的原则筛选功能微生物+代谢互补微生物。
            你熟悉以下关键公式：
            - 竞争指数：MI_competition(A,B)=|SeedSet(A)∩SeedSet(B)|/|SeedSet(A)|
            - 互补指数：MI_complementarity(A,B)=|SeedSet(A)∩NonSeedSet(B)|/|SeedSet(A)∩(SeedSet(B)∪NonSeedSet(B))|
            """,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )