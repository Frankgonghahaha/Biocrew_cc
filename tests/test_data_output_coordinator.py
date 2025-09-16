#!/usr/bin/env python3
"""
测试数据输出协调器功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from tools.data_output_coordinator import DataOutputCoordinator

def test_data_output_coordinator_creation():
    """测试数据输出协调器创建"""
    print("=== 测试数据输出协调器创建 ===")
    
    # 创建数据输出协调器实例
    coordinator = DataOutputCoordinator()
    
    print(f"工具名称: {coordinator.name}")
    print(f"工具描述: {coordinator.description}")
    
    # 验证工具基本信息
    assert coordinator.name == "数据输出协调器", f"工具名称不正确: {coordinator.name}"
    assert "生成完整、结构化和多元化的数据输出" in coordinator.description, f"工具描述不正确: {coordinator.description}"
    
    print("✓ 数据输出协调器创建成功")
    print("✓ 工具名称正确")
    print("✓ 工具描述正确")
    
    print("\n数据输出协调器创建测试完成。")

def test_format_output_function():
    """测试格式化输出功能"""
    print("\n=== 测试格式化输出功能 ===")
    
    # 创建数据输出协调器实例
    coordinator = DataOutputCoordinator()
    
    # 测试数据
    test_data = {
        "microorganisms": ["Bacillus subtilis", "Pseudomonas putida"],
        "genes": ["degA", "degB"],
        "complementarity_index": 0.85
    }
    
    # 测试JSON格式化
    print("测试JSON格式化:")
    result = coordinator.format_output(test_data, "json")
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  格式类型: {result['format_type']}")
        print("  格式化数据:")
        print(result['formatted_data'][:100] + "..." if len(result['formatted_data']) > 100 else result['formatted_data'])
    else:
        print(f"  错误: {result['message']}")
    
    # 测试表格格式化
    print("\n测试表格格式化:")
    result = coordinator.format_output(test_data, "table")
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  格式类型: {result['format_type']}")
        print("  格式化数据:")
        print(result['formatted_data'])
    else:
        print(f"  错误: {result['message']}")
    
    # 测试列表格式化
    print("\n测试列表格式化:")
    result = coordinator.format_output(test_data, "list")
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  格式类型: {result['format_type']}")
        print("  格式化数据:")
        for item in result['formatted_data'][:3]:  # 只显示前3项
            print(f"    {item}")
    else:
        print(f"  错误: {result['message']}")
    
    print("\n格式化输出功能测试完成。")

def test_combine_data_function():
    """测试数据整合功能"""
    print("\n=== 测试数据整合功能 ===")
    
    # 创建数据输出协调器实例
    coordinator = DataOutputCoordinator()
    
    # 测试数据
    local_data = {"organism": "Bacillus subtilis", "source": "local"}
    external_data = {"pathway": "degradation pathway", "source": "KEGG"}
    metadata = {"query": "aldrin", "timestamp": "2023-01-01"}
    
    # 测试数据整合
    print("测试数据整合:")
    result = coordinator.combine_data(local_data, external_data, metadata=metadata)
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  数据源数量: {result['sources_count']}")
        print("  整合后的数据:")
        for key, value in list(result['combined_data'].items())[:3]:  # 只显示前3项
            print(f"    {key}: {value}")
    else:
        print(f"  错误: {result['message']}")
    
    print("\n数据整合功能测试完成。")

def test_generate_report_function():
    """测试生成报告功能"""
    print("\n=== 测试生成报告功能 ===")
    
    # 创建数据输出协调器实例
    coordinator = DataOutputCoordinator()
    
    # 测试数据
    title = "功能微生物组识别报告"
    sections = [
        {"title": "微生物识别结果", "content": "识别到2种功能微生物: Bacillus subtilis, Pseudomonas putida"},
        {"title": "基因数据分析", "content": "发现相关降解基因: degA, degB"},
        {"title": "互补性指数", "content": "计算得到互补性指数为0.85"}
    ]
    metadata = {"query": "aldrin", "processing_time": "2.5s"}
    
    # 测试生成报告
    print("测试生成报告:")
    result = coordinator.generate_report(title, sections, metadata)
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  报告标题: {result['report']['title']}")
        print(f"  章节数量: {result['statistics']['section_count']}")
        print(f"  总字符数: {result['statistics']['total_characters']}")
        print("  报告内容:")
        for section in result['report']['sections'][:2]:  # 只显示前2个章节
            print(f"    {section['title']}: {section['content'][:50]}...")
    else:
        print(f"  错误: {result['message']}")
    
    print("\n生成报告功能测试完成。")

def test_assess_completeness_function():
    """测试评估完整性功能"""
    print("\n=== 测试评估完整性功能 ===")
    
    # 创建数据输出协调器实例
    coordinator = DataOutputCoordinator()
    
    # 测试数据
    data_to_assess = {
        "microorganisms": ["Bacillus subtilis"],
        "genes": None,
        "complementarity_index": 0.85
    }
    required_fields = ["microorganisms", "genes", "complementarity_index"]
    
    # 测试评估完整性
    print("测试评估完整性:")
    result = coordinator.assess_completeness(data_to_assess, required_fields)
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  完整性评分: {result['completeness_score']:.2f}%")
        print(f"  存在字段: {result['present_fields']}")
        print(f"  缺失字段: {result['missing_fields']}")
        print("  建议:")
        for recommendation in result['recommendations']:
            print(f"    {recommendation}")
    else:
        print(f"  错误: {result['message']}")
    
    print("\n评估完整性功能测试完成。")

if __name__ == "__main__":
    print("开始测试数据输出协调器功能...")
    test_data_output_coordinator_creation()
    test_format_output_function()
    test_combine_data_function()
    test_generate_report_function()
    test_assess_completeness_function()
    print("\n=== 所有测试完成 ===")