#!/usr/bin/env python3
"""
全流程测试文件
逐步测试所有工具并解决可能面临的问题
"""

import os
import sys
from pathlib import Path
import traceback

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 创建必要的目录
data_dir = project_root / "data"
reactions_dir = data_dir / "reactions"
genomes_dir = data_dir / "genomes"
models_dir = project_root / "outputs" / "metabolic_models"
genome_features_dir = project_root / "outputs" / "genome_features"

# 确保目录存在
for directory in [data_dir, reactions_dir, genomes_dir, models_dir, genome_features_dir]:
    directory.mkdir(parents=True, exist_ok=True)

def test_envipath_enhanced_tool():
    """测试增强版EnviPath工具"""
    print("=" * 60)
    print("测试1: 增强版EnviPath工具")
    print("=" * 60)
    
    try:
        from core.tools.database.envipath_enhanced import EnviPathEnhancedTool
        
        # 初始化工具
        tool = EnviPathEnhancedTool()
        print("✓ 增强版EnviPath工具导入成功")
        
        # 测试化合物搜索
        print("正在搜索 'phthalic acid' 的代谢路径信息...")
        result = tool._run(compound_name="phthalic acid")
        
        print(f"工具运行结果: {result}")
        
        if result.get("status") == "success":
            print("✓ 增强版EnviPath工具测试成功")
            # 保存CSV格式的反应数据
            csv_result = tool._run(compound_name="phthalic acid", output_format="csv")
            if csv_result.get("status") == "success":
                print(f"✓ CSV格式反应数据生成成功: {csv_result.get('file_path')}")
                return csv_result.get('file_path')
            return None
        else:
            print("✗ 增强版EnviPath工具测试失败")
            return None
            
    except Exception as e:
        print(f"✗ 增强版EnviPath工具测试出错: {e}")
        traceback.print_exc()
        return None

def test_ncbi_tools():
    """测试NCBI工具"""
    print("\n" + "=" * 60)
    print("测试2: NCBI工具")
    print("=" * 60)
    
    try:
        # 测试NCBI基因组查询工具
        from core.tools.database.ncbi import NCBIGenomeQueryTool
        
        query_tool = NCBIGenomeQueryTool()
        print("✓ NCBI基因组查询工具导入成功")
        
        print("正在查询 'Pseudomonas putida' 的基因组信息...")
        query_result = query_tool._run(organism_name="Pseudomonas putida", max_results=1)
        print(f"查询结果:\n{query_result}")
        
        if "Assembly Accession" in str(query_result):
            print("✓ NCBI基因组查询工具测试成功")
        else:
            print("✗ NCBI基因组查询工具测试失败")
            return None, None
        
        # 测试NCBI基因组下载工具
        from core.tools.database.ncbi_genome_download_tool import NCBIGenomeDownloadTool
        
        download_tool = NCBIGenomeDownloadTool()
        print("✓ NCBI基因组下载工具导入成功")
        
        print("正在下载 'Pseudomonas putida' 的基因组文件...")
        download_result = download_tool._run(
            organism_name="Pseudomonas putida",
            download_path=str(genomes_dir),
            max_results=1
        )
        
        print(f"下载结果: {download_result}")
        
        if download_result.get("status") == "success":
            contigs_file = download_result["data"]["downloaded_files"]["contigs_file"]
            proteins_file = download_result["data"]["downloaded_files"]["proteins_file"]
            print(f"✓ NCBI基因组下载工具测试成功")
            print(f"  Contigs文件: {contigs_file}")
            print(f"  Proteins文件: {proteins_file}")
            return contigs_file, proteins_file
        else:
            print("✗ NCBI基因组下载工具测试失败")
            return None, None
            
    except Exception as e:
        print(f"✗ NCBI工具测试出错: {e}")
        traceback.print_exc()
        return None, None

def test_genome_processing_workflow():
    """测试基因组处理工作流工具"""
    print("\n" + "=" * 60)
    print("测试3: 基因组处理工作流工具")
    print("=" * 60)
    
    try:
        from core.tools.design.genome_processing_workflow import GenomeProcessingWorkflow
        
        workflow_tool = GenomeProcessingWorkflow()
        print("✓ 基因组处理工作流工具导入成功")
        
        print("正在运行基因组处理工作流...")
        workflow_result = workflow_tool._run(
            organism_names=["Pseudomonas putida"],
            download_path=str(genomes_dir),
            models_path=str(genome_features_dir)
        )
        
        print(f"工作流结果: {workflow_result}")
        
        if workflow_result.get("status") == "success":
            print("✓ 基因组处理工作流工具测试成功")
            return workflow_result
        else:
            print("✗ 基因组处理工作流工具测试失败")
            return None
            
    except Exception as e:
        print(f"✗ 基因组处理工作流工具测试出错: {e}")
        traceback.print_exc()
        return None

def test_carveme_tool():
    """测试CarveMe工具"""
    print("\n" + "=" * 60)
    print("测试4: CarveMe工具")
    print("=" * 60)
    
    try:
        from core.tools.design.carveme import CarvemeTool
        
        carveme_tool = CarvemeTool()
        print("✓ CarveMe工具导入成功")
        
        # 使用模拟蛋白质文件路径测试
        print("正在使用模拟数据测试CarveMe工具...")
        carveme_result = carveme_tool._run(
            input_path=str(genomes_dir),  # 使用下载的基因组文件目录
            output_path=str(models_dir),
            overwrite=True
        )
        
        print(f"CarveMe结果: {carveme_result}")
        
        if carveme_result.get("status") == "success":
            print("✓ CarveMe工具测试成功")
            return carveme_result
        else:
            print("✗ CarveMe工具测试失败")
            return None
            
    except Exception as e:
        print(f"✗ CarveMe工具测试出错: {e}")
        traceback.print_exc()
        return None

def test_reaction_addition_tool(reactions_csv_path):
    """测试反应添加工具"""
    print("\n" + "=" * 60)
    print("测试5: 反应添加工具")
    print("=" * 60)
    
    try:
        from core.tools.evaluation.reaction_addition import ReactionAdditionTool
        
        reaction_tool = ReactionAdditionTool()
        print("✓ 反应添加工具导入成功")
        
        # 首先检查是否有模型文件
        model_files = list(models_dir.glob("*.xml"))
        if not model_files:
            print("⚠ 警告: 未找到代谢模型文件，创建测试模型...")
            # 创建一个简单的测试模型
            test_model_path = models_dir / "test_model.xml"
            create_test_model(test_model_path)
            model_files = [test_model_path]
        
        if reactions_csv_path and os.path.exists(reactions_csv_path):
            print(f"正在为模型添加反应数据: {reactions_csv_path}")
            reaction_result = reaction_tool._run(
                models_path=str(models_dir),
                reactions_csv=reactions_csv_path
            )
        else:
            print("正在为模型添加 'phthalic acid' 的反应数据...")
            reaction_result = reaction_tool._run(
                models_path=str(models_dir),
                pollutant_name="phthalic acid"
            )
        
        print(f"反应添加结果: {reaction_result}")
        
        if reaction_result.get("status") == "success":
            print("✓ 反应添加工具测试成功")
            return reaction_result
        else:
            print("✗ 反应添加工具测试失败")
            return None
            
    except Exception as e:
        print(f"✗ 反应添加工具测试出错: {e}")
        traceback.print_exc()
        return None

def create_test_model(model_path):
    """创建测试模型文件"""
    sbml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" xmlns:fbc="http://www.sbml.org/sbml/level3/version1/fbc/version2" level="3" version="1" fbc:required="false">
  <model id="test_model" name="Test Model" fbc:strict="true">
    <listOfCompartments>
      <compartment id="c" name="cytosol" constant="true"/>
      <compartment id="e" name="extracellular" constant="true"/>
    </listOfCompartments>
    <listOfSpecies>
      <species id="M_glc__D_e" name="D-Glucose" compartment="e" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>
      <species id="M_ac_e" name="Acetate" compartment="e" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>
      <species id="M_glc__D_c" name="D-Glucose" compartment="c" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>
      <species id="M_ac_c" name="Acetate" compartment="c" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>
    </listOfSpecies>
    <listOfParameters>
      <parameter id="cobra_default_lb" value="-1000" constant="true"/>
      <parameter id="cobra_default_ub" value="1000" constant="true"/>
      <parameter id="cobra_0_bound" value="0" constant="true"/>
    </listOfParameters>
    <listOfReactions>
      <reaction id="R_EX_glc__D_e" name="D-Glucose exchange" reversible="true" fast="false" fbc:lowerFluxBound="cobra_default_lb" fbc:upperFluxBound="cobra_default_ub">
        <listOfReactants>
          <speciesReference species="M_glc__D_e" stoichiometry="1" constant="true"/>
        </listOfReactants>
      </reaction>
      <reaction id="R_EX_ac_e" name="Acetate exchange" reversible="true" fast="false" fbc:lowerFluxBound="cobra_default_lb" fbc:upperFluxBound="cobra_default_ub">
        <listOfProducts>
          <speciesReference species="M_ac_e" stoichiometry="1" constant="true"/>
        </listOfProducts>
      </reaction>
    </listOfReactions>
    <fbc:listOfObjectives fbc:activeObjective="obj">
      <fbc:objective fbc:id="obj" fbc:type="maximize">
        <fbc:listOfFluxObjectives>
          <fbc:fluxObjective fbc:reaction="R_EX_glc__D_e" fbc:coefficient="1"/>
        </fbc:listOfFluxObjectives>
      </fbc:objective>
    </fbc:listOfObjectives>
  </model>
</sbml>'''
    
    with open(model_path, 'w') as f:
        f.write(sbml_content)
    print(f"✓ 创建测试模型文件: {model_path}")

def test_kegg_tool():
    """测试KEGG工具"""
    print("\n" + "=" * 60)
    print("测试6: KEGG工具")
    print("=" * 60)
    
    try:
        from core.tools.database.kegg import KeggTool
        
        kegg_tool = KeggTool()
        print("✓ KEGG工具导入成功")
        
        # 测试化合物智能查询
        print("正在智能查询 'phthalic acid' 的代谢信息...")
        kegg_result = kegg_tool._run(compound_name="phthalic acid")
        
        print(f"KEGG查询结果: {kegg_result}")
        
        if kegg_result.get("status") == "success":
            print("✓ KEGG工具测试成功")
            return kegg_result
        else:
            print("✗ KEGG工具测试失败")
            return None
            
    except Exception as e:
        print(f"✗ KEGG工具测试出错: {e}")
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("开始全流程测试")
    print("=" * 60)
    
    # 存储各步骤的结果
    results = {}
    
    # 1. 测试增强版EnviPath工具
    results['envipath_csv'] = test_envipath_enhanced_tool()
    
    # 2. 测试NCBI工具
    contigs_file, proteins_file = test_ncbi_tools()
    results['contigs_file'] = contigs_file
    results['proteins_file'] = proteins_file
    
    # 3. 测试基因组处理工作流工具
    results['genome_workflow'] = test_genome_processing_workflow()
    
    # 4. 测试CarveMe工具
    results['carveme'] = test_carveme_tool()
    
    # 5. 测试反应添加工具
    results['reaction_addition'] = test_reaction_addition_tool(results['envipath_csv'])
    
    # 6. 测试KEGG工具
    results['kegg'] = test_kegg_tool()
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("全流程测试总结")
    print("=" * 60)
    
    success_count = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        if result is not None:
            if isinstance(result, bool) and result:
                print(f"✓ {test_name}: 成功")
                success_count += 1
            elif isinstance(result, dict) and result.get("status") == "success":
                print(f"✓ {test_name}: 成功")
                success_count += 1
            elif result:  # 非空值
                print(f"✓ {test_name}: 成功")
                success_count += 1
            else:
                print(f"✗ {test_name}: 失败")
        else:
            print(f"✗ {test_name}: 失败")
    
    print(f"\n测试完成: {success_count}/{total_tests} 个测试成功")
    
    if success_count == total_tests:
        print("🎉 所有测试都成功完成！")
        return True
    else:
        print("⚠ 部分测试失败，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)