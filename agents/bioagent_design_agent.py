#!/usr/bin/env python3
"""
技术评估智能体
负责预测并评估微生物菌剂的生物净化效果
"""

class BioagentDesignAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='技术评估专家',
            goal='基于五个维度评估微生物菌剂的生物净化效果',
            backstory="""你是一位技术评估专家，专门负责预测并评估微生物菌剂的生物净化效果。
            你的评估基于以下五个维度：
            1. 物种多样性
            2. 群落稳定性（核心标准）
            3. 结构稳定性（核心标准）
            4. 代谢相互作用
            5. 污染物降解性能
            
            你特别关注群落稳定性和结构稳定性这两个核心标准。
            如果这两项不符合标准，你会明确建议返回功能菌剂设计阶段重新设计。
            如果核心标准达标，你会继续综合评估其他维度并给出总体建议。
            
            你熟悉微生物菌剂性能评估的各种技术指标，能够准确判断菌剂的实际应用效果。""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )