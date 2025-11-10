from __future__ import annotations

from crewai import Task


class MicrobialAgentEvaluationTask:
    """评估任务：解析菌剂组合并构建 FAA 文件"""

    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None):
        description = """
        请完成菌剂评估前的准备工作，确保评估所需的群落成员与蛋白序列文件齐全。

        ### Step 1：解析 DesignAgent 结果
        - 输入：`test_results/DesignAgent/DesignAgent.json`
        - 调用 `ParseDesignConsortiaTool`，解析 `consortium_id=1`（如需评估其他组合，可根据上下文调整）。
        - 输出：需要评估的菌剂成员列表（members list），并校验记录中的 `S_consort` 等关键字段。

        ### Step 2：构建 FAA 文件
        - 输入：Step 1 解析得到的 `members` 列表。
        - 调用 `FaaBuildTool`：
            - 依据成员名称查询数据库中的蛋白序列；
            - 将每个物种的氨基酸序列写入 `test_results/EvaluateAgent/faa/<物种>.faa`；
            - 如果文件已存在则跳过，避免重复生成；
            - 返回生成成功与缺失的物种信息，便于后续评估阶段补齐。

        ### Step 3：构建代谢模型
        - 输入：Step 2 的 FAA 目录。
        - 调用 `CarvemeModelBuildTool`：
            - 基于现有 FAA 文件批量运行 CarveMe；
            - 输出模型目录 `test_results/EvaluateAgent/Model`；
            - 若目标模型已存在则跳过构建，并在结果中说明。

        ### Step 4：生成推荐培养基
        - 输入：Step 3 输出的模型目录。
        - 调用 `MediumBuildTool`：
            - 递归扫描模型，使用 MICOM complete_medium / complete_community_medium 估算进口需求；
            - 按 p75 分档生成推荐培养基 CSV；
            - 输出目录 `test_results/EvaluateAgent/Medium/recommended_medium.csv`。

        ### Step 5：添加污染物降解路径
        - 输入：Step 3 或 Step 4 使用的模型目录（默认 `test_results/EvaluateAgent/Model`）。
        - 调用 `AddPathwayTool`：
            - 为每个模型添加 DBP → phthalate + butanol 的降解通路（含交换、转运、主反应）；
            - 输出到 `test_results/EvaluateAgent/Model_pathway`；
            - 若目标文件已存在则跳过，并在结果中记录。

        ### Step 6：MICOM 两步模拟
        - 输入：Step 5 输出的 `Model_pathway` 目录与 Step 4 的推荐培养基 CSV。
        - 调用 `MicomSimulationTool`：
            - 通过 MICOM 构建社区模型并执行“两阶段”优化；
            - 输出 `test_results/EvaluateAgent/MICOM/Result_MICOM.xlsx`（含总体结果、成员生长、可选 α 扫描与鲁棒性分析）。

        ### 输出要求
        1. 给出解析到的菌剂成员名单及其来源 JSON（包含 consortium 的关键指标，便于评估阶段引用）。
        2. 说明 FAA 构建结果：生成了哪些文件、缺失/跳过哪些物种、下一步如何处理。
        3. 记录代谢模型构建情况（生成/跳过的模型列表及输出目录）。
        4. 输出推荐培养基结果（CSV 路径、候选 EX 条目数量、调用模式）。
        5. 描述通路添加结果：新模型输出目录、处理的模型数、已存在而跳过的文件。
        6. 汇总 MICOM 模拟结果：输出路径、Biomass_max、阶段二摄入通量及 α 扫描/鲁棒性运行情况。
        7. 若某些物种缺少序列或模型，需在报告中记录原因并提出补救建议。
        8. 结果整理成结构化说明，确保 EvaluateAgent 在评估启动时即可复用这些文件。
        """

        expected_output = """
        - 解析到的 consortium 记录（含 members、S_consort、avg_S_microbe 等字段）。
        - FAA 文件生成概览，列出成功/缺失的物种与输出目录。
        - 代谢模型、培养基、通路添加与 MICOM 模拟概览（包含输出路径、生成/跳过数量）。
        - 对缺失项的处理计划或额外需求说明。
        """

        task = Task(
            description=description.strip(),
            expected_output=expected_output.strip(),
            agent=agent,
            context=[context_task] if context_task else None,
            llm=self.llm,
        )
        return task
