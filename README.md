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
│   ├── microorganism_matching_agent.py # 生物净化策略开发专家
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
2. **生物净化策略开发专家** - 根据目标污水厂的生物净化任务（含污水治理目标、工艺参数、目标污染物）确定微生物菌剂
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

评价流程逻辑：
- 技术评估专家基于上述五个维度对菌剂进行评估
- 重点关注群落稳定性和结构稳定性这两个核心标准
- 如果这两个核心标准不达标，则返回功能菌剂设计阶段重新设计
- 如果核心标准达标，则继续综合评估其他维度并给出总体建议

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

3. **重要提示**：
   - `QWEN_API_BASE` 需要替换为实际的API端点地址
   - `QWEN_API_KEY` 需要替换为有效的API密钥
   - 如果使用阿里云Qwen模型，请注册阿里云账号并获取API密钥
   - 如果使用其他兼容OpenAI的API，请确保端点支持OpenAI格式的请求

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 测试系统

可以运行测试脚本来验证系统功能：

```bash
python test_system.py
```

## 后续开发

根据具体的工作流程链路，需要进一步完善：
1. 定义具体的任务（tasks）
2. 开发自定义工具（tools）
3. 完善智能体间的协作流程