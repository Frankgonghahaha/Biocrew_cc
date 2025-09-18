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
        
        # 导入统一数据工具
        try:
            from tools.unified_data_tool import UnifiedDataTool
            unified_tool = UnifiedDataTool()
            tools = [unified_tool]
        except Exception as e:
            print(f"工具初始化失败: {e}")
            tools = []
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标筛选功能微生物和代谢互补微生物',
            backstory="""你是一位功能微生物组识别专家，专注于从数据库获取领域知识以识别最适合的工程微生物。
            
            # 核心能力：
            # 1. 使用统一数据访问工具一站式查询所有相关数据
            # 2. 基于微调大语言模型，按"互补指数＞竞争指数"筛选功能微生物
            # 3. 重点关注微生物对目标污染物的降解能力和代谢途径
            
            # 工具使用：
            # - unified_tool._run({"operation": "query_pollutant_data", "pollutant_name": "目标污染物"})
            # - unified_tool._run({"operation": "get_pollutant_summary", "pollutant_name": "目标污染物"})
            # - unified_tool._run({"operation": "search_pollutants", "keyword": "搜索词"})
            
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

