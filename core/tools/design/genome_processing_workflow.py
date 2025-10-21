#!/usr/bin/env python3
"""
基因组处理工作流工具
集成基因组下载、GenomeSPOT分析等功能
"""

from crewai.tools import BaseTool
from typing import Type, List, Optional, Dict, Any
from pydantic import BaseModel, Field
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入NCBI基因组下载工具
from core.tools.database.ncbi_genome_download_tool import NCBIGenomeDownloadTool

class GenomeProcessingWorkflowSchema(BaseModel):
    """基因组处理工作流工具的输入参数"""
    organism_names: List[str] = Field(
        description="微生物名称列表，例如 ['Pseudomonas putida', 'Rhodococcus jostii']"
    )
    download_path: str = Field(
        default="/tmp/genomes",
        description="基因组文件下载目录"
    )
    models_path: str = Field(
        default="/tmp/models",
        description="GenomeSPOT模型目录路径"
    )
    output_prefix: Optional[str] = Field(
        default=None,
        description="输出文件前缀"
    )

class GenomeProcessingWorkflow(BaseTool):
    name: str = "基因组处理工作流工具"
    description: str = "集成基因组下载和GenomeSPOT分析的完整工作流工具"
    args_schema: Type[BaseModel] = GenomeProcessingWorkflowSchema

    def _run(self, organism_names: List[str], download_path: str = "/tmp/genomes", 
             models_path: str = "/tmp/models", output_prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        运行完整的基因组处理工作流
        
        Args:
            organism_names: 微生物名称列表
            download_path: 基因组文件下载目录
            models_path: GenomeSPOT模型目录路径
            output_prefix: 输出文件前缀
            
        Returns:
            dict: 处理结果
        """
        print(f"[GenomeProcessingWorkflow] 开始处理基因组数据，基因组数量: {len(organism_names)}")
        
        try:
            results = {}
            
            for organism_name in organism_names:
                print(f"[GenomeProcessingWorkflow] 处理 {organism_name}")
                
                # 步骤1: 下载基因组文件
                print(f"[GenomeProcessingWorkflow] 下载 {organism_name} 的基因组文件")
                ncbi_tool = NCBIGenomeDownloadTool()
                download_result = ncbi_tool._run(
                    organism_name=organism_name,
                    download_path=download_path,
                    max_results=1
                )
                
                if download_result["status"] != "success":
                    results[organism_name] = {
                        "status": "error",
                        "message": f"下载基因组文件失败: {download_result.get('message', '未知错误')}"
                    }
                    continue
                
                # 获取下载的文件路径
                contigs_file = download_result["data"]["downloaded_files"]["contigs_file"]
                proteins_file = download_result["data"]["downloaded_files"]["proteins_file"]
                
                print(f"[GenomeProcessingWorkflow] 成功下载基因组文件:")
                print(f"  Contigs文件: {contigs_file}")
                print(f"  Proteins文件: {proteins_file}")
                
                # 步骤2: 运行GenomeSPOT分析（这里使用模拟结果）
                genome_spot_result = self._run_genome_spot_analysis(
                    contigs_file, proteins_file, models_path, 
                    f"{output_prefix}_{organism_name}" if output_prefix else organism_name
                )
                
                results[organism_name] = genome_spot_result
            
            return {
                "status": "success",
                "data": results
            }
            
        except Exception as e:
            print(f"[GenomeProcessingWorkflow] 处理过程中出错: {str(e)}")
            return {"status": "error", "message": f"处理过程中出错: {str(e)}"}
    
    def _run_genome_spot_analysis(self, fna_path: str, faa_path: str, models_path: str, 
                                 output_prefix: str) -> Dict[str, Any]:
        """
        运行GenomeSPOT分析
        """
        # 实际实现应该调用GenomeSPOTTool
        # 这里返回模拟结果
        organism_name = os.path.basename(fna_path).split('_')[0]
        
        if "pseudomonas" in organism_name.lower():
            result = {
                "temperature_optimum": {
                    "value": 30.0,
                    "error": 2.5,
                    "units": "°C"
                },
                "ph_optimum": {
                    "value": 7.0,
                    "error": 0.3,
                    "units": ""
                },
                "salinity_optimum": {
                    "value": 1.0,
                    "error": 0.2,
                    "units": "% NaCl"
                },
                "oxygen_tolerance": {
                    "value": "tolerant",
                    "units": ""
                }
            }
        elif "rhodococcus" in organism_name.lower():
            result = {
                "temperature_optimum": {
                    "value": 28.0,
                    "error": 3.0,
                    "units": "°C"
                },
                "ph_optimum": {
                    "value": 7.2,
                    "error": 0.4,
                    "units": ""
                },
                "salinity_optimum": {
                    "value": 3.0,
                    "error": 0.8,
                    "units": "% NaCl"
                },
                "oxygen_tolerance": {
                    "value": "facultative",
                    "units": ""
                }
            }
        else:
            result = {
                "temperature_optimum": {
                    "value": 25.0,
                    "error": 5.0,
                    "units": "°C"
                },
                "ph_optimum": {
                    "value": 7.0,
                    "error": 1.0,
                    "units": ""
                },
                "salinity_optimum": {
                    "value": 0.5,
                    "error": 1.0,
                    "units": "% NaCl"
                },
                "oxygen_tolerance": {
                    "value": "aerobic",
                    "units": ""
                }
            }
        
        return {
            "status": "success (simulated)",
            "data": result
        }