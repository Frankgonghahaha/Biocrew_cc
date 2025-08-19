# BioCrew: 基于CrewAI的水质生物净化技术开发多智能体系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

这是一个使用[CrewAI](https://github.com/joaomdmoura/crewAI)框架构建的多智能体系统，专门用于水质生物净化技术的开发和优化。系统通过模拟专家团队协作的方式，为水处理工程师和环境科学家提供智能化的生物净化解决方案。

## 项目特色

- **多智能体协作**：模拟真实专家团队的协作流程，实现高效的生物净化技术开发
- **专业领域知识**：基于水质处理和微生物学专业知识构建的专家系统
- **灵活配置**：支持多种工作模式，可根据需求定制处理流程
- **易于扩展**：模块化设计，便于添加新的专家角色和处理流程

## 致谢

本项目基于 [CrewAI](https://github.com/joaomdmoura/crewAI) 框架开发，感谢 CrewAI 团队提供的强大而灵活的多智能体协作框架。

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

## 核心智能体

系统包含以下5个核心智能体：

1. **任务协调专家** - 调控其他智能体的执行顺序，确保工作流程的顺畅进行
2. **功能微生物匹配专家** - 根据污染物类型和处理目标，匹配最适宜的功能微生物
3. **技术评估专家** - 基于五个维度评估微生物菌剂的生物净化效果
4. **技术方案生成专家** - 基于微生物菌剂和生物净化效果，制定完整的技术方案
5. **知识管理专家** - 整合与生物净化任务相关的领域知识，提供理论支持

## 功能菌剂评价体系

系统采用基于五个维度的评价体系：

1. **物种多样性** - 评估菌剂中微生物种类的丰富程度
2. **群落稳定性**（核心标准） - 评估菌剂在不同环境条件下的稳定性
3. **结构稳定性**（核心标准） - 评估菌剂内部微生物群落结构的稳定性
4. **代谢相互作用** - 评估微生物间的协同代谢能力
5. **污染物降解性能** - 评估对目标污染物的降解效率

## 工作模式

系统支持两种工作模式：

- **顺序执行模式**（默认） - 按照预定义顺序执行所有任务
- **分层执行模式** - 由任务协调专家动态决定任务执行顺序

## 快速开始

### 环境配置

1. 复制 `.env.example` 文件为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 文件中配置你的QWEN3模型URL和Token:
   ```env
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY=你的API密钥
   QWEN_MODEL_NAME=qwen3-30b-a3b-instruct-2507
   ```

3. **获取API密钥**：
   - 注册阿里云账号并获取API密钥
   - 确保账户有足够的配额访问Qwen3模型

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

### 测试系统

可以运行测试脚本来验证系统功能：

```bash
python test_system.py
```

## 开发指南

### 添加新的智能体

1. 在 `agents/` 目录下创建新的智能体文件
2. 继承 `BaseAgent` 类并实现相应方法
3. 在 `main.py` 中导入并注册新的智能体

### 扩展评价维度

1. 修改 `tools/evaluation_tool.py` 中的评价逻辑
2. 更新相关智能体的评估标准

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。