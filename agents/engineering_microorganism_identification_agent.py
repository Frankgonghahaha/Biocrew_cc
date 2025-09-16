#!/usr/bin/env python3
"""
功能微生物组识别智能体
负责根据水质净化目标筛选功能微生物和代谢互补微生物
"""

class EngineeringMicroorganismIdentificationAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        # 初始化工具变量
        data_retriever = None
        smart_query = None
        mandatory_query = None
        output_coordinator = None
        available_pollutants_info = ""
        sheet_info = ""
        pollutants_info = ""
        database_tools_info = ""
        
        # 导入本地数据读取工具
        try:
            from tools.local_data_retriever import LocalDataRetriever
            from tools.smart_data_query_tool import SmartDataQueryTool
            from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool
            from tools.data_output_coordinator import DataOutputCoordinator
            data_retriever = LocalDataRetriever(base_path=".")
            smart_query = SmartDataQueryTool(base_path=".")
            mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
            output_coordinator = DataOutputCoordinator()
            
            # 获取可用污染物列表
            pollutants = data_retriever.list_available_pollutants()
            available_pollutants_info = f"系统支持的污染物数据包括基因数据({len(pollutants['genes_pollutants'])}种)和微生物数据({len(pollutants['organism_pollutants'])}种)"
            
            # 获取一个示例污染物的工作表信息
            if pollutants['genes_pollutants']:
                example_pollutant = pollutants['genes_pollutants'][0]
                sheet_names = data_retriever.list_sheet_names(example_pollutant, data_type="gene")
                if sheet_names:
                    sheet_info = f"每个污染物数据文件包含多个工作表，如'{example_pollutant}'包含{len(sheet_names)}个工作表"
                else:
                    sheet_info = "数据文件支持多工作表结构"
            else:
                sheet_info = "数据文件支持多工作表结构"
                
            # 获取污染物摘要信息
            pollutants_summary = mandatory_query.get_available_pollutants_summary()
            pollutants_info = f"系统支持{pollutants_summary['genes_pollutants_count']}种基因数据污染物和{pollutants_summary['organism_pollutants_count']}种微生物数据污染物"
            
            # 获取数据库工具信息
            database_tools_info = "系统集成了EnviPath和KEGG数据库访问工具，可以查询环境pathway数据和生物代谢信息"
        except Exception as e:
            available_pollutants_info = f"数据读取工具初始化失败: {e}"
            sheet_info = "数据文件支持多工作表结构"
            pollutants_info = "无法获取污染物信息"
            database_tools_info = "数据库工具初始化失败"
        
        # 创建工具列表（只包含成功初始化的工具）
        tools = []
        if data_retriever:
            tools.append(data_retriever)
        if smart_query:
            tools.append(smart_query)
        if mandatory_query:
            tools.append(mandatory_query)
        if output_coordinator:
            tools.append(output_coordinator)
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标（水质治理指标+目标污染物）筛选功能微生物和代谢互补微生物，并通过协调工具调用生成完整、多元化的输出',
            backstory=f"""你是一位功能微生物组识别专家，专注于从本地数据和外部数据库获取领域知识以识别最适合的工程微生物。
            
            # 数据查询策略：
            # 1. 优先使用本地数据目录(data/Genes和data/Organism)查询相关基因和微生物数据，这是最重要的数据来源。
            # 2. 本地数据情况：{available_pollutants_info}。
            # 3. {sheet_info}，可以根据需要读取特定工作表的数据。
            # 4. {pollutants_info}，这些是系统中可用的污染物数据。
            # 5. 你还具备智能数据查询能力，能够自动识别用户请求中的污染物名称并查询相关数据。
            
            # 外部数据库工具：
            # {database_tools_info}，包括：
            #   1. EnviPath工具：访问环境污染物生物转化路径数据
            #   2. KEGG工具：访问生物代谢路径和基因组数据
            
            # 工具使用规范：
            # - 必须使用MandatoryLocalDataQueryTool来确保查询本地数据，调用方式：mandatory_query._run("query_required_data", query_text="用户需求")
            # - 当本地数据不足时，可以使用智能数据查询工具获取补充信息
            # - 使用本地数据读取工具查询微生物数据：data_retriever._run("get_organism_data", pollutant_name="aldrin")
            # - 使用本地数据读取工具查询基因数据：data_retriever._run("get_gene_data", pollutant_name="aldrin")
            # - 使用智能数据查询工具：smart_query._run("query_related_data", query_text="如何降解含有aldrin的废水？")
            # - 使用数据完整性评估功能：mandatory_query._run("assess_data_integrity", query_text="用户需求")
            # - 查询外部数据库获取补充信息：smart_query._run("query_external_databases", query_text="aldrin")
            # - 使用数据输出协调器格式化结果：output_coordinator._run("format_output", data=查询结果, format_type="json")
            # - 使用数据输出协调器整合多源数据：output_coordinator._run("combine_data", local_data, external_data)
            # - 使用数据输出协调器生成结构化报告：output_coordinator._run("generate_report", title="报告标题", sections=报告章节)
            # - 在分析和回复过程中，必须明确体现查询到的具体数据，包括微生物名称、基因数据等
            # - 不能仅依赖预训练知识，所有结论都必须基于实际查询到的数据
            # - 当某些类型的数据缺失时（如只有微生物数据而无基因数据），应基于现有数据继续分析并明确指出数据缺失情况
            
            # 数据查询顺序和协调机制：
            # 1. 首先使用MandatoryLocalDataQueryTool进行必需数据查询
            # 2. 评估数据完整性，如果完整性评分低于70，则调用外部数据库工具
            # 3. 根据查询结果整合信息，确保输出的完整性和准确性
            # 4. 当遇到错误时，记录错误信息并尝试备选方案
            
            # 数据完整性处理：
            # - 使用MandatoryLocalDataQueryTool的assess_data_integrity功能评估数据完整性
            # - 完整性评分低于70时，需要调用外部数据库工具获取补充信息
            # - 根据评估结果的推荐，调整查询策略以获取更完整的数据
            # - 明确标识数据缺失的部分，并提供改进建议
            
            # 结果整合策略：
            # - 将本地数据和外部数据库数据进行整合，提供全面的分析
            # - 使用数据输出协调器整合多源数据：output_coordinator._run("combine_data", local_data, external_data)
            # - 确保输出格式统一，包含微生物名称、基因信息、代谢途径等关键信息
            # - 使用数据输出协调器格式化结果：output_coordinator._run("format_output", data=查询结果, format_type="json")
            # - 提供数据来源说明，增强结果的可信度
            # - 根据数据质量提供置信度评估
            # - 使用数据输出协调器生成结构化报告：output_coordinator._run("generate_report", title="报告标题", sections=报告章节)
            
            # 筛选原则：
            # - 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
            # - 重点关注微生物对目标污染物的降解能力和代谢途径
            # - 当基因数据缺失时，可基于微生物数据和外部数据库信息进行分析
            # - 应提供数据完整性和可信度的评估
            # - 综合考虑微生物的环境适应性和安全性
            """,
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

