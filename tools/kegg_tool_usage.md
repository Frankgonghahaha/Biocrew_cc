# KEGG工具使用说明

## 工具概述
KEGG工具用于访问KEGG数据库，查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息。该工具可以帮助智能体获取生物代谢路径、基因功能、酶反应等相关信息。

## 功能列表
1. `get_database_info(database)` - 获取数据库信息
2. `list_entries(database, organism)` - 列出数据库中的条目
3. `find_entries(database, keywords)` - 根据关键词搜索条目
4. `get_entry(entry_id, format_type)` - 获取特定条目的详细信息
5. `link_entries(target_db, source_db_entries)` - 查找相关条目
6. `convert_id(target_db, source_ids)` - 转换ID格式
7. `search_pathway_by_compound(compound_id)` - 根据化合物ID搜索相关代谢路径
8. `search_genes_by_pathway(pathway_id)` - 根据pathway ID搜索相关基因
9. `search_enzymes_by_compound(compound_id)` - 根据化合物ID搜索相关酶

## 使用示例

### 1. 获取数据库信息
```python
from tools.kegg_tool import KeggTool

kegg_tool = KeggTool()
result = kegg_tool.get_database_info("pathway")
print(result)
```

### 2. 搜索基因
```python
from tools.kegg_tool import KeggTool

kegg_tool = KeggTool()
result = kegg_tool.find_entries("genes", "cadmium")
print(result)
```

### 3. 列出人类基因
```python
from tools.kegg_tool import KeggTool

kegg_tool = KeggTool()
result = kegg_tool.list_entries("genes", "hsa")
print(result)
```

### 4. 搜索代谢路径
```python
from tools.kegg_tool import KeggTool

kegg_tool = KeggTool()
result = kegg_tool.find_entries("pathway", "heavy metal")
print(result)
```

## 数据库说明
KEGG工具支持以下数据库：
- `pathway`: 代谢路径信息
- `ko`: KEGG Orthology信息
- `genome`: 基因组信息
- `reaction`: 生化反应信息
- `enzyme`: 酶信息
- `genes`: 基因信息

## 返回结果格式
所有方法都返回一个字典，包含以下字段：
- `status`: "success" 或 "error"
- `data`: 查询结果数据（成功时）或 None（失败时）
- `message`: 错误信息（失败时）或空字符串（成功时）
- 其他特定于方法的字段

## 错误处理
如果查询过程中发生错误，工具会返回包含错误信息的字典，不会抛出异常。

## 注意事项
1. 该工具需要网络连接才能访问KEGG API
2. 某些查询可能需要较长时间，请耐心等待
3. 请合理使用API，避免频繁查询
4. KEGG数据库有查询频率限制，请不要过于频繁地调用API