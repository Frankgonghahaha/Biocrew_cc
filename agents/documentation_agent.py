#!/usr/bin/env python3
"""
文档智能体
负责技术文档的编写和整理
"""

class DocumentationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='技术文档专家',
            goal='编写和整理生物净化技术相关文档',
            backstory="""你是一位技术文档专家，擅长将复杂的技术内容整理成清晰的文档。
            你能编写技术方案、操作手册、实验报告、项目总结等各种技术文档。
            你确保所有技术内容准确、完整、易于理解。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )