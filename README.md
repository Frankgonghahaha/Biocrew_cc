# 基于CrewAI的水质生物净化技术开发多智能体系统

这是一个使用CrewAI框架构建的多智能体系统，专门用于水质生物净化技术的开发和优化。

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
│   ├── bioagent_design_agent.py        # 功能菌剂设计专家
│   ├── treatment_plan_agent.py         # 净化方案生成专家
├── tasks/                 # 任务定义（待完善）
├── tools/                 # 自定义工具（待完善）
└── models/                # 模型配置（待完善）
```

## 智能体介绍

根据最新需求，系统包含以下4个核心智能体：

1. **任务协调专家** - 识别用户需求并协调调用其他智能体
2. **功能微生物匹配专家** - 根据污染物类型匹配相应的功能微生物
3. **功能菌剂设计专家** - 设计和优化功能微生物菌剂配方
4. **净化方案生成专家** - 对评估后的群落组成进行可行性分析并提供购买渠道查询

## 配置说明

1. 复制 `.env.example` 文件为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 文件中配置你的QWEN3模型URL和Token:
   ```env
   QWEN_API_BASE=你的API地址
   QWEN_API_KEY=你的API密钥
   QWEN_MODEL_NAME=QWEN3
   ```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 后续开发

根据具体的工作流程链路，需要进一步完善：
1. 定义具体的任务（tasks）
2. 开发自定义工具（tools）
3. 完善智能体间的协作流程