# SmartDataQueryTool 使用说明

## 简介
SmartDataQueryTool 是一个智能数据查询工具，能够在Agent的思考过程中自动识别和查询相关的基因或微生物数据。它基于LocalDataRetriever工具构建，提供了更高级的自动化数据查询功能。

## 安装依赖
确保已安装以下依赖：
```bash
pip install pandas openpyxl
```

## 使用方法

### 1. 导入并初始化
```python
from tools.smart_data_query_tool import SmartDataQueryTool

# 创建智能数据查询工具实例
smart_query = SmartDataQueryTool()
```

### 2. 自动识别并查询相关数据
```python
# 根据用户输入或Agent思考内容自动查询相关数据
query_text = "我们需要处理Alpha-hexachlorocyclohexane污染问题"
result = smart_query.query_related_data(query_text)

if result["status"] == "success":
    print("匹配的污染物:", result["matched_pollutants"])
    
    # 查看基因数据
    for pollutant, data_info in result["gene_data"].items():
        if "error" not in data_info:
            print(f"{pollutant} 基因数据形状: {data_info['shape']}")
            print(f"列名: {data_info['columns']}")
    
    # 查看微生物数据
    for pollutant, data_info in result["organism_data"].items():
        if "error" not in data_info:
            print(f"{pollutant} 微生物数据形状: {data_info['shape']}")
            print(f"列名: {data_info['columns']}")
```

### 3. 查询指定类型的数据
```python
# 只查询基因数据
result = smart_query.query_related_data(query_text, data_type="gene")

# 只查询微生物数据
result = smart_query.query_related_data(query_text, data_type="organism")
```

### 4. 查询指定工作表的数据
```python
# 查询特定工作表
result = smart_query.query_related_data(query_text, sheet_name=1)  # 第二个工作表
result = smart_query.query_related_data(query_text, sheet_name="Sheet2")  # 指定名称的工作表
```

### 5. 查询所有工作表数据
```python
# 查询指定污染物的所有工作表数据
all_sheets_data = smart_query.query_all_sheets_for_pollutant("Alpha-hexachlorocyclohexane")
```

### 6. 获取数据摘要
```python
# 获取数据摘要信息
summary = smart_query.get_data_summary("Alpha-hexachlorocyclohexane")
print("基因数据摘要:", summary["gene_summary"])
print("微生物数据摘要:", summary["organism_summary"])
```

## 在智能体中使用示例

### 工程微生物组识别智能体中使用
```python
from tools.smart_data_query_tool import SmartDataQueryTool

class EngineeringMicroorganismIdentificationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.smart_query = SmartDataQueryTool()
    
    def process_user_request(self, user_input):
        """处理用户请求并自动查询相关数据"""
        # 自动识别并查询相关数据
        query_result = self.smart_query.query_related_data(user_input)
        
        if query_result["status"] == "success":
            # 构建数据上下文供LLM使用
            data_context = self._build_data_context(query_result)
            return data_context
        else:
            return "未找到相关数据"
    
    def _build_data_context(self, query_result):
        """构建数据上下文"""
        context = "根据您的请求，我找到了以下相关数据:\n\n"
        
        # 添加基因数据信息
        if query_result["gene_data"]:
            context += "基因数据:\n"
            for pollutant, data_info in query_result["gene_data"].items():
                if "error" not in data_info:
                    context += f"- {pollutant}: {data_info['shape'][0]}行{data_info['shape'][1]}列\n"
        
        # 添加微生物数据信息
        if query_result["organism_data"]:
            context += "\n微生物数据:\n"
            for pollutant, data_info in query_result["organism_data"].items():
                if "error" not in data_info:
                    context += f"- {pollutant}: {data_info['shape'][0]}行{data_info['shape'][1]}列\n"
        
        return context
    
    def create_agent(self):
        from crewai import Agent
        
        return Agent(
            role='功能微生物组识别专家',
            goal='根据水质净化目标筛选功能微生物和代谢互补微生物',
            backstory="""你是一位功能微生物组识别专家，能够智能地从本地数据中查询相关信息。
            你可以自动识别用户请求中的污染物名称，并查询相关的基因和微生物数据。""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
```

## 方法说明

### query_related_data(query_text, data_type="both", sheet_name=0)
根据查询文本自动识别并查询相关数据

**参数:**
- `query_text` (str): 查询文本
- `data_type` (str): 数据类型，"gene"、"organism" 或 "both"
- `sheet_name` (str or int): 工作表名称或索引

**返回:**
- `dict`: 包含查询结果的字典

### query_all_sheets_for_pollutant(pollutant_name, data_type="both")
查询指定污染物的所有工作表数据

**参数:**
- `pollutant_name` (str): 污染物名称
- `data_type` (str): 数据类型，"gene"、"organism" 或 "both"

**返回:**
- `dict`: 包含所有工作表数据的字典

### get_data_summary(pollutant_name, data_type="both")
获取指定污染物的数据摘要

**参数:**
- `pollutant_name` (str): 污染物名称
- `data_type` (str): 数据类型，"gene"、"organism" 或 "both"

**返回:**
- `dict`: 数据摘要信息

## 注意事项
1. 工具会自动识别文本中的污染物名称并查询相关数据
2. 支持模糊匹配，能够处理不完全匹配的名称
3. 返回的数据包含基本信息和示例数据，便于Agent理解和使用
4. 错误处理机制确保即使部分数据查询失败也不会影响整体流程
