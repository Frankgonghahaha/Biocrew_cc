# ReactionAdditionTool 详细说明

## 概述

ReactionAdditionTool 是一个用于为代谢模型添加特定反应的工具。该工具能够读取反应数据并将其添加到现有的代谢模型中，以扩展模型的代谢能力。

## 文件位置

`core/tools/evaluation/reaction_addition_tool/reaction_addition_tool.py`

## 功能描述

ReactionAdditionTool 的主要功能包括：
1. 读取现有的代谢模型文件
2. 读取反应数据（从CSV文件或模拟生成）
3. 将指定反应添加到模型中
4. 保存修改后的模型文件
5. 提供反应添加过程的详细日志

## 参数说明

### 输入参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| models_path | str | 是 | 代谢模型文件的目录路径 |
| pollutant_name | str | 是 | 目标污染物名称 |
| reactions_csv | str | 否 | 反应数据CSV文件路径（可选） |
| auto_extrans | bool | 否 | 是否自动添加外部传输反应，默认为False |

### 输出结果

工具执行成功时返回包含以下字段的字典：
- `status`: "success"
- `results`: 包含每个模型处理结果的列表
- `message`: 处理总结信息

工具执行失败时返回包含以下字段的字典：
- `status`: "error"
- `message`: 错误信息

## 使用示例

```python
from core.tools.evaluation.reaction_addition_tool import ReactionAdditionTool

# 初始化工具
tool = ReactionAdditionTool()

# 调用工具
result = tool._run(
    models_path="/path/to/metabolic/models",
    pollutant_name="phthalic acid",
    reactions_csv="/path/to/reactions.csv"
)

# 检查结果
if result.get("status") == "success":
    print("反应添加成功")
    results = result.get("results", [])
    for res in results:
        print(f"模型 {res.get('model')}: {res.get('message')}")
else:
    print(f"反应添加失败: {result.get('message')}")
```

## 工作原理

1. **模型读取**: 工具扫描指定目录中的所有代谢模型文件
2. **反应数据获取**: 从CSV文件或模拟生成反应数据
3. **反应添加**: 为每个模型添加指定的反应
4. **模型保存**: 保存修改后的模型文件
5. **结果返回**: 返回处理结果和详细信息

## 反应数据格式

CSV文件应包含以下列：
- `id`: 反应ID
- `name`: 反应名称
- `subsystem`: 子系统名称
- `lower_bound`: 反应下限
- `upper_bound`: 反应上限
- `reactants`: 反应物（格式：metabolite_id:stoichiometry|...）
- `products`: 产物（格式：metabolite_id:stoichiometry|...）

## 注意事项

1. 确保输入的模型文件格式正确
2. 反应数据CSV文件格式应符合要求
3. 注意模型中代谢物ID的一致性
4. 确保有足够的权限读取输入文件和写入输出文件

## 常见问题和解决方案

### 1. 反应添加失败
**问题**: 工具返回错误状态或部分模型处理失败
**解决方案**: 
- 检查反应数据格式是否正确
- 确认模型文件是否完整
- 查看详细的错误信息日志

### 2. 反应未正确连接
**问题**: 反应添加成功但未正确连接到代谢网络
**解决方案**:
- 检查反应物和产物的代谢物ID
- 验证化学计量系数的正确性
- 确认模型中存在相应的代谢物

### 3. 性能问题
**问题**: 工具处理大量模型时速度较慢
**解决方案**:
- 分批处理模型文件
- 优化反应数据文件大小
- 使用更高性能的计算资源