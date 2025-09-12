#!/usr/bin/env python3
"""
EnviPath数据库访问工具
用于查询环境pathway数据和化合物代谢信息
"""

import requests
import json
from typing import Dict, List, Optional

class EnviPathTool:
    def __init__(self, base_url: str = "https://envipath.ethz.ch/rest"):
        """
        初始化EnviPath工具
        
        Args:
            base_url (str): EnviPath API的基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'BioCrew/1.0 (envipath-tool)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        # 禁用SSL验证（仅用于测试环境，生产环境应启用）
        # 注意：在生产环境中应修复SSL问题而不是禁用验证
        self.session.verify = True
    
    def search_compound(self, compound_name: str) -> Dict:
        """
        搜索化合物信息
        
        Args:
            compound_name (str): 化合物名称
            
        Returns:
            dict: 化合物搜索结果
        """
        try:
            # 使用REST API端点
            url = f"{self.base_url}/search"
            params = {
                "query": compound_name
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.json() if response.content else {},
                "query": compound_name
            }
        except requests.exceptions.SSLError as e:
            return {
                "status": "error",
                "message": f"SSL连接错误，请检查网络环境或联系系统管理员: {str(e)}",
                "query": compound_name,
                "suggestion": "EnviPath工具当前无法连接，请使用KEGG工具或其他本地数据源"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "query": compound_name
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"JSON解析错误: {str(e)}",
                "query": compound_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "query": compound_name
            }
    
    def get_pathway_info(self, pathway_id: str) -> Dict:
        """
        获取特定pathway的详细信息
        
        Args:
            pathway_id (str): pathway ID
            
        Returns:
            dict: pathway信息
        """
        try:
            url = f"{self.base_url}/pathways/{pathway_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.json() if response.content else {},
                "pathway_id": pathway_id
            }
        except requests.exceptions.SSLError as e:
            return {
                "status": "error",
                "message": f"SSL连接错误，请检查网络环境或联系系统管理员: {str(e)}",
                "pathway_id": pathway_id,
                "suggestion": "EnviPath工具当前无法连接，请使用KEGG工具或其他本地数据源"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "pathway_id": pathway_id
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"JSON解析错误: {str(e)}",
                "pathway_id": pathway_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "pathway_id": pathway_id
            }
    
    def get_compound_pathways(self, compound_id: str) -> Dict:
        """
        获取与特定化合物相关的代谢路径
        
        Args:
            compound_id (str): 化合物ID
            
        Returns:
            dict: 相关pathway信息
        """
        try:
            url = f"{self.base_url}/compounds/{compound_id}/pathways"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.json() if response.content else {},
                "compound_id": compound_id
            }
        except requests.exceptions.SSLError as e:
            return {
                "status": "error",
                "message": f"SSL连接错误，请检查网络环境或联系系统管理员: {str(e)}",
                "compound_id": compound_id,
                "suggestion": "EnviPath工具当前无法连接，请使用KEGG工具或其他本地数据源"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "compound_id": compound_id
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"JSON解析错误: {str(e)}",
                "compound_id": compound_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "compound_id": compound_id
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
            url = f"{self.base_url}/pathways"
            params = {
                "search": keyword
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.json() if response.content else {},
                "keyword": keyword
            }
        except requests.exceptions.SSLError as e:
            return {
                "status": "error",
                "message": f"SSL连接错误，请检查网络环境或联系系统管理员: {str(e)}",
                "keyword": keyword,
                "suggestion": "EnviPath工具当前无法连接，请使用KEGG工具或其他本地数据源"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求错误: {str(e)}",
                "keyword": keyword
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"JSON解析错误: {str(e)}",
                "keyword": keyword
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "keyword": keyword
            }

# 使用示例
if __name__ == "__main__":
    # 创建EnviPath工具实例
    envipath_tool = EnviPathTool()
    
    # 示例：搜索化合物
    print("搜索化合物 'cadmium':")
    result = envipath_tool.search_compound("cadmium")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 示例：根据关键词搜索pathway
    print("\n搜索包含'heavy metal'的pathway:")
    result = envipath_tool.search_pathways_by_keyword("heavy metal")
    print(json.dumps(result, indent=2, ensure_ascii=False))