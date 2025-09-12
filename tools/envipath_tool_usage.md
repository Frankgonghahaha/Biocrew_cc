# EnviPath工具使用说明

## 工具概述
EnviPath工具用于访问EnviPath数据库，查询环境化合物代谢路径信息。该工具可以帮助智能体获取环境中污染物的代谢路径和相关生物降解信息。

## 功能列表
1. `search_compound(compound_name)` - 搜索化合物信息
2. `get_pathway_info(pathway_id)` - 获取特定pathway的详细信息
3. `get_compound_pathways(compound_id)` - 获取与特定化合物相关的代谢路径
4. `search_pathways_by_keyword(keyword)` - 根据关键词搜索pathway

## 使用示例

### 1. 搜索化合物
```python
from tools.envipath_tool import EnviPathTool

envipath_tool = EnviPathTool()
result = envipath_tool.search_compound("cadmium")
print(result)
```

### 2. 根据关键词搜索pathway
```python
from tools.envipath_tool import EnviPathTool

envipath_tool = EnviPathTool()
result = envipath_tool.search_pathways_by_keyword("heavy metal")
print(result)
```

## 返回结果格式
所有方法都返回一个字典，包含以下字段：
- `status`: "success" 或 "error"
- `data`: 查询结果数据（成功时）或 None（失败时）
- `message`: 错误信息（失败时）或空字符串（成功时）
- 其他特定于方法的字段

## 错误处理
如果查询过程中发生错误，工具会返回包含错误信息的字典，不会抛出异常。

## 注意事项
1. 该工具需要网络连接才能访问EnviPath API
2. 某些查询可能需要较长时间，请耐心等待
3. 请合理使用API，避免频繁查询