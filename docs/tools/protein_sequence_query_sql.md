# ProteinSequenceQuerySQLTool使用说明

## 工具概述

ProteinSequenceQuerySQLTool是一个基于SQL数据库的蛋白质序列查询工具，用于替代传统的.faa文件处理方式。该工具可以直接从SQL数据库中查询蛋白质序列，提供快速、高效的序列比对功能。

## 功能特点

1. **快速查询**：通过SQL数据库索引实现快速序列检索
2. **阈值控制**：支持BLAST的三个关键阈值：
   - 最小序列相似度百分比 (min_identity)
   - 最大E-value阈值 (max_evalue)
   - 最小比对长度 (min_alignment_length)
3. **灵活配置**：支持自定义数据库路径和查询参数
4. **高效比对**：使用优化的序列比对算法

## 使用方法

### 1. 导入工具
```python
from core.tools.design import ProteinSequenceQuerySQLTool
```

### 2. 创建工具实例
```python
tool = ProteinSequenceQuerySQLTool()
```

### 3. 执行查询
```python
result = tool._run(
    query_sequence="MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK",
    min_identity=50.0,
    max_evalue=1e-5,
    min_alignment_length=50,
    limit=100,
    database_path="protein_sequences.db"
)
```

## 参数说明

### 输入参数
- `query_sequence` (str): 必需，查询蛋白质序列
- `min_identity` (float): 可选，默认50.0，最小序列相似度百分比(0-100)
- `max_evalue` (float): 可选，默认1e-5，最大E-value阈值
- `min_alignment_length` (int): 可选，默认50，最小比对长度
- `limit` (int): 可选，默认100，返回结果数量限制
- `database_path` (str): 可选，默认"protein_sequences.db"，SQL数据库文件路径

### 返回结果
```json
{
  "status": "success",
  "query_sequence_length": 1143,
  "results": [
    {
      "species_name": "Escherichia coli",
      "gene_name": "lacZ",
      "protein_id": "P00722",
      "sequence": "MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK",
      "identity": 100.0,
      "evalue": 1e-200,
      "alignment_length": 1143
    }
  ],
  "total_results": 1
}
```

## 数据库结构

工具期望的数据库结构如下：

```sql
CREATE TABLE protein_sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_name VARCHAR(255),
    gene_name VARCHAR(255),
    protein_id VARCHAR(100),
    sequence TEXT,
    sequence_length INTEGER
);

-- 创建索引以提高查询性能
CREATE INDEX idx_species ON protein_sequences(species_name);
CREATE INDEX idx_gene ON protein_sequences(gene_name);
CREATE INDEX idx_protein_id ON protein_sequences(protein_id);
CREATE INDEX idx_sequence_length ON protein_sequences(sequence_length);
```

## 与传统.faa文件处理的对比

| 特性 | 传统.faa文件处理 | ProteinSequenceQuerySQLTool |
|------|------------------|-----------------------------|
| 查询速度 | 慢 | 快 |
| 存储方式 | 文件系统 | 数据库 |
| 并发处理 | 有限 | 支持 |
| 数据管理 | 复杂 | 简单 |
| 扩展性 | 有限 | 强 |
| 维护成本 | 高 | 低 |

## 使用场景

1. **替代本地.faa文件处理**：当需要快速查询蛋白质序列时
2. **大规模序列比对**：当处理大量蛋白质序列时
3. **集成到应用中**：当需要将序列查询功能集成到应用程序中时
4. **离线查询**：当无法访问外部数据库服务时

## 注意事项

1. 需要预先构建包含蛋白质序列的SQL数据库
2. E-value计算是简化的估算，可能与BLAST的精确值有差异
3. 序列相似度计算使用简单的逐位比对，不考虑氨基酸理化性质
4. 数据库性能取决于索引和硬件配置