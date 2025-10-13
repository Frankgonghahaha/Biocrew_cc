#!/usr/bin/env python3
"""
测试GenomeSPOT工具的集成效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from genome_spot_tool import GenomeSPOTTool

def test_genome_spot_tool():
    """测试GenomeSPOT工具"""
    # 创建工具实例
    tool = GenomeSPOTTool()
    
    # 测试参数
    test_params = {
        "fna_path": "/home/axlhuang/Agent-tool/DesignAgent/Tool_GenomeSPOT/Code/tests/test_data/GCA_000172155.1_ASM17215v1_genomic.fna.gz",
        "faa_path": "/home/axlhuang/Agent-tool/DesignAgent/Tool_GenomeSPOT/Code/tests/test_data/GCA_000172155.1_ASM17215v1_protein.faa.gz",
        "models_path": "/home/axlhuang/Agent-tool/DesignAgent/Tool_GenomeSPOT/Code/models",
        "output_prefix": "/tmp/genome_spot_test"
    }
    
    # 检查测试文件是否存在
    if not os.path.exists(test_params["fna_path"]):
        print(f"测试文件不存在: {test_params['fna_path']}")
        return
    
    if not os.path.exists(test_params["faa_path"]):
        print(f"测试文件不存在: {test_params['faa_path']}")
        return
    
    if not os.path.exists(test_params["models_path"]):
        print(f"模型目录不存在: {test_params['models_path']}")
        return
    
    # 运行工具
    print("运行GenomeSPOT工具...")
    result = tool._run(**test_params)
    
    # 输出结果
    print("测试结果:")
    print(f"状态: {result.get('status')}")
    if result.get('status') == 'success':
        data = result.get('data', {})
        print("预测结果:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print(f"错误信息: {result.get('message')}")

if __name__ == "__main__":
    test_genome_spot_tool()