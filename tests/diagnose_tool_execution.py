#!/usr/bin/env python3
"""
详细诊断脚本 - 检查为什么工具使用模拟执行
"""

import sys
import os
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_genome_spot():
    """诊断GenomeSPOTTool问题"""
    print("=== 诊断GenomeSPOTTool ===")
    
    try:
        from tools.microbial_agent_design.genome_spot_tool.genome_spot_tool import GenomeSPOTTool
        tool = GenomeSPOTTool()
        print("✓ GenomeSPOTTool加载成功")
        
        # 检查路径
        import tools.microbial_agent_design.genome_spot_tool.genome_spot_tool as genome_spot_module
        current_dir = os.path.dirname(os.path.abspath(genome_spot_module.__file__))
        genome_spot_path = os.path.join(current_dir, '..', '..', 'external_tools', 'genome_spot')
        genome_spot_main_path = os.path.join(genome_spot_path, 'genome_spot', 'genome_spot.py')
        
        print(f"GenomeSPOT路径: {genome_spot_path}")
        print(f"GenomeSPOT主文件: {genome_spot_main_path}")
        print(f"GenomeSPOT实际路径: {os.path.realpath(genome_spot_path)}")
        
        if os.path.exists(genome_spot_path):
            print("✓ GenomeSPOT目录存在")
        else:
            print("✗ GenomeSPOT目录不存在")
            print("当前目录内容:")
            try:
                parent_dir = os.path.dirname(current_dir)
                print(f"父目录 {parent_dir}: {os.listdir(parent_dir)}")
                grandparent_dir = os.path.dirname(parent_dir)
                print(f"祖父目录 {grandparent_dir}: {os.listdir(grandparent_dir)}")
            except Exception as e:
                print(f"列出目录内容失败: {e}")
            return
            
        if os.path.exists(genome_spot_main_path):
            print("✓ GenomeSPOT主文件存在")
        else:
            print("✗ GenomeSPOT主文件不存在")
            return
            
        # 尝试导入
        try:
            sys.path.append(genome_spot_path)
            from genome_spot.genome_spot import run_genome_spot
            print("✓ GenomeSPOT模块可导入")
        except ImportError as e:
            print(f"✗ GenomeSPOT模块导入失败: {e}")
            return
            
        # 尝试实际调用（使用模拟参数）
        print("尝试调用GenomeSPOT...")
        result = tool._run(
            fna_path="/nonexistent/fna/file.fna",
            faa_path="/nonexistent/faa/file.faa", 
            models_path="/nonexistent/models"
        )
        print(f"调用结果: {result['status']}")
        if "simulated" in result['status']:
            print("⚠️  使用模拟执行")
        else:
            print("✅ 真实执行")
            
    except Exception as e:
        print(f"✗ GenomeSPOTTool诊断失败: {e}")
        import traceback
        traceback.print_exc()

def diagnose_dlkcat():
    """诊断DLkcatTool问题"""
    print("\n=== 诊断DLkcatTool ===")
    
    try:
        from tools.microbial_agent_design.dlkcat_tool.dlkcat_tool import DLkcatTool
        tool = DLkcatTool()
        print("✓ DLkcatTool加载成功")
        
        # 检查脚本路径
        import tools.microbial_agent_design.dlkcat_tool.dlkcat_tool as dlkcat_module
        current_dir = os.path.dirname(os.path.abspath(dlkcat_module.__file__))
        dlkcat_script = os.path.join(current_dir, '..', '..', 'external_tools', 'dlkcat', 'run_DLkcat.py')
        
        print(f"DLkcat脚本路径: {dlkcat_script}")
        
        if os.path.exists(dlkcat_script):
            print("✓ DLkcat脚本存在")
        else:
            print("✗ DLkcat脚本不存在")
            return
            
        # 尝试执行脚本
        print("尝试执行DLkcat脚本...")
        try:
            cmd = [sys.executable, dlkcat_script, "--help"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            print(f"执行结果: returncode={result.returncode}")
            if result.returncode == 0:
                print("✓ DLkcat脚本可执行")
            else:
                print(f"✗ DLkcat脚本执行失败: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("✗ DLkcat脚本执行超时")
        except Exception as e:
            print(f"✗ DLkcat脚本执行异常: {e}")
            
    except Exception as e:
        print(f"✗ DLkcatTool诊断失败: {e}")
        import traceback
        traceback.print_exc()

def diagnose_carveme():
    """诊断CarvemeTool问题"""
    print("\n=== 诊断CarvemeTool ===")
    
    try:
        from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool
        tool = CarvemeTool()
        print("✓ CarvemeTool加载成功")
        
        # 检查脚本路径
        import tools.microbial_agent_design.carveme_tool.carveme_tool as carveme_module
        current_dir = os.path.dirname(os.path.abspath(carveme_module.__file__))
        carveme_script = os.path.join(current_dir, '..', '..', 'external_tools', 'carveme', 'build_GSMM_from_aa.py')
        
        print(f"Carveme脚本路径: {carveme_script}")
        
        if os.path.exists(carveme_script):
            print("✓ Carveme脚本存在")
        else:
            print("✗ Carveme脚本不存在")
            return
            
        # 尝试执行脚本
        print("尝试执行Carveme脚本...")
        try:
            cmd = [sys.executable, carveme_script, "--help"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            print(f"执行结果: returncode={result.returncode}")
            if result.returncode == 0:
                print("✓ Carveme脚本可执行")
            else:
                print(f"✗ Carveme脚本执行失败: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("✗ Carveme脚本执行超时")
        except Exception as e:
            print(f"✗ Carveme脚本执行异常: {e}")
            
    except Exception as e:
        print(f"✗ CarvemeTool诊断失败: {e}")
        import traceback
        traceback.print_exc()

def diagnose_phylomint():
    """诊断PhylomintTool问题"""
    print("\n=== 诊断PhylomintTool ===")
    
    try:
        from tools.microbial_agent_design.phylomint_tool.phylomint_tool import PhylomintTool
        tool = PhylomintTool()
        print("✓ PhylomintTool加载成功")
        
        # 检查脚本路径
        import tools.microbial_agent_design.phylomint_tool.phylomint_tool as phylomint_module
        current_dir = os.path.dirname(os.path.abspath(phylomint_module.__file__))
        phylomint_script = os.path.join(current_dir, '..', '..', 'external_tools', 'phylomint', 'run_phylomint.py')
        
        print(f"Phylomint脚本路径: {phylomint_script}")
        
        if os.path.exists(phylomint_script):
            print("✓ Phylomint脚本存在")
        else:
            print("✗ Phylomint脚本不存在")
            return
            
        # 尝试执行脚本
        print("尝试执行Phylomint脚本...")
        try:
            cmd = [sys.executable, phylomint_script, "--help"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            print(f"执行结果: returncode={result.returncode}")
            if result.returncode == 0:
                print("✓ Phylomint脚本可执行")
            else:
                print(f"✗ Phylomint脚本执行失败: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("✗ Phylomint脚本执行超时")
        except Exception as e:
            print(f"✗ Phylomint脚本执行异常: {e}")
            
    except Exception as e:
        print(f"✗ PhylomintTool诊断失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("BioCrew - 工具执行问题诊断")
    print("=" * 50)
    
    try:
        diagnose_genome_spot()
        diagnose_dlkcat()
        diagnose_carveme()
        diagnose_phylomint()
        print("\n诊断完成!")
    except Exception as e:
        print(f"\n诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()