# 强制本地数据查询工具使用说明

## 概述
强制本地数据查询工具(MandatoryLocalDataQueryTool)是一个确保智能体在处理过程中必须调用本地数据查询的工具。它强制智能体优先使用本地Excel数据，而不是仅依赖预训练知识。

## 主要功能
1. 强制查询本地基因和微生物数据
2. 获取可用污染物数据摘要
3. 确保智能体回复中包含具体的本地数据查询结果

## 使用方法

### 1. 初始化工具
```python
from tools.mandatory_local_data_query_tool import MandatoryLocalDataQueryTool

# 创建工具实例
mandatory_query = MandatoryLocalDataQueryTool(base_path=".")
```

### 2. 查询必需数据
```python
# 查询与特定文本相关的数据
query_result = mandatory_query.query_required_data(
    query_text="处理含有磺胺甲恶唑(SMX)的制药废水", 
    data_type="both"  # "gene", "organism" 或 "both"
)
```

### 3. 获取污染物摘要
```python
# 获取可用污染物数据摘要
pollutants_summary = mandatory_query.get_available_pollutants_summary()
```

## 在智能体中的集成
该工具已集成到`EngineeringMicroorganismIdentificationAgent`中，智能体会自动使用此工具确保本地数据查询。

## 测试验证
使用`test_smx_degradation.py`脚本可以验证工具的效果，智能体的回复将明确体现本地数据查询结果。