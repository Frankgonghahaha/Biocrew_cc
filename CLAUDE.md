# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 目录

- [项目概述](#项目概述)
- [代码库架构](#代码库架构)
- [常用开发命令](#常用开发命令)
- [项目结构](#项目结构)
- [关键实现细节](#关键实现细节)
- [开发指南](#开发指南)
- [近期架构优化](#近期架构优化)
- [近期增强功能](#近期增强功能)

## 项目概述

这是一个使用CrewAI框架构建的多智能体系统，专门用于污水微生物净化技术的开发和优化。系统通过6类AI智能体的协作，实现"筛选功能微生物→设计菌剂→评估效果→生成落地方案"全流程自动化。

注意：核心算法（Tool_api、Tool_Carveme、ctFBA和评估公式）目前仅在智能体背景故事和任务描述中有所描述，实际实现仍在进行中，代码库中用TODO注释标明。

## 代码库架构

系统采用两层架构设计，包含6类智能体：

### 功能执行层（核心4类智能体）

1. **工程微生物组识别智能体** - 根据水质净化目标筛选功能微生物和代谢互补微生物
2. **微生物菌剂设计智能体** - 使用ctFBA（合作权衡代谢通量平衡）方法设计微生物菌剂
3. **菌剂评估智能体** - 评估生物净化效果和群落生态特性
4. **实施方案生成智能体** - 生成完整的微生物净化技术落地方案

### 支撑服务层（2类智能体）

5. **知识管理智能体** - 获取、存储和提供领域知识
6. **任务协调智能体** - 控制工作流执行顺序，处理多目标和异常情况

## 常用开发命令

### 环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 然后编辑.env文件添加API密钥
```

### 运行应用程序

```bash
# 运行主应用程序
python3 main.py

# 运行测试
python3 tests/test_workflow.py

# 运行结果分析
```

### 代码验证

```bash
# 检查语法错误
python3 -m py_compile main.py

# 检查所有Python文件的语法错误
find . -name "*.py" -exec python3 -m py_compile {} \;
```

### Git操作

```bash
# 推送到仓库
git push origin master
```

## 项目结构

```
BioCrew/
├── main.py                 # 主程序入口（已完全实现）
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量配置示例
├── CLAUDE.md              # Claude Code开发指南
├── config/                # 配置文件
│   ├── __init__.py
│   ├── config.py          # 主配置文件（已完全实现）
│   └── paths.py           # 路径配置
├── core/                  # 核心模块
│   ├── agents/            # 智能体定义（已完全实现，核心算法有TODO）
│   │   ├── __init__.py
│   │   ├── identification_agent.py     # 工程微生物组识别智能体
│   │   ├── design_agent.py             # 微生物菌剂设计智能体
│   │   ├── evaluation_agent.py         # 菌剂评估智能体
│   │   ├── implementation_agent.py     # 实施方案生成智能体
│   │   ├── coordination_agent.py       # 任务协调智能体
│   │   └── knowledge_agent.py          # 知识管理智能体
│   ├── tasks/             # 任务定义（已完全实现，核心算法有TODO）
│   │   ├── __init__.py
│   │   ├── identification_task.py      # 微生物组识别任务
│   │   ├── design_task.py              # 微生物菌剂设计任务
│   │   ├── evaluation_task.py          # 菌剂评估任务
│   │   ├── implementation_task.py      # 实施方案生成任务
│   │   └── coordination_task.py        # 任务协调任务
│   └── tools/             # 自定义工具（统一管理）
│       ├── __init__.py
│       ├── database/      # 数据库工具
│       │   ├── __init__.py
│       │   ├── factory.py              # 数据库工具工厂
│       │   ├── envipath_enhanced.py    # 增强版EnviPath数据库访问工具
│       │   ├── kegg.py                 # KEGG数据库访问工具
│       │   ├── ncbi.py                 # NCBI基因组查询工具
│       │   ├── ncbi_genome_download_tool.py # NCBI基因组下载工具
│       │   ├── complementarity_query.py # 微生物互补性查询工具
│       │   ├── complementarity_model.py # 微生物互补性数据模型
│       │   ├── complementarity_tool.py # 微生物互补性查询工具
│       │   ├── pollutant_query.py      # 污染物数据查询工具
│       │   ├── gene_query.py           # 基因数据查询工具
│       │   ├── organism_query.py       # 微生物数据查询工具
│       │   ├── summary.py              # 污染物摘要工具
│       │   ├── search.py               # 污染物搜索工具
│       │   └── name_utils.py           # 污染物名称标准化工具
│       ├── external/      # 外部数据库工具
│       │   ├── __init__.py
│       │   └── genome.py               # 基因组工具
│       ├── design/        # 菌剂设计工具
│       │   ├── __init__.py
│       │   ├── genome_processing.py    # 基因组处理工具
│       │   ├── genome_processing_workflow.py # 基因组处理工作流工具
│       │   ├── genome_spot.py          # GenomeSPOT工具
│       │   ├── dlkcat.py               # DLkcat工具
│       │   ├── carveme.py              # Carveme工具
│       │   ├── phylomint.py            # Phylomint工具
│       │   ├── ctfba.py                # ctFBA工具
│       │   ├── pollutant_query.py      # 污染物数据查询工具
│       │   ├── gene_query.py           # 基因数据查询工具
│       │   ├── organism_query.py       # 微生物数据查询工具
│       │   ├── summary.py              # 污染物摘要工具
│       │   ├── search.py               # 污染物搜索工具
│       │   └── name_utils.py           # 污染物名称标准化工具
│       ├── evaluation/    # 菌剂评估工具
│       │   ├── __init__.py
│       │   ├── evaluation.py           # 评估工具
│       │   ├── reaction_addition.py    # 代谢反应填充工具
│       │   ├── reaction_addition_original.py # 原始代谢反应填充工具
│       │   ├── medium_recommendation.py # 培养基推荐工具
│       │   └── ctfba.py                # ctFBA工具（共享）
│       └── services/      # 服务工具
│           ├── __init__.py
│           ├── genomic_data.py         # 基因组数据服务
│           └── intermediate_check.py   # 中间产物检查工具
├── data/                  # 本地数据
│   ├── genomes/           # 基因组数据
│   ├── reactions/         # 反应数据
│   └── medium/            # 培养基数据
├── outputs/               # 输出文件
│   ├── genome_features/   # 基因组特征
│   ├── metabolic_models/  # 代谢模型
│   └── results/           # 结果文件
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── e2e/               # 端到端测试
│   │   └── full_workflow_test.py      # 完整工作流测试
│   ├── test_workflow.py               # 完整工作流测试
│   ├── test_identification_phase.py   # 工程微生物组识别阶段测试
│   ├── test_design_phase.py           # 微生物菌剂设计阶段测试
│   ├── test_evaluation_phase.py       # 菌剂评估阶段测试
│   ├── test_full_workflow.py          # 完整工作流程测试
│   └── unit/              # 单元测试
│       ├── final_test_medium.py       # 培养基测试
│       ├── test_correct_candidate_ex.py # 候选EX测试
│       └── test_medium_recommendation.py # 培养基推荐测试
└── docs/                  # 文档
    ├── AGENTS.md         # 智能体文档
    ├── TASKS.md          # 任务文档
    ├── TOOLS.md          # 工具文档
    ├── TESTS.md          # 测试文档
    ├── workflow/          # 工作流程文档
    │   └── complete_workflow.md  # 完整工作流程说明
    └── tools/             # 工具详细说明
        ├── detailed/      # 详细工具说明
        │   ├── carveme_tool.md     # Carveme工具详细说明
        │   └── reaction_addition_tool.md  # ReactionAdditionTool详细说明
        └── ...
```

## 关键实现细节

### 数据流

- 知识管理 → 功能执行层智能体
- 前一个智能体输出 → 下一个智能体输入
- 反馈循环：评估失败 → 更新提示词 → 重新识别微生物

### 核心算法（部分实现，有TODO）

1. **Tool_api和Tool_Carveme** - 用于检索基因组/酶序列数据并将基因组转换为代谢模型
   - 目前仅在智能体背景故事中描述，实际实现待完成

2. **ctFBA算法** - 合作权衡代谢通量平衡方法用于代谢通量计算
   - 目前仅在智能体背景故事中描述，实际实现待完成

3. **评估公式** - 包括竞争指数、互补指数、Pianka niche overlap指数、物种敲除指数
   - 目前仅在智能体背景故事中描述，实际实现待完成

### 配置

系统通过`.env`文件中的环境变量支持DashScope（Qwen）和OpenAI模型配置。

### 专门化数据访问

系统现在使用专门化的数据库工具替代了之前的统一数据工具，为不同的数据访问需求提供专注的接口：

1. **PollutantDataQueryTool** - 查询指定污染物的所有数据
2. **GeneDataQueryTool** - 查询指定污染物的基因数据
3. **OrganismDataQueryTool** - 查询指定污染物的微生物数据
4. **PollutantSummaryTool** - 获取指定污染物的摘要统计信息
5. **PollutantSearchTool** - 根据关键字搜索污染物

这些工具由DatabaseToolFactory管理，便于实例化和使用。

### 污染物名称标准化

新增工具模块`pollutant_name_utils.py`用于处理污染物名称标准化：
- 将不同格式的污染物名称标准化为一致的格式以进行数据库查询
- 生成多个名称变体以改进搜索和匹配
- 处理希腊字母、缩写和特殊字符

### 外部数据库访问工具

系统通过以下工具集成外部数据库：

1. **EnviPathTool** - 访问enviPath数据库中的环境污染物生物转化路径数据
   - `_run(operation, **kwargs)` - 所有EnviPath操作的统一接口
   - 操作：`search_compound`、`get_pathway_info`、`get_compound_pathways`、`search_pathways_by_keyword`
   - 也支持直接方法调用：`search_compound(compound_name)`、`get_pathway_info(pathway_id)`等

2. **KeggTool** - 访问KEGG数据库中的生物路径和基因组数据
   - `_run(operation, **kwargs)` - 所有KEGG操作的统一接口
   - 操作：`get_database_info`、`list_entries`、`find_entries`、`get_entry`、`link_entries`、`convert_id`、`search_pathway_by_compound`、`search_genes_by_pathway`、`search_enzymes_by_compound`
   - 也支持每个操作的直接方法调用

3. **NCBIGenomeQueryTool** - 访问NCBI数据库中的微生物基因组数据
   - `_run(operation, **kwargs)` - 所有NCBI基因组查询操作的统一接口
   - 操作：`search_genome`、`get_genome_info`
   - 也支持直接方法调用

### 微生物菌剂设计专用工具

系统包含多个微生物菌剂设计专用工具：

1. **GenomeSPOTTool** - 预测微生物的环境适应性特征
2. **DLkcatTool** - 预测降解酶对于特定底物的降解速率
3. **CarvemeTool** - 构建基因组规模代谢模型(GSMM)
4. **PhylomintTool** - 分析微生物间的代谢互补性和竞争性
5. **CtfbaTool** - 计算微生物群落的代谢通量

### 外部工具集成

系统通过`core/tools/external/`目录内部集成了多个外部工具脚本，避免了对外部路径的依赖：

1. **GenomeSPOT** - 预测微生物环境适应性的机器学习工具
2. **DLkcat** - 预测酶催化速率的工具
3. **Carveme** - 构建基因组规模代谢模型的工具
4. **Phylomint** - 分析微生物间代谢互补性的工具

这些外部工具脚本被复制到项目内部，确保了项目的可移植性和一致性。

### 微生物菌剂评估专用工具

系统包含多个微生物菌剂评估专用工具：

1. **ReactionAdditionTool** - 批量为SBML模型添加代谢反应
2. **MediumRecommendationTool** - 使用MICOM生成推荐培养基组分
3. **EvaluationTool** - 分析和评估微生物菌剂效果
4. **CtfbaTool** - 计算微生物群落的代谢通量

## 开发指南

### 代码组织

- 每个智能体在`agents/`目录中定义在自己的文件中
- 每个任务在`tasks/`目录中定义在自己的文件中
- 共享功能应在`tools/`目录中实现
- 配置通过`config/`目录管理
- 本地数据存储在`data/`目录中

### 工具结构

所有工具遵循一致的模式：
1. 每个工具继承自`crewai.tools.BaseTool`以确保CrewAI兼容性
2. 每个工具都有专用的Pydantic模型用于输入参数（args_schema）
3. 工具实现带有显式参数定义的`_run()`方法
4. 工具使用`object.__setattr__`和`object.__getattribute__`处理实例属性并避免Pydantic验证问题
5. 工具返回包含`status`、`data`和错误信息的一致结果格式

### 工具工厂模式

数据库工具通过DatabaseToolFactory管理：
1. 提供创建所有数据库工具的集中方式
2. 允许按名称轻松实例化单个工具
3. 确保整个应用程序中一致的工具初始化

### 智能体结构

智能体遵循一致的模式：
1. 每个智能体实现为具有`create_agent()`方法的类
2. `create_agent()`方法返回配置的CrewAI Agent实例
3. 智能体定义其角色、目标和背景故事
4. 智能体可以使用自定义工具实现专门功能

### 任务结构

任务遵循一致的模式：
1. 每个任务实现为具有`create_task()`方法的类
2. `create_task()`方法返回配置的CrewAI Task实例
3. 任务定义其描述和预期输出
4. 任务可以通过context参数依赖其他任务

### 添加新功能

1. 要添加新智能体，在`agents/`目录中创建新文件并遵循现有模式
2. 要添加新任务，在`tasks/`目录中创建新文件并遵循现有模式
3. 在`main.py`中注册新智能体和任务
4. 更新`main.py`中的Crew配置以包含新智能体和任务
5. 对于数据访问功能，在`tools/`目录中实现新工具
6. 为新功能添加相应的测试文件，确保功能正确性

## 近期架构优化

系统经历了重大优化以简化架构并提高可维护性：

### 工具专门化

- 用专门化的数据库工具替换了遗留的统一数据工具
- 每个工具现在都有特定的职责，提高了清晰度和可维护性
- 包括：
  - PollutantDataQueryTool
  - GeneDataQueryTool
  - OrganismDataQueryTool
  - PollutantSummaryTool
  - PollutantSearchTool

### 智能体背景故事简化

- 大幅减少了智能体背景故事的长度和复杂性
- 精简了工具使用说明
- 提高了清晰度和核心功能的专注度

### 优化的好处

1. **提高清晰度**：每个工具都有明确、定义良好的目的
2. **更好的可维护性**：更容易更新和扩展单个工具
3. **增强的可靠性**：减少了工具协调问题的潜在风险
4. **更容易调试**：问题可以隔离到特定工具
5. **更好的性能**：工具针对其特定功能进行了优化

## 近期增强功能

### 自然语言处理改进

- 增强了工程微生物识别智能体中的污染物识别和翻译能力
- 添加了将自然语言污染物描述自动翻译为标准科学术语的支持
- 改进了工具调用功能，具有更好的错误处理和数据完整性评估

### 动态工作流实现

- 在main.py中实现了可以根据评估结果重新执行任务的动态工作流
- 添加了用于微生物识别和设计持续改进的反馈循环
- 实现了最大迭代限制以防止无限循环

### 用户输入支持

- 在主应用程序中添加了对用户定义水质处理需求的支持
- 创建了允许用户输入自定义污染物名称进行数据库查询的测试脚本
- 改进了用户体验，提供清晰的提示和说明

### 数据库查询增强

- 增强了数据库工具，具有更好的错误处理和数据验证
- 添加了污染物名称标准化工具以提高数据库查询准确性
- 实现了更强大的数据库连接管理

### KEGG工具优化

- 添加了超时机制以防止KEGG数据库查询时的长时间等待
- 实现了数据大小限制以避免超出模型输入限制
- 增强了错误处理和恢复机制以提高可靠性
- 优化了smart_query方法以自动处理复杂的查询逻辑

### 智能体性能改进

- 优化了智能体工具调用策略，要求全面使用所有可用工具
- 加强了数据注释要求，明确区分直接查询结果和综合分析结论
- 标准化了输出格式，要求特定的数据源和置信度评估

### 测试文件增强

- 添加了多个新的测试文件，用于验证功能微生物识别和菌剂设计功能
- 创建了专门的测试文件来验证工具调用能力
- 增强了测试覆盖度，确保各个功能模块的正确性
- 清理了冗余的测试文件，优化了测试结构，提高了维护性

### 菌剂评估工具增强

- 实现了ReactionAdditionTool工具，用于批量为SBML模型添加代谢反应
- 实现了MediumRecommendationTool工具，使用MICOM生成推荐培养基组分
- 增强了菌剂评估智能体，集成了新工具并更新了评估流程
- 创建了专门的测试文件验证新工具的功能