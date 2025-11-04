#!/usr/bin/env python3
"""
微生物菌剂设计任务
输入：水质净化目标、工程微生物组、菌剂设计提示词
核心功能：遍历工程微生物组，设计最优微生物菌剂
"""

class MicrobialAgentDesignTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        from crewai import Task
        
        description = """
        根据工程微生物识别结果及目标水质条件，完成双阶段菌剂设计流程，输出可直接进入评估阶段的候选菌群。
        
        ### Step 1：Design_pipeline_1（候选物种筛选与单菌打分）
        1. 整理核心输入表：Sheet1_Complementarity、Sheet2_Species_environment、Sheet3_Function_enzyme_kact、Sheet4_species_enzyme、Sheet5_PhyloMint；
        2. 依据目标温度 / pH / 盐度 / 氧环境筛选功能菌与互补菌，输出 `Result1_candidate_function_species.csv`；
        3. 计算软环境匹配分（温度、pH 采用三角隶属 + 指数尾部，盐度超限指数衰减，氧环境匹配评分）；
        4. 生成单菌综合得分 `S_microbe = 0.5·Norm01(kcat_max) + 0.4·env_soft_score + 0.1·Norm01(enzyme_diversity)`，输出 `Result2_candidate_scores.csv`；
        5. 融合 Sheet1 与 PhyloMint 构建两两互作矩阵（competition / complementarity / delta），输出 `Result3_pair_Com_index.csv`。
        
        ### Step 2：Design_pipeline_2（组合搜索与菌群评分）
        1. 以 Step1 产物为输入，设定搜索范围（topN、kmin/kmax、模式 greedy 或 exhaustive 等）；
        2. 组合得分 `S_consort = α·avg(S_microbe) + β·avg(delta⁺) - γ·avg(comp⁺) + λ·avg(kcat_max) - μ·size`；
        3. 输出最优组合列表 `Result4_optimal_consortia.csv`（含成员、综合得分、互作指标来源）；
        4. 输出成员贡献度排名 `Result4_members_rank.csv`，支持后续评估阶段重点关注关键物种；
        5. 对候选组合给出工况匹配和协同风险分析，为评估阶段提供明确复核要点。
        
        ### 工具使用策略
        - 使用 GenomeSPOTTool / SpeciesEnvironmentQueryTool 获取环境适配性；
        - 使用 DLkcatTool 汇总酶 Kcat 信息，配合 Sheet4 统计酶多样性；
        - 使用 MicrobialComplementarityDBQueryTool / PhyloMint 数据库计算互补与竞争指标；
        - 使用 CarvemeTool、CtfbaTool 等在需要时辅助验证模型可行性；
        - 对目标污染物调用 DegradingMicroorganismIdentificationTool、ProteinSequenceQuery 等数据库工具补充资料；
        - 保持原始数据与结果 CSV 的目录一致性，便于后续复核与评估阶段读取。
        
        关键输出需覆盖功能筛选、单菌评分、互作矩阵、组合评分四个层级，确保评估智能体能够直接复用相关结果。
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        1. Result1_candidate_function_species.csv：满足目标工况的功能菌候选及互补通过率统计
        2. Result2_candidate_scores.csv：功能菌与互补菌的单菌综合打分
        3. Result3_pair_Com_index.csv：两两互作矩阵（competition / complementarity / delta，注明数据来源）
        4. Result4_optimal_consortia.csv：最优菌群组合（含成员列表、S_consort、avg_kcat、互作指标均值等）
        5. Result4_members_rank.csv：成员贡献排名与关键物种说明
        6. 设计报告：总结目标工况、单菌评分逻辑、组合筛选策略、风险提示与培育条件建议
        7. 供评估阶段使用的复核要点：需要重点验证的组合、潜在风险点、建议关注的环境参数
        """
        
        # 如果有上下文任务，设置依赖关系
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent,
            'verbose': True
        }
        
        if context_task:
            task_params['context'] = [context_task]
            
        return Task(**task_params)
