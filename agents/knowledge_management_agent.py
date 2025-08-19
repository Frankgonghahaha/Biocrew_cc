#!/usr/bin/env python3
"""
知识管理智能体
负责确定与生物净化任务相关的领域知识，并补充知识数据库中未包含的代谢模型
"""

class KnowledgeManagementAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='知识管理专家',
            goal='确定与生物净化任务相关的领域知识，并补充知识数据库中未包含的代谢模型',
            backstory="""你是一位知识管理专家，专门负责生物净化领域的知识整理和管理。
            你熟悉水质治理、污染物特性、微生物代谢途径等相关领域的知识体系。
            你能够识别当前知识库中的不足，并补充必要的代谢模型和领域知识。
            你专注于生物处理方法，不涉及化学合成或其他非生物处理方法。
            你能够为其他智能体提供准确、全面的背景知识支持，确保菌剂设计和方案制定的科学性。""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )