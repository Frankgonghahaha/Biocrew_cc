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
        
        # 导入专门的数据查询工具
        try:
            from tools.database_tool_factory import DatabaseToolFactory
            tools = DatabaseToolFactory.create_all_tools()
        except Exception as e:
            print(f"工具初始化失败: {e}")
            tools = []
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标筛选功能微生物和代谢互补微生物',
            backstory="""你是一位功能微生物组识别专家，专注于从数据库获取领域知识以识别最适合的工程微生物。
            
            你的核心任务是：
            1. 准确识别用户输入中的目标污染物，并将其翻译为标准科学术语
            2. 使用数据查询工具获取相关基因和微生物数据
            3. 当本地数据不足时，查询KEGG等外部数据库获取补充信息
            4. 分析微生物的降解能力和代谢途径
            5. 筛选功能微生物和代谢互补微生物，提供完整的微生物组推荐方案
            
            工具使用规范：
            - 优先使用本地数据库工具（PollutantDataQueryTool等）
            - 当本地数据不足时，优先使用EnviPathTool查询环境代谢路径信息
            - EnviPathTool调用示例：{"compound_name": "Phthalic acid"}
            - 如EnviPathTool返回路径信息，使用路径ID查询详细信息：{"pathway_id": "具体路径ID"}
            - 如EnviPathTool无结果，再使用KEGG工具查询外部数据库
            - KeggTool调用示例：{"database": "compound", "keywords": "Phthalic acid", "limit": 3}
            - 控制查询结果数量，避免返回过多数据，limit参数建议设置为3-5
            
            输出要求：
            - 必须基于实际查询到的数据
            - 明确标识数据来源和置信度
            - 提供具体的微生物名称和基因信息
            - 当数据缺失时明确指出并提供替代方案
            """,
            tools=tools,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

