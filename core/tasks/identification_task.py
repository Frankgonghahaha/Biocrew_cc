#!/usr/bin/env python3
"""
微生物识别任务
定义工程微生物识别任务的创建和配置
"""

from crewai import Task
from textwrap import dedent
from core.tools.database.factory import DatabaseToolFactory


class MicroorganismIdentificationTask:
    """微生物识别任务类"""
    
    def __init__(self, llm):
        """
        初始化微生物识别任务
        
        Args:
            llm: 大语言模型实例
        """
        self.llm = llm

    def create_task(self, agent, user_requirement: str, protein_sequence_results: dict | None = None) -> Task:
        """
        创建微生物识别任务实例
        
        Args:
            agent: 执行任务的智能体
            user_requirement: 用户需求描述
            
        Returns:
            Task: 配置好的任务实例
        """
        # 创建工具实例
        tools = DatabaseToolFactory.create_all_tools()
        
        sequence_context = ""
        if protein_sequence_results:
            sequence_context = dedent("""
                ---
                
                ## 已有的蛋白质序列比对结果（供参考和进一步分析）
                {sequence_results}
                
                > 请基于上述已识别的潜在降解功能微生物，调用相关工具（特别是MicrobialComplementarityDBQueryTool）进一步分析互补微生物组合。
            """).format(sequence_results=protein_sequence_results)
        
        sequence_results = getattr(self, "sequence_results", None)
        sequence_context = ""
        if sequence_results:
            sequence_context = dedent("""
                
                ---
                
                ## 已有的蛋白质序列比对结果（供参考和进一步分析）
                {sequence_results}
                
                > 请基于上述已识别的潜在降解功能微生物，调用相关工具（特别是MicrobialComplementarityDBQueryTool）进一步分析互补微生物组合。
            """).format(sequence_results=sequence_results)
        else:
            sequence_context = dedent("""
                
                ---
                
                ## 已有的蛋白质序列比对结果（供参考和进一步分析）
                尚未提供预先计算的序列比对结果。请在任务执行过程中调用ProteinSequenceQuerySQLTool获取结果，并基于识别出的降解功能微生物及时使用MicrobialComplementarityDBQueryTool分析互补微生物组合。
            """)
        
        description_template = dedent("""
                根据降解污染物，识别出降解功能微生物清单及其互补微生物，形成一份包含功能微生物和互补微生物在内的工程微生物清单。
                
                识别步骤：
                # 1. 分析水质净化目标（水质治理指标+目标污染物）
                # 2. 从用户输入中准确识别目标污染物并将其翻译为标准科学术语；完成后使用PollutantSummaryTool或PollutantDataQueryTool校验标准化名称、CAS号和化学式，如无法获取需在报告中声明数据缺失及原因
                # 3. 以第2步得到的污染物英文标准术语为输入，调用一次EnviPathEnhancedTool获取目标污染物的降解路径信息
                # 4. 使用同一英文标准术语仅针对起始降解步骤调用一次KeggTool，获取该步骤的降解基因、酶名称及EC编号；禁止扩展或推理至后续步骤（如EC 1.14.12.7）
                # 5. 针对步骤3和步骤4的直接查询结果，仅做信息整合并生成一张表格，列名依次为“降解路径、降解反应式、降解基因、降解酶、EC编号、KO号”，此阶段不得进行额外推理或补全
                # 6. 若步骤5表格中起始降解步骤的基因或酶名称缺失，可再次调用KeggTool，但仅限起始降解步骤（例如酯水解，对应EC 3.1.1.- 或其具体编号）；优先使用KO号检索Symbol和Name，若仅有EC编号则去除通配符“-”后查询Orthology获取KO号；若仍无结果需记录原因，并不得针对后续步骤发起查询
                # 7. 使用步骤6补全后的表格，分析中间产物毒性并确定需要构建的降解终点
                # 8. 功能微生物清单组成一：结合步骤6和步骤7的结果，推荐具备降解功能的微生物
                # 9. 功能微生物清单组成二：以步骤6确定的降解基因为输入，必须先调用UniProtTool检索起始酶（如pehA）的蛋白质序列并记录检索结果；调用UniProtTool时只能使用具体的基因符号或已知的UniProt ID，禁止使用“carboxylesterase”等泛化酶名称；完成起始酶检索后再查询其它路径基因，必要时尝试文献中报道的具体蛋白ID，并在未获取到明确序列时记录失败原因及替代依据；
                # 10. 必须以检索到的降解酶氨基酸序列为输入，调用ProteinSequenceQuerySQLTool进行序列比对，固定参数min_identity=5、min_alignment_length=0、max_evalue=1e-5，输出比对结果并重点关注起始降解酶（如pehA）的匹配物种；如仍无结果需在报告中说明原因及后续处理建议。
                # 11. 识别互补微生物：基于步骤10识别出的降解功能微生物，以物种名称为输入，使用降解功能微生物识别工具(DegradingMicroorganismIdentificationTool)识别对应的互补微生物
                # 12. 整合步骤8、步骤9和步骤10的结果，形成最终工程微生物清单
                
                工具调用策略：
                # 1. 首先使用PollutantSummaryTool或PollutantDataQueryTool确定污染物的标准化名称及基础属性，若缺失需在报告中注明
                # 2. 按顺序调用一次EnviPathEnhancedTool、一次KeggTool并立即生成步骤5要求的表格，仅整合工具返回结果；KeggTool 调用仅限起始降解步骤
                # 3. 如需补全起始降解步骤信息，可再次调用KeggTool，但不得扩展到后续降解步骤；优先使用KO号补全Symbol与Name，若仅有EC编号需先查询Orthology获取KO号，并完整记录处理过程；若检索结果与预期功能不符，应在表格中使用推断基因名称（如pehA）并在备注中说明依据
                # 4. 使用UniProtTool查询关键降解酶的蛋白质序列和功能特性，必须优先完成起始水解酶检索，且查询输入只能使用具体基因符号或UniProt ID（如pehA、Q45087），禁止使用“carboxylesterase”等泛化酶名称；无论检索成功与否都需在报告中说明
                # 5. 在获取UniProt蛋白质序列后，使用基于SQL的蛋白质序列查询工具(ProteinSequenceQuerySQLTool)进行序列对比分析，统一使用min_identity=5、min_alignment_length=0、max_evalue=1e-5等参数，仅比对起始降解步骤的酶（如pehA）
                # 6. 使用降解功能微生物识别工具(DegradingMicroorganismIdentificationTool)识别降解功能微生物及其互补微生物
                # 7. 若两次KeggTool调用后仍缺少起始降解步骤的基因或酶名称，应在报告中列出缺失项及未能补全的原因，而非直接推断
                
                用户需求：{user_requirement}
{sequence_context}
                
{sequence_context}
                请严格遵循以下输出格式：
                
                # 工程微生物组识别报告：降解[污染物标准名称]的微生物组合
                
                ## 1. 目标污染物识别
                - **原始用户输入**：[用户原始输入]
                - **标准科学术语**：[标准化术语]
                - **化学式**：[化学式]
                - **CAS号**：[CAS号]
                - **分类**：[污染物分类]
                
                ## 2. 降解路径分析（基于EnviPathEnhancedTool + KeggTool）
                [展示步骤5生成并在步骤6补全的表格，列名依次为降解路径、降解反应式、降解基因、降解酶、EC编号、KO号；表格内容严格对应工具返回值及第二次KeggTool补全结果，如需使用推断信息必须在单元格内标注“(推断)”并在备注说明依据]
                
                > **完整降解路径**：[起始物质] → [中间产物1] → [中间产物2] → ... → [最终产物] 
                > **提示**：氨基酸序列仅需在结构化 JSON 中提供，避免在正文中重复输出
                ---
                
                ## 3. 工程微生物清单构建结果
                [以表格形式展示工程微生物清单结果，包含降解功能微生物物种名称、对应的互补微生物；若一个功能微生物有多种互补微生物，以顿号隔开，仅保留3种；请至少列出一株负责起始降解步骤的功能微生物]
                
                ## 4. 结构化结果（传递给DesignAgent）
                请在报告末尾附上一个 JSON，对应以下结构，并在生成后将完整 JSON 序列化保存到 `test_results/IdentificationAgent_Result_<ISO8601时间戳>.json`（例如 `IdentificationAgent_Result_2025-03-15T08-30-12.json`，其中冒号替换为破折号）：
                ```json
                {{
                  "functional_microbes": [
                    {{
                      "strain": "功能微生物物种名称",
                      "degradation_steps": [
                        "该功能微生物负责的降解反应式（从第2部分表格提取）"
                      ],
                      "enzymes": [
                        {{
                          "name": "酶名称",
                          "uniprot_id": "可选的 UniProt ID，若未知请设 null",
                          "sequence": "氨基酸序列"
                        }}
                      ],
                      "enzyme_diversity": 2,
                      "complements": [
                        {{
                          "strain": "互补微生物名称",
                          "relation_score": {{
                            "competition": 0.21,
                            "complementarity": 0.62,
                            "delta": 0.41
                          }},
                          "enzymes": [
                            {{
                              "name": "互补微生物酶名称",
                              "uniprot_id": null,
                              "sequence": "氨基酸序列；若无序列可用，则留空数组"
                            }}
                          ]
                        }}
                      ]
                    }}
                  ],
                  "metadata": {{
                    "pollutant": "目标污染物名称",
                    "target_environment": {{
                      "temperature": 25,
                      "ph": 7.0,
                      "salinity": 0.02,
                      "oxygen": "tolerant"
                    }},
                    "generated_at": "ISO8601 时间戳",
                    "source_agent": "IdentificationAgent vX.Y"
                  }}
                }}
                ```
                > 字段说明：
                > - `functional_microbes`：功能菌数组；每项需列出该菌的酶列表（名称 / UniProt ID / 氨基酸序列）。
                > - `degradation_steps`：列出该菌承担的降解步骤，内容来自第2部分“降解路径分析”中的降解反应式。
                > - `enzyme_diversity`：酶种类数量，可根据 `enzymes` 列表长度计算。
                > - `complements`：互补菌数组；`relation_score` 中保留 `competition` / `complementarity` / `delta` 三个指标，若缺失用 `null`。
                > - `metadata`：记录污染物、目标工况、生成时间与智能体版本，便于 DesignAgent 使用。
                --- 
                
            """)
        task = Task(
            description=description_template.format(
                user_requirement=user_requirement,
                sequence_context=sequence_context,
            ),
            agent=agent,
            expected_output=dedent("""
                完整的工程微生物组识别报告，包含：
                1. 目标污染物识别结果
                2. 详细的降解路径分析
                3. 工程微生物组清单（含关键功能微生物及互补微生物）
                4. 面向 DesignAgent 的 JSON 数据（结构参考描述，需同时保存至 `test_results/IdentificationAgent_Result_<ISO时间>.json`）
                5. 数据可信度评估

                报告应包含基于EC编号查询的基因信息，当查询无结果时应提供基于推断的结果和置信度评估。

            """),
            tools=tools
        )
        
        return task
