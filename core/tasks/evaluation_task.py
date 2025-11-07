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
            - 返回生成成功与缺失的物种信息，便于后续评估阶段补齐。

        ### 输出要求
        1. 给出解析到的菌剂成员名单及其来源 JSON（包含 consortium 的关键指标，便于评估阶段引用）。
        2. 说明 FAA 构建结果：生成了哪些文件、缺失哪些物种、下一步如何处理。
        3. 若某些物种缺少序列，需在报告中记录原因并提出补救建议。
        4. 结果整理成结构化说明，确保 EvaluateAgent 在评估启动时即可复用这些文件。
        """

        expected_output = """
        - 解析到的 consortium 记录（含 members、S_consort、avg_S_microbe 等字段）。
        - FAA 文件生成概览，列出成功/缺失的物种与输出目录。
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
