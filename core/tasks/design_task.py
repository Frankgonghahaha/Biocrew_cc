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
        根据工程微生物识别结果 JSON 及目标水质条件，执行菌剂设计流程，输出可直接进入评估阶段的候选菌群。
        
        ### Step 0：解析识别结果
        1. 读取最新的 `IdentificationAgent_Result_*.json`；
        2. 解析 `metadata.pollutant`（含 SMILES）、`metadata.target_environment` 与 `functional_microbes`、`complements`；
        3. 记录每个微生物的酶信息（名称、UniProt ID、sequence），建立后续评分所需的数据结构。
        
        ### Step 1：环境适应性打分
        1. 对所有功能微生物与互补微生物调用 ScoreEnvironmentTool；
        2. 输入的环境参数为目标 temperature / pH / salinity / oxygen；
        3. 记录 ScoreEnvironmentTool 返回的 `env_soft_score` 与四项子评分，确保权重（wT=0.35, wPH=0.35, wS=0.10, wO2=0.20）按工具输出执行；
        4. 整理环境匹配评分及缺失说明，作为后续综合分析的基础。
        
        ### Step 2：降解功能打分
        1. 功能微生物：收集其有效氨基酸序列，调用 ScoreEnzymeDegradationTool，得到 kcat 估计及归一化结果；
        2. 互补微生物：直接设定 `Norm1(kcat)=0`，并说明原因；
        3. 汇总所有微生物的 kcat 统计信息，保留工具输出与缺失记录。
        
        ### Step 3：酶多样性打分
        1. 统计每个微生物去重后的酶种类数；
        2. 执行 0-1 归一化（Norm1），得到 `Norm1(enzyme_diversity)`；
        3. 标注数据来源与异常情况。
        
        ### Step 4：单菌综合评分
        1. 组合上述三类评分，默认 `S_microbe = 0.5·Norm1(kcat) + 0.4·env_soft_score + 0.1·Norm1(enzyme_diversity)`；
        2. 对互补微生物保持统一公式（因 `Norm1(kcat)=0`）；
        3. 形成功能菌与互补菌的候选清单，记录原始数据、工具调用情况及缺失项处理策略。
        
        ### Step 5：互作矩阵与菌群组合
        1. 整理 IdentificationAgent JSON 中的 competition / complementarity / delta 指标，必要时补充 MicrobialComplementarityDBQueryTool；
        2. 构建两两互作矩阵，保留指标来源；
        3. 基于 S_microbe 与互作指标执行组合搜索，计算 `S_consort = α·avg(S_microbe) + β·avg(delta⁺) - γ·avg(comp⁺) + λ·avg(kcat_max) - μ·size`；
        4. 在报告中以表格形式列出前 10 个菌群组合的评分情况（列：consortium_id、members、size、avg_S_microbe、avg_delta_pos、avg_comp_pos、avg_kcat、S_consort、used_pairs、source_count），并附风险提示；
        5. 提炼评估阶段的复核要点（环境敏感参数、潜在竞争关系）。
        
        ### 工具使用策略
        - ScoreEnvironmentTool：环境评分权重与三角隶属/指数衰减由工具统一实现；
        - ScoreEnzymeDegradationTool：评估功能菌酶降解能力；互补菌保持 0 分；
        - MicrobialComplementarityDBQueryTool：如需补充互作信息时调用；
        - 输出前 10 个组合的评分表时，同时生成 `test_results/DesignAgent/DesignAgent_<时间戳>.json`（ISO8601 时间格式，将冒号替换为短横），包含 `consortium_id`、`members`、`size`、`avg_S_microbe`、`avg_delta_pos`、`avg_comp_pos`、`avg_kcat`、`S_consort`、`used_pairs`、`source_count` 字段，便于后续评估阶段直接读取。
        
        关键输出需覆盖单菌评分、互作分析、组合评分三大层级，保证评估智能体可以直接复用设计结果。
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        1. 设计报告：总结目标工况、单菌评分逻辑、组合筛选策略、风险提示与培育条件建议，并附上前 10 个组合评分表格（列：consortium_id、members、size、avg_S_microbe、avg_delta_pos、avg_comp_pos、avg_kcat、S_consort、used_pairs、source_count）
        2. 单菌评分明细：包含环境适应性、kcat 估计、酶多样性及工具调用说明
        3. 互作分析摘要：列出关键的 competition / complementarity / delta 指标及数据来源
        4. 菌群组合评估：给出最佳组合、评分拆解、风险提示与实验建议，并将前 10 个组合的评分数据写入 `test_results/DesignAgent/DesignAgent_<时间戳>.json`
        5. 供评估阶段使用的复核要点：需要重点验证的组合、潜在风险点、建议关注的环境参数
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
