#!/usr/bin/env python3
"""
微生物识别任务
定义工程微生物识别任务的创建和配置
"""

from crewai import Task
from typing import List
from textwrap import dedent
from core.tools.database.factory import DatabaseToolFactory


class MicroorganismIdentificationTask:
    """微生物识别任务类"""
    
    def __init__(self, llm):
        """
        初始化微生物识别任务
        
        Args:
            llm: 大语言模型实例
        """
        self.llm = llm

    def create_task(self, agent, user_requirement: str) -> Task:
        """
        创建微生物识别任务实例
        
        Args:
            agent: 执行任务的智能体
            user_requirement: 用户需求描述
            
        Returns:
            Task: 配置好的任务实例
        """
        # 创建工具实例
        tools = DatabaseToolFactory.create_all_tools()
        
        task = Task(
            description=dedent(f"""
                根据水质净化目标识别工程微生物组，包含功能菌和代谢互补微生物。
                
                识别步骤：
                # 1. 分析水质净化目标（水质治理指标+目标污染物）
                # 2. 从用户输入中准确识别目标污染物并将其翻译为标准科学术语
                # 3. 使用专门的数据查询工具查询相关基因和微生物数据
                # 4. 从公开数据库（Web of Science、HydroWASTE、KEGG、NCBI、EnviPath）获取补充领域知识
                # 5. 使用EnviPath工具查询环境化合物代谢路径信息
                # 6. 使用KEGG工具查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息
                # 7. 使用NCBI基因组查询工具获取推荐微生物的基因组Assembly Accession信息
                # 8. 使用微生物互补性数据库查询工具获取预先计算的微生物竞争指数和互补指数
                # 9. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
                # 10. 判断是否可获取全基因组信息
                # 11. 评估微生物的生长环境要求
                # 12. 分析微生物对目标污染物的降解效果
                
                # 关键公式：
                # - 竞争指数：MI_competition(A,B)=|SeedSet(A)∩SeedSet(B)|/|SeedSet(A)∪SeedSet(B)|
                # - 互补指数：MI_complementarity(A,B)=(|ProductionSet(A)∩NonSeedSet(B)|+|ProductionSet(B)∩NonSeedSet(A)|)/(|ProductionSet(A)|+|ProductionSet(B)|)
                
                工具调用策略：
                # 1. 首先使用PollutantSummaryTool或PollutantDataQueryTool确定污染物的标准化名称
                # 2. 使用EnviPathTool查询目标污染物的完整代谢路径，重点关注每步反应的EC编号和酶名称
                # 3. 基于EC编号使用KEGG工具查询对应的基因和代谢信息
                # 4. 使用NCBI基因组查询工具获取推荐微生物的基因组Assembly Accession信息
                # 5. 使用MicrobialComplementarityDBQueryTool查询微生物间的互补性数据
                
                用户需求：{user_requirement}
                
                请严格遵循以下输出格式：
                
                # 工程微生物组识别报告：降解[污染物标准名称]的微生物组合
                
                ## 1. 目标污染物识别
                - **原始用户输入**：[用户原始输入]
                - **标准科学术语**：[标准化术语]
                - **化学式**：[化学式]
                - **CAS号**：[CAS号]
                - **分类**：[污染物分类]
                
                ## 2. 降解路径分析（基于EnviPathTool）
                [以表格形式展示降解路径，包含步骤、反应描述、底物、产物、EC编号、酶名称、相关基因（推断）等信息]
                
                > **完整降解路径**：[起始物质] → [中间产物1] → [中间产物2] → ... → CO₂ + H₂O  
                > **关键限速步骤**：[关键步骤说明]
                
                ---
                
                ## 3. 推荐功能微生物与代谢互补微生物
                [以表格形式展示推荐微生物列表，包含微生物名称、科学分类信息、降解能力描述、相关基因列表、代谢路径关键步骤、数据来源、置信度评估、NCBI Assembly Accession等信息]
                
                > **备注**：[备注信息]
                
                ---
                
                ## 4. 生长环境评估
                [以表格形式展示每个微生物的生长环境要求，包括温度范围、pH范围、盐度要求、氧气需求、特殊条件等]
                
                > **兼容性分析**：[微生物间的环境兼容性分析]
                
                ---
                
                ## 5. 全基因组信息获取判断
                [以表格形式展示每个微生物的全基因组信息获取情况]
                
                ---
                
                ## 6. 降解效果分析
                ## 6. 降解效果分析
                [以表格形式展示每个微生物的降解效率、中间产物积累、最终产物、是否矿化等信息]
                
                > **结论**：[降解效果结论]
                
                ---
                
                ## 7. 代谢互补性分析（基于微生物互补性数据库查询工具）
                [分析微生物组合的代谢互补性，如果有数据库中的数据则直接引用，如果没有则基于路径推断]
                
                ### 代谢互补性分析逻辑：
                [说明分析逻辑]
                
                ### 指数计算（如果有数据库支持）：
                - **MI_competition(A,B)** = [数值]
                - **MI_complementarity(A,B)** = [数值]
                
                > **推论**：[基于指数的推论]
                
                ---
                
                ## 8. 微生物组推荐组合表
                [以表格形式展示最终推荐的微生物组合，包含微生物名称、科学分类信息、降解能力描述、相关基因列表、代谢路径关键步骤、数据来源、置信度评估、NCBI Assembly Accession、竞争指数、互补指数等信息]
                
                > **推荐理由**：[推荐理由]
                
                ---
                
                ## 9. 数据完整性与可信度评估
                [以表格形式展示各项数据的可用性、来源、备注等信息]
                
                > **主要局限**：[主要局限性说明]
                
                ---
                
                ## 10. 结论与建议
                **最终推荐工程微生物组**：  
                **[微生物A] + [微生物B]**  
                
                ✔️ **科学依据**：
                [科学依据列表]
                
                🔧 **后续建议**：
                [后续建议列表]
                
                --- 
                
                **附录：NCBI基因组下载链接**
                [提供NCBI基因组下载链接]
            """),
            agent=agent,
            expected_output=dedent("""
                完整的工程微生物组识别报告，包含：
                1. 目标污染物识别结果
                2. 详细的降解路径分析
                3. 推荐的功能微生物和代谢互补微生物列表
                4. 微生物的生长环境评估
                5. 全基因组信息获取判断
                6. 降解效果分析
                7. 代谢互补性分析
                8. 最终推荐的微生物组组合
                9. 数据完整性与可信度评估
                10. 结论与建议
            """),
            tools=tools
        )
        
        return task