# Repository Guidelines

## 项目结构与模块组织
- `main.py` 为 CLI 入口，负责串联多智能体流程与运行模式选择。
- `core/agents/`、`core/tasks/`、`core/tools/` 分别存放 CrewAI 智能体、任务与领域工具，实现“识别→设计→评估→实施”的主干逻辑。
- `config/` 提供模型、数据库与路径配置；`.env` 覆盖运行时密钥与 `MODEL_MAX_TOKENS` 等参数。
- 数据资产集中于 `data/`（基因组、反应、培养基等）和 `outputs/`（中间模型与最终结果），测试数据落在 `test_data/`。
- 自动化测试位于 `tests/`，区分阶段性脚本与端到端用例；生成的测试日志保存在 `test_results/`。

## 构建、测试与开发命令
- `pip install -r requirements.txt`：安装运行与工具依赖。
- `python main.py`：交互式启动流程，可在提示中选择顺序或分层模式。
- `python tests/test_identification_phase.py` 等脚本：运行阶段性验证，测试完成后会在 `test_results/` 写入日志与 JSON。
- `pytest tests/unit`：执行以 `pytest` 风格编写的单元测试（若只需快速验证逻辑）。
- `python -m crewai.cli.check core/agents`（可选）：在启用 CLI 扩展后核对智能体配置。

## 编码风格与命名规范
- 采用 Python 4 空格缩进，遵循 PEP 8；函数与变量使用 `snake_case`，类名使用 `PascalCase`。
- 新增工具须继承 `crewai.tools.BaseTool`，在 `_run` 中明确输入输出，并使用类型提示。
- 配置常量集中放入 `Config` 类，避免散布硬编码路径或密钥。
- 推荐在提交前运行 `python -m compileall core config tests` 快速检查语法。

## 测试指南
- 阶段测试脚本以 `test_<phase>_phase.py` 命名，负责验证对应智能体链路；请确保关键 API 调用使用模拟数据或本地缓存，避免外部限流。
- 端到端流程位于 `tests/e2e/`，在修改跨阶段逻辑时务必运行。
- 新增测试需写入 `tests/` 并在结果中记录重要输出路径，便于回归对比。

## 提交与 Pull Request 规范
- 提交信息遵循 “简要动词 + 修改范围” 的中英文混合风格示例（如 `修复: 更新识别阶段提示词`）；保持 50 字以内首行摘要。
- PR 描述需包含：变更背景、主要改动点、测试覆盖情况及相关工单链接；涉及界面或报告生成时附带关键截图或结果文件路径。
- 禁止提交带有真实密钥的 `.env`；如需新增配置，请同步更新 `README.md` 与相关示例文件。

## 配置与安全提示
- 运行前复制 `.env.example` 为 `.env` 并填写 DashScope、数据库等密钥；测试环境可用单独的 `.env.test` 配置，在脚本中通过 `load_dotenv` 加载。
- 数据库凭据与外部 API 限额敏感，提交前请确认未写入日志或测试快照。
