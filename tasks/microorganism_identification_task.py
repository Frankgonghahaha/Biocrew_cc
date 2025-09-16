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
        # 1. 分析水质净化目标（水质治理指标+目标污染物）
        # 2. 首先从本地数据目录(data/Genes和data/Organism)查询相关基因和微生物数据
        # 3. 从公开数据库（Web of Science、HydroWASTE、KEGG、NCBI、EnviPath）获取补充领域知识
        # 4. 使用EnviPath工具查询环境化合物代谢路径信息
        # 5. 使用KEGG工具查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息
        # 6. 调用Tool_api工具拉取基因组/酶序列数据
        # 7. 使用Tool_Carveme工具将基因组转为代谢模型.xml文件
        # 8. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
        
        # 关键公式：
        # - 竞争指数：MI_competition(A,B)=|SeedSet(A)∩SeedSet(B)|/|SeedSet(A)|
        # - 互补指数：MI_complementarity(A,B)=|SeedSet(A)∩NonSeedSet(B)|/|SeedSet(A)∩(SeedSet(B)∪NonSeedSet(B))|
        
        # 数据完整性处理指导：
        # 1. 必须优先使用本地数据查询工具(LocalDataRetriever和SmartDataQueryTool)获取具体数据
        #    - 使用方式：smart_query._run("query_related_data", query_text="用户需求")
        #    - 或者：data_retriever._run("get_organism_data", pollutant_name="污染物名称")
        # 2. 当某些类型的数据缺失时（如只有微生物数据而无基因数据），应基于现有数据继续分析并明确指出数据缺失情况
        # 3. 利用外部数据库工具(EnviPath、KEGG等)获取补充信息以完善分析
        #    - EnviPath使用方式：envipath_tool._run("search_compound", compound_name="化合物名称")
        #    - KEGG使用方式：kegg_tool._run("find_entries", database="genes", keywords="关键词")
        # 4. 在最终报告中明确体现查询到的微生物名称、基因数据等具体内容，不能仅依赖预训练知识
        # 5. 提供数据完整性和可信度的评估，明确指出哪些数据可用，哪些数据缺失
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        提供完整的工程微生物组识别报告，包括：
        1. 识别的功能微生物列表（优先基于本地数据查询到的具体微生物名称，若数据缺失则说明情况）
        2. 代谢互补微生物列表（优先基于本地数据查询到的具体微生物名称，若数据缺失则说明情况）
        3. 竞争指数和互补指数计算结果（基于可用的本地数据，数据缺失时应说明）
        4. 微生物组选择的科学依据（结合本地数据和外部数据库信息）
        5. 本地数据查询的具体结果（包括查询到的基因数据、微生物数据等详细信息）
        6. 数据完整性和可信度评估（明确指出哪些数据可用，哪些数据缺失）
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