# 基于CrewAI的水质生物净化技术开发多智能体系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CrewAI](https://img.shields.io/badge/CrewAI-Framework-orange)](https://crewai.com)

这是一个使用CrewAI框架构建的多智能体系统，专门用于水质生物净化技术的开发和优化。系统通过多个专业AI智能体的协作，实现从污染物识别、功能微生物匹配、菌剂设计、性能评估到技术方案生成的全流程自动化。

## 项目特色

- **多智能体协作**：5个专业领域的AI智能体协同工作
- **科学评估体系**：基于5个维度的菌剂性能评估模型
- **闭环优化机制**：支持菌剂设计-评估-优化的循环迭代
- **灵活配置**：支持多种大语言模型（Qwen、OpenAI等）
- **易于扩展**：模块化设计，便于添加新的智能体和任务

## 项目结构

```
BioCrew/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量配置示例
├── config/
│   └── config.py          # 配置文件
├── agents/                # 智能体定义
│   ├── task_coordination_agent.py      # 任务协调专家
│   ├── microorganism_matching_agent.py # 功能微生物匹配专家
│   ├── bioagent_design_agent.py        # 技术评估专家
│   ├── treatment_plan_agent.py         # 技术方案生成专家
│   └── knowledge_management_agent.py   # 知识管理专家
├── tasks/                 # 任务定义
│   ├── design_task.py              # 菌剂设计任务
│   └── evaluation_task.py          # 菌剂评价任务
├── tools/                 # 自定义工具
│   └── evaluation_tool.py          # 评价工具
└── models/                # 模型配置（待完善）
```

## 智能体介绍

系统包含以下5个核心智能体：

1. **任务协调专家** - 调控生物净化技术开发智能体、技术评估智能体、技术方案生成智能体的执行顺序
2. **功能微生物匹配专家** - 根据污染物类型和处理要求匹配最适宜的功能微生物
3. **技术评估专家** - 基于五个维度评估微生物菌剂的生物净化效果
4. **技术方案生成专家** - 基于微生物菌剂和生物净化效果，确定技术方案
5. **知识管理专家** - 确定与生物净化任务相关的领域知识，并补充知识数据库中未包含的代谢模型

## 功能菌剂评价流程

系统采用基于五个维度的评价体系：

1. 物种多样性
2. 群落稳定性（核心标准）
3. 结构稳定性（核心标准）
4. 代谢相互作用
5. 污染物降解性能

### 评价流程逻辑

- 技术评估专家基于上述五个维度对菌剂进行评估
- 重点关注群落稳定性和结构稳定性这两个核心标准
- 如果这两个核心标准不达标，则返回功能菌剂设计阶段重新设计
- 如果核心标准达标，则继续综合评估其他维度并给出总体建议

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

## 系统优化与扩展

### 当前优化

- [x] 修复API连接问题，支持DashScope Qwen模型
- [x] 完善智能体角色定义和专业背景
- [x] 优化菌剂评价体系
- [x] 改进任务流程设计

### 后续开发计划

1. 添加更多专业领域的智能体
2. 开发自定义工具增强智能体能力
3. 完善智能体间的协作流程
4. 添加可视化界面
5. 实现历史数据存储和分析功能
6. 支持更多类型的污染物处理

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

项目链接: [https://github.com/Axl1Huang/Bio_Crew](https://github.com/Axl1Huang/Bio_Crew)