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
            from core.tools.design.parse1_json_tool import ParseDegradationJSONTool
            tools.append(ParseDegradationJSONTool())
            design_stage_tools_info.append("ParseDegradationJSONTool")
        except Exception as e:
            design_stage_tools_info.append(f"ParseDegradationJSONTool 初始化失败: {e}")

        try:
            from core.tools.design.parse2_json_tool import ParseEnvironmentJSONTool
            tools.append(ParseEnvironmentJSONTool())
            design_stage_tools_info.append("ParseEnvironmentJSONTool")
        except Exception as e:
            design_stage_tools_info.append(f"ParseEnvironmentJSONTool 初始化失败: {e}")

        try:
            from core.tools.design.score_environment_tool import ScoreEnvironmentTool
            tools.append(ScoreEnvironmentTool())
            design_stage_tools_info.append("ScoreEnvironmentTool")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreEnvironmentTool 初始化失败: {e}")

        try:
            from core.tools.design.score_enzyme_degradation_tool import (
                ScoreEnzymeDegradationTool,
            )
            tools.append(ScoreEnzymeDegradationTool())
            design_stage_tools_info.append("ScoreEnzymeDegradationTool")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreEnzymeDegradationTool 初始化失败: {e}")

        try:
            from core.tools.design.score_single_species_tool import ScoreSingleSpeciesTool
            tools.append(ScoreSingleSpeciesTool())
            design_stage_tools_info.append("ScoreSingleSpeciesTool")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreSingleSpeciesTool 初始化失败: {e}")

        try:
            from core.tools.database.complementarity_query import (
                MicrobialComplementarityDBQueryTool,
            )
            tools.append(MicrobialComplementarityDBQueryTool())
            design_stage_tools_info.append("微生物互补性数据库查询工具")
        except Exception as e:
            design_stage_tools_info.append(
                f"微生物互补性数据库查询工具 初始化失败: {e}"
            )

        try:
            from core.tools.design.score_candidate_tool import ScoreCandidateTool
            tools.append(ScoreCandidateTool())
            design_stage_tools_info.append("ScoreCandidateTool")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreCandidateTool 初始化失败: {e}")

        try:
            from core.tools.design.score_metabolic_tool import (
                ScoreMetabolicInteractionTool,
            )
            tools.append(ScoreMetabolicInteractionTool())
            design_stage_tools_info.append("ScoreMetabolicInteractionTool")
        except Exception as e:
            design_stage_tools_info.append(
                f"ScoreMetabolicInteractionTool 初始化失败: {e}"
            )

        try:
            from core.tools.design.score_consortia_tool import ScoreConsortiaTool
            tools.append(ScoreConsortiaTool())
            design_stage_tools_info.append("ScoreConsortiaTool")
        except Exception as e:
            design_stage_tools_info.append(f"ScoreConsortiaTool 初始化失败: {e}")

        design_stage_tools_summary = (
            "; ".join(design_stage_tools_info)
            if design_stage_tools_info
            else "核心设计工具初始化成功"
        )
        database_tools_info = "已加载微生物互补性数据库查询工具辅助互作补充"

        return Agent(
            role='微生物菌剂设计专家',
            goal='基于功能微生物组设计高效且稳定的微生物菌剂',
            backstory=f"""你是一位微生物菌剂设计专家，现在的设计流程以 IdentificationAgent 输出的 JSON 结果为核心输入。
            
            ## Step 0：识别结果解析
            - 读取最新的 `IdentificationAgent_Result_*.json` 文件，使用 ParseDegradationJSONTool 提取功能菌酶名称、酶序列及 `metadata.pollutant.smiles`；
            - 使用 ParseEnvironmentJSONTool 获取功能菌与互补菌物种清单，以及目标环境参数（temperature / ph / salinity / oxygen）；
            - 若缺失污染物 SMILES 或关键环境信息，立即记录缺口并尝试通过数据库工具补齐后再进入评分。
            
            ## Step 1：降解能力评分（ScoreEnzymeDegradationTool）
            - 对 ParseDegradationJSONTool 返回的物种集合执行酶降解评分，输出每个物种的 `kcat_max`、`kcat_mean` 与序列级统计；
            - 互补微生物不承担降解任务，通常无酶序列，需将其 `Norm01(kcat_max)`（旧版命名 `Norm1(kcat)`）固定为 0，并在结果中说明原因；
            - 保存工具调用参数与返回值，确保后续追踪。
            
            ## Step 2：环境适应性评分（ScoreEnvironmentTool）
            - 以 ParseEnvironmentJSONTool 返回的物种清单为基准，统一调用 ScoreEnvironmentTool；
            - 传入目标环境参数，记录 `env_soft_score` 及四项子评分，确认权重 `wT=0.35、wPH=0.35、wS=0.10、wO2=0.20`，并标明缺失项的处理策略。
            
            ## Step 3：单菌综合评分（ScoreSingleSpeciesTool）
            - 将 Step 1 与 Step 2 的结果输入 ScoreSingleSpeciesTool，自动执行归一化计算；
            - 套用统一公式 `S_microbe = 0.5·Norm1(kcat) + 0.4·env_soft_score + 0.1·Norm01(enzyme_diversity)`（其中 `Norm1(kcat)` 与 `Norm01(kcat_max)` 等价，`Norm1(enzyme_diversity)` 与 `Norm01(enzyme_diversity)` 等价）；
            - 生成功能菌与互补菌的综合评分表，并保留 `Result_functional_candidates.csv` / `Result_complementary_candidates.csv` 等结构化输出。
            
            ## Step 4：互作强度与菌群设计
            - 借助 ScoreMetabolicInteractionTool（可由 MicrobialComplementarityDBQueryTool 辅助）计算 competition / complementarity / delta 指标；
            - 使用 ScoreConsortiaTool 将 `S_microbe` 与互作指标融合，计算 `S_consort = α·avg(S_microbe) + β·avg(delta⁺) - γ·avg(comp⁺) + λ·avg(kcat_max) - μ·成员数量`；
            - 输出前 10 个菌群组合列表，包含评分拆解、环境匹配与风险提示，为评估阶段提供依据。
            
            ## 已初始化工具
            - 设计支持工具：{design_stage_tools_summary}
            - 其他工具：{database_tools_info}
            
            ## 输出要求
            - 准确记录 ScoreEnvironmentTool / ScoreEnzymeDegradationTool 的调用参数与结果，互补微生物的 kcat 评分固定为 0；
            - 输出功能菌与互补菌的单独评分表、组合设计表、设计说明文档，并给评估阶段提供重点复核清单；
            - 说明缺失数据及补救措施，确保设计阶段结果可复现、可追踪。
            """,
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
