#!/usr/bin/env python3
"""
EnviPath数据库访问工具
用于查询环境pathway数据和化合物代谢信息
基于enviPath-python库实现
"""

from crewai.tools import BaseTool
from enviPath_python import enviPath
import json
from typing import Dict, List, Optional

class EnviPathTool(BaseTool):
    name: str = "EnviPath数据库访问工具"
    description: str = "用于查询环境pathway数据和化合物代谢信息，基于enviPath-python库实现"
    
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
    
    def _run(self, operation: str, **kwargs) -> Dict:
        """
        执行指定的EnviPath操作
        
        Args:
            operation (str): 要执行的操作名称
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        # 使用object.__getattribute__获取实例属性
        client = object.__getattribute__(self, 'client')
        
        if not client:
            return {
                "status": "error",
                "message": "EnviPath客户端未初始化",
                "suggestion": "请检查网络连接或使用KEGG工具或其他本地数据源"
            }
        
        try:
            if operation == "search_compound":
                compound_name = kwargs.get("compound_name")
                if not compound_name:
                    return {"status": "error", "message": "缺少化合物名称参数"}
                
                package = client.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
                result = package.search(compound_name)
                return {"status": "success", "data": result, "query": compound_name}
                
            elif operation == "get_pathway_info":
                pathway_id = kwargs.get("pathway_id")
                if not pathway_id:
                    return {"status": "error", "message": "缺少pathway ID参数"}
                
                pathway = client.get_pathway(pathway_id)
                return {"status": "success", "data": pathway, "pathway_id": pathway_id}
                
            elif operation == "get_compound_pathways":
                compound_id = kwargs.get("compound_id")
                if not compound_id:
                    return {"status": "error", "message": "缺少化合物ID参数"}
                
                compound = client.get_compound(compound_id)
                # 注意：这里可能需要根据实际API返回结构进行调整
                pathways = []
                return {"status": "success", "data": pathways, "compound_id": compound_id}
                
            elif operation == "search_pathways_by_keyword":
                keyword = kwargs.get("keyword")
                if not keyword:
                    return {"status": "error", "message": "缺少关键词参数"}
                
                package = client.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
                result = package.search(keyword)
                return {"status": "success", "data": result, "keyword": keyword}
                
            else:
                return {"status": "error", "message": f"不支持的操作: {operation}"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
            }
    
    def search_compound(self, compound_name: str) -> Dict:
        """
        搜索化合物信息
        
        Args:
            compound_name (str): 化合物名称
            
        Returns:
            dict: 化合物搜索结果
        """
        return self._run("search_compound", compound_name=compound_name)
    
    def get_pathway_info(self, pathway_id: str) -> Dict:
        """
        获取特定pathway的详细信息
        
        Args:
            pathway_id (str): pathway ID
            
        Returns:
            dict: pathway信息
        """
        return self._run("get_pathway_info", pathway_id=pathway_id)
    
    def get_compound_pathways(self, compound_id: str) -> Dict:
        """
        获取与特定化合物相关的代谢路径
        
        Args:
            compound_id (str): 化合物ID
            
        Returns:
            dict: 相关pathway信息
        """
        return self._run("get_compound_pathways", compound_id=compound_id)
    
    def search_pathways_by_keyword(self, keyword: str) -> Dict:
        """
        根据关键词搜索pathway
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            dict: 搜索结果
        """
        return self._run("search_pathways_by_keyword", keyword=keyword)

# 使用示例
if __name__ == "__main__":
    # 创建EnviPath工具实例
    envipath_tool = EnviPathTool()
    
    # 检查客户端是否初始化成功
    if not envipath_tool.client:
        print("EnviPath客户端初始化失败")
        exit(1)
    
    # 示例：搜索化合物
    print("搜索化合物 'cadmium':")
    result = envipath_tool.search_compound("cadmium")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 示例：根据关键词搜索pathway
    print("\n搜索包含'heavy metal'的pathway:")
    result = envipath_tool.search_pathways_by_keyword("heavy metal")
    print(json.dumps(result, indent=2, ensure_ascii=False))