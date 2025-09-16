# 测试文件说明

## 核心测试文件

### 1. test_microorganism_identification_agent.py
**功能微生物识别智能体单元测试**
- 测试智能体创建功能
- 测试任务创建功能
- 测试本地数据工具
- 测试强制本地数据查询工具
- 测试数据完整性处理能力
- 运行方式: `python3 tests/test_microorganism_identification_agent.py`

### 2. test_data_integrity_handling.py
**数据完整性专项测试**
- 专门测试智能体在不同数据完整性情况下的表现
- 测试完整数据、部分数据、无本地数据等场景
- 验证智能体对数据缺失情况的处理能力
- 运行方式: `python3 tests/test_data_integrity_handling.py`

## 其他测试文件

### 3. test_database_tools.py
**数据库工具测试**
- 测试EnviPath和KEGG数据库访问工具
- 验证外部数据库查询功能
- 运行方式: `python3 tests/test_database_tools.py`

### 4. test_task_coordination.py
**任务协调专家测试**
- 测试任务协调专家的决策能力
- 验证任务协调逻辑的正确性
- 运行方式: `python3 tests/test_task_coordination.py`

### 5. test_main_fixes.py
**main.py修复功能测试**
- 测试main.py中修复的问题
- 验证CrewAI配置的正确性
- 运行方式: `python3 tests/test_main_fixes.py`
# 运行所有测试文件
python3 -m pytest tests/

# 或者逐个运行核心测试
python3 tests/test_microorganism_identification_agent.py
python3 tests/test_data_integrity_handling.py
```