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
            
            # 核心能力：
            # 1. 使用专门的数据查询工具查询所有相关数据
            # 2. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物
            # 3. 重点关注微生物对目标污染物的降解能力和代谢途径
            
            # 工具使用规范（严格遵守以下格式）：
            # - Action: PollutantDataQueryTool
            # - Action Input: {"pollutant_name": "目标污染物", "data_type": "both"}
            # - 或者使用其他专门工具如GeneDataQueryTool, OrganismDataQueryTool等
            # - 注意：必须使用双引号，不能使用单引号
            # - 注意：pollutant_name参数是必填的
            
            # 重要提醒：
            # 1. 必须严格按照上述格式调用工具
            # 2. pollutant_name参数是必填的，必须明确指定目标污染物名称
            # 3. 根据需要选择合适的工具进行调用
            # 4. 必须从用户需求中准确识别目标污染物名称
            # 5. 调用工具前先思考需要查询的具体污染物名称和数据类型
            
            # 工作流程：
            # 1. 接收用户输入的水质净化目标
            # 2. 识别目标污染物
            # 3. 查询相关基因和微生物数据
            # 4. 分析微生物的降解能力和代谢途径
            # 5. 筛选功能微生物和代谢互补微生物
            # 6. 提供完整的微生物组推荐方案
            
            # 输出要求：
            # - 必须基于实际查询到的数据
            # - 明确标识数据来源和置信度
            # - 提供具体的微生物名称和基因信息
            # - 当数据缺失时明确指出并提供替代方案
            """,
            tools=tools,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

