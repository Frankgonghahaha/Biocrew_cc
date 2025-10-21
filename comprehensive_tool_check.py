#!/usr/bin/env python3
"""
全面的工具状态检测脚本
检测每个工具的当前状态并识别问题
"""

import os
import sys
from pathlib import Path
import subprocess

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的工具
from core.tools.database.envipath import EnviPathTool
from core.tools.database.ncbi import NCBIGenomeQueryTool
from core.tools.design.carveme import CarvemeTool

# 导入新增的工具
from core.tools.database.envipath_enhanced import EnviPathEnhancedTool
from core.tools.database.ncbi_genome_download_tool import NCBIGenomeDownloadTool
from core.tools.design.genome_processing_workflow import GenomeProcessingWorkflow
from core.tools.evaluation.reaction_addition import ReactionAdditionTool

def check_envipath_tool():
    """检测EnviPath工具状态"""
    print("=== 检测EnviPath工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = EnviPathTool()
        print("✓ EnviPath工具导入成功")
        
        # 尝试运行工具
        result = tool._run(
            pollutant_name="phthalic acid",
            output_dir=str(project_root / "data" / "reactions")
        )
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ EnviPath工具能正常运行")
            return True, "工具正常运行"
        else:
            error_msg = result.get("message", "未知错误")
            print(f"✗ EnviPath工具运行失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"✗ EnviPath工具发生异常: {e}")
        return False, str(e)

def check_envipath_enhanced_tool():
    """检测增强版EnviPath工具状态"""
    print("\n=== 检测增强版EnviPath工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = EnviPathEnhancedTool()
        print("✓ 增强版EnviPath工具导入成功")
        
        # 尝试运行工具
        result = tool._run(
            compound_name="phthalic acid"
        )
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ 增强版EnviPath工具能正常运行")
            return True, "工具正常运行"
        else:
            error_msg = result.get("message", "未知错误")
            print(f"✗ 增强版EnviPath工具运行失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"✗ 增强版EnviPath工具发生异常: {e}")
        return False, str(e)

def check_ncbi_tool():
    """检测NCBI工具状态"""
    print("\n=== 检测NCBI工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = NCBIGenomeQueryTool()
        print("✓ NCBI工具导入成功")
        
        # 尝试运行工具
        result = tool._run(
            organism_name="Pseudomonas putida",
            max_results=1
        )
        
        print(f"工具运行结果: {result}")
        
        if "Assembly Accession" in result:
            print("✓ NCBI工具能正常获取真实数据")
            return True, "工具正常运行"
        else:
            print("✗ NCBI工具无法获取有效数据")
            return False, "无法获取有效数据"
            
    except Exception as e:
        print(f"✗ NCBI工具发生异常: {e}")
        return False, str(e)

def check_ncbi_download_tool():
    """检测NCBI基因组下载工具状态"""
    print("\n=== 检测NCBI基因组下载工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = NCBIGenomeDownloadTool()
        print("✓ NCBI基因组下载工具导入成功")
        
        # 尝试运行工具（使用模拟数据）
        result = tool._run(
            organism_name="Pseudomonas putida",
            download_path=str(project_root / "data" / "genomes"),
            max_results=1
        )
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ NCBI基因组下载工具能正常运行")
            return True, "工具正常运行"
        else:
            error_msg = result.get("message", "未知错误")
            print(f"✗ NCBI基因组下载工具运行失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"✗ NCBI基因组下载工具发生异常: {e}")
        return False, str(e)

def check_carveme_tool():
    """检测CarveMe工具状态"""
    print("\n=== 检测CarveMe工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = CarvemeTool()
        print("✓ CarveMe工具导入成功")
        
        # 检查项目内部脚本是否存在
        script_dir = os.path.dirname(os.path.abspath(__file__))
        carveme_script = os.path.join(script_dir, '..', 'external', 'build_GSMM_from_aa.py')
        
        if os.path.exists(carveme_script):
            print("✓ CarveMe构建脚本存在")
        else:
            print("⚠ CarveMe构建脚本不存在，将使用模拟执行")
        
        # 尝试运行工具（使用一个不存在的输入路径来测试）
        result = tool._run(
            input_path="/nonexistent/path",
            output_path=str(project_root / "outputs" / "metabolic_models")
        )
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ CarveMe工具能正常运行")
            return True, "工具正常运行"
        else:
            error_msg = result.get("message", "未知错误")
            print(f"✗ CarveMe工具运行失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"✗ CarveMe工具发生异常: {e}")
        return False, str(e)

def check_genome_processing_workflow_tool():
    """检测基因组处理工作流工具状态"""
    print("\n=== 检测基因组处理工作流工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = GenomeProcessingWorkflow()
        print("✓ 基因组处理工作流工具导入成功")
        
        # 尝试运行工具（使用模拟数据）
        result = tool._run(
            organism_names=["Pseudomonas putida"],
            download_path=str(project_root / "data" / "genomes"),
            models_path=str(project_root / "outputs" / "genome_features")
        )
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ 基因组处理工作流工具能正常运行")
            return True, "工具正常运行"
        else:
            error_msg = result.get("message", "未知错误")
            print(f"✗ 基因组处理工作流工具运行失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"✗ 基因组处理工作流工具发生异常: {e}")
        return False, str(e)

def check_reaction_addition_tool():
    """检测反应添加工具状态"""
    print("\n=== 检测反应添加工具状态 ===")
    
    try:
        # 检查工具是否能正确导入
        tool = ReactionAdditionTool()
        print("✓ 反应添加工具导入成功")
        
        # 尝试运行工具（使用模拟数据）
        result = tool._run(
            models_path=str(project_root / "outputs" / "metabolic_models"),
            pollutant_name="phthalic acid"
        )
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ 反应添加工具能正常运行")
            return True, "工具正常运行"
        else:
            error_msg = result.get("message", "未知错误")
            print(f"✗ 反应添加工具运行失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"✗ 反应添加工具发生异常: {e}")
        return False, str(e)

def check_dependencies():
    """检查依赖项"""
    print("\n=== 检查依赖项 ===")
    
    # 检查COBRApy
    try:
        import cobra
        print(f"✓ COBRApy版本: {cobra.__version__}")
        cobrapy_available = True
    except ImportError:
        print("✗ COBRApy未安装")
        cobrapy_available = False
    
    # 检查CarveMe
    try:
        result = subprocess.run(["carve", "--help"], capture_output=True, timeout=10)
        print("✓ CarveMe命令行工具可用")
        carveme_available = True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("✗ CarveMe命令行工具不可用")
        carveme_available = False
    
    # 检查enviPath-python库
    try:
        import enviPath_python
        print("✓ enviPath-python库可用")
        envipath_lib_available = True
    except ImportError:
        print("✗ enviPath-python库不可用")
        envipath_lib_available = False
    
    return {
        "cobrapy": cobrapy_available,
        "carveme": carveme_available,
        "envipath_lib": envipath_lib_available
    }

def main():
    """主函数"""
    print("开始全面的工具状态检测")
    
    # 创建必要的目录
    (project_root / "data" / "reactions").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "genomes").mkdir(parents=True, exist_ok=True)
    (project_root / "outputs" / "metabolic_models").mkdir(parents=True, exist_ok=True)
    (project_root / "outputs" / "genome_features").mkdir(parents=True, exist_ok=True)
    
    # 检查依赖项
    dependencies = check_dependencies()
    
    # 检查各个工具
    envipath_status, envipath_msg = check_envipath_tool()
    envipath_enhanced_status, envipath_enhanced_msg = check_envipath_enhanced_tool()
    ncbi_status, ncbi_msg = check_ncbi_tool()
    ncbi_download_status, ncbi_download_msg = check_ncbi_download_tool()
    carveme_status, carveme_msg = check_carveme_tool()
    genome_processing_status, genome_processing_msg = check_genome_processing_workflow_tool()
    reaction_addition_status, reaction_addition_msg = check_reaction_addition_tool()
    
    # 总结结果
    print("\n" + "="*50)
    print("工具状态检测总结")
    print("="*50)
    print(f"EnviPath工具: {'✓ 正常' if envipath_status else '✗ 异常'} - {envipath_msg}")
    print(f"增强版EnviPath工具: {'✓ 正常' if envipath_enhanced_status else '✗ 异常'} - {envipath_enhanced_msg}")
    print(f"NCBI工具: {'✓ 正常' if ncbi_status else '✗ 异常'} - {ncbi_msg}")
    print(f"NCBI基因组下载工具: {'✓ 正常' if ncbi_download_status else '✗ 异常'} - {ncbi_download_msg}")
    print(f"CarveMe工具: {'✓ 正常' if carveme_status else '✗ 异常'} - {carveme_msg}")
    print(f"基因组处理工作流工具: {'✓ 正常' if genome_processing_status else '✗ 异常'} - {genome_processing_msg}")
    print(f"反应添加工具: {'✓ 正常' if reaction_addition_status else '✗ 异常'} - {reaction_addition_msg}")
    print(f"COBRApy依赖: {'✓ 可用' if dependencies['cobrapy'] else '✗ 不可用'}")
    print(f"CarveMe依赖: {'✓ 可用' if dependencies['carveme'] else '✗ 不可用'}")
    print(f"enviPath-python库: {'✓ 可用' if dependencies['envipath_lib'] else '✗ 不可用'}")
    
    # 识别需要解决的问题
    issues = []
    if not envipath_status:
        issues.append("EnviPath工具无法获取真实数据，需要配置API密钥")
    if not envipath_enhanced_status:
        issues.append("增强版EnviPath工具存在问题")
    if not ncbi_status:
        issues.append("NCBI工具存在问题")
    if not ncbi_download_status:
        issues.append("NCBI基因组下载工具存在问题")
    if not carveme_status:
        issues.append("CarveMe工具无法正常执行")
    if not genome_processing_status:
        issues.append("基因组处理工作流工具存在问题")
    if not reaction_addition_status:
        issues.append("反应添加工具存在问题")
    if not dependencies['cobrapy']:
        issues.append("缺少COBRApy依赖")
    if not dependencies['carveme']:
        issues.append("缺少CarveMe命令行工具")
    if not dependencies['envipath_lib']:
        issues.append("缺少enviPath-python库")
    
    if issues:
        print(f"\n发现 {len(issues)} 个问题需要解决:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        return False
    else:
        print("\n🎉 所有工具都正常工作！")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)