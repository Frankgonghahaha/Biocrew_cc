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
        
        ### Step 0：解析识别结果（准备工具输入）
        1. 读取最新的 `IdentificationAgent_Result_*.json`；
        2. 调用 `ParseDegradationJSONTool` 提取 `functional_microbes` 的 `enzymes.name`、`enzymes.sequence` 以及 `metadata.pollutant.smiles`；
        3. 调用 `ParseEnvironmentJSONTool` 收集功能菌与互补菌的物种清单，并解析 `metadata.target_environment`（temperature / ph / salinity / oxygen），标注缺失字段。
        
        ### Step 1：降解功能打分
        1. 以 Step 0 的酶序列集合为输入，调用 `ScoreEnzymeDegradationTool`（`core/tools/design/score_enzyme_degradation_tool.py`）计算各菌株的 kcat 指标，并记录归一化结果（沿用旧版命名 `Norm1(kcat)`，即本文使用的 `Norm01(kcat_max)`）；
        2. 对互补菌的 `Norm01(kcat_max)` 固定为 0，并在记录中说明原因；
        3. 汇总工具返回的 `kcat_max`、`kcat_mean` 与序列明细，为后续评分使用。
        
        ### Step 2：环境适应性打分
        1. 使用 Step 0 的物种清单与目标环境参数，调用 `ScoreEnvironmentTool`（`core/tools/design/score_environment_tool.py`）统一计算 `env_soft_score`；
        2. 记录工具返回的四项子评分，确认权重 `wT=0.35、wPH=0.35、wS=0.10、wO2=0.20` 已生效；
        3. 标注明确评分来源与缺失项，作为综合分析依据。
        
        ### Step 3：单菌综合评分
        1. 将 Step 1 与 Step 2 的结果输入 `ScoreSingleSpeciesTool`（`core/tools/design/score_single_species_tool.py`），执行归一化：`Norm01(kcat_max)`（互补菌固定 0，报告中保留 `Norm1(kcat)` 别名）、`env_soft_score`、`Norm01(enzyme_diversity)`（并在说明中保留旧版命名 `Norm1(enzyme_diversity)` 以保持兼容）；
        2. 应用统一公式 `S_microbe = 0.5 * Norm1(kcat) + 0.4 * env_soft_score + 0.1 * Norm01(enzyme_diversity)`（解释 `Norm1(kcat)` 与 `Norm01(kcat_max)` 等价，`Norm1(enzyme_diversity)` 与 `Norm01(enzyme_diversity)` 等价，以兼容旧版日志）；
        3. 生成功能菌与互补菌的评分明细，记录原始数据、缺失补偿策略与工具调用日志。
        
        ### Step 4：互作强度计算
        1. 将 Step 0 中的功能菌与互补菌物种清单输入 `ScoreMetabolicInteractionTool`（`core/tools/design/score_metabolic_tool.py`）；
        2. 输出每对物种的 competition / complementarity / delta 指标，必要时补充 `MicrobialComplementarityDBQueryTool` 数据；
        3. 对结果进行去重与数据来源标注，为群落打分做准备。
        
        ### Step 5：菌群组合评分
        1. 使用 Step 3 的单菌评分与 Step 4 的互作指标，调用 `ScoreConsortiaTool`（`core/tools/design/score_consortia_tool.py`），构建候选菌群并计算 `S_consort = α·avg(S_microbe) + β·avg(delta⁺) - γ·avg(comp⁺) + λ·avg(kcat_max) - μ·size`；
        2. 输出前 10 个菌群组合的评分表（列：consortium_id、members、size、avg_S_microbe、avg_delta_pos、avg_comp_pos、avg_kcat、S_consort、used_pairs、source_count），并说明选择理由与风险；
        3. 提炼评估阶段复核要点（环境敏感参数、潜在竞争关系、数据缺口）。
        
        ### 工具使用策略
        - ParseDegradationJSONTool / ParseEnvironmentJSONTool：保证降解评分与生境评分的输入结构化、可复用；
        - ScoreEnzymeDegradationTool：评估功能菌酶降解能力；互补菌保持 0 分；
        - ScoreEnvironmentTool：环境评分权重与三角隶属/指数衰减由工具统一实现；
        - ScoreSingleSpeciesTool：合并 kcat、环境与酶多样性信息生成 `S_microbe`；
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
