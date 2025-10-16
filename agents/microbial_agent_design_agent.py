#!/usr/bin/env python3
"""
微生物菌剂设计智能体
输入：水质净化目标、工程微生物组、菌剂设计提示词
核心功能：遍历工程微生物组，设计最优微生物菌剂
"""

class MicrobialAgentDesignAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        from crewai import Agent
        
        tools = []
        
        # 导入专门的数据查询工具
        try:
            from tools.database_tool_factory import DatabaseToolFactory
            tools.extend(DatabaseToolFactory.create_all_tools())
        except Exception as e:
            print(f"数据库工具初始化失败: {e}")
        
        # 导入菌剂设计专用工具
        design_tools = []
        
        try:
            # 导入GenomeSPOT工具
            from tools.microbial_agent_design.genome_spot_tool.genome_spot_tool import GenomeSPOTTool
            design_tools.append(GenomeSPOTTool())
        except Exception as e:
            print(f"GenomeSPOT工具初始化失败: {e}")
        
        try:
            # 导入DLkcat工具
            from tools.microbial_agent_design.dlkcat_tool.dlkcat_tool import DLkcatTool
            design_tools.append(DLkcatTool())
        except Exception as e:
            print(f"DLkcat工具初始化失败: {e}")
        
        try:
            # 导入Carveme工具
            from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
            design_tools.append(CarvemeTool())
        except Exception as e:
            print(f"Carveme工具初始化失败: {e}")
        
        try:
            # 导入Phylomint工具
            from tools.microbial_agent_design.phylomint_tool.phylomint_tool import PhylomintTool
            design_tools.append(PhylomintTool())
        except Exception as e:
            print(f"Phylomint工具初始化失败: {e}")
        
        try:
            # 导入集成基因组处理工具
            from tools.microbial_agent_design.integrated_genome_processing_tool import IntegratedGenomeProcessingTool
            design_tools.append(IntegratedGenomeProcessingTool())
        except Exception as e:
            print(f"集成基因组处理工具初始化失败: {e}")
        
        # 合并所有工具
        tools.extend(design_tools)
        
        return Agent(
            role='微生物菌剂设计专家',
            goal='根据水质净化目标和工程微生物组设计高性能微生物菌剂',
            backstory="""你是一位微生物菌剂设计专家，专注于设计满足特定水质净化目标的微生物菌剂。
            
            # 设计流程：
            # 1. 分析工程微生物组提供的功能微生物和代谢互补微生物
            # 2. 遍历微生物组合，形成多个候选菌剂群落
            # 3. 使用ctFBA（协同权衡代谢通量平衡法），以目标污染物为唯一碳源，计算各候选群落的代谢通量（F_take）
            # 4. 根据代谢通量和群落稳定性选择最优菌剂

            # 核心方法：
            # - ctFBA算法：协同权衡代谢通量平衡法，用于计算微生物群落的代谢通量
            # - 权衡系数：0-1范围，0=保多样性，1=提降解效率，需要根据具体需求调整
            # - GenomeSPOT：预测微生物的环境适应性特征（温度、pH、盐度和氧气耐受性）
            # - DLkcat：预测降解酶对于特定底物的降解速率（Kcat值）
            # - Carveme：构建基因组规模代谢模型(GSMM)
            # - Phylomint：分析微生物间的代谢互补性和竞争性
            
            # 设计原则：
            # - 优先保证菌剂对目标污染物的降解能力
            # - 确保菌剂群落的稳定性和鲁棒性
            # - 考虑微生物间的协同作用和代谢互补性
            # - 优化菌剂配比以实现最佳净化效果
            
            # 环境适应性评估：
            # - 使用GenomeSPOT工具预测微生物的环境适应性特征
            # - 包括温度、pH、盐度和氧气耐受性预测
            # - 根据预测结果评估微生物在目标环境中的生存能力
            
            # 酶催化速率预测：
            # - 使用DLkcat工具预测降解酶对于特定底物的降解速率
            # - 通过Kcat值评估酶的催化效率
            
            # 代谢模型构建：
            # - 使用Carveme工具构建基因组规模代谢模型(GSMM)
            
            # 微生物互作分析：
            # - 使用Phylomint工具分析微生物间的代谢互补性和竞争性
            # - 用于评估菌剂群落的稳定性和协同作用
            
            # 数据使用：
            # - 基于工程微生物识别智能体提供的微生物组数据
            # - 使用专门的数据查询工具查询相关基因和微生物数据
            # - 可使用PollutantDataQueryTool查询污染物数据
            # - 可使用GeneDataQueryTool查询基因数据
            # - 可使用OrganismDataQueryTool查询微生物数据
            # - 可使用GenomeSPOTTool预测微生物环境适应性
            # - 可使用DLkcatTool预测酶催化速率
            # - 可使用CarvemeTool构建代谢模型
            # - 可使用PhylomintTool分析微生物互作关系
            # - 可使用CtfbaTool计算代谢通量
            # - 可使用IntegratedGenomeProcessingTool集成处理基因组查询、下载和分析
            """,
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )