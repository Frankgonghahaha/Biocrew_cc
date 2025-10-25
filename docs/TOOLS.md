# 工具详细说明

## 概述

本项目包含多种工具，分为数据库工具、外部数据库访问工具、设计工具和评估工具四类。所有工具都遵循CrewAI框架的工具规范，并通过DatabaseToolFactory进行统一管理。

## 数据库工具

### 1. PollutantDataQueryTool

**文件**: `core/tools/database/pollutant_query.py`

**功能**: 查询指定污染物的所有相关数据，包括基因数据和微生物数据

**参数**:
- `pollutant_name` (str): 污染物名称（必填）
- `data_type` (str): 数据类型，可选值为"gene"、"organism"、"both"，默认为"both"

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `pollutant_name`: 查询的污染物名称
- `gene_data`: 基因数据列表（如果请求了基因数据）
- `organism_data`: 微生物数据列表（如果请求了微生物数据）

**使用示例**:
```python
tool = PollutantDataQueryTool()
result = tool._run(pollutant_name="endrin", data_type="both")
```

### 2. GeneDataQueryTool

**文件**: `core/tools/database/gene_query.py`

**功能**: 查询指定污染物的基因数据

**参数**:
- `pollutant_name` (str): 污染物名称（必填）

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `pollutant_name`: 查询的污染物名称
- `gene_data`: 基因数据列表

**使用示例**:
```python
tool = GeneDataQueryTool()
result = tool._run(pollutant_name="endrin")
```

### 3. ProteinSequenceQuerySQLTool

**文件**: `core/tools/design/protein_sequence_query_sql.py`

**功能**: 基于SQL数据库的蛋白质序列查询工具，用于替代传统的.faa文件处理方式

**参数**:
- `query_sequence` (str): 查询蛋白质序列（必填）
- `min_identity` (float): 最小序列相似度百分比，默认50.0
- `max_evalue` (float): 最大E-value阈值，默认1e-5
- `min_alignment_length` (int): 最小比对长度，默认50
- `limit` (int): 返回结果数量限制，默认100
- `database_path` (str): SQL数据库文件路径，默认"protein_sequences.db"

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `query_sequence_length`: 查询序列长度
- `results`: 匹配结果列表，每个结果包含物种名、基因名、蛋白质ID、序列、相似度、E-value和比对长度
- `total_results`: 匹配结果总数

**使用示例**:
```python
tool = ProteinSequenceQuerySQLTool()
result = tool._run(
    query_sequence="MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK",
    min_identity=50.0,
    max_evalue=1e-5,
    min_alignment_length=50,
    limit=100,
    database_path="protein_sequences.db"
)
```

### 5. OrganismDataQueryTool

**文件**: `core/tools/database/organism_query.py`

**功能**: 查询指定污染物的微生物数据

**参数**:
- `pollutant_name` (str): 污染物名称（必填）

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `pollutant_name`: 查询的污染物名称
- `organism_data`: 微生物数据列表

**使用示例**:
```python
tool = OrganismDataQueryTool()
result = tool._run(pollutant_name="endrin")
```

### 6. PollutantSummaryTool

**文件**: `core/tools/database/summary.py`

**功能**: 获取指定污染物的摘要统计信息

**参数**:
- `pollutant_name` (str): 污染物名称（必填）

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `pollutant_name`: 查询的污染物名称
- `summary`: 污染物摘要信息

**使用示例**:
```python
tool = PollutantSummaryTool()
result = tool._run(pollutant_name="endrin")
```

### 7. PollutantSearchTool

**文件**: `core/tools/database/search.py`

**功能**: 根据关键字搜索污染物

**参数**:
- `keyword` (str): 搜索关键字（必填）

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `keyword`: 搜索关键字
- `results`: 匹配的污染物列表

**使用示例**:
```python
tool = PollutantSearchTool()
result = tool._run(keyword="endrin")
```

### 8. UniProtTool

**文件**: `core/tools/database/uniprot.py`

**功能**: 查询UniProt数据库中的蛋白质信息，包括蛋白质序列、功能注释等

**方法**:
- `_run(query, query_type, format, limit)`: 通用查询方法
- `search_by_protein_name(protein_name, limit)`: 根据蛋白质名称搜索
- `search_by_gene_name(gene_name, limit)`: 根据基因名称搜索
- `get_protein_sequence(uniprot_id)`: 获取蛋白质序列

**参数**:
- `query` (str): 查询字符串
- `query_type` (str): 查询类型（protein_name, id, gene_name, organism）
- `format` (str): 返回数据格式（json, xml, txt）
- `limit` (int): 返回结果数量限制

**返回值**: 包含以下字段的字典
- `status`: 状态信息（"success"或"error"）
- `query`: 查询字符串
- `query_type`: 查询类型
- `results`: 查询结果

**使用示例**:
```python
tool = UniProtTool()
# 通过蛋白质名称查询
result = tool.search_by_protein_name("lacZ", limit=5)
# 通过UniProt ID查询
result = tool.search_by_id("P00722")
# 获取蛋白质序列
result = tool.get_protein_sequence("P00722")
```

### 9. DatabaseToolFactory

**文件**: `core/tools/database/factory.py`

**功能**: 工具工厂类，用于创建和管理所有数据库工具

**方法**:
1. `create_all_tools()`: 创建所有数据库工具实例
2. `get_tool_by_name(tool_name: str)`: 根据工具名称获取工具实例

**使用示例**:
```python
from tools.database_tool_factory import DatabaseToolFactory
tools = DatabaseToolFactory.create_all_tools()
```

## 外部数据库访问工具

### 1. EnviPathTool

**文件**: `core/tools/database/envipath.py`

**功能**: 访问enviPath数据库中的环境污染物生物转化路径数据

**方法**:
- `_run(operation, **kwargs)`: 统一接口
- `search_compound(compound_name)`: 搜索化合物
- `get_pathway_info(pathway_id)`: 获取路径信息
- `get_compound_pathways(compound_id)`: 获取化合物路径
- `search_pathways_by_keyword(keyword)`: 根据关键字搜索路径

**使用示例**:
```python
tool = EnviPathTool()
result = tool._run(operation="search_compound", compound_name="endrin")
# 或者
result = tool.search_compound("endrin")
```

### 2. KeggTool

**文件**: `core/tools/database/kegg.py`

**功能**: 访问KEGG数据库中的生物通路和基因组数据

**方法**:
- `_run(operation, **kwargs)`: 统一接口
- `get_database_info(database)`: 获取数据库信息
- `list_entries(database)`: 列出数据库条目
- `find_entries(database, query)`: 查找条目
- `get_entry(entry_id)`: 获取条目详情
- `link_entries(source_db, target_db, entries)`: 链接条目
- `convert_id(source_db, target_db, entries)`: 转换ID
- `search_pathway_by_compound(compound_id)`: 根据化合物搜索通路
- `search_genes_by_pathway(pathway_id)`: 根据通路搜索基因
- `search_enzymes_by_compound(compound_id)`: 根据化合物搜索酶

**使用示例**:
```python
tool = KeggTool()
result = tool._run(operation="get_database_info", database="pathway")
# 或者
result = tool.get_database_info("pathway")
```

## 评估工具

### 1. EvaluationTool

**文件**: `core/tools/evaluation/evaluation.py`

**功能**: 分析和评估微生物菌剂的有效性

**方法**:
- `_run(operation, **kwargs)`: 统一接口
- `analyze_evaluation_result(evaluation_report)`: 分析评估结果
- `check_core_standards(evaluation_report)`: 检查核心标准

**使用示例**:
```python
tool = EvaluationTool()
result = tool._run(operation="analyze_evaluation_result", evaluation_report=report)
# 或者
result = tool.analyze_evaluation_result(report)
```

## 工具使用规范

### 参数格式
所有工具参数都使用双引号，不能使用单引号。

### 错误处理
所有工具都应正确处理异常，并返回包含状态信息的结果。

### 返回格式
工具返回结果应包含status字段，值为"success"或"error"。

## 工具架构优势

1. **职责分离**: 每个工具都有明确的职责，提高了代码的可读性和可维护性
2. **易于扩展**: 添加新工具时不会影响现有工具的功能
3. **错误隔离**: 单个工具的问题不会影响其他工具的正常运行
4. **性能优化**: 每个工具都针对其特定功能进行了优化
5. **统一接口**: 所有工具都遵循相同的接口规范，便于使用和管理