# 数据库工具报告

## 概述

本项目使用专门化的数据库工具替代了原有的统一数据工具，以提供更精确和可维护的数据访问服务。所有工具都遵循CrewAI框架的工具规范，并通过DatabaseToolFactory进行统一管理。

## 工具列表

### 1. PollutantDataQueryTool
- **文件**: `pollutant_data_query_tool.py`
- **功能**: 查询指定污染物的所有相关数据，包括基因数据和微生物数据
- **主要方法**: `_run(pollutant_name: str, data_type: str = "both")`
- **返回值**: 包含基因数据和微生物数据的字典

### 2. GeneDataQueryTool
- **文件**: `gene_data_query_tool.py`
- **功能**: 查询指定污染物的基因数据
- **主要方法**: `_run(pollutant_name: str)`
- **返回值**: 包含基因数据的字典

### 3. OrganismDataQueryTool
- **文件**: `organism_data_query_tool.py`
- **功能**: 查询指定污染物的微生物数据
- **主要方法**: `_run(pollutant_name: str)`
- **返回值**: 包含微生物数据的字典

### 4. PollutantSummaryTool
- **文件**: `pollutant_summary_tool.py`
- **功能**: 获取指定污染物的摘要统计信息
- **主要方法**: `_run(pollutant_name: str)`
- **返回值**: 包含污染物摘要信息的字典

### 5. PollutantSearchTool
- **文件**: `pollutant_search_tool.py`
- **功能**: 根据关键字搜索污染物
- **主要方法**: `_run(keyword: str)`
- **返回值**: 包含匹配污染物列表的字典

### 6. DatabaseToolFactory
- **文件**: `database_tool_factory.py`
- **功能**: 工具工厂类，用于创建和管理所有数据库工具
- **主要方法**: 
  - `create_all_tools()`: 创建所有数据库工具实例
  - `get_tool_by_name(tool_name: str)`: 根据工具名称获取工具实例

### 7. EnviPathTool
- **文件**: `envipath_tool.py`
- **功能**: 访问enviPath数据库中的环境污染物生物转化路径数据
- **主要方法**: 
  - `_run(operation, **kwargs)`: 统一接口
  - `search_compound(compound_name)`: 搜索化合物
  - `get_pathway_info(pathway_id)`: 获取路径信息

### 8. KeggTool
- **文件**: `kegg_tool.py`
- **功能**: 访问KEGG数据库中的生物通路和基因组数据
- **主要方法**: 
  - `_run(operation, **kwargs)`: 统一接口
  - 多种操作方法，如`get_database_info`, `list_entries`, `find_entries`等

### 9. EvaluationTool
- **文件**: `evaluation_tool.py`
- **功能**: 分析和评估微生物菌剂的有效性
- **主要方法**: 
  - `_run(operation, **kwargs)`: 统一接口
  - `analyze_evaluation_result(evaluation_report)`: 分析评估结果
  - `check_core_standards(evaluation_report)`: 检查核心标准

## 工具架构优势

1. **职责分离**: 每个工具都有明确的职责，提高了代码的可读性和可维护性
2. **易于扩展**: 添加新工具时不会影响现有工具的功能
3. **错误隔离**: 单个工具的问题不会影响其他工具的正常运行
4. **性能优化**: 每个工具都针对其特定功能进行了优化
5. **统一接口**: 所有工具都遵循相同的接口规范，便于使用和管理

## 使用方式

所有数据库工具都通过DatabaseToolFactory创建和管理。智能体在创建时会获取所有数据库工具实例：

```python
from tools.database_tool_factory import DatabaseToolFactory
tools = DatabaseToolFactory.create_all_tools()
```

## 维护建议

1. 定期检查数据库连接配置，确保工具能够正常访问数据源
2. 监控工具的性能表现，必要时进行优化
3. 保持工具接口的一致性，避免破坏性更改
4. 为新功能开发专门的工具，而不是扩展现有工具的功能