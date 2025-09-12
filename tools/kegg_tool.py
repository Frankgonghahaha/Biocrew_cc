#!/usr/bin/env python3
"""
KEGG数据库访问工具
用于查询pathway、ko、genome、reaction、enzyme、genes等信息
"""

from crewai.tools import BaseTool
import requests
import json
from typing import Dict, List, Optional, Any

class KeggTool(BaseTool):
    name: str = "KEGG数据库访问工具"
    description: str = "用于查询pathway、ko、genome、reaction、enzyme、genes等生物代谢信息"
    
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
    
    def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的KEGG数据库操作
        
        Args:
            operation (str): 要执行的操作名称
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            if operation == "get_database_info":
                database = kwargs.get("database")
                if not database:
                    return {"status": "error", "message": "缺少数据库名称参数"}
                return self.get_database_info(database)
                
            elif operation == "list_entries":
                database = kwargs.get("database")
                organism = kwargs.get("organism")
                if not database:
                    return {"status": "error", "message": "缺少数据库名称参数"}
                return self.list_entries(database, organism)
                
            elif operation == "find_entries":
                database = kwargs.get("database")
                keywords = kwargs.get("keywords")
                if not database or not keywords:
                    return {"status": "error", "message": "缺少数据库名称或关键词参数"}
                return self.find_entries(database, keywords)
                
            elif operation == "get_entry":
                entry_id = kwargs.get("entry_id")
                format_type = kwargs.get("format_type", "json")
                if not entry_id:
                    return {"status": "error", "message": "缺少条目ID参数"}
                return self.get_entry(entry_id, format_type)
                
            elif operation == "link_entries":
                target_db = kwargs.get("target_db")
                source_db_entries = kwargs.get("source_db_entries")
                if not target_db or not source_db_entries:
                    return {"status": "error", "message": "缺少目标数据库或源数据库条目参数"}
                return self.link_entries(target_db, source_db_entries)
                
            elif operation == "convert_id":
                target_db = kwargs.get("target_db")
                source_ids = kwargs.get("source_ids")
                if not target_db or not source_ids:
                    return {"status": "error", "message": "缺少目标数据库或源ID参数"}
                return self.convert_id(target_db, source_ids)
                
            elif operation == "search_pathway_by_compound":
                compound_id = kwargs.get("compound_id")
                if not compound_id:
                    return {"status": "error", "message": "缺少化合物ID参数"}
                return self.search_pathway_by_compound(compound_id)
                
            elif operation == "search_genes_by_pathway":
                pathway_id = kwargs.get("pathway_id")
                if not pathway_id:
                    return {"status": "error", "message": "缺少路径ID参数"}
                return self.search_genes_by_pathway(pathway_id)
                
            elif operation == "search_enzymes_by_compound":
                compound_id = kwargs.get("compound_id")
                if not compound_id:
                    return {"status": "error", "message": "缺少化合物ID参数"}
                return self.search_enzymes_by_compound(compound_id)
                
            else:
                return {"status": "error", "message": f"不支持的操作: {operation}"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
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
    
    def find_entries(self, database: str, keywords: str) -> Dict:
        """
        根据关键词搜索条目
        
        Args:
            database (str): 数据库名称
            keywords (str): 搜索关键词
            
        Returns:
            dict: 搜索结果
        """
        try:
            # 将空格替换为+号以符合KEGG API要求
            keywords = keywords.replace(' ', '+')
            url = f"{self.base_url}/find/{database}/{keywords}"
            
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
                "keyword": keywords.replace('+', ' '),
                "count": len(entries)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database": database,
                "keyword": keywords.replace('+', ' ') if 'keywords' in locals() else ""
            }
    
    def get_entry(self, entry_id: str, format_type: str = "json") -> Dict:
        """
        获取特定条目的详细信息
        
        Args:
            entry_id (str): 条目ID (如 hsa:10458)
            format_type (str): 返回格式 (json, aaseq, ntseq等)
            
        Returns:
            dict: 条目详细信息
        """
        try:
            url = f"{self.base_url}/get/{entry_id}/{format_type}"
            response = self.session.get(url)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.text,
                "entry_id": entry_id,
                "format": format_type
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "entry_id": entry_id,
                "format": format_type
            }
    
    def link_entries(self, target_db: str, source_db_entries: str) -> Dict:
        """
        查找相关条目
        
        Args:
            target_db (str): 目标数据库
            source_db_entries (str): 源数据库条目 (如 hsa)
            
        Returns:
            dict: 关联信息
        """
        try:
            url = f"{self.base_url}/link/{target_db}/{source_db_entries}"
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析返回的文本数据
            links = []
            for line in response.text.strip().split('\n'):
                if line:
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
    
    def search_pathway_by_compound(self, compound_id: str) -> Dict:
        """
        根据化合物ID搜索相关代谢路径
        
        Args:
            compound_id (str): 化合物ID (如 C00001)
            
        Returns:
            dict: 相关pathway信息
        """
        return self.link_entries("pathway", compound_id)
    
    def search_genes_by_pathway(self, pathway_id: str) -> Dict:
        """
        根据pathway ID搜索相关基因
        
        Args:
            pathway_id (str): pathway ID (如 path:hsa00010)
            
        Returns:
            dict: 相关基因信息
        """
        return self.link_entries("genes", pathway_id)
    
    def search_enzymes_by_compound(self, compound_id: str) -> Dict:
        """
        根据化合物ID搜索相关酶
        
        Args:
            compound_id (str): 化合物ID
            
        Returns:
            dict: 相关酶信息
        """
        return self.link_entries("enzyme", compound_id)

# 使用示例
if __name__ == "__main__":
    # 创建KEGG工具实例
    kegg_tool = KeggTool()
    
    # 示例：获取pathway数据库信息
    print("获取pathway数据库信息:")
    result = kegg_tool.get_database_info("pathway")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:200] + "...")
    
    # 示例：搜索与镉相关的基因
    print("\n搜索与'cadmium'相关的基因:")
    result = kegg_tool.find_entries("genes", "cadmium")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:200] + "...")
    
    # 示例：列出前10个人类基因
    print("\n列出前10个人类基因:")
    result = kegg_tool.list_entries("genes", "hsa")
    if result["status"] == "success":
        print(json.dumps(result["data"][:10], indent=2, ensure_ascii=False))
    
    # 示例：搜索与重金属相关的pathway
    print("\n搜索与'heavy metal'相关的pathway:")
    result = kegg_tool.find_entries("pathway", "heavy metal")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:200] + "...")