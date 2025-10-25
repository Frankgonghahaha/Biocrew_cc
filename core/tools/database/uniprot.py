#!/usr/bin/env python3
"""
UniProt数据库查询工具
用于查询蛋白质序列、功能注释和其他相关数据
"""

import requests
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniProtQueryInput(BaseModel):
    """UniProt查询输入参数"""
    query: str = Field(..., description="查询字符串，可以是蛋白质名称、UniProt ID、基因名称等")
    query_type: str = Field(
        default="protein_name",
        description="查询类型: protein_name, id, gene_name, organism等"
    )
    format: str = Field(
        default="json",
        description="返回数据格式: json, xml, txt等"
    )
    limit: int = Field(
        default=10,
        description="返回结果数量限制"
    )


class UniProtTool(BaseTool):
    """UniProt数据库查询工具"""
    
    name: str = "UniProt数据库查询工具"
    description: str = """用于查询UniProt数据库中的蛋白质信息。
    可以通过蛋白质名称、UniProt ID、基因名称等方式查询蛋白质序列和功能信息。
    """
    args_schema: type[BaseModel] = UniProtQueryInput
    
    def __init__(self):
        super().__init__()
        # UniProt API基础URL
        object.__setattr__(self, 'base_url', "https://rest.uniprot.org")
        
    def _run(self, query: str, query_type: str = "protein_name", 
             format: str = "json", limit: int = 10) -> Dict[str, Any]:
        """
        查询UniProt数据库
        
        Args:
            query: 查询字符串
            query_type: 查询类型
            format: 返回格式
            limit: 结果数量限制
            
        Returns:
            dict: 查询结果
        """
        try:
            # 构建查询URL
            if query_type == "protein_name":
                query_string = f"protein_name:{query}"
            elif query_type == "id":
                query_string = f"accession:{query}"
            elif query_type == "gene_name":
                query_string = f"gene:{query}"
            elif query_type == "organism":
                query_string = f"organism_name:{query}"
            else:
                query_string = query
                
            url = f"{self.base_url}/uniprotkb/search"
            
            params = {
                'query': query_string,
                'format': format,
                'size': limit
            }
            
            logger.info(f"查询UniProt数据库: {url} with params {params}")
            
            # 发送请求
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            if format == "json":
                data = response.json()
                return {
                    "status": "success",
                    "query": query,
                    "query_type": query_type,
                    "results": data.get('results', []),
                    "total_results": data.get('totalResults', 0)
                }
            else:
                return {
                    "status": "success",
                    "query": query,
                    "query_type": query_type,
                    "results": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniProt查询请求错误: {e}")
            return {
                "status": "error",
                "message": f"请求UniProt数据库时出错: {str(e)}",
                "query": query
            }
        except Exception as e:
            logger.error(f"UniProt查询处理错误: {e}")
            return {
                "status": "error",
                "message": f"处理UniProt查询结果时出错: {str(e)}",
                "query": query
            }
            
    def search_by_protein_name(self, protein_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        根据蛋白质名称搜索
        
        Args:
            protein_name: 蛋白质名称
            limit: 结果数量限制
            
        Returns:
            dict: 查询结果
        """
        return self._run(protein_name, "protein_name", "json", limit)
        
    def search_by_id(self, uniprot_id: str) -> Dict[str, Any]:
        """
        根据UniProt ID搜索
        
        Args:
            uniprot_id: UniProt ID
            
        Returns:
            dict: 查询结果
        """
        return self._run(uniprot_id, "id", "json", 1)
        
    def search_by_gene_name(self, gene_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        根据基因名称搜索
        
        Args:
            gene_name: 基因名称
            limit: 结果数量限制
            
        Returns:
            dict: 查询结果
        """
        return self._run(gene_name, "gene_name", "json", limit)
        
    def get_protein_sequence(self, uniprot_id: str) -> Dict[str, Any]:
        """
        获取蛋白质序列
        
        Args:
            uniprot_id: UniProt ID
            
        Returns:
            dict: 包含蛋白质序列信息的结果
        """
        try:
            url = f"{self.base_url}/uniprotkb/{uniprot_id}.fasta"
            response = requests.get(url)
            response.raise_for_status()
            
            return {
                "status": "success",
                "uniprot_id": uniprot_id,
                "sequence": response.text
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"获取蛋白质序列错误: {e}")
            return {
                "status": "error",
                "message": f"获取蛋白质序列时出错: {str(e)}",
                "uniprot_id": uniprot_id
            }