# ProteinBLASTSQL工具使用说明

## 工具概述

ProteinBLASTSQL工具是一个基于SQL数据库的蛋白质序列比对工具，模拟了BLAST的三个关键阈值：
- EVALUE_THRESHOLD = 1e-5
- IDENTITY_THRESHOLD = 50.0
- MIN_ALIGNMENT_LENGTH = 50

该工具可以在SQL数据库中快速查询蛋白质序列，提供类似BLAST的功能，但具有更快的查询速度和更好的可扩展性。

## 数据库结构

### 主要数据表

1. **protein_sequences表** - 存储蛋白质序列信息
   ```sql
   CREATE TABLE protein_sequences (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       species_name VARCHAR(255),     -- 物种名称
       gene_name VARCHAR(255),        -- 基因名称
       protein_id VARCHAR(100),       -- 蛋白质ID
       sequence TEXT,                 -- 蛋白质序列
       sequence_length INTEGER        -- 序列长度
   );
   ```

2. **kmer_index表** - 存储k-mer索引用于快速筛选
   ```sql
   CREATE TABLE kmer_index (
       kmer VARCHAR(7),               -- 7-mer序列
       protein_id INTEGER,            -- 对应蛋白质ID
       position INTEGER,              -- 在序列中的位置
       FOREIGN KEY (protein_id) REFERENCES protein_sequences(id)
   );
   ```

## 核心功能

### 1. 序列相似度计算
工具使用逐位比对方法计算两个序列的相似度百分比：
```python
def _calculate_sequence_identity(self, seq1: str, seq2: str) -> float:
    min_len = min(len(seq1), len(seq2))
    matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
    return (matches / min_len) * 100.0
```

### 2. E-value估算
使用简化公式估算E-value：
```python
def _estimate_evalue(self, alignment_length: int, matched_positions: int) -> float:
    identity = matched_positions / alignment_length if alignment_length > 0 else 0
    evalue = math.exp(-0.3 * (alignment_length - 10)) * 1000000 / (20 ** alignment_length)
    return max(evalue, 1e-200)
```

### 3. 查询逻辑
1. 首先通过序列长度筛选候选序列
2. 对候选序列进行详细比对
3. 应用三个阈值进行筛选
4. 按相似度排序返回结果

## 使用方法

### 1. 导入和初始化
```python
from core.tools.database.protein_blast_sql import ProteinBlastSQLTool

# 创建工具实例
tool = ProteinBlastSQLTool("protein_sequences.db")
```

### 2. 添加蛋白质序列
```python
# 添加蛋白质序列到数据库
tool.add_protein_sequence(
    species_name="Escherichia coli",
    gene_name="lacZ",
    protein_id="P00722",
    sequence="MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK"
)
```

### 3. 执行查询
```python
# 执行BLAST-like查询
result = tool._run(
    query_sequence="MKQLIVGASGSGKSTFLKFLEGYDWAEGNLVNVDPKDFLDAMTEGFLGSYDGNFVHVDYGINASLVYGNTDIYVAPQMVSGLNLPFYSQDPAVHAHFHQRLFGDQFSEFAEQVAAVDAVVKDTGMNLGQILQDAQIDPALAELGIQVVNQVDPKLQKLGFDAVIAVSLRQGHDAVMFGYDLAGIGMDVALQELHAKLNAQAALVVVSLGSMGDQEGYVDLLKHLGLKPDGIVLTSGYAHKQVVKSAAKYGVPVVVSSAYGGVDGQDGSYVAPAGIQAELGKLTGLAATVDSGAVVSDNQSFVAGYALTADGGRRAATVNGGQVVVTDGTTLTGTRAAATAEKFGGETVIVDGNQVVYGTQGGKATYANGQAVDYAAVVLQGLK",
    min_identity=50.0,
    max_evalue=1e-5,
    min_alignment_length=50,
    limit=10
)
```

## 参数说明

### 查询参数
- `query_sequence` (str): 必需，查询蛋白质序列
- `min_identity` (float): 可选，默认50.0，最小序列相似度百分比(0-100)
- `max_evalue` (float): 可选，默认1e-5，最大E-value阈值
- `min_alignment_length` (int): 可选，默认50，最小比对长度
- `limit` (int): 可选，默认100，返回结果数量限制

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

## 性能优化

### 1. 索引优化
```sql
CREATE INDEX idx_species ON protein_sequences(species_name);
CREATE INDEX idx_gene ON protein_sequences(gene_name);
CREATE INDEX idx_protein_id ON protein_sequences(protein_id);
CREATE INDEX idx_sequence_length ON protein_sequences(sequence_length);
CREATE INDEX idx_kmer ON kmer_index(kmer);
CREATE INDEX idx_protein_position ON kmer_index(protein_id, position);
```

### 2. k-mer预计算
工具会自动为每个蛋白质序列预计算7-mer，用于快速筛选候选序列。

## 与传统BLAST的对比

| 特性 | 传统BLAST | ProteinBLASTSQL |
|------|-----------|-----------------|
| 查询速度 | 较慢 | 快速 |
| 数据库支持 | 无 | SQLite/MySQL/PostgreSQL |
| 并行处理 | 支持 | 支持 |
| 相似度计算 | 复杂算法 | 简化算法 |
| E-value计算 | 精确 | 估算 |
| 易于维护 | 困难 | 容易 |

## 使用场景

1. **快速蛋白质序列查询** - 当需要快速查询相似蛋白质时
2. **大规模序列比对** - 当处理大量蛋白质序列时
3. **集成到应用中** - 当需要将序列比对功能集成到应用程序中时
4. **离线查询** - 当无法访问外部BLAST服务时

## 注意事项

1. E-value计算是简化的估算，可能与BLAST的精确值有差异
2. 序列相似度计算使用简单的逐位比对，不考虑氨基酸理化性质
3. 数据库性能取决于索引和硬件配置
4. 对于非常精确的比对需求，建议使用传统BLAST工具