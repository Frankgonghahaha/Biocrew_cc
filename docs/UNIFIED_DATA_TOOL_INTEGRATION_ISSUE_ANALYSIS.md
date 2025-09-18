# UnifiedDataTool与CrewAI框架集成问题分析报告

## 问题概述

在智能体与统一数据工具集成过程中，发现以下问题：
1. 智能体生成的JSON字符串格式是正确的
2. 工具本身能够正确处理JSON字符串参数
3. 但当通过CrewAI框架调用时，工具返回"缺少必需参数"错误

## 问题分析

通过测试发现，问题根源在于CrewAI框架与UnifiedDataTool参数传递机制不匹配：

### 1. 不同调用方式的行为差异

**直接调用（成功）：**
```python
tool._run("query_pollutant_data", pollutant_name="Aldrin")
```

**JSON字符串调用（成功）：**
```python
tool._run('{"operation": "query_pollutant_data", "pollutant_name": "Aldrin"}')
```

**CrewAI框架调用（失败）：**
```python
tool._run({"operation": "query_pollutant_data", "pollutant_name": "Aldrin"})
```

### 2. 参数解析逻辑不足

当前UnifiedDataTool的`_run`方法参数解析逻辑存在以下问题：
1. 只能处理第一个参数为字符串的情况
2. 对于字典形式的参数传递处理不足
3. 无法正确识别CrewAI框架传递的参数格式

## 解决方案

### 方案一：增强参数解析逻辑（推荐）

修改UnifiedDataTool的`_run`方法，增强其参数解析能力：

```python
def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
    """
    增强版参数解析逻辑
    """
    try:
        # 检查operation是否为字典（CrewAI框架调用方式）
        if isinstance(operation, dict):
            # 直接使用字典作为参数
            processed_kwargs = operation.copy()
            # 从processed_kwargs中获取operation
            operation = processed_kwargs.pop('operation', '')
        # 检查operation是否为JSON字符串
        elif isinstance(operation, str) and operation.startswith('{') and operation.endswith('}'):
            try:
                parsed_operation = json.loads(operation)
                if isinstance(parsed_operation, dict):
                    # 使用解析后的字典作为参数
                    processed_kwargs = parsed_operation.copy()
                    # 从processed_kwargs中获取operation
                    operation = processed_kwargs.pop('operation', operation)
                else:
                    # 如果不是字典，保持原样
                    processed_kwargs = kwargs.copy()
            except Exception as e:
                # 如果解析失败，保持原样
                processed_kwargs = kwargs.copy()
        else:
            # 处理普通字符串参数和kwargs
            processed_kwargs = kwargs.copy()
            
            # 处理可能的JSON字符串参数
            for key, value in processed_kwargs.items():
                # 如果值是字符串且看起来像JSON，尝试解析它
                if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                    try:
                        parsed_value = json.loads(value)
                        # 如果解析后的值是字典，合并到processed_kwargs中
                        if isinstance(parsed_value, dict):
                            processed_kwargs.update(parsed_value)
                    except:
                        # 如果解析失败，保持原样
                        pass
        
        # ... 后续处理逻辑保持不变
```

### 方案二：修改工具的args_schema

为UnifiedDataTool定义更完整的参数模式，明确指定所有可能的参数：

```python
class UnifiedDataTool(BaseTool):
    name: str = "统一数据访问工具"
    description: str = "整合本地数据库和外部数据库的数据访问功能，提供一站式数据查询服务"
    
    # 定义更完整的参数模式
    def __init__(self):
        super().__init__()
        # 设置args_schema以支持所有可能的参数
        self.args_schema = type(
            "UnifiedDataToolSchema",
            (BaseModel,),
            {
                "operation": Field(description="要执行的操作名称"),
                "pollutant_name": Field(default=None, description="污染物名称"),
                "data_type": Field(default="both", description="数据类型"),
                "enzyme_type": Field(default=None, description="酶类型"),
                "organism_type": Field(default=None, description="微生物类型"),
                "query_text": Field(default=None, description="查询文本"),
                "keyword": Field(default=None, description="搜索关键词")
            }
        )
```

## 实施建议

1. **优先采用方案一**：增强参数解析逻辑，使工具能够兼容多种调用方式
2. **保持向后兼容性**：确保现有调用方式仍然有效
3. **增加测试用例**：验证各种调用方式的正确性
4. **文档更新**：更新工具使用文档，说明支持的调用方式

## 测试验证

创建测试用例验证修复效果：

```python
def test_crewai_integration():
    """测试CrewAI框架集成"""
    tool = UnifiedDataTool()
    
    # 测试CrewAI框架调用方式
    result = tool._run({"operation": "query_pollutant_data", "pollutant_name": "Aldrin"})
    assert result["status"] == "success"
    assert result["pollutant_name"] == "Aldrin"
```

## 结论

通过增强UnifiedDataTool的参数解析逻辑，可以有效解决与CrewAI框架集成时的参数传递问题，确保工具在各种调用方式下都能正常工作。
