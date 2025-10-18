# CarvemeTool 详细说明

## 概述

CarvemeTool 是一个用于构建基因组规模代谢模型(GSMM)的工具，基于 CarveMe 算法实现。该工具能够从蛋白质序列数据生成微生物的代谢模型。

## 文件位置

`core/tools/design/carveme_tool/carveme_tool.py`

## 功能描述

CarvemeTool 的主要功能包括：
1. 读取输入的蛋白质序列文件
2. 使用 CarveMe 算法构建代谢模型
3. 生成 SBML 格式的代谢模型文件
4. 提供模型验证和质量检查功能

## 参数说明

### 输入参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| input_path | str | 是 | 输入蛋白质序列文件的目录路径 |
| output_path | str | 是 | 输出代谢模型文件的目录路径 |
| genomes_path | str | 否 | 基因组文件路径（可选） |
| threads | int | 否 | 并行处理线程数，默认为1 |
| overwrite | bool | 否 | 是否覆盖已存在的输出文件，默认为False |

### 输出结果

工具执行成功时返回包含以下字段的字典：
- `status`: "success"
- `data`: 包含输出路径、模型数量等信息的字典

工具执行失败时返回包含以下字段的字典：
- `status`: "error"
- `message`: 错误信息

## 使用示例

```python
from core.tools.design.carveme_tool import CarvemeTool

# 初始化工具
tool = CarvemeTool()

# 调用工具
result = tool._run(
    input_path="/path/to/input/proteins",
    output_path="/path/to/output/models",
    threads=4,
    overwrite=True
)

# 检查结果
if result.get("status") == "success":
    print("模型构建成功")
else:
    print(f"模型构建失败: {result.get('message')}")
```

## 工作原理

1. **输入处理**: 工具首先检查输入目录中的蛋白质序列文件（通常是FASTA格式）
2. **模型构建**: 使用 CarveMe 算法为每个输入文件构建代谢模型
3. **输出生成**: 将生成的模型保存为 SBML 格式的 XML 文件
4. **结果验证**: 验证生成的模型文件是否完整和有效

## 注意事项

1. 输入文件应为有效的蛋白质序列文件
2. 确保有足够的磁盘空间存储输出模型文件
3. 根据系统资源适当设置线程数
4. 注意输出路径的权限设置

## 常见问题和解决方案

### 1. 模型构建失败
**问题**: 工具返回错误状态
**解决方案**: 
- 检查输入文件格式是否正确
- 确认输入文件路径是否存在
- 查看详细的错误信息日志

### 2. 输出文件不完整
**问题**: 生成的模型文件缺少必要组件
**解决方案**:
- 重新运行工具并启用调试模式
- 检查输入序列的质量和完整性
- 验证 CarveMe 算法的参数设置

### 3. 性能问题
**问题**: 工具执行时间过长
**解决方案**:
- 减少输入文件数量，分批处理
- 增加线程数（根据系统资源）
- 使用更高性能的计算资源