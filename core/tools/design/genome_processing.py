#!/usr/bin/env python3
"""
综合基因组处理工具
集成基因组下载、特征提取和代谢模型构建功能
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import subprocess
import os
import sys
from pathlib import Path
import requests
import gzip
import shutil
from Bio import SeqIO
import pandas as pd
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.tools.design.carveme import CarvemeTool

# 定义统一的输出目录
OUTPUTS_DIR = os.path.join(project_root, 'outputs')
GENOME_FEATURES_DIR = os.path.join(OUTPUTS_DIR, 'genome_features')
METABOLIC_MODELS_DIR = os.path.join(OUTPUTS_DIR, 'metabolic_models')
os.makedirs(GENOME_FEATURES_DIR, exist_ok=True)
os.makedirs(METABOLIC_MODELS_DIR, exist_ok=True)

class IntegratedGenomeProcessingToolInput(BaseModel):
    genome_urls: Dict[str, str] = Field(..., description="基因组URL字典，格式为 {物种名: URL}")
    output_dir: str = Field(default="./outputs", description="输出目录")
    run_genome_spot: bool = Field(
        default=False,
        description="是否运行GenomeSPOT分析（当前功能暂不可用，保留参数以兼容旧流程）",
    )
    run_carveme: bool = Field(default=True, description="是否运行CarveMe构建代谢模型")

class IntegratedGenomeProcessingTool(BaseTool):
    name: str = "IntegratedGenomeProcessingTool"
    description: str = "综合基因组处理工具，集成基因组下载、特征提取和代谢模型构建功能"
    args_schema: type[BaseModel] = IntegratedGenomeProcessingToolInput
    
    def _run(self, genome_urls: Dict[str, str], output_dir: str = "./outputs", 
             run_genome_spot: bool = True, run_carveme: bool = True) -> Dict[str, Any]:
        """
        运行综合基因组处理工具
        
        Args:
            genome_urls: 基因组URL字典，格式为 {物种名: URL}
            output_dir: 输出目录
            run_genome_spot: 是否运行GenomeSPOT分析
            run_carveme: 是否运行CarveMe构建代谢模型
            
        Returns:
            dict: 处理结果
        """
        print(f"[IntegratedGenomeProcessingTool] 开始处理基因组数据，基因组数量: {len(genome_urls)}")
        
        try:
            # 下载基因组文件
            downloaded_files = self._download_genomes(genome_urls)
            if not downloaded_files:
                return {"status": "error", "message": "未能下载任何基因组文件"}
            
            # 解压文件
            uncompressed_files = self._uncompress_files(downloaded_files)
            
            # 提取基因组特征（目前禁用）
            genome_features = {}
            if run_genome_spot:
                print("[IntegratedGenomeProcessingTool] GenomeSPOT 功能已停用，跳过环境特征分析。")
            
            # 构建代谢模型
            metabolic_models = {}
            if run_carveme:
                metabolic_models = self._build_metabolic_models(uncompressed_files)
            
            result = {
                "status": "success",
                "data": {
                    "downloaded_files": uncompressed_files,
                    "genome_features": genome_features,
                    "metabolic_models": metabolic_models
                }
            }
            
            print(f"[IntegratedGenomeProcessingTool] 处理完成，结果: {result}")
            return result
            
        except Exception as e:
            print(f"[IntegratedGenomeProcessingTool] 处理过程中出错: {str(e)}")
            return {"status": "error", "message": f"处理过程中出错: {str(e)}"}
    
    def _download_genomes(self, genome_urls: Dict[str, str]) -> Dict[str, str]:
        """
        下载基因组文件
        
        Args:
            genome_urls: 基因组URL字典
            
        Returns:
            dict: 下载文件路径字典
        """
        print(f"[IntegratedGenomeProcessingTool] 开始下载基因组文件")
        downloaded_files = {}
        
        for species, url in genome_urls.items():
            try:
                print(f"[IntegratedGenomeProcessingTool] 下载 {species} 的基因组文件: {url}")
                response = requests.get(url, timeout=300)  # 5分钟超时
                response.raise_for_status()
                
                # 生成文件名
                file_extension = ".gz" if url.endswith(".gz") else ""
                filename = f"{species.replace(' ', '_')}.fna{file_extension}"
                file_path = os.path.join(GENOME_FEATURES_DIR, filename)
                
                # 保存文件
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_files[species] = file_path
                print(f"[IntegratedGenomeProcessingTool] 成功下载 {species} 的基因组文件到: {file_path}")
                
            except Exception as e:
                print(f"[IntegratedGenomeProcessingTool] 下载 {species} 的基因组文件失败: {str(e)}")
        
        return downloaded_files
    
    def _uncompress_files(self, files: Dict[str, str]) -> Dict[str, str]:
        """
        解压.gz文件
        
        Args:
            files: 文件路径字典
            
        Returns:
            dict: 解压后文件路径字典
        """
        print(f"[IntegratedGenomeProcessingTool] 开始解压文件")
        uncompressed_files = {}
        
        for species, file_path in files.items():
            try:
                if file_path.endswith(".gz"):
                    # 解压.gz文件
                    uncompressed_path = file_path[:-3]  # 移除.gz扩展名
                    with gzip.open(file_path, 'rb') as f_in:
                        with open(uncompressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    uncompressed_files[species] = uncompressed_path
                    print(f"[IntegratedGenomeProcessingTool] 成功解压 {species} 的基因组文件到: {uncompressed_path}")
                else:
                    uncompressed_files[species] = file_path
                    
            except Exception as e:
                print(f"[IntegratedGenomeProcessingTool] 解压 {species} 的基因组文件失败: {str(e)}")
                uncompressed_files[species] = file_path  # 即使解压失败也保留原文件路径
        
        return uncompressed_files
    
    def _extract_genome_features(self, genome_files: Dict[str, str]) -> Dict[str, Any]:
        """兼容旧接口，目前返回空结果。"""
        print(
            "[IntegratedGenomeProcessingTool] GenomeSPOT 已移除，无法提取基因组特征，返回空字典。"
        )
        return {}
    
    def _build_metabolic_models(self, genome_files: Dict[str, str]) -> Dict[str, Any]:
        """
        构建代谢模型
        
        Args:
            genome_files: 基因组文件路径字典
            
        Returns:
            dict: 代谢模型字典
        """
        print(f"[IntegratedGenomeProcessingTool] 开始构建代谢模型")
        
        # 初始化CarveMe工具
        carveme_tool = CarvemeTool()
        
        # 为CarveMe准备输入目录
        carveme_input_dir = os.path.join(GENOME_FEATURES_DIR, "carveme_input")
        os.makedirs(carveme_input_dir, exist_ok=True)
        
        # 复制基因组文件到输入目录
        for species, file_path in genome_files.items():
            try:
                # 生成目标文件名
                target_filename = f"{species.replace(' ', '_')}.fna"
                target_path = os.path.join(carveme_input_dir, target_filename)
                
                # 复制文件
                shutil.copy2(file_path, target_path)
                print(f"[IntegratedGenomeProcessingTool] 复制 {species} 的基因组文件到CarveMe输入目录: {target_path}")
                
            except Exception as e:
                print(f"[IntegratedGenomeProcessingTool] 复制 {species} 的基因组文件到CarveMe输入目录时出错: {str(e)}")
        
        # 运行CarveMe工具
        try:
            print(f"[IntegratedGenomeProcessingTool] 调用CarveMe工具构建代谢模型")
            print(f"[IntegratedGenomeProcessingTool] CarveMe输入目录: {carveme_input_dir}")
            print(f"[IntegratedGenomeProcessingTool] CarveMe输出目录: {METABOLIC_MODELS_DIR}")
            
            # 检查输入目录是否存在且包含文件
            if not os.path.exists(carveme_input_dir):
                print(f"[IntegratedGenomeProcessingTool] CarveMe输入目录不存在: {carveme_input_dir}")
                return {}
            
            input_files = list(Path(carveme_input_dir).glob("*.fna"))
            if not input_files:
                print(f"[IntegratedGenomeProcessingTool] CarveMe输入目录中未找到.fna文件: {carveme_input_dir}")
                return {}
            
            print(f"[IntegratedGenomeProcessingTool] 找到 {len(input_files)} 个输入文件")
            
            # 调用CarveMe工具
            result = carveme_tool._run(
                input_path=carveme_input_dir,
                output_path=METABOLIC_MODELS_DIR,
                threads=4,
                overwrite=True,
                # 添加额外参数以提高模型质量
                carve_extra=["--gapfill", "--verbose"]
            )
            
            print(f"[IntegratedGenomeProcessingTool] CarveMe工具返回结果: {result}")
            
            if result.get("status") == "success":
                data = result.get("data", {})
                print(f"[IntegratedGenomeProcessingTool] 成功构建代谢模型，生成 {data.get('model_count', 0)} 个模型")
                print(f"[IntegratedGenomeProcessingTool] 模型文件: {data.get('output_files', [])}")
                if data.get('invalid_models'):
                    print(f"[IntegratedGenomeProcessingTool] 无效模型: {data.get('invalid_models')}")
                return data
            else:
                error_msg = result.get('message', '未知错误')
                print(f"[IntegratedGenomeProcessingTool] 构建代谢模型失败: {error_msg}")
                # 尝试查看输出目录中是否有任何文件
                output_files = list(Path(METABOLIC_MODELS_DIR).glob("*.xml"))
                if output_files:
                    print(f"[IntegratedGenomeProcessingTool] 但在输出目录中找到了 {len(output_files)} 个文件，尝试使用这些文件")
                    return {
                        "output_path": METABOLIC_MODELS_DIR,
                        "model_count": len(output_files),
                        "output_files": [str(f) for f in output_files],
                        "invalid_models": []
                    }
                return {}
                
        except Exception as e:
            print(f"[IntegratedGenomeProcessingTool] 运行CarveMe工具时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 即使出错也尝试查看输出目录中是否有任何文件
            try:
                output_files = list(Path(METABOLIC_MODELS_DIR).glob("*.xml"))
                if output_files:
                    print(f"[IntegratedGenomeProcessingTool] 但在输出目录中找到了 {len(output_files)} 个文件，尝试使用这些文件")
                    return {
                        "output_path": METABOLIC_MODELS_DIR,
                        "model_count": len(output_files),
                        "output_files": [str(f) for f in output_files],
                        "invalid_models": []
                    }
            except Exception as inner_e:
                print(f"[IntegratedGenomeProcessingTool] 检查输出目录时出错: {str(inner_e)}")
            return {}
