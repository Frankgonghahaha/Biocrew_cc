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
        # 2. 从用户输入中准确识别目标污染物并将其翻译为标准科学术语
        # 3. 使用专门的数据查询工具查询相关基因和微生物数据
        # 4. 从公开数据库（Web of Science、HydroWASTE、KEGG、NCBI、EnviPath）获取补充领域知识
        # 5. 使用EnviPath工具查询环境化合物代谢路径信息
        # 6. 使用KEGG工具查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息
        # 7. 调用Tool_api工具拉取基因组/酶序列数据
        # 8. 使用Tool_Carveme工具将基因组转为代谢模型.xml文件
        # 9. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
        # 10. 判断是否可获取全基因组信息
        # 11. 评估微生物的生长环境要求
        # 12. 分析微生物对目标污染物的降解效果
        
        # 关键公式：
        # - 竞争指数：MI_competition(A,B)=|SeedSet(A)∩SeedSet(B)|/|SeedSet(A)|
        # - 互补指数：MI_complementarity(A,B)=|SeedSet(A)∩NonSeedSet(B)|/|SeedSet(A)∩(SeedSet(B)∪NonSeedSet(B))|
        
        # 污染物识别与翻译要求：
        # 1. 必须从用户输入的自然语言中准确识别目标污染物
        # 2. 将识别出的污染物名称翻译为标准科学术语，例如：
        #    - "重金属镉" -> "Cadmium"
        #    - "苯系化合物" -> "Benzene compounds"
        #    - "有机磷农药" -> "Organophosphorus pesticides"
        #    - "塑料垃圾微粒" -> "Microplastics"
        #    - "多氯联苯" -> "Polychlorinated biphenyls"
        # 3. 使用翻译后的标准科学术语作为pollutant_name参数调用数据查询工具
        # 4. 在报告中同时提供原始用户输入中的污染物描述和翻译后的标准科学术语
        
        # 数据查询指导：
        # 1. 必须综合使用所有可用工具获取完整信息，而不是仅依赖单一工具
        # 2. 同时使用本地数据库工具查询具体数据
        #    - 使用方式：pollutant_data_query_tool._run({"pollutant_name": "翻译后的标准污染物名称", "data_type": "both"})
        #    - 或者：pollutant_summary_tool._run({"pollutant_name": "翻译后的标准污染物名称"})
        #    - 重要：pollutant_name参数是必填的，必须明确指定翻译后的标准污染物名称
        #    - 重要：必须使用双引号，不能使用单引号
        #    - 注意：系统现在支持自动标准化污染物名称格式，可以使用连字符、空格或下划线等不同格式
        # 3. 同时使用EnviPath工具获取环境代谢路径信息
        #    - EnviPath使用方式：envipath_tool._run({"compound_name": "翻译后的标准化合物名称"})
        # 4. 同时使用KEGG工具获取生物代谢信息
        #    - KEGG使用方式：kegg_tool._run({"compound_name": "翻译后的标准化合物名称"})
        #    - 优先使用smart_query获取完整分析
        # 5. 综合分析所有工具返回的结果，形成完整的代谢网络图
        # 6. 在最终报告中明确体现各工具查询到的具体信息和综合分析结论
        # 7. 提供数据完整性和可信度的评估，明确指出哪些数据可用，哪些数据缺失
        # 8. 对于每个识别的微生物，需要判断是否可获取全基因组信息
        # 9. 评估微生物的生长环境要求（温度、pH值、盐度等）
        # 10. 分析微生物对目标污染物的降解效果
        
        # 全基因组信息获取判断：
        # 1. 通过GeneDataQueryTool查询基因组数据
        # 2. 如果能查询到完整的基因组序列信息，则标记为"可获取全基因组"
        # 3. 如果只能查询到部分基因信息，则标记为"基因组信息不完整"
        # 4. 如果查询不到任何基因信息，则标记为"无法获取基因组信息"
        
        # 生长环境评估：
        # 1. 通过OrganismDataQueryTool查询微生物的生长条件
        # 2. 评估适宜的温度范围、pH值范围、盐度要求等
        # 3. 评估对氧气需求（好氧、厌氧、兼性厌氧）
        
        # 降解效果分析：
        # 1. 结合基因数据和代谢路径信息分析降解能力
        # 2. 评估对目标污染物的降解效率
        # 3. 评估降解过程中的中间产物和最终产物
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
        7. 全基因组信息获取判断（对每个推荐的微生物，明确是否可获取全基因组信息）
        8. 生长环境评估（对每个推荐的微生物，提供适宜的生长环境条件）
        9. 降解效果分析（对每个推荐的微生物，评估对目标污染物的降解效果）
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