#!/usr/bin/env python3
"""
NCBI基因组查询工具
使用NCBI E-utilities API查询微生物基因组的Assembly Accession信息
"""

from crewai.tools import BaseTool
from typing import Type, Optional
import requests
from pydantic import BaseModel, Field
import time
import json

class NCBIGenomeQueryToolSchema(BaseModel):
    """NCBI基因组查询工具的输入参数"""
    organism_name: str = Field(
        description="微生物名称，例如 'Rhodococcus jostii RHA1' 或 'Brevibacillus brevis'"
    )
    max_results: Optional[int] = Field(
        default=5,
        description="返回的最大结果数量，默认为5"
    )

class NCBIGenomeQueryTool(BaseTool):
    name: str = "NCBI基因组查询工具"
    description: str = "使用NCBI E-utilities API查询微生物基因组的Assembly Accession信息，并提供完整的科学分类信息"
    args_schema: Type[BaseModel] = NCBIGenomeQueryToolSchema
    max_retries: int = 3
    retry_delay: int = 2

    def _run(self, organism_name: str, max_results: int = 5) -> str:
        """
        使用NCBI E-utilities API查询微生物基因组信息
        
        Args:
            organism_name: 微生物名称
            max_results: 返回的最大结果数量
            
        Returns:
            包含基因组信息的字符串
        """
        try:
            # 构建搜索URL
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'assembly',
                'term': f'{organism_name}[Organism]',
                'retmax': max_results,
                'retmode': 'json',
                'usehistory': 'y'
            }
            
            # 执行搜索
            search_response = requests.get(search_url, params=search_params, timeout=30)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # 检查是否有搜索结果
            if 'esearchresult' not in search_data or 'idlist' not in search_data['esearchresult']:
                return f"未找到与'{organism_name}'相关的基因组数据"
            
            id_list = search_data['esearchresult']['idlist']
            if not id_list:
                return f"未找到与'{organism_name}'相关的基因组数据"
            
            # 获取详细信息
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                'db': 'assembly',
                'id': ','.join(id_list),
                'retmode': 'json'
            }
            
            summary_response = requests.get(summary_url, params=summary_params, timeout=30)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # 解析结果
            if 'result' not in summary_data:
                return f"无法获取'{organism_name}'的基因组详细信息"
            
            results = []
            for assembly_id in id_list:
                if assembly_id in summary_data['result']:
                    assembly_info = summary_data['result'][assembly_id]
                    accession = assembly_info.get('assemblyaccession', 'N/A')
                    assembly_name = assembly_info.get('assemblyname', 'N/A')
                    organism = assembly_info.get('organism', 'N/A')
                    taxid = assembly_info.get('taxid', 'N/A')
                    species_taxid = assembly_info.get('species_taxid', 'N/A')
                    ftp_path = assembly_info.get('ftppath_refseq', assembly_info.get('ftppath_genbank', 'N/A'))
                    
                    # 获取分类信息
                    organism_parts = organism.split()
                    if len(organism_parts) >= 2:
                        genus = organism_parts[0]
                        species = organism_parts[1]
                        full_species_name = f"{genus} {species}"
                    else:
                        full_species_name = organism
                    
                    result = {
                        'accession': accession,
                        'assembly_name': assembly_name,
                        'organism': organism,
                        'full_species_name': full_species_name,
                        'taxid': taxid,
                        'species_taxid': species_taxid,
                        'ftp_path': ftp_path
                    }
                    results.append(result)
            
            # 格式化输出
            if results:
                output_lines = [f"找到 {len(results)} 个'{organism_name}'的基因组记录:"]
                for i, result in enumerate(results, 1):
                    output_lines.append(f"{i}. 微生物名称: {result['full_species_name']}")
                    output_lines.append(f"   完整学名: {result['organism']}")
                    output_lines.append(f"   Assembly Accession: {result['accession']}")
                    output_lines.append(f"   Assembly Name: {result['assembly_name']}")
                    output_lines.append(f"   Taxonomy ID: {result['taxid']}")
                    output_lines.append(f"   Species Taxonomy ID: {result['species_taxid']}")
                    output_lines.append(f"   FTP Path: {result['ftp_path']}")
                    output_lines.append("")
                
                # 添加JSON格式输出，便于其他工具解析
                output_lines.append("JSON格式数据:")
                output_lines.append(json.dumps(results, ensure_ascii=False, indent=2))
                
                return "\n".join(output_lines)
            else:
                return f"未找到与'{organism_name}'相关的基因组数据"
                
        except requests.exceptions.RequestException as e:
            return f"网络请求错误: {str(e)}"
        except json.JSONDecodeError as e:
            return f"JSON解析错误: {str(e)}"
        except Exception as e:
            return f"查询过程中发生错误: {str(e)}"

    def _arun(self, organism_name: str, max_results: int = 5) -> str:
        """异步运行方法"""
        return self._run(organism_name, max_results)