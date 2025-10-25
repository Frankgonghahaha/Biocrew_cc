# 基于SQL的蛋白质序列查询工具使用指南

## 概述

本文档详细介绍了如何使用基于SQL的蛋白质序列查询工具替代传统的.faa文件处理方式。该工具通过将蛋白质序列存储在SQLite数据库中，并提供高效的查询接口，显著提升了蛋白质序列检索的性能和便利性。

## 传统.faa文件处理方式的问题

1. **查询效率低**: 需要遍历整个文件才能找到匹配的序列
2. **并发处理困难**: 文件锁定机制限制了多用户同时访问
3. **数据管理复杂**: 需要管理大量的.faa文件
4. **存储成本高**: 文件系统存储效率较低
5. **扩展性差**: 添加新数据需要重新组织文件结构

## 基于SQL的解决方案优势

1. **更快的查询速度**: SQL索引提供O(log n)查询时间复杂度
2. **更好的并发处理**: 数据库支持多用户同时查询
3. **更简单的数据管理**: 集中式数据库管理
4. **更低的存储成本**: 数据库存储通常比文件存储更高效
5. **更强的数据一致性**: 事务支持确保数据完整性
6. **更好的可扩展性**: 可以轻松添加新的蛋白质序列数据

## 工具组件

### 1. ProteinSequenceQuerySQLTool (核心查询工具)

位于: `core/tools/design/protein_sequence_query_sql.py`

功能:
- 从SQLite数据库中查询蛋白质序列
- 支持序列相似度、E-value、比对长度等BLAST-like阈值过滤
- 返回满足条件的蛋白质序列列表

### 2. 数据库初始化脚本

位于: `scripts/init_protein_db.py`

功能:
- 创建SQLite数据库
- 创建蛋白质序列表结构
- 插入示例蛋白质序列数据

### 3. 更新的CarvemeTool

位于: `scripts/update_carveme_for_sql.py`

功能:
- 集成SQL查询功能
- 自动将查询结果转换为.faa格式供Carveme处理
- 无缝替代传统.faa文件处理流程

## 使用方法

### 1. 初始化数据库

```bash
python3 scripts/init_protein_db.py
```

### 2. 使用蛋白质序列查询工具

```python
from core.tools.design.protein_sequence_query_sql import ProteinSequenceQuerySQLTool

# 创建工具实例
tool = ProteinSequenceQuerySQLTool()

# 查询相似蛋白质序列
result = tool._run(
    query_sequence="MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF",
    min_identity=50.0,
    max_evalue=1e-5,
    min_alignment_length=50,
    limit=100,
    database_path="protein_sequences.db"
)

# 处理查询结果
if result['status'] == 'success':
    for match in result['results']:
        print(f"物种: {match['species_name']}")
        print(f"基因: {match['gene_name']}")
        print(f"蛋白质ID: {match['protein_id']}")
        print(f"相似度: {match['identity']}%")
        print(f"序列: {match['sequence']}")
```

### 3. 使用更新的CarvemeTool

```python
from scripts.update_carveme_for_sql import UpdatedCarvemeTool

# 创建工具实例
tool = UpdatedCarvemeTool()

# 使用SQL查询结果运行Carveme
result = tool._run_with_sql_query(
    query_sequence="MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF",
    min_identity=50.0,
    max_evalue=1e-5,
    min_alignment_length=50,
    limit=100,
    database_path="protein_sequences.db",
    output_path="./outputs/metabolic_models",
    threads=4,
    overwrite=True
)
```

## 数据库结构

### protein_sequences 表

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | INTEGER PRIMARY KEY | 主键，自增ID |
| species_name | TEXT | 物种名称 |
| gene_name | TEXT | 基因名称 |
| protein_id | TEXT | 蛋白质ID（唯一） |
| sequence | TEXT | 蛋白质氨基酸序列 |
| sequence_length | INTEGER | 序列长度 |
| description | TEXT | 描述信息 |

### 索引

1. `idx_sequence_length` - 在sequence_length字段上创建的索引
2. `idx_species_name` - 在species_name字段上创建的索引
3. `idx_protein_id` - 在protein_id字段上创建的索引

## 性能优化

### 1. 查询优化

- 使用sequence_length索引进行初步筛选
- 通过长度差异容忍度减少需要详细比对的候选序列数量
- 对候选序列进行排序以优先处理最可能匹配的序列

### 2. 数据库优化

- 合理的索引设计
- 定期维护数据库统计信息
- 使用适当的缓存策略

## 扩展性

### 添加新的蛋白质序列

```python
import sqlite3

def add_protein_sequence(db_path, species_name, gene_name, protein_id, sequence, description):
    """
    向数据库添加新的蛋白质序列
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO protein_sequences 
        (species_name, gene_name, protein_id, sequence, sequence_length, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (species_name, gene_name, protein_id, sequence, len(sequence), description))
    
    conn.commit()
    conn.close()
```

### 批量导入.faa文件

```python
def import_faa_file(db_path, faa_file_path, species_name):
    """
    将.faa文件导入数据库
    """
    # 解析.faa文件并插入数据库
    # 实现细节省略
    pass
```

## 故障排除

### 1. 数据库文件不存在

确保已运行初始化脚本:
```bash
python3 scripts/init_protein_db.py
```

### 2. 查询结果为空

检查以下参数设置:
- 降低min_identity阈值
- 增加max_evalue阈值
- 减少min_alignment_length要求

### 3. 性能问题

- 检查数据库索引是否正确创建
- 确保查询序列长度合理
- 调整length_tolerance参数

## 最佳实践

1. **定期维护数据库**: 更新统计信息，重建索引
2. **合理设置查询参数**: 根据实际需求调整相似度和E-value阈值
3. **监控查询性能**: 记录查询时间，优化慢查询
4. **备份重要数据**: 定期备份数据库文件
5. **版本控制**: 对数据库模式变更进行版本控制

## 结论

基于SQL的蛋白质序列查询工具提供了一种高效、可扩展的替代方案，用于替代传统的.faa文件处理方式。通过利用数据库的优势，我们可以显著提升蛋白质序列查询的性能，简化数据管理，并为未来的扩展提供良好的基础。