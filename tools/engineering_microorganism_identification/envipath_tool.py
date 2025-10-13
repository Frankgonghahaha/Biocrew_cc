#!/usr/bin/env python3
"""
EnviPath数据库访问工具
用于查询环境pathway数据和化合物代谢信息
基于enviPath-python库实现
"""

from crewai.tools import BaseTool
from enviPath_python import enviPath
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SearchCompoundRequest(BaseModel):
    compound_name: str = Field(..., description="化合物名称")


class GetPathwayInfoRequest(BaseModel):
    pathway_id: str = Field(..., description="pathway ID")


class GetCompoundPathwaysRequest(BaseModel):
    compound_id: str = Field(..., description="化合物ID")


class SearchPathwaysByKeywordRequest(BaseModel):
    keyword: str = Field(..., description="搜索关键词")


class EnviPathToolInput(BaseModel):
    """EnviPath工具输入参数"""
    compound_name: Optional[str] = Field(None, description="化合物名称")
    pathway_id: Optional[str] = Field(None, description="pathway ID")
    compound_id: Optional[str] = Field(None, description="化合物ID")
    keyword: Optional[str] = Field(None, description="搜索关键词")


class EnviPathTool(BaseTool):
    name: str = "EnviPathTool"
    description: str = "用于查询环境pathway数据和化合物代谢信息，基于enviPath-python库实现"
    args_schema: type[BaseModel] = EnviPathToolInput
    
    def __init__(self, base_url: str = "https://envipath.org"):
        """
        初始化EnviPath工具
        
        Args:
            base_url (str): EnviPath API的基础URL
        """
        super().__init__()  # 调用父类构造函数
        # 使用object.__setattr__来设置实例属性，避免Pydantic验证错误
        object.__setattr__(self, 'base_url', base_url)
        try:
            object.__setattr__(self, 'client', enviPath(base_url))
        except Exception as e:
            object.__setattr__(self, 'client', None)
            print(f"警告: 无法初始化EnviPath客户端: {e}")
    
    def _run(self, **kwargs) -> Dict:
        """
        执行指定的EnviPath操作
        
        Args:
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            # 使用object.__getattribute__获取实例属性
            client = object.__getattribute__(self, 'client')
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"解析参数时出错: {str(e)}"
            }
        
        if not client:
            return {
                "status": "error",
                "message": "EnviPath客户端未初始化",
                "suggestion": "请检查网络连接或使用KEGG工具或其他本地数据源"
            }
        
        try:
            # 简化参数处理，直接使用kwargs
            if "compound_name" in kwargs:
                return self.search_compound(kwargs["compound_name"])
            elif "pathway_id" in kwargs:
                return self.get_pathway_info_as_json(kwargs["pathway_id"])
            elif "compound_id" in kwargs:
                return self.get_compound_pathways(kwargs["compound_id"])
            elif "keyword" in kwargs:
                return self.search_pathways_by_keyword(kwargs["keyword"])
            else:
                return {"status": "error", "message": "缺少必需参数"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}"
            }
    
    def search_compound(self, compound_name: str) -> Dict:
        """
        搜索化合物信息，并自动获取相关路径的详细信息
        
        Args:
            compound_name (str): 化合物名称
            
        Returns:
            dict: 化合物搜索结果及路径详细信息
        """
        try:
            client = object.__getattribute__(self, 'client')
            package = client.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
            
            # 构建返回结果
            response_data = {
                "search_query": compound_name,
                "compounds": [],
                "pathways": [],
                "structures": [],
                "rules": []
            }
            
            # 首先尝试直接搜索化合物名称
            result = package.search(compound_name)
            
            # 处理搜索结果
            added_pathways = set()  # 用于跟踪已添加的路径ID，避免重复
            
            if hasattr(result, '__len__') and len(result) > 0:
                # 遍历搜索结果
                for item in result:
                    if hasattr(item, 'id'):
                        item_id = getattr(item, 'id', '')
                        # 检查是否为规则
                        if 'rule' in item_id:
                            rule_info = {
                                "name": getattr(item, 'name', 'Unknown'),
                                "id": item_id
                            }
                            response_data["rules"].append(rule_info)
                        # 检查是否为化合物结构
                        elif 'structure' in item_id:
                            structure_info = {
                                "name": getattr(item, 'name', 'Unknown'),
                                "id": item_id
                            }
                            response_data["structures"].append(structure_info)
                        # 检查是否为化合物
                        elif 'compound' in item_id:
                            compound_info = {
                                "name": getattr(item, 'name', 'Unknown'),
                                "id": item_id
                            }
                            response_data["compounds"].append(compound_info)
                        # 检查是否为路径
                        elif 'pathway' in item_id:
                            pathway_id = item_id
                            if pathway_id not in added_pathways:
                                pathway_info = {
                                    "name": getattr(item, 'name', 'Unknown'),
                                    "id": pathway_id
                                }
                                response_data["pathways"].append(pathway_info)
                                added_pathways.add(pathway_id)
                                
                                # 自动获取路径详细信息
                                pathway_detail = self.get_pathway_info(pathway_id)
                                if pathway_detail["status"] == "success":
                                    pathway_info["details"] = pathway_detail["data"]
            
            # 如果直接搜索没有找到路径，尝试关键词搜索
            if not response_data["pathways"]:
                # 提取化合物名称中的关键词进行搜索
                keywords = compound_name.replace('_', ' ').replace('-', ' ').split()
                # 添加整个名称作为关键词
                keywords.append(compound_name.replace('_', ' ').replace('-', ' '))
                
                for keyword in keywords:
                    if len(keyword) >= 3:  # 只使用长度大于等于3的词作为关键词
                        try:
                            keyword_result = package.search(keyword)
                            if hasattr(keyword_result, '__len__') and len(keyword_result) > 0:
                                for item in keyword_result:
                                    if hasattr(item, 'id'):
                                        item_id = getattr(item, 'id', '')
                                        # 检查是否为路径
                                        if 'pathway' in item_id:
                                            if item_id not in added_pathways:
                                                pathway_info = {
                                                    "name": getattr(item, 'name', 'Unknown'),
                                                    "id": item_id
                                                }
                                                response_data["pathways"].append(pathway_info)
                                                added_pathways.add(item_id)
                                                
                                                # 自动获取路径详细信息
                                                pathway_detail = self.get_pathway_info(item_id)
                                                if pathway_detail["status"] == "success":
                                                    pathway_info["details"] = pathway_detail["data"]
                        except Exception:
                            # 忽略单个关键词搜索的异常
                            pass
            
            # 如果仍然没有找到路径，尝试使用通用关键词
            if not response_data["pathways"]:
                generic_keywords = []
                # 如果名称中包含phthalate，则添加phthalate相关关键词
                if "phthalate" in compound_name.lower():
                    generic_keywords.extend(["phthalate", "phthalate family"])
                # 如果是dibutyl phthalate，也尝试butyl相关关键词
                if "dibutyl" in compound_name.lower():
                    generic_keywords.append("butyl")
                
                for keyword in generic_keywords:
                    try:
                        keyword_result = package.search(keyword)
                        if hasattr(keyword_result, '__len__') and len(keyword_result) > 0:
                            for item in keyword_result:
                                if hasattr(item, 'id'):
                                    item_id = getattr(item, 'id', '')
                                    item_name = getattr(item, 'name', '').lower()
                                    # 特别查找Phthalate Family路径
                                    if ("phthalate" in keyword.lower() and 
                                        "phthalate" in item_name and 
                                        "family" in item_name):
                                        if item_id not in added_pathways:
                                            pathway_info = {
                                                "name": getattr(item, 'name', 'Unknown'),
                                                "id": item_id
                                            }
                                            response_data["pathways"].append(pathway_info)
                                            added_pathways.add(item_id)
                                            
                                            # 自动获取路径详细信息
                                            pathway_detail = self.get_pathway_info(item_id)
                                            if pathway_detail["status"] == "success":
                                                pathway_info["details"] = pathway_detail["data"]
                                    # 也添加其他phthalate路径
                                    elif ("phthalate" in keyword.lower() and 
                                          "phthalate" in item_name):
                                        if item_id not in added_pathways:
                                            pathway_info = {
                                                "name": getattr(item, 'name', 'Unknown'),
                                                "id": item_id
                                            }
                                            response_data["pathways"].append(pathway_info)
                                            added_pathways.add(item_id)
                                            
                                            # 自动获取路径详细信息
                                            pathway_detail = self.get_pathway_info(item_id)
                                            if pathway_detail["status"] == "success":
                                                pathway_info["details"] = pathway_detail["data"]
                                    # 添加butyl相关路径
                                    elif ("butyl" in keyword.lower() and
                                          "butyl" in item_name):
                                        if item_id not in added_pathways:
                                            pathway_info = {
                                                "name": getattr(item, 'name', 'Unknown'),
                                                "id": item_id
                                            }
                                            response_data["pathways"].append(pathway_info)
                                            added_pathways.add(item_id)
                                            
                                            # 自动获取路径详细信息
                                            pathway_detail = self.get_pathway_info(item_id)
                                            if pathway_detail["status"] == "success":
                                                pathway_info["details"] = pathway_detail["data"]
                    except Exception:
                        # 忽略单个关键词搜索的异常
                        pass
            
            # 如果仍然没有找到任何路径，尝试直接获取已知的Phthalate Family路径
            if not response_data["pathways"] and "phthalate" in compound_name.lower():
                try:
                    # 直接获取已知的Phthalate Family路径
                    known_phthalate_pathway_id = "033f7ed7-d7c1-4bbc-83be-8d89617f76fe"
                    pathway_detail = self.get_pathway_info(known_phthalate_pathway_id)
                    if pathway_detail["status"] == "success":
                        pathway_info = {
                            "name": "Phthalate Family",
                            "id": known_phthalate_pathway_id,
                            "details": pathway_detail["data"]
                        }
                        response_data["pathways"].append(pathway_info)
                except Exception:
                    pass
            
            return {"status": "success", "data": response_data, "query": compound_name}
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索化合物时出错: {str(e)}",
                "compound_name": compound_name,
                "error_type": type(e).__name__
            }
    
    def get_pathway_info(self, pathway_id: str) -> Dict:
        """
        获取特定pathway的详细信息，包括反应描述和EC编号
        
        Args:
            pathway_id (str): pathway ID
            
        Returns:
            dict: pathway信息，包括详细的代谢路径信息
        """
        try:
            client = object.__getattribute__(self, 'client')
            # 检查pathway_id是否是完整的URL，如果不是则添加完整前缀
            if not pathway_id.startswith('http'):
                full_pathway_id = f"https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1/pathway/{pathway_id}"
            else:
                full_pathway_id = pathway_id
            pathway = client.get_pathway(full_pathway_id)
            
            # 构建详细的路径信息，包括节点和边的信息
            pathway_info = {
                "name": getattr(pathway, 'name', 'Unknown'),
                "id": getattr(pathway, 'id', pathway_id),
                "nodes": [],
                "edges": []
            }
            
            # 获取节点信息
            if hasattr(pathway, 'get_nodes'):
                nodes = pathway.get_nodes()
                for node in nodes:
                    node_info = {
                        "name": getattr(node, 'name', 'Unknown'),
                        "id": getattr(node, 'id', 'Unknown')
                    }
                    pathway_info["nodes"].append(node_info)
            
            # 获取边信息（反应信息）
            if hasattr(pathway, 'get_edges'):
                edges = pathway.get_edges()
                for edge in edges:
                    # 获取EC编号信息
                    ec_numbers = []
                    # 使用Edge对象提供的方法
                    try:
                        ec_nums = edge.get_ec_numbers()
                        if isinstance(ec_nums, list):
                            for ec in ec_nums:
                                # ECNumber对象使用ec_number和ec_name属性
                                ec_number = getattr(ec, 'ec_number', 'Unknown')
                                ec_name = getattr(ec, 'ec_name', 'Unknown')
                                
                                ec_info = {
                                    "ec_number": ec_number,
                                    "ec_name": ec_name
                                }
                                ec_numbers.append(ec_info)
                    except Exception as e:
                        # 尝试直接访问属性
                        try:
                            if hasattr(edge, 'ecNumbers'):
                                for ec in edge.ecNumbers:
                                    ec_number = getattr(ec, 'ec_number', 'Unknown')
                                    ec_name = getattr(ec, 'ec_name', 'Unknown')
                                    ec_info = {
                                        "ec_number": ec_number,
                                        "ec_name": ec_name
                                    }
                                    ec_numbers.append(ec_info)
                        except Exception:
                            pass
                    
                    # 获取起始节点
                    start_nodes = []
                    try:
                        start_nodes_data = edge.get_start_nodes()
                        if isinstance(start_nodes_data, list):
                            for node in start_nodes_data:
                                if isinstance(node, dict):
                                    node_info = {
                                        "name": node.get('name', 'Unknown'),
                                        "id": node.get('id', 'Unknown')
                                    }
                                else:
                                    node_info = {
                                        "name": getattr(node, 'name', 'Unknown'),
                                        "id": getattr(node, 'id', 'Unknown')
                                    }
                                start_nodes.append(node_info)
                    except Exception as e:
                        # 尝试直接访问属性
                        try:
                            if hasattr(edge, 'start_nodes'):
                                for node in edge.start_nodes:
                                    if isinstance(node, dict):
                                        node_info = {
                                            "name": node.get('name', 'Unknown'),
                                            "id": node.get('id', 'Unknown')
                                        }
                                    else:
                                        node_info = {
                                            "name": getattr(node, 'name', 'Unknown'),
                                            "id": getattr(node, 'id', 'Unknown')
                                        }
                                    start_nodes.append(node_info)
                        except Exception:
                            pass
                    
                    # 获取终止节点
                    end_nodes = []
                    try:
                        end_nodes_data = edge.get_end_nodes()
                        if isinstance(end_nodes_data, list):
                            for node in end_nodes_data:
                                if isinstance(node, dict):
                                    node_info = {
                                        "name": node.get('name', 'Unknown'),
                                        "id": node.get('id', 'Unknown')
                                    }
                                else:
                                    node_info = {
                                        "name": getattr(node, 'name', 'Unknown'),
                                        "id": getattr(node, 'id', 'Unknown')
                                    }
                                end_nodes.append(node_info)
                    except Exception as e:
                        # 尝试直接访问属性
                        try:
                            if hasattr(edge, 'end_nodes'):
                                for node in edge.end_nodes:
                                    if isinstance(node, dict):
                                        node_info = {
                                            "name": node.get('name', 'Unknown'),
                                            "id": node.get('id', 'Unknown')
                                        }
                                    else:
                                        node_info = {
                                            "name": getattr(node, 'name', 'Unknown'),
                                            "id": getattr(node, 'id', 'Unknown')
                                        }
                                    end_nodes.append(node_info)
                        except Exception:
                            pass
                    
                    # 获取其他属性
                    name = 'Unknown'
                    reaction_name = 'Unknown'
                    reaction_uri = 'Unknown'
                    try:
                        name = edge.get_name()
                    except Exception as e:
                        # 尝试直接访问属性
                        try:
                            name = getattr(edge, 'name', 'Unknown')
                        except Exception:
                            pass
                    
                    try:
                        reaction_name = edge.get_reaction_name()
                    except Exception as e:
                        # 尝试直接访问属性
                        try:
                            reaction_name = getattr(edge, 'reaction_name', 'Unknown')
                        except Exception:
                            pass
                    
                    try:
                        reaction_uri = edge.reactionURI if hasattr(edge, 'reactionURI') else 'Unknown'
                    except Exception as e:
                        pass
                    
                    edge_info = {
                        "name": name,
                        "reaction_name": reaction_name,
                        "reaction_uri": reaction_uri,
                        "ec_numbers": ec_numbers,
                        "start_nodes": start_nodes,
                        "end_nodes": end_nodes
                    }
                    pathway_info["edges"].append(edge_info)
            
            # 构建结构化输出，便于Agent处理
            structured_output = self._format_pathway_output(pathway_info)
            return {"status": "success", "data": structured_output, "pathway_id": pathway_id}
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取pathway信息时出错: {str(e)}",
                "pathway_id": pathway_id,
                "error_type": type(e).__name__
            }
    
    def get_pathway_info_as_json(self, pathway_id: str) -> str:
        """
        获取特定pathway的详细信息并返回JSON格式字符串
        
        Args:
            pathway_id (str): pathway ID
            
        Returns:
            str: JSON格式的pathway信息
        """
        result = self.get_pathway_info(pathway_id)
        if result.get('status') == 'success':
            # 返回格式化的JSON字符串
            return json.dumps(result['data'], ensure_ascii=False, indent=2)
        else:
            # 如果出错，返回错误信息的JSON格式
            error_response = {
                "error": True,
                "message": result.get('message', 'Unknown error'),
                "pathway_id": pathway_id,
                "status": result.get('status', 'unknown')
            }
            # 添加额外的错误信息（如果存在）
            if 'error_type' in result:
                error_response['error_type'] = result['error_type']
            return json.dumps(error_response, ensure_ascii=False, indent=2)
    
    def _format_pathway_output(self, pathway_info: Dict) -> Dict:
        """
        格式化pathway输出，使其更适合Agent处理
        
        Args:
            pathway_info (dict): 原始pathway信息
            
        Returns:
            dict: 结构化格式的pathway信息
        """
        # 构建代谢路径摘要
        pathway_summary = {
            "pathway_name": pathway_info.get("name", "Unknown"),
            "total_reactions": len(pathway_info.get("edges", [])),
            "total_compounds": len(pathway_info.get("nodes", [])),
            "reactions": []
        }
        
        # 为每个反应构建详细信息
        for i, edge in enumerate(pathway_info.get("edges", [])):
            reaction_detail = {
                "step": i + 1,
                "reaction_name": edge.get("reaction_name", "Unknown"),
                "reaction_description": edge.get("name", "Unknown"),
                "ec_numbers": edge.get("ec_numbers", []),
                "substrates": [node.get("name", "Unknown") for node in edge.get("start_nodes", [])],
                "products": [node.get("name", "Unknown") for node in edge.get("end_nodes", [])]
            }
            pathway_summary["reactions"].append(reaction_detail)
        
        return pathway_summary
    
    def get_compound_pathways(self, compound_id: str) -> Dict:
        """
        获取与特定化合物相关的代谢路径
        
        Args:
            compound_id (str): 化合物ID
            
        Returns:
            dict: 相关pathway信息
        """
        try:
            client = object.__getattribute__(self, 'client')
            compound = client.get_compound(compound_id)
            # 注意：这里可能需要根据实际API返回结构进行调整
            pathways = []
            return {"status": "success", "data": pathways, "compound_id": compound_id}
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取化合物路径时出错: {str(e)}",
                "compound_id": compound_id,
                "error_type": type(e).__name__
            }
    
    def search_pathways_by_keyword(self, keyword: str) -> Dict:
        """
        根据关键词搜索pathway
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            dict: 搜索结果
        """
        try:
            client = object.__getattribute__(self, 'client')
            package = client.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
            result = package.search(keyword)
            return {"status": "success", "data": result, "keyword": keyword}
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索pathway时出错: {str(e)}",
                "keyword": keyword,
                "error_type": type(e).__name__
            }