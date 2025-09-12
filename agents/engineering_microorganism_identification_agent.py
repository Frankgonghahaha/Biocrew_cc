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
        
        # 导入本地数据读取工具
        try:
            from tools.local_data_retriever import LocalDataRetriever
            from tools.smart_data_query_tool import SmartDataQueryTool
            from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool
            from tools.envipath_tool import EnviPathTool
            from tools.kegg_tool import KeggTool
            data_retriever = LocalDataRetriever(base_path=".")
            smart_query = SmartDataQueryTool(base_path=".")
            mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
            envipath_tool = EnviPathTool()
            kegg_tool = KeggTool()
            
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
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标（水质治理指标+目标污染物）筛选功能微生物和代谢互补微生物',
            backstory=f"""你是一位功能微生物组识别专家，专注于从公开数据库（Web of Science、HydroWASTE、KEGG、NCBI、EnviPath）和本地数据获取领域知识。
            # 你必须优先使用本地数据目录(data/Genes和data/Organism)查询相关基因和微生物数据，这是最重要的数据来源。
            # 你也可以从本地数据目录读取基因和微生物数据，{available_pollutants_info}。
            # {sheet_info}，可以根据需要读取特定工作表的数据。
            # 你还具备智能数据查询能力，能够自动识别用户请求中的污染物名称并查询相关数据。
            # {pollutants_info}，这些是系统中可用的污染物数据。
            # {database_tools_info}，包括：
            #   1. EnviPath工具：用于查询环境化合物代谢路径信息
            #   2. KEGG工具：用于查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息
            # 重要：在分析和回复过程中，你必须明确体现本地数据查询的结果，包括具体的微生物名称、基因数据等，
            # 不能仅依赖预训练知识。你的回复需要包含从本地Excel文件中查询到的具体数据。
            # 你必须使用MandatoryLocalDataQueryTool来确保查询本地数据。
            
            # TODO: 实现Tool_api和Tool_Carveme工具的调用
            # TODO: 实现基于互补指数和竞争指数的筛选算法
            """,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

