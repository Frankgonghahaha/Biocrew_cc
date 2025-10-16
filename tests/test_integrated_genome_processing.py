#!/usr/bin/env python3
"""
测试集成基因组处理工具
验证基因组查询、下载和GenomeSPOT分析的完整工作流
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.microbial_agent_design.integrated_genome_processing_tool import IntegratedGenomeProcessingTool

def test_integrated_genome_processing():
    """测试集成基因组处理工具"""
    print("测试集成基因组处理工具...")
    
    # 创建工具实例
    tool = IntegratedGenomeProcessingTool()
    
    # 测试参数
    organism_names = ["Pseudomonas putida", "Rhodococcus jostii"]
    download_path = "/tmp/genomes_test"
    models_path = "/tmp/genome_spot_models"  # 在实际使用中应该指向真实的模型目录
    output_prefix = "test_output"
    
    # 运行工具
    result = tool._run(
        organism_names=organism_names,
        download_path=download_path,
        models_path=models_path,
        output_prefix=output_prefix,
        max_results=1
    )
    
    # 输出结果
    print("测试结果:")
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        for organism, data in result['data'].items():
            print(f"\n{organism}:")
            print(f"  状态: {data['status']}")
            if data['status'] == 'success' or 'success' in data['status']:
                for trait, value in data['data'].items():
                    print(f"  {trait}: {value['value']} ± {value['error']} {value['units']}")
            else:
                print(f"  错误信息: {data.get('message', '未知错误')}")
    else:
        print(f"错误信息: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    test_integrated_genome_processing()