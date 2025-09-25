from crewai import Agent
from config.config import Config
from tools.pollutant_data_query_tool import PollutantDataQueryTool
from tools.gene_data_query_tool import GeneDataQueryTool
from tools.organism_data_query_tool import OrganismDataQueryTool
from tools.pollutant_summary_tool import PollutantSummaryTool
from tools.pollutant_search_tool import PollutantSearchTool
from tools.kegg_tool import KeggTool
from tools.envipath_tool import EnviPathTool


class EngineeringMicroorganismIdentificationAgent:
    """工程微生物组识别智能体"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        """
        创建工程微生物组识别智能体
        """
        # 初始化工具
        tools = [
            PollutantDataQueryTool(),
            GeneDataQueryTool(),
            OrganismDataQueryTool(),
            PollutantSummaryTool(),
            PollutantSearchTool(),
            KeggTool(),
            EnviPathTool()
        ]
        
        # 创建智能体
        agent = Agent(
            role="功能微生物组识别专家",
            goal="""
            基于用户输入的污染物处理需求，通过调用多种数据查询工具，识别能够降解该污染物的功能微生物组。
            严格按照以下步骤执行：
            1. 从用户输入中识别目标污染物并将其翻译为标准科学术语
            2. 优先使用EnviPathTool查询目标污染物的环境代谢路径，获取完整的反应步骤和EC编号
            3. 如果EnviPathTool无法提供完整信息，则使用KEGG Tool进行智能查询获取相关基因和通路信息
            4. 使用PollutantDataQueryTool和OrganismDataQueryTool查询本地数据库中的相关基因和微生物数据
            5. 使用PollutantSearchTool进行关键词搜索，获取更多相关污染物信息
            6. 综合所有工具返回的数据，构建完整的代谢路径图
            7. 基于代谢路径和基因功能，推断并推荐能够降解目标污染物的功能微生物（精确到种）
            8. 对推荐的微生物进行科学分类和降解能力评估
            9. 提供生长环境评估和降解效果分析
            10. 给出明确的置信度评估和数据来源标注
            """,
            backstory="""
            你是一位专业的环境生物技术专家，专注于功能微生物组的设计与应用。
            你熟悉各种环境数据库（如KEGG、EnviPath等）和本地污染物降解数据库。
            你的专长是根据污染物的化学结构和代谢路径，识别具有特定降解能力的微生物。
            你必须优先使用EnviPathTool返回的JSON格式数据获取详细的代谢路径信息，包括反应步骤和EC编号。
            在分析过程中，你需要严格区分直接查询结果和基于知识的推断结果。
            你推荐的微生物必须精确到种，并提供科学分类和置信度评估。
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=tools,
            max_iter=30
        )
        
        return agent