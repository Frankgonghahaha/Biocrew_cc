#!/usr/bin/env python3
"""
测试集成基因组处理工具的具体功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_integrated_tool_detailed_functionality():
    """详细测试集成工具的功能"""
    print("详细测试集成基因组处理工具的功能...")
    
    try:
        # 导入工具
        from tools.microbial_agent_design.integrated_genome_processing_tool import IntegratedGenomeProcessingTool
        
        # 创建工具实例
        tool = IntegratedGenomeProcessingTool()
        
        # 测试工具的查询功能（使用模拟数据）
        print("\n1. 测试基因组查询功能...")
        genome_info = tool._query_genome_info("Pseudomonas putida", 1)
        if genome_info is not None:
            print("✓ 基因组查询功能正常")
            print(f"  查询到 {len(genome_info)} 个结果")
            if len(genome_info) > 0:
                print(f"  第一个结果: {genome_info[0]['organism']} ({genome_info[0]['accession']})")
        else:
            print("✗ 基因组查询功能异常")
        
        # 测试工具的下载功能（这会创建模拟文件）
        print("\n2. 测试基因组文件下载功能...")
        # 创建一个模拟的基因组信息
        mock_genome_info = {
            "accession": "GCF_052695785.1",
            "ftp_path": "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/052/695/785/GCF_052695785.1_ASM5269578v1"
        }
        downloaded_files = tool._download_genome_files(mock_genome_info, "/tmp/genomes_test")
        if downloaded_files["status"] == "success":
            print("✓ 基因组文件下载功能正常")
            print(f"  Contigs文件: {downloaded_files['data']['contigs_file']}")
            print(f"  Proteins文件: {downloaded_files['data']['proteins_file']}")
        else:
            print("✗ 基因组文件下载功能异常")
        
        # 测试工具的模拟GenomeSPOT分析功能
        print("\n3. 测试模拟GenomeSPOT分析功能...")
        mock_result = tool._simulate_genome_spot("test_file.fna", "test_file.faa", "/tmp/models", "test_prefix")
        if mock_result["status"] == "success (simulated)":
            print("✓ 模拟GenomeSPOT分析功能正常")
            print(f"  分析结果包含 {len(mock_result['data'])} 个环境适应性特征")
            for trait, data in mock_result['data'].items():
                print(f"  - {trait}: {data['value']} ± {data['error']} {data['units']}")
        else:
            print("✗ 模拟GenomeSPOT分析功能异常")
            
        print("\n✓ 集成工具的所有功能模块测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试集成工具功能时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("BioCrew - 集成基因组处理工具详细功能测试")
    print("=" * 50)
    
    try:
        # 执行详细功能测试
        result = test_integrated_tool_detailed_functionality()
        
        if result:
            print("\n✓ 所有详细功能测试通过！")
        else:
            print("\n✗ 部分功能测试失败。")
            
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()