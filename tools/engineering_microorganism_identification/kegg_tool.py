#!/usr/bin/env python3
"""
KEGG数据库访问工具
用于查询pathway、ko、genome、reaction、enzyme、genes等信息
"""

from crewai.tools import BaseTool
import requests
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class KeggToolInput(BaseModel):
    """KEGG工具输入参数"""
    database: Optional[str] = Field(None, description="数据库名称 (pathway, ko, genome, reaction, enzyme, genes, compound)")
    keywords: Optional[str] = Field(None, description="搜索关键词")
    entry_id: Optional[str] = Field(None, description="条目ID")
    target_db: Optional[str] = Field(None, description="目标数据库")
    source_db_entries: Optional[str] = Field(None, description="源数据库条目")
    source_ids: Optional[str] = Field(None, description="源ID")
    compound_id: Optional[str] = Field(None, description="化合物ID")
    compound_name: Optional[str] = Field(None, description="化合物名称，用于智能查询")
    pathway_id: Optional[str] = Field(None, description="pathway ID")
    format_type: Optional[str] = Field("json", description="返回格式")
    organism: Optional[str] = Field(None, description="物种代码")
    limit: Optional[int] = Field(5, description="返回结果的最大数量")


class KeggTool(BaseTool):
    name: str = "KeggTool"
    description: str = "用于查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息"
    args_schema: type[BaseModel] = KeggToolInput
    
    def __init__(self, base_url: str = "https://rest.kegg.jp"):
        """
        初始化KEGG工具
        
        Args:
            base_url (str): KEGG API的基础URL
        """
        super().__init__()  # 调用父类构造函数
        # 使用object.__setattr__来设置实例属性，避免Pydantic验证错误
        object.__setattr__(self, 'base_url', base_url)
        object.__setattr__(self, 'session', requests.Session())
        # 设置默认超时时间
        object.__setattr__(self, 'default_timeout', 30)
    
    def _run(self, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的KEGG数据库操作
        
        Args:
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            # 简化参数处理，直接使用kwargs
            # 注意：需要检查参数值是否为None，避免错误匹配
            
            # 优先处理智能查询
            if "compound_name" in kwargs and kwargs.get("compound_name") is not None:
                return self.smart_query(kwargs["compound_name"])
            
            # 处理compound_id和pathway_id组合情况
            if "compound_id" in kwargs and "pathway_id" in kwargs and kwargs.get("compound_id") is not None and kwargs.get("pathway_id") is not None:
                # 当同时有compound_id和pathway_id时，优先处理pathway_id
                return self.search_genes_by_pathway(kwargs["pathway_id"])
            
            # 处理单一参数情况
            if "database" in kwargs and "organism" in kwargs and kwargs.get("database") is not None and kwargs.get("organism") is not None:
                return self.list_entries(kwargs["database"], kwargs.get("organism"))
            elif "database" in kwargs and "keywords" in kwargs and kwargs.get("database") is not None and kwargs.get("keywords") is not None:
                return self.find_entries(kwargs["database"], kwargs["keywords"], kwargs.get("limit", 5))
            elif "entry_id" in kwargs and kwargs.get("entry_id") is not None:
                return self.get_entry(kwargs["entry_id"], kwargs.get("format_type"))
            elif "target_db" in kwargs and "source_db_entries" in kwargs and kwargs.get("target_db") is not None and kwargs.get("source_db_entries") is not None:
                return self.link_entries(kwargs["target_db"], kwargs["source_db_entries"])
            elif "target_db" in kwargs and "source_ids" in kwargs and kwargs.get("target_db") is not None and kwargs.get("source_ids") is not None:
                return self.convert_id(kwargs["target_db"], kwargs["source_ids"])
            elif "compound_id" in kwargs and kwargs.get("compound_id") is not None:
                # 默认执行search_enzymes_by_compound操作
                return self.search_enzymes_by_compound(kwargs["compound_id"])
            elif "pathway_id" in kwargs and kwargs.get("pathway_id") is not None:
                # 当只有pathway_id时，查询相关基因
                return self.search_genes_by_pathway(kwargs["pathway_id"])
            elif "database" in kwargs and kwargs.get("database") is not None:
                # 默认执行get_database_info操作
                return self.get_database_info(kwargs["database"])
            else:
                return {"status": "error", "message": "缺少必需参数"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}"
            }
    
    def get_database_info(self, database: str) -> Dict:
        """
        获取数据库信息
        
        Args:
            database (str): 数据库名称 (pathway, ko, genome, reaction, enzyme, genes)
            
        Returns:
            dict: 数据库信息
        """
        try:
            url = f"{self.base_url}/info/{database}"
            response = self.session.get(url)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.text,
                "database": database
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database": database
            }
    
    def list_entries(self, database: str, organism: Optional[str] = None) -> Dict:
        """
        列出数据库中的条目
        
        Args:
            database (str): 数据库名称
            organism (str, optional): 物种代码 (如 hsa 表示人类)
            
        Returns:
            dict: 条目列表
        """
        try:
            if organism:
                url = f"{self.base_url}/list/{organism}:{database}"
            else:
                url = f"{self.base_url}/list/{database}"
                
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析返回的文本数据
            entries = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        entries.append({
                            "id": parts[0],
                            "description": parts[1]
                        })
                    elif len(parts) == 1:
                        entries.append({
                            "id": parts[0],
                            "description": ""
                        })
            
            return {
                "status": "success",
                "data": entries,
                "database": database,
                "count": len(entries)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database": database
            }
    
    def find_entries(self, database: str, keywords: str, limit: int = 5, timeout: int = None) -> Dict:
        """
        根据关键词搜索条目
        
        Args:
            database (str): 数据库名称
            keywords (str): 搜索关键词
            limit (int): 返回结果的最大数量，默认5
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 搜索结果
        """
        try:
            # 将空格替换为+号以符合KEGG API要求
            keywords = keywords.replace(' ', '+')
            url = f"{self.base_url}/find/{database}/{keywords}"
            
            # 使用传入的超时时间或类的默认超时时间
            timeout = timeout or self.default_timeout
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # 解析返回的文本数据，限制返回数量
            entries = []
            for line in response.text.strip().split('\n'):
                if line and len(entries) < limit:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        entries.append({
                            "id": parts[0],
                            "description": parts[1]
                        })
                    elif len(parts) == 1:
                        entries.append({
                            "id": parts[0],
                            "description": ""
                        })
            
            return {
                "status": "success",
                "data": entries,
                "database": database,
                "keyword": keywords.replace('+', ' '),
                "count": len(entries),
                "limit": limit
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": f"请求超时: find_entries({database}, {keywords})",
                "database": database,
                "keyword": keywords.replace('+', ' ') if 'keywords' in locals() else ""
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "database": database,
                "keyword": keywords.replace('+', ' ') if 'keywords' in locals() else ""
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database": database,
                "keyword": keywords.replace('+', ' ') if 'keywords' in locals() else ""
            }
    
    def get_entry(self, entry_id: str, format_type: str = None, timeout: int = None) -> Dict:
        """
        获取特定条目的详细信息
        
        Args:
            entry_id (str): 条目ID (如 hsa:10458)
            format_type (str): 返回格式 (json, aaseq, ntseq等)，默认为None表示基本格式
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 条目详细信息
        """
        try:
            if format_type:
                url = f"{self.base_url}/get/{entry_id}/{format_type}"
            else:
                url = f"{self.base_url}/get/{entry_id}"
            # 使用传入的超时时间或类的默认超时时间
            timeout = timeout or self.default_timeout
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.text,
                "entry_id": entry_id,
                "format": format_type or "default"
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": f"请求超时: {entry_id}",
                "entry_id": entry_id,
                "format": format_type or "default"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "entry_id": entry_id,
                "format": format_type or "default"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "entry_id": entry_id,
                "format": format_type or "default"
            }
    
    def link_entries(self, target_db: str, source_db_entries: str, timeout: int = None) -> Dict:
        """
        查找相关条目
        
        Args:
            target_db (str): 目标数据库
            source_db_entries (str): 源数据库条目 (如 hsa)
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 关联信息
        """
        try:
            url = f"{self.base_url}/link/{target_db}/{source_db_entries}"
            # 使用传入的超时时间或类的默认超时时间
            timeout = timeout or self.default_timeout
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # 解析返回的文本数据，限制返回数量以提高性能
            links = []
            for line in response.text.strip().split('\n'):
                if line and len(links) < 20:  # 限制最多返回20个链接
                    parts = line.split('\t')
                    if len(parts) == 2:
                        links.append({
                            "source": parts[0],
                            "target": parts[1]
                        })
            
            return {
                "status": "success",
                "data": links,
                "target_db": target_db,
                "source": source_db_entries,
                "count": len(links)
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": f"请求超时: link_entries({target_db}, {source_db_entries})",
                "target_db": target_db,
                "source": source_db_entries
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "target_db": target_db,
                "source": source_db_entries
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "target_db": target_db,
                "source": source_db_entries
            }
    
    def convert_id(self, target_db: str, source_ids: str) -> Dict:
        """
        转换ID格式
        
        Args:
            target_db (str): 目标数据库 (如 ncbi-geneid)
            source_ids (str): 源ID (如 eco)
            
        Returns:
            dict: 转换结果
        """
        try:
            url = f"{self.base_url}/conv/{target_db}/{source_ids}"
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析返回的文本数据
            conversions = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) == 2:
                        conversions.append({
                            "source": parts[0],
                            "target": parts[1]
                        })
            
            return {
                "status": "success",
                "data": conversions,
                "target_db": target_db,
                "source": source_ids,
                "count": len(conversions)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "target_db": target_db,
                "source": source_ids
            }
    
    def search_pathway_by_compound(self, compound_id: str, timeout: int = None) -> Dict:
        """
        根据化合物ID搜索相关代谢路径
        
        Args:
            compound_id (str): 化合物ID (如 C00001)
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 相关pathway信息
        """
        return self.link_entries("pathway", compound_id, timeout)
    
    def search_genes_by_pathway(self, pathway_id: str, timeout: int = None) -> Dict:
        """
        根据pathway ID搜索相关基因
        
        Args:
            pathway_id (str): pathway ID (如 path:hsa00010)
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 相关基因信息
        """
        try:
            # 确保pathway_id格式正确
            clean_pathway_id = pathway_id
            if clean_pathway_id.startswith("path:"):
                clean_pathway_id = clean_pathway_id[5:]  # 移除"path:"前缀
            
            # 首先尝试直接链接（可能不支持）
            result = self.link_entries("genes", clean_pathway_id, timeout)
            if result["status"] == "success" and result.get("count", 0) > 0:
                return result
            
            # 如果直接链接失败，尝试通过KO（KEGG Orthology）作为中介
            # 先获取pathway相关的KO
            ko_result = self.link_entries("ko", clean_pathway_id, timeout)
            if ko_result["status"] == "success" and ko_result.get("data"):
                # 从KO获取基因
                genes = []
                for ko_link in ko_result["data"][:10]:  # 限制KO的数量
                    if "target" in ko_link:
                        ko_id = ko_link["target"]
                        # 获取KO相关的基因
                        gene_result = self.link_entries("genes", ko_id, timeout//2 if timeout else None)
                        if gene_result["status"] == "success" and gene_result.get("data"):
                            genes.extend(gene_result["data"][:5])  # 限制每个KO的基因数量
                            # 如果基因数量已达到限制，提前退出
                            if len(genes) >= 20:
                                break
                
                return {
                    "status": "success",
                    "data": genes[:20],  # 最多返回20个基因
                    "target_db": "genes",
                    "source": clean_pathway_id,
                    "count": len(genes[:20]),
                    "method": "indirect_via_ko"
                }
            
            # 如果所有方法都失败，返回原始结果
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索基因时出错: {str(e)}",
                "pathway_id": pathway_id
            }
    
    def search_enzymes_by_compound(self, compound_id: str, timeout: int = None) -> Dict:
        """
        根据化合物ID搜索相关酶
        
        Args:
            compound_id (str): 化合物ID
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 相关酶信息
        """
        return self.link_entries("enzyme", compound_id, timeout)
    
    def get_pathway_detail(self, pathway_id: str, timeout: int = None) -> Dict:
        """
        获取特定代谢路径的详细信息，包括反应、基因、化合物等
        
        Args:
            pathway_id (str): pathway ID (如 path:map00624)
            timeout (int): 超时时间（秒），默认使用类的默认超时时间
            
        Returns:
            dict: 路径详细信息
        """
        try:
            # 获取路径的完整信息
            url = f"{self.base_url}/get/{pathway_id}"
            # 使用传入的超时时间或类的默认超时时间
            timeout = timeout or self.default_timeout
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # 解析KEGG路径文件格式
            lines = response.text.strip().split('\n')
            pathway_info = {
                "id": pathway_id,
                "name": "",
                "description": "",
                "classes": [],
                "reactions": [],
                "compounds": [],
                "genes": [],
                "modules": []
            }
            
            # 解析路径信息
            for line in lines:
                if line.startswith("NAME"):
                    pathway_info["name"] = line.split(None, 1)[1] if len(line.split()) > 1 else ""
                elif line.startswith("DESCRIPTION"):
                    pathway_info["description"] = line.split(None, 1)[1] if len(line.split()) > 1 else ""
                elif line.startswith("CLASS"):
                    pathway_info["classes"].append(line.split(None, 1)[1] if len(line.split()) > 1 else "")
            
            # 获取路径相关的反应（添加超时参数）
            reaction_result = self.link_entries("reaction", pathway_id, timeout//2)
            if reaction_result["status"] == "success":
                pathway_info["reactions"] = reaction_result["data"]
                
            # 获取路径相关的基因（添加超时参数）
            # 确保pathway_id格式正确
            gene_pathway_id = pathway_id
            if gene_pathway_id.startswith("path:"):
                gene_pathway_id = gene_pathway_id[5:]  # 移除"path:"前缀
            gene_result = self.link_entries("genes", gene_pathway_id, timeout//2)
            if gene_result["status"] == "success":
                pathway_info["genes"] = gene_result["data"]
                
            # 获取路径相关的化合物（添加超时参数）
            compound_result = self.link_entries("compound", pathway_id, timeout//2)
            if compound_result["status"] == "success":
                pathway_info["compounds"] = compound_result["data"]
            
            return {
                "status": "success",
                "data": pathway_info,
                "pathway_id": pathway_id
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": f"请求超时: get_pathway_detail({pathway_id})",
                "pathway_id": pathway_id
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "pathway_id": pathway_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取路径详细信息时出错: {str(e)}",
                "pathway_id": pathway_id
            }
    
    def compound_to_pathway_workflow(self, compound_name_or_id: str, limit: int = 5) -> Dict:
        """
        化合物到路径的完整工作流，获取化合物相关的所有信息
        
        Args:
            compound_name_or_id (str): 化合物名称或ID
            limit (int): 返回结果的最大数量
            
        Returns:
            dict: 完整的化合物代谢信息
        """
        try:
            # 1. 如果是名称，先查找化合物ID
            if not compound_name_or_id.startswith("cpd:"):
                compound_result = self.find_entries("compound", compound_name_or_id, limit)
                if compound_result["status"] != "success" or not compound_result["data"]:
                    return {
                        "status": "error",
                        "message": f"未找到化合物: {compound_name_or_id}"
                    }
                compound_id = compound_result["data"][0]["id"]
                compound_name = compound_result["data"][0]["description"]
            else:
                compound_id = compound_name_or_id
                compound_name = compound_name_or_id
                
            # 2. 获取化合物相关的代谢路径
            pathway_result = self.search_pathway_by_compound(compound_id)
            if pathway_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"获取化合物路径失败: {pathway_result['message']}"
                }
                
            # 3. 获取每个路径的详细信息（限制数量并简化数据）
            detailed_pathways = []
            for pathway in pathway_result["data"][:min(5, len(pathway_result["data"]))]:  # 最多只处理5个路径
                pathway_id = pathway["target"]
                pathway_detail = self.get_pathway_detail(pathway_id)
                if pathway_detail["status"] == "success":
                    # 简化路径数据，只保留关键信息
                    simplified_data = {
                        "id": pathway_detail["data"]["id"],
                        "name": pathway_detail["data"]["name"],
                        "description": pathway_detail["data"]["description"][:100] + "..." if len(pathway_detail["data"]["description"]) > 100 else pathway_detail["data"]["description"],
                        "classes": pathway_detail["data"]["classes"][:3] if pathway_detail["data"]["classes"] else [],  # 最多保留3个分类
                        "reactions_count": min(len(pathway_detail["data"]["reactions"]), 10),  # 最多统计10个反应
                        "compounds_count": min(len(pathway_detail["data"]["compounds"]), 10),  # 最多统计10个化合物
                        "genes_count": min(len(pathway_detail["data"]["genes"]), 10)  # 最多统计10个基因
                    }
                    detailed_pathways.append(simplified_data)
                    
            # 4. 获取相关的KO条目
            ko_result = self.link_entries("ko", compound_id)
            
            # 5. 获取相关的酶
            enzyme_result = self.search_enzymes_by_compound(compound_id)
            
            # 6. 获取相关的反应
            reaction_result = self.link_entries("reaction", compound_id)
            
            return {
                "status": "success",
                "query_type": "compound_to_pathway",
                "compound": {
                    "id": compound_id,
                    "name": compound_name
                },
                "pathways": detailed_pathways,
                "kos": ko_result.get("data", []),
                "enzymes": enzyme_result.get("data", []),
                "reactions": reaction_result.get("data", [])
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行化合物到路径工作流出错: {str(e)}"
            }
    
    def smart_query(self, compound_name: str, timeout: int = 60) -> Dict:
        """
        智能查询方法，自动处理复杂查询逻辑，为Agent提供简单接口
        
        Args:
            compound_name (str): 化合物名称
            timeout (int): 总体查询超时时间（秒），默认60秒
            
        Returns:
            dict: 综合分析结果（已限制数据量）
        """
        try:
            # 1. 获取化合物基本信息（限制超时时间）
            compound_info = self._get_compound_info(compound_name, timeout // 4)
            if compound_info["status"] != "success":
                return compound_info
            
            # 2. 获取代谢路径信息（限制超时时间）
            pathway_info = self._get_pathway_info(compound_info, timeout // 4)
            
            # 3. 获取基因信息（限制超时时间）
            gene_info = self._get_gene_info(pathway_info, timeout // 4)
            
            # 4. 获取功能微生物信息（限制超时时间）
            microbe_info = self._get_microbe_info(gene_info, timeout // 4)
            
            # 5. 评估置信度
            confidence = self._assess_confidence(compound_info, pathway_info, gene_info, microbe_info)
            
            # 6. 限制返回的数据量
            result = {
                "status": "success",
                "query_type": "smart_compound_analysis",
                "compound": compound_info,
                "pathways": pathway_info,
                "genes": gene_info,
                "microbes": microbe_info,
                "confidence": confidence,
                "query_strategy": "direct_and_inferred"
            }
            
            # 限制result的大小，避免超出模型输入限制
            # 只保留关键信息，删除冗余数据
            if "pathways" in result and "data" in result["pathways"]:
                # 限制路径数量
                result["pathways"]["data"] = result["pathways"]["data"][:3]  # 减少到3个
                
            if "genes" in result and "genes" in result["genes"]:
                # 限制基因数量
                result["genes"]["genes"] = result["genes"]["genes"][:5]  # 减少到5个
                
            if "genes" in result and "kos" in result["genes"]:
                # 限制KO数量
                result["genes"]["kos"] = result["genes"]["kos"][:5]  # 减少到5个
                
            if "genes" in result and "modules" in result["genes"]:
                # 限制模块数量
                result["genes"]["modules"] = result["genes"]["modules"][:3]  # 减少到3个
                
            if "microbes" in result and "microbes" in result["microbes"]:
                # 限制微生物数量
                result["microbes"]["microbes"] = result["microbes"]["microbes"][:5]  # 减少到5个
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"智能查询执行出错: {str(e)}"
            }
    
    def _get_compound_info(self, compound_name: str, timeout: int = None) -> Dict:
        """获取化合物基本信息"""
        # 1. 直接查询目标化合物
        compound_result = self.find_entries("compound", compound_name, 3, timeout)
        if compound_result["status"] == "success" and compound_result["data"]:
            return {
                "status": "success",
                "data": compound_result["data"][0],
                "search_term": compound_name,
                "query_type": "direct"
            }
        
        # 2. 如果直接查询失败，尝试相关化合物查询
        related_terms = self._generate_related_terms(compound_name)
        for term in related_terms:
            compound_result = self.find_entries("compound", term, 3, timeout)
            if compound_result["status"] == "success" and compound_result["data"]:
                return {
                    "status": "success",
                    "data": compound_result["data"][0],
                    "search_term": compound_name,
                    "related_term": term,
                    "query_type": "related"
                }
        
        return {
            "status": "warning",
            "message": f"未找到化合物 {compound_name} 的直接信息",
            "search_term": compound_name
        }
    
    def _get_pathway_info(self, compound_info: Dict, timeout: int = None) -> Dict:
        """获取代谢路径信息"""
        if compound_info["status"] != "success":
            return {"status": "warning", "message": "无法获取化合物信息，跳过路径查询"}
        
        compound_id = compound_info["data"]["id"]
        compound_name = compound_info["data"]["description"]
        
        # 1. 直接查询路径
        pathway_result = self.search_pathway_by_compound(compound_id)
        if pathway_result["status"] == "success" and pathway_result["data"]:
            # 获取详细路径信息（限制数量并简化数据）
            detailed_pathways = []
            for pathway in pathway_result["data"][:3]:  # 减少到最多只处理3个路径
                pathway_id = pathway["target"]
                pathway_detail = self.get_pathway_detail(pathway_id)
                if pathway_detail["status"] == "success":
                    # 简化路径数据，只保留关键信息
                    simplified_data = {
                        "id": pathway_detail["data"]["id"],
                        "name": pathway_detail["data"]["name"],
                        "description": pathway_detail["data"]["description"][:100] + "..." if len(pathway_detail["data"]["description"]) > 100 else pathway_detail["data"]["description"],  # 减少描述长度
                        "classes": pathway_detail["data"]["classes"][:3] if pathway_detail["data"]["classes"] else [],  # 最多保留3个分类
                        "reactions_count": min(len(pathway_detail["data"]["reactions"]), 10),  # 最多统计10个反应
                        "compounds_count": min(len(pathway_detail["data"]["compounds"]), 10),  # 最多统计10个化合物
                        "genes_count": min(len(pathway_detail["data"]["genes"]), 10)  # 最多统计10个基因
                    }
                    detailed_pathways.append(simplified_data)
            
            return {
                "status": "success",
                "data": detailed_pathways,
                "query_type": "direct",
                "source_compound": compound_id
            }
        
        # 2. 如果直接查询失败，查询相关代谢物的路径
        related_compounds = self._find_related_metabolites(compound_name)
        for related in related_compounds:
            pathway_result = self.search_pathway_by_compound(related["id"])
            if pathway_result["status"] == "success" and pathway_result["data"]:
                # 获取详细路径信息（限制数量并简化数据）
                detailed_pathways = []
                for pathway in pathway_result["data"][:3]:  # 减少到最多只处理3个路径
                    pathway_id = pathway["target"]
                    pathway_detail = self.get_pathway_detail(pathway_id)
                    if pathway_detail["status"] == "success":
                        # 简化路径数据，只保留关键信息
                        simplified_data = {
                            "id": pathway_detail["data"]["id"],
                            "name": pathway_detail["data"]["name"],
                            "description": pathway_detail["data"]["description"][:100] + "..." if len(pathway_detail["data"]["description"]) > 100 else pathway_detail["data"]["description"],  # 减少描述长度
                            "classes": pathway_detail["data"]["classes"][:3] if pathway_detail["data"]["classes"] else [],  # 最多保留3个分类
                            "reactions_count": min(len(pathway_detail["data"]["reactions"]), 10),  # 最多统计10个反应
                            "compounds_count": min(len(pathway_detail["data"]["compounds"]), 10),  # 最多统计10个化合物
                            "genes_count": min(len(pathway_detail["data"]["genes"]), 10)  # 最多统计10个基因
                        }
                        detailed_pathways.append(simplified_data)
                
                return {
                    "status": "success",
                    "data": detailed_pathways,
                    "query_type": "inferred",
                    "source_compound": compound_id,
                    "inferred_from": related
                }
        
        return {
            "status": "warning",
            "message": "未找到相关代谢路径信息",
            "source_compound": compound_id
        }
    
    def _get_gene_info(self, pathway_info: Dict, timeout: int = None) -> Dict:
        """获取基因信息"""
        if pathway_info["status"] != "success":
            return {"status": "warning", "message": "无法获取路径信息，跳过基因查询"}
        
        # 从路径信息中提取基因和KO条目（限制数量）
        genes = []
        kos = []
        
        for pathway in pathway_info["data"][:2]:  # 进一步减少处理路径数量至2个
            # 获取路径中的KO条目
            if "id" in pathway:
                # 实际调用API获取KO信息
                try:
                    # 从pathway ID中提取路径ID部分
                    pathway_id = pathway["id"]
                    if pathway_id.startswith("path:"):
                        pathway_id = pathway_id[5:]  # 移除"path:"前缀
                    
                    # 查询与pathway关联的KO条目（添加超时参数）
                    ko_result = self.link_entries("ko", pathway_id, timeout)
                    if ko_result["status"] == "success" and "data" in ko_result:
                        for link in ko_result["data"][:3]:  # 进一步减少KO数量至3个
                            if "target" in link:
                                kos.append(link["target"])
                                
                                # 获取KO的详细信息（添加超时参数）
                                ko_detail = self.get_entry(link["target"], timeout=timeout//2)
                                if ko_detail["status"] == "success":
                                    genes.append({
                                        "ko_id": link["target"],
                                        "detail": ko_detail["data"][:100] + "..." if len(ko_detail["data"]) > 100 else ko_detail["data"]  # 减少详细信息长度
                                    })
                                    
                                # 如果基因数量已达到限制，提前退出
                                if len(genes) >= 5:  # 减少基因数量限制至5个
                                    break
                                    
                        # 如果基因数量已达到限制，提前退出外层循环
                        if len(genes) >= 5:  # 减少基因数量限制至5个
                            break
                except Exception as e:
                    # 如果获取KO信息失败，继续处理下一个路径
                    continue
        
        # 查询模块信息（限制数量）
        modules = []
        if kos:
            for ko_id in kos[:2]:  # 进一步减少查询数量至2个
                try:
                    # 查询与KO关联的模块（添加超时参数）
                    module_result = self.link_entries("module", ko_id, timeout)
                    if module_result["status"] == "success" and "data" in module_result:
                        for link in module_result["data"][:2]:  # 进一步限制模块数量至2个
                            if "target" in link:
                                # 获取模块的详细信息（添加超时参数）
                                module_detail = self.get_entry(link["target"], timeout=timeout//2)
                                if module_detail["status"] == "success":
                                    modules.append({
                                        "module_id": link["target"],
                                        "detail": module_detail["data"][:100] + "..." if len(module_detail["data"]) > 100 else module_detail["data"]  # 减少详细信息长度
                                    })
                                    
                                # 如果模块数量已达到限制，提前退出
                                if len(modules) >= 3:  # 减少模块数量限制至3个
                                    break
                                    
                        # 如果模块数量已达到限制，提前退出外层循环
                        if len(modules) >= 3:  # 减少模块数量限制至3个
                            break
                except Exception as e:
                    # 如果获取模块信息失败，继续处理下一个KO
                    continue
        
        return {
            "status": "success" if genes or modules else "warning",
            "genes": genes[:5],  # 减少最多返回基因数量至5个
            "kos": kos[:5],  # 减少最多返回KO数量至5个
            "modules": modules[:3],  # 减少最多返回模块数量至3个
            "message": "基因信息查询完成" if genes or modules else "未找到相关基因信息"
        }
    
    def _get_microbe_info(self, gene_info: Dict, timeout: int = None) -> Dict:
        """获取功能微生物信息"""
        if gene_info["status"] != "success":
            return {"status": "warning", "message": "无法获取基因信息，跳过微生物查询"}
        
        microbes = []
        
        # 从KO信息中提取可能的微生物信息
        if "kos" in gene_info and gene_info["kos"]:
            for ko_id in gene_info["kos"][:5]:  # 减少KO数量至5个
                try:
                    # 查询与KO关联的基因组（微生物）（添加超时参数）
                    genome_result = self.link_entries("genome", ko_id, timeout)
                    if genome_result["status"] == "success" and "data" in genome_result:
                        for link in genome_result["data"][:3]:  # 减少基因组数量至3个
                            if "target" in link:
                                # 获取基因组的详细信息（添加超时参数）
                                genome_detail = self.get_entry(link["target"], timeout=timeout//2)
                                if genome_detail["status"] == "success":
                                    # 解析基因组信息，提取微生物名称
                                    genome_text = genome_detail["data"]
                                    # 简单解析微生物名称（实际应用中可能需要更复杂的解析）
                                    lines = genome_text.split('\n')
                                    organism_name = ""
                                    for line in lines:
                                        if line.startswith("ORGANISM"):
                                            organism_name = line.split(None, 1)[1] if len(line.split()) > 1 else link["target"]
                                            break
                                    
                                    microbes.append({
                                        "microbe": organism_name if organism_name else link["target"],
                                        "source": "ko_associated",
                                        "ko_id": ko_id,
                                        "genome_id": link["target"],
                                        "detail": genome_text[:100] + "..." if len(genome_text) > 100 else genome_text  # 减少详细信息长度
                                    })
                                    
                                    # 如果微生物数量已达到限制，提前退出
                                    if len(microbes) >= 5:  # 减少微生物数量限制至5个
                                        break
                                    
                except Exception:
                    # 如果获取微生物信息失败，继续处理下一个KO
                    continue
                
                # 如果微生物数量已达到限制，提前退出外层循环
                if len(microbes) >= 5:  # 减少微生物数量限制至5个
                    break
        
        # 从模块信息中提取微生物（限制数量）
        if "modules" in gene_info and gene_info["modules"]:
            for module in gene_info["modules"][:3]:  # 减少模块数量至3个
                try:
                    # 查询与模块关联的基因组（微生物）（添加超时参数）
                    if "module_id" in module:
                        genome_result = self.link_entries("genome", module["module_id"], timeout)
                        if genome_result["status"] == "success" and "data" in genome_result:
                            for link in genome_result["data"][:2]:  # 减少基因组数量至2个
                                if "target" in link:
                                    # 获取基因组的详细信息（添加超时参数）
                                    genome_detail = self.get_entry(link["target"], timeout=timeout//2)
                                    if genome_detail["status"] == "success":
                                        # 解析基因组信息，提取微生物名称
                                        genome_text = genome_detail["data"]
                                        # 简单解析微生物名称（实际应用中可能需要更复杂的解析）
                                        lines = genome_text.split('\n')
                                        organism_name = ""
                                        for line in lines:
                                            if line.startswith("ORGANISM"):
                                                organism_name = line.split(None, 1)[1] if len(line.split()) > 1 else link["target"]
                                                break
                                        
                                        microbes.append({
                                            "microbe": organism_name if organism_name else link["target"],
                                            "source": "module_complete",
                                            "module_id": module["module_id"],
                                            "genome_id": link["target"],
                                            "detail": genome_text[:100] + "..." if len(genome_text) > 100 else genome_text  # 减少详细信息长度
                                        })
                                        
                                        # 如果微生物数量已达到限制，提前退出
                                        if len(microbes) >= 5:  # 减少微生物数量限制至5个
                                            break
                                    
                except Exception:
                    # 如果获取微生物信息失败，继续处理下一个模块
                    continue
                
                # 如果微生物数量已达到限制，提前退出外层循环
                if len(microbes) >= 5:  # 减少微生物数量限制至5个
                    break
        
        # 去重并限制数量
        unique_microbes = []
        seen = set()
        for microbe in microbes:
            microbe_key = microbe["microbe"]
            if microbe_key not in seen:
                unique_microbes.append(microbe)
                seen.add(microbe_key)
                if len(unique_microbes) >= 5:  # 减少最多返回微生物数量至5个
                    break
        
        return {
            "status": "success" if unique_microbes else "warning",
            "microbes": unique_microbes,
            "total_count": len(unique_microbes),
            "message": f"找到{len(unique_microbes)}个潜在功能微生物" if unique_microbes else "未找到相关微生物信息"
        }
    
    def _assess_confidence(self, compound_info: Dict, pathway_info: Dict, gene_info: Dict, microbe_info: Dict) -> Dict:
        """评估查询结果的置信度"""
        confidence_scores = {
            "compound": "high" if compound_info["status"] == "success" else "low",
            "pathway": "high" if pathway_info["status"] == "success" else "medium" if pathway_info["status"] == "warning" and pathway_info.get("query_type") == "inferred" else "low",
            "gene": "high" if gene_info["status"] == "success" else "low",
            "microbe": "high" if microbe_info["status"] == "success" else "low"
        }
        
        overall_confidence = "high"
        if "low" in confidence_scores.values():
            overall_confidence = "low"
        elif list(confidence_scores.values()).count("medium") > 1:
            overall_confidence = "medium"
        
        return {
            "scores": confidence_scores,
            "overall": overall_confidence,
            "assessment": "结果可靠" if overall_confidence == "high" else "结果部分可靠" if overall_confidence == "medium" else "结果可靠性较低"
        }
    
    def _generate_related_terms(self, compound_name: str) -> list:
        """生成相关查询词"""
        terms = []
        # 移除常见后缀
        base_name = compound_name.lower()
        suffixes = ["ate", "ic acid", "acid", "ester", "phthalate", "phthalic"]
        for suffix in suffixes:
            if base_name.endswith(suffix):
                terms.append(base_name[:-len(suffix)].strip())
        
        # 添加常见相关词
        if "phthalate" in base_name or "phthalic" in base_name:
            terms.extend(["phthalate", "phthalic acid", "o-phthalic acid"])
        
        return list(set(terms))  # 去重
    
    def _find_related_metabolites(self, compound_name: str) -> list:
        """查找相关代谢物"""
        related_compounds = []
        
        # 对于酯类化合物，查找其水解产物
        if "dibutyl" in compound_name.lower() and "phthalate" in compound_name.lower():
            # 查找phthalate
            phthalate_result = self.find_entries("compound", "phthalate", 1)
            if phthalate_result["status"] == "success" and phthalate_result["data"]:
                related_compounds.append(phthalate_result["data"][0])
        
        return related_compounds