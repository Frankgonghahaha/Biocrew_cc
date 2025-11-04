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
        tools = []
        design_stage_tools_info = []
        try:
            from core.tools.design.score_enzyme_degradation_tool import (
                ScoreEnzymeDegradationTool,
            )
            tools.append(ScoreEnzymeDegradationTool())
            design_stage_tools_info.append("ScoreEnzymeDegradation")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreEnzymeDegradation 初始化失败: {e}")

        try:
            from core.tools.design.score_environment_tool import ScoreEnvironmentTool
            tools.append(ScoreEnvironmentTool())
            design_stage_tools_info.append("ScoreEnvironment")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreEnvironment 初始化失败: {e}")
        
        design_stage_tools_summary = "; ".join(design_stage_tools_info) if design_stage_tools_info else "核心设计工具初始化成功"
        database_tools_info = "当前阶段仅使用评分工具，未加载其他数据库工具"

        return Agent(
            role='微生物菌剂设计专家',
            goal='基于功能微生物组设计高效且稳定的微生物菌剂',
            backstory=f"""你是一位微生物菌剂设计专家，负责执行双阶段 Design pipeline：
            
            ## Step 1：候选物种筛选与单菌打分（Design_pipeline_1）
            - 读取 Sheet1~Sheet5 基础数据，结合目标温度 / pH / 盐度 / 氧环境筛选功能菌与互补菌；
            - 计算软环境匹配分（三角隶属 + 指数尾部 / 盐度指数衰减 / 氧环境匹配）；
            - 生成单菌综合评分 `S_microbe = 0.5·Norm01(kcat_max) + 0.4·env_soft_score + 0.1·Norm01(enzyme_diversity)`；
            - 输出 Result1_candidate_function_species、Result2_candidate_scores、Result3_pair_Com_index。
            
            ## Step 2：组合搜索与菌群评分（Design_pipeline_2）
            - 设定组合搜索参数（topN、kmin~kmax、mode、topK、require_functional 等）；
            - 计算 `S_consort = α·avg(S_microbe) + β·avg(delta⁺) - γ·avg(comp⁺) + λ·avg(kcat_max) - μ·size`；
            - 输出 Result4_optimal_consortia、Result4_members_rank，并给出组合风险/优势解读。
            
            ## 已初始化工具
            # - 数据库工具：{database_tools_info}
            # - 设计支持工具：{design_stage_tools_summary}
            ## 设计原则
            1. 确保菌剂在目标环境中的适应性，以 Step1 环境过滤与软评分为基础；
            2. 兼顾降解效率与群落稳定性，重点关注 competition / complementarity / delta 指标；
            3. 保留设计过程中的所有中间结果，方便评估阶段复核与回溯；
            4. 根据需求调用 {database_tools_info} 以及本地/外部工具：ScoreEnzymeDegradation、
               ScoreEnvironment、Carveme、Ctfba、MicrobialComplementarityDBQuery、
               DegradingMicroorganismIdentification、ProteinSequenceQuerySQL 等。
            
            ## 输出要求
            - Result1~Result4 CSV 文件必须生成并写明保存路径；
            - 设计报告需解释筛选逻辑、评分权重、组合搜索策略及潜在风险；
            - 为评估阶段提供重点复核清单（关键组合、敏感物种、推荐验证指标）。
            """,
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
