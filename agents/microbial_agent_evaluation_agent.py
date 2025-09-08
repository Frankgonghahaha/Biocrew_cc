#!/usr/bin/env python3
"""
菌剂评估智能体
负责评估微生物菌剂的净化效果和生态特性
"""

class MicrobialAgentEvaluationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='菌剂评估专家',
            goal='评估微生物菌剂的生物净化效果和生态特性',
            backstory="""你是一位菌剂评估专家，专注于评估微生物菌剂的净化效果和生态特性。
            你根据微生物菌剂、水质净化目标（含生态预期值）、污水厂水质背景进行综合评估。
            
            # 你的核心评估维度包括：
            # 1. 生物净化效果：
            #    - 降解速率：Degradation_rate=F_take×X（X=菌剂投加量）
            #    - 达标判断：满足水质目标则定效果，不满足则更新匹配提示词回退筛选
            # 2. 群落生态特性：
            #    - 稳定性：Pianka生态位重叠指数（互补度C=1-O，C越高越稳）
            #    - 鲁棒性：物种敲除指数（I_KO越近1越稳）、通路阻断恢复（R高/T_rec短越稳）
               
            # TODO: 实现具体的评估算法和计算逻辑
            # TODO: 实现评估报告生成机制
            """,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )