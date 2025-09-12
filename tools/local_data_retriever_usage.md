# LocalDataRetriever 使用说明

## 简介
LocalDataRetriever 是一个用于从本地 data/Genes 和 data/Organism 目录中读取表格数据的工具类。它支持根据污染物名称查找并读取相应的 Excel 文件，并返回 pandas DataFrame 格式的数据。该工具还支持处理包含多个工作表的Excel文件。

## 安装依赖
确保已安装以下依赖：
```bash
pip install pandas openpyxl
```

## 使用方法

### 1. 导入并初始化
```python
from tools.local_data_retriever import LocalDataRetriever

# 创建数据读取工具实例
data_retriever = LocalDataRetriever()
```

### 2. 获取基因数据（默认第一个工作表）
```python
# 根据污染物名称获取基因数据（默认读取第一个工作表）
gene_data = data_retriever.get_gene_data("Alpha-hexachlorocyclohexane")

if gene_data is not None:
    print("基因数据:")
    print(gene_data.head())  # 显示前几行数据
else:
    print("未找到相关基因数据")
```

### 3. 获取指定工作表的基因数据
```python
# 读取特定工作表的数据
gene_data_sheet2 = data_retriever.get_gene_data("Alpha-hexachlorocyclohexane", sheet_name=1)  # 读取第二个工作表
# 或者按工作表名称读取
gene_data_by_name = data_retriever.get_gene_data("Alpha-hexachlorocyclohexane", sheet_name="Sheet2")
```

### 4. 获取所有工作表的基因数据
```python
# 获取所有工作表的数据
all_gene_sheets = data_retriever.get_gene_data_all_sheets("Alpha-hexachlorocyclohexane")

if all_gene_sheets is not None:
    for sheet_name, df in all_gene_sheets.items():
        print(f"工作表 '{sheet_name}' 数据形状: {df.shape}")
```

### 5. 获取微生物数据
```python
# 根据污染物名称获取微生物数据
organism_data = data_retriever.get_organism_data("Alpha-hexachlorocyclohexane")

if organism_data is not None:
    print("微生物数据:")
    print(organism_data.head())  # 显示前几行数据
else:
    print("未找到相关微生物数据")
```

### 6. 列出文件中的所有工作表名称
```python
# 获取指定文件的所有工作表名称
sheet_names = data_retriever.list_sheet_names("Alpha-hexachlorocyclohexane", data_type="gene")
if sheet_names is not None:
    print("工作表名称:")
    for name in sheet_names:
        print(f"  - {name}")
```

### 7. 列出所有可用污染物
```python
# 获取所有可用的污染物名称
pollutants = data_retriever.list_available_pollutants()
print("可用的基因数据污染物:")
for pollutant in pollutants["genes_pollutants"]:
    print(f"  - {pollutant}")

print("可用的微生物数据污染物:")
for pollutant in pollutants["organism_pollutants"]:
    print(f"  - {pollutant}")
```

### 8. 按关键词搜索文件
```python
# 根据关键词搜索相关数据文件
results = data_retriever.search_files_by_keyword("hexachloro")
print("匹配的基因数据文件:")
for file in results["matching_genes"]:
    print(f"  - {file}")

print("匹配的微生物数据文件:")
for file in results["matching_organisms"]:
    print(f"  - {file}")
```

## 在智能体中使用示例

### 工程微生物组识别智能体中使用
```python
from tools.local_data_retriever import LocalDataRetriever

class EngineeringMicroorganismIdentificationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.data_retriever = LocalDataRetriever()
    
    def create_agent(self):
        from crewai import Agent
        
        # 获取可用污染物列表
        pollutants = self.data_retriever.list_available_pollutants()
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标筛选功能微生物和代谢互补微生物',
            backstory=f"""你是一位功能微生物组识别专家，能够访问本地基因和微生物数据。
            可用的污染物数据包括: {', '.join(pollutants['genes_pollutants'][:10])} 等""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
```

## 错误处理
工具类包含基本的错误处理机制：
- 文件不存在时会抛出 FileNotFoundError 异常
- 读取文件出错时会打印错误信息并返回 None
- 路径配置错误时会在初始化时抛出异常

## 注意事项
1. 确保 data/Genes/Genes 和 data/Organism/Organism 目录结构正确
2. Excel 文件格式应为 .xlsx 或 .xls
3. 污染物名称匹配支持模糊搜索，但建议使用准确的名称以获得最佳结果
4. 工作表索引从0开始（第一个工作表索引为0）
5. 如果Excel文件只有一个工作表，使用默认参数即可
