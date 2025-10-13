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
python3 tests/test_Agent_Search.py
python3 tests/test_database_query_user_input.py
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
├── tests/                 # 测试文件
│   ├── test_Agent_Search.py               # Agent搜索测试
│   └── test_database_query_user_input.py  # 数据库查询测试（支持用户输入）
├── config/
│   └── config.py          # 配置文件（已完全实现）
├── agents/                # 智能体定义（已完全实现，核心算法有TODO）
│   ├── task_coordination_agent.py              # 任务协调智能体
│   ├── engineering_microorganism_identification_agent.py  # 工程微生物组识别智能体
│   ├── microbial_agent_design_agent.py         # 微生物菌剂设计智能体
│   ├── microbial_agent_evaluation_agent.py     # 菌剂评估智能体
│   ├── implementation_plan_generation_agent.py  # 实施方案生成智能体
│   └── knowledge_management_agent.py           # 知识管理智能体
├── tasks/                 # 任务定义（已完全实现，核心算法有TODO）
│   ├── microorganism_identification_task.py    # 微生物组识别任务
│   ├── microbial_agent_design_task.py          # 微生物菌剂设计任务
│   ├── microbial_agent_evaluation_task.py      # 菌剂评估任务
│   ├── implementation_plan_generation_task.py  # 实施方案生成任务
│   └── task_coordination_task.py               # 任务协调任务
├── tools/                 # 自定义工具（部分实现）
│   ├── database_tool_factory.py               # 数据库工具工厂
│   ├── engineering_microorganism_identification/     # 工程微生物识别工具
│   │   ├── envipath_tool.py                  # EnviPath数据库访问工具
│   │   ├── kegg_tool.py                      # KEGG数据库访问工具
│   │   ├── ncbi_genome_query_tool.py         # NCBI基因组查询工具
│   │   ├── microbial_complementarity_db_query_tool.py  # 微生物互补性数据库查询工具
│   │   ├── microbial_complementarity_model.py          # 微生物互补性数据模型
│   │   └── microbial_complementarity_query_tool.py     # 微生物互补性查询工具
│   ├── microbial_agent_design/               # 微生物菌剂设计工具
│   │   ├── gene_data_query_tool.py           # 基因数据查询工具
│   │   ├── organism_data_query_tool.py       # 微生物数据查询工具
│   │   ├── pollutant_data_query_tool.py      # 污染物数据查询工具
│   │   ├── pollutant_summary_tool.py         # 污染物摘要工具
│   │   ├── pollutant_search_tool.py          # 污染物搜索工具
│   │   ├── pollutant_name_utils.py           # 污染物名称标准化工具
│   │   ├── genome_spot_tool/                 # GenomeSPOT工具
│   │   ├── dlkcat_tool/                      # DLkcat工具
│   │   ├── carveme_tool/                     # Carveme工具
│   │   ├── phylomint_tool/                   # Phylomint工具
│   │   └── ctfba_tool/                       # ctFBA工具
│   ├── microbial_agent_evaluation/           # 微生物菌剂评估工具
│   │   └── evaluation_tool.py                # 评估工具
│   ├── implementation_plan_generation/       # 实施方案生成工具
│   └── task_coordination/                    # 任务协调工具
└── models/                # 模型配置（待完善）
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

### 评估工具

**EvaluationTool** - 分析和评估微生物菌剂效果
- `_run(operation, **kwargs)` - 评估操作的统一接口
- 操作：`analyze_evaluation_result`、`check_core_standards`
- 也支持直接方法调用：`analyze_evaluation_result(evaluation_report)`、`check_core_standards(evaluation_report)`

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