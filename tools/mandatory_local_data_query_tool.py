#!/usr/bin/env python3
"""
强制本地数据查询工具
确保智能体在处理过程中必须调用本地数据查询工具
"""

from crewai.tools import BaseTool
from tools.local_data_retriever import LocalDataRetriever
from tools.smart_data_query_tool import SmartDataQueryTool
from typing import Dict, Any

class MandatoryLocalDataQueryTool(BaseTool):
    name: str = "强制本地数据查询工具"
    description: str = "确保智能体在处理过程中必须调用本地数据查询工具"
    
    def __init__(self, base_path="."):
        """
        初始化强制本地数据查询工具
        
        Args:
            base_path (str): 项目根路径，默认为当前目录
        """
        super().__init__()  # 调用父类构造函数
        # 使用object.__setattr__来设置实例属性，避免Pydantic验证错误
        object.__setattr__(self, 'local_data_retriever', LocalDataRetriever(base_path))
        object.__setattr__(self, 'smart_query', SmartDataQueryTool(base_path))
    
    def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的强制本地数据查询操作
        
        Args:
            operation (str): 要执行的操作名称
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            if operation == "query_required_data":
                query_text = kwargs.get("query_text")
                data_type = kwargs.get("data_type", "both")
                if not query_text:
                    return {"status": "error", "message": "缺少查询文本参数"}
                return self.query_required_data(query_text, data_type)
                
            elif operation == "get_available_pollutants_summary":
                result = self.get_available_pollutants_summary()
                return {"status": "success", "data": result}
                
            else:
                return {"status": "error", "message": f"不支持的操作: {operation}"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
            }
    
    def query_required_data(self, query_text, data_type="both"):
        """
        强制查询必需的本地数据
        
        Args:
            query_text (str): 查询文本
            data_type (str): 数据类型，"gene"、"organism" 或 "both"
            
        Returns:
            dict: 包含查询结果的字典
        """
        # 使用智能数据查询工具查询相关数据
        result = self.smart_query.query_related_data(query_text, data_type)
        
        # 添加查询状态信息
        result["query_required"] = True
        result["tool_used"] = "MandatoryLocalDataQueryTool"
        
        return result
    
    def get_available_pollutants_summary(self):
        """
        获取可用污染物数据摘要
        
        Returns:
            dict: 可用污染物数据摘要
        """
        pollutants = self.local_data_retriever.list_available_pollutants()
        return {
            "genes_pollutants_count": len(pollutants["genes_pollutants"]),
            "organism_pollutants_count": len(pollutants["organism_pollutants"]),
            "genes_pollutants_sample": pollutants["genes_pollutants"][:5],  # 前5个示例
            "organism_pollutants_sample": pollutants["organism_pollutants"][:5]  # 前5个示例
        }