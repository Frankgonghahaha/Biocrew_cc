#!/usr/bin/env python3
"""
工程微生物组识别任务
负责根据水质净化目标识别工程微生物组
"""

class MicroorganismIdentificationTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        from crewai import Task
        
        description = """
        根据水质净化目标识别工程微生物组，包含功能菌和代谢互补微生物。
        
        识别步骤：
        1. 分析水质净化目标（水质治理指标+目标污染物）
        2. 从公开数据库（Web of Science、HydroWASTE、KEGG、NCBI）获取领域知识
        3. 调用Tool_api工具拉取基因组/酶序列数据
        4. 使用Tool_Carveme工具将基因组转为代谢模型.xml文件
        5. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
        
        关键公式：
        - 竞争指数：MI_competition(A,B)=|SeedSet(A)∩SeedSet(B)|/|SeedSet(A)|
        - 互补指数：MI_complementarity(A,B)=|SeedSet(A)∩NonSeedSet(B)|/|SeedSet(A)∩(SeedSet(B)∪NonSeedSet(B))|
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        提供完整的工程微生物组识别报告，包括：
        1. 识别的功能微生物列表
        2. 代谢互补微生物列表
        3. 竞争指数和互补指数计算结果
        4. 微生物组选择的科学依据
        """
        
        # 如果有上下文任务，设置依赖关系
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent,
            'verbose': True
        }
        
        if context_task:
            task_params['context'] = [context_task]
            
        return Task(**task_params)