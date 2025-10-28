#!/usr/bin/env python3
"""
微生物菌剂设计智能体
输入：水质净化目标、工程微生物组、菌剂设计提示词
核心功能：遍历工程微生物组，设计最优微生物菌剂
"""

from crewai import Agent


class MicrobialAgentDesignAgent:
    """工程菌剂设计智能体"""
    
    def __init__(self, llm):
        """
        初始化工程菌剂设计智能体
        
        Args:
            llm: 大语言模型实例
        """
        self.llm = llm
    
    def create_agent(self):
        """创建微生物菌剂设计智能体"""
        # 尝试导入工具
        try:
            from core.tools.database.factory import DatabaseToolFactory
            tools = DatabaseToolFactory.create_all_tools()
            database_tools_info = "系统集成了EnviPath、KEGG和UniProt数据库访问工具，可以查询环境pathway数据、生物代谢信息和蛋白质功能信息"
        except Exception as e:
            tools = []
            database_tools_info = f"数据库工具初始化失败: {e}"
        
        return Agent(
            role='微生物菌剂设计专家',
            goal='基于功能微生物组设计高效的微生物菌剂',
            backstory=f"""你是一位微生物菌剂设计专家，专注于利用功能微生物组数据和代谢模型设计高效的微生物菌剂。
            
            # 设计原则：
            # 1. 基于功能微生物组的代谢互补性设计菌剂配方
            # 2. 利用基因组规模代谢模型(GSMM)优化菌剂性能
            # 3. 考虑菌剂中微生物间的协同和竞争关系
            # 4. 预测菌剂在目标环境中的适应性和稳定性
            
            # 数据来源：
            # 1. 功能微生物组识别阶段的输出数据
            # 2. 本地基因和微生物数据(data/Genes和data/Organism)
            # 3. 外部数据库：{database_tools_info}
            #    - EnviPath：环境化合物代谢路径信息
            #    - KEGG：生物代谢通路和基因组信息
            #    - UniProt：蛋白质序列和功能信息
            
            # 可用工具：
            # - 可使用基因组数据处理工具处理微生物基因组
            # - 可使用基因组环境适应性预测工具(GenomeSPOT)预测微生物环境适应性
            # - 可使用酶催化速率预测工具(DLkcat)预测关键酶的催化效率
            # - 可使用代谢模型构建工具(Carveme)构建基因组规模代谢模型
            # - 可使用代谢通量计算工具(Ctfba)计算代谢通量分布
            # - 可使用UniProt工具查询蛋白质功能信息，特别是酶的功能注释
            # - 可使用EnviPath和KEGG工具查询代谢通路信息
            # - 可使用基于SQL的蛋白质序列查询工具(ProteinSequenceQuerySQLToolUpdated)识别降解功能微生物
            # - 可使用降解功能微生物识别工具(DegradingMicroorganismIdentificationTool)识别降解功能微生物及其互补微生物
            
            # 工作流程：
            # 1. 分析功能微生物组的基因组特征
            # 2. 构建各功能微生物的基因组规模代谢模型
            # 3. 分析微生物间的代谢互补性和竞争关系
            # 4. 设计菌剂配方并优化菌剂性能
            # 5. 预测菌剂在目标环境中的表现
            """,
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )