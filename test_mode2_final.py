#!/usr/bin/env python3
"""
最终测试脚本 - 验证模式2功能
测试工具使用功能，针对Aldrin污染物识别需求
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from tools.data_output_coordinator import DataOutputCoordinator

def test_mode2_final():
    """最终测试模式2功能"""
    print("=== 最终测试模式2功能 - Aldrin污染物识别 ===")
    
    # 创建数据输出协调器
    coordinator = DataOutputCoordinator()
    
    # 模拟用户需求
    user_requirement = "帮我识别出一下能降解Aldrin污染物的功能微生物"
    print(f"用户需求: {user_requirement}")
    
    # 使用智能数据查询工具获取数据（这里直接使用之前测试的结果）
    # 在实际应用中，这会通过Agent调用工具来获取
    sample_data = {
        "pollutant": "Aldrin",
        "microorganisms": [
            {
                "name": "Anabaena cylindrica CCAIU 629",
                "type": "Eukaryota",
                "metabolism": "Bioaccumulation",
                "intermediates": "Epoxide; Dieldrin",
                "final_product": "Dieldrin",
                "habitat": "Freshwater enriched by nutrients from agricultural runoff",
                "reference": "Schauberger and Wildman. 1977"
            },
            {
                "name": "Anacystis nidulans",
                "type": "Eukaryota",
                "metabolism": "Bioaccumulation",
                "intermediates": "Epoxide; Dieldrin",
                "final_product": "Dieldrin",
                "habitat": "Freshwater enriched by nutrients from agricultural runoff",
                "reference": "Schauberger and Wildman. 1977"
            },
            {
                "name": "Nostoc muscorum",
                "type": "Eukaryota",
                "metabolism": "Bioaccumulation",
                "intermediates": "Epoxide; Dieldrin",
                "final_product": "Dieldrin",
                "habitat": "Freshwater enriched by nutrients from agricultural runoff",
                "reference": "Schauberger and Wildman. 1977"
            }
        ],
        "data_integrity_score": 85,
        "recommendations": [
            "本地微生物数据完整，可直接使用",
            "建议结合KEGG数据库查询相关代谢途径信息",
            "可考虑查询相关基因数据以增强分析深度"
        ]
    }
    
    # 使用数据输出协调器格式化结果
    print("\n1. 生成结构化报告:")
    report_result = coordinator._run("generate_report", 
                                   title="Aldrin降解功能微生物识别报告",
                                   data=sample_data)
    print(f"   报告生成结果: {report_result['status']}")
    
    # 使用数据输出协调器格式化输出
    print("\n2. 格式化输出结果:")
    formatted_result = coordinator._run("format_output",
                                      data=sample_data,
                                      format_type="json")
    print(f"   格式化结果: {formatted_result['status']}")
    
    # 显示简要结果
    print("\n=== 识别结果摘要 ===")
    print(f"目标污染物: {sample_data['pollutant']}")
    print(f"识别到的功能微生物数量: {len(sample_data['microorganisms'])}")
    print(f"数据完整性评分: {sample_data['data_integrity_score']}/100")
    
    print("\n功能微生物列表:")
    for i, microorganism in enumerate(sample_data['microorganisms'], 1):
        print(f"  {i}. {microorganism['name']}")
        print(f"     类型: {microorganism['type']}")
        print(f"     代谢方式: {microorganism['metabolism']}")
        print(f"     中间产物: {microorganism['intermediates']}")
        print(f"     最终产物: {microorganism['final_product']}")
    
    print("\n建议:")
    for recommendation in sample_data['recommendations']:
        print(f"  - {recommendation}")

if __name__ == "__main__":
    test_mode2_final()