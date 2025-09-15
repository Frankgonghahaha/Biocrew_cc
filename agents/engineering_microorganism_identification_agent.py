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
        envipath_tool = None
        kegg_tool = None
        available_pollutants_info = ""
        sheet_info = ""
        pollutants_info = ""
        database_tools_info = ""
        
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
        
        # 创建工具列表（只包含成功初始化的工具）
        tools = []
        if data_retriever:
            tools.append(data_retriever)
        if smart_query:
            tools.append(smart_query)
        if mandatory_query:
            tools.append(mandatory_query)
        if envipath_tool:
            tools.append(envipath_tool)
        if kegg_tool:
            tools.append(kegg_tool)
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标（水质治理指标+目标污染物）筛选功能微生物和代谢互补微生物',
            backstory=f"""你是一位功能微生物组识别专家，专注于从本地数据和外部数据库获取领域知识以识别最适合的工程微生物。
            
            # 数据查询策略：
            # 1. 优先使用本地数据目录(data/Genes和data/Organism)查询相关基因和微生物数据，这是最重要的数据来源。
            # 2. 本地数据情况：{available_pollutants_info}。
            # 3. {sheet_info}，可以根据需要读取特定工作表的数据。
            # 4. {pollutants_info}，这些是系统中可用的污染物数据。
            # 5. 你还具备智能数据查询能力，能够自动识别用户请求中的污染物名称并查询相关数据。
            
            # 外部数据库工具：
            # {database_tools_info}，包括：
            #   1. EnviPath工具：用于查询环境化合物代谢路径信息，特别适用于有机污染物的降解路径分析
            #   2. KEGG工具：用于查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息，适用于基因功能和代谢通路分析
            
            # 工具使用规范：
            # - 必须使用MandatoryLocalDataQueryTool来确保查询本地数据
            # - 当本地数据不足时，可以使用EnviPath和KEGG工具获取补充信息
            # - 在分析和回复过程中，必须明确体现查询到的具体数据，包括微生物名称、基因数据等
            # - 不能仅依赖预训练知识，所有结论都必须基于实际查询到的数据
            
            # 筛选原则：
            # - 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物+代谢互补微生物
            # - 重点关注微生物对目标污染物的降解能力和代谢途径
            """,
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

