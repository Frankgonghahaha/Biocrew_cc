# 基于CrewAI的水质生物净化技术开发多智能体系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CrewAI](https://img.shields.io/badge/CrewAI-Framework-orange)](https://crewai.com)

这是一个使用CrewAI框架构建的多智能体系统，专门用于污水微生物净化技术的开发和优化。系统通过6类AI智能体的协作，实现"筛选功能微生物→设计菌剂→评估效果→生成落地方案"全流程自动化，输出可在目标污水厂应用的高效降解菌剂及方案。

## 项目核心定位

- **领域**：污水微生物净化技术
- **目标**：解决传统工艺（调参数、培单菌）耗时耗力、净化效果差的问题
- **核心方案**：通过6类智能体协作，实现全流程自动化，输出可在目标污水厂应用的高效降解菌剂及方案

## 系统架构（6类智能体，分2层）

### 功能执行层（核心4类智能体）

1. **工程微生物组识别智能体**
   - 输入：水质净化目标（水质治理指标+目标污染物）、匹配提示词
   - 依赖：知识管理智能体（提供领域知识）
   - 核心功能：从公开数据库和本地数据获取数据，调用工具筛选功能微生物+代谢互补微生物

2. **微生物菌剂设计智能体**
   - 输入：水质净化目标、工程微生物组、菌剂设计提示词
   - 核心功能：遍历工程微生物组，使用ctFBA方法设计最优候选群落

3. **菌剂评估智能体**
   - 输入：微生物菌剂、水质净化目标（含生态预期值）、污水厂水质背景
   - 核心功能：评估生物净化效果和群落生态特性

4. **实施方案生成智能体**
   - 输入：微生物菌剂、评估报告、实施方案提示词
   - 核心功能：生成完整的微生物净化技术落地方案

### 支撑服务层（2类智能体）

5. **知识管理智能体**
   - 功能：获取、存储和提供领域知识

6. **任务协调智能体**
   - 功能：调控流程执行顺序，处理多目标和异常情况

## 项目结构

```
BioCrew/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量配置示例
├── config/
│   └── config.py          # 配置文件
├── agents/                # 智能体定义
│   ├── task_coordination_agent.py              # 任务协调专家
│   ├── engineering_microorganism_identification_agent.py  # 工程微生物组识别专家
│   ├── microbial_agent_design_agent.py         # 微生物菌剂设计专家
│   ├── microbial_agent_evaluation_agent.py     # 菌剂评估专家
│   ├── implementation_plan_generation_agent.py  # 实施方案生成专家
│   └── knowledge_management_agent.py           # 知识管理专家
├── tasks/                 # 任务定义
│   ├── microorganism_identification_task.py    # 工程微生物组识别任务
│   ├── microbial_agent_design_task.py          # 微生物菌剂设计任务
│   ├── microbial_agent_evaluation_task.py      # 菌剂评估任务
│   └── implementation_plan_generation_task.py  # 实施方案生成任务
├── tools/                 # 自定义工具
│   ├── evaluation_tool.py                     # 评价工具
│   ├── local_data_retriever.py               # 本地数据读取工具
│   ├── smart_data_query_tool.py              # 智能数据查询工具
│   ├── mandatory_local_data_query_tool.py    # 强制本地数据查询工具
│   ├── envipath_tool.py                      # EnviPath数据库访问工具
│   ├── kegg_tool.py                          # KEGG数据库访问工具
│   ├── local_data_retriever_usage.md         # 本地数据读取工具使用说明
│   ├── smart_data_query_tool_usage.md        # 智能数据查询工具使用说明
│   ├── mandatory_local_data_query_tool_usage.md # 强制本地数据查询工具使用说明
│   ├── envipath_tool_usage.md                # EnviPath工具使用说明
│   ├── kegg_tool_usage.md                    # KEGG工具使用说明
│   └── smart_data_query_in_agent_example.py  # 智能体中使用数据工具的示例
├── data/                  # 本地数据文件
│   ├── Genes/             # 基因数据目录
│   │   └── Genes/         # 基因数据文件
│   └── Organism/          # 微生物数据目录
│       └── Organism/      # 微生物数据文件
├── tests/                 # 测试文件
│   ├── test_local_data_query.py              # 本地数据查询测试
│   ├── test_database_tools.py                # 数据库工具测试
│   └── test_engineering_microorganism_identification.py # 工程微生物识别测试
└── models/                # 模型配置（待完善）
```

## 核心协作逻辑

- **数据流向**：知识管理→执行层智能体；前序智能体输出→后序智能体输入
- **反馈闭环**：菌剂评估不达标→更新提示词→回退工程微生物组筛选
- **流程管控**：任务协调智能体统一调度执行顺序，处理多目标/异常

## 项目优势

- **技术创新**：大语言模型+ctFBA模拟+生态学评估结合，理性+数据双驱动
- **落地性**：方案覆盖全环节，菌剂过生态评估，无工程风险
- **效率**：全流程自动化，缩短技术开发周期
- **数据驱动**：集成本地数据查询工具，支持从Excel文件中读取基因和微生物数据

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置说明

1. 复制 `.env.example` 文件为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 文件中配置你的模型API信息:
   ```env
   # DashScope (阿里云Qwen)配置示例
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY=your_api_key_here
   QWEN_MODEL_NAME=qwen3-30b-a3b-instruct-2507
   
   # OpenAI配置示例
   OPENAI_API_BASE=https://api.openai.com/v1
   OPENAI_API_KEY=your_openai_api_key_here
   
   # 其他配置
   VERBOSE=True
   ```

3. **重要提示**：
   - `QWEN_API_KEY` 需要替换为有效的阿里云API密钥
   - 如果使用其他兼容OpenAI的API，请确保端点支持OpenAI格式的请求
   - 建议使用高性能模型以获得更好的效果

### 运行程序

```bash
python main.py
```

### 测试本地数据工具

项目包含了本地数据查询工具的测试文件，可以单独运行测试：

```bash
# 测试本地数据查询功能
python test_local_data_query.py

# 测试工程微生物识别智能体
python test_engineering_microorganism_identification.py
```

## 本地数据工具

项目新增了三个本地数据工具，用于从Excel文件中读取基因和微生物数据：

1. **LocalDataRetriever** - 核心数据读取工具
2. **SmartDataQueryTool** - 智能数据查询工具，可根据文本自动识别相关数据
3. **MandatoryLocalDataQueryTool** - 强制本地数据查询工具，确保数据来自本地文件

## 公开数据库工具

项目新增了两个公开数据库访问工具，用于获取环境和生物代谢信息：

1. **EnviPathTool** - 用于查询环境化合物代谢路径信息（当前存在SSL连接问题，建议使用KEGG工具）
2. **KeggTool** - 用于查询KEGG数据库中的pathway、ko、genome、reaction、enzyme、genes等生物代谢信息

详细使用说明请查看：
- [LocalDataRetriever使用说明](tools/local_data_retriever_usage.md)
- [SmartDataQueryTool使用说明](tools/smart_data_query_tool_usage.md)
- [MandatoryLocalDataQueryTool使用说明](tools/mandatory_local_data_query_tool_usage.md)
- [EnviPathTool使用说明](tools/envipath_tool_usage.md)
- [KeggTool使用说明](tools/kegg_tool_usage.md)

## 系统优化与扩展

### 当前优化

- [x] 重构智能体架构，符合6类智能体框架要求
- [x] 完善任务流程设计，实现完整的协作逻辑
- [x] 优化菌剂评价体系
- [x] 集成本地数据查询工具，支持从Excel文件读取数据
- [x] 优化项目结构，添加测试文件和工具文档

### 后续开发计划

1. 实现Tool_api和Tool_Carveme工具
2. 开发ctFBA算法和代谢通量计算功能
3. 实现具体的评估公式和算法
4. 完善反馈闭环机制
5. 添加可视化界面
6. 实现历史数据存储和分析功能
7. 修复EnviPath工具的SSL连接问题，完善数据库工具功能

## 贡献指南

欢迎任何形式的贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 致谢

- [CrewAI](https://crewai.com) - 多智能体框架
- [阿里云DashScope](https://dashscope.aliyuncs.com) - Qwen大语言模型支持
- 所有为项目做出贡献的开发者

## 联系方式

项目维护者: Axl1Huang - [GitHub](https://github.com/Axl1Huang)

项目链接: [https://github.com/Water-Quality-Risk-Control-Engineering/BioCrew](https://github.com/Water-Quality-Risk-Control-Engineering/BioCrew)