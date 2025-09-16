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
            # 记录输入参数用于调试
            import json
            params_log = {
                "operation": operation,
                "kwargs": kwargs
            }
            print(f"[DEBUG] MandatoryLocalDataQueryTool._run 调用参数: {json.dumps(params_log, ensure_ascii=False)}")
            
            # 如果operation是JSON字符串，解析它
            if isinstance(operation, str) and operation.startswith('{'):
                import json
                try:
                    params = json.loads(operation)
                    operation = params.get('operation', operation)
                    # 合并参数，确保所有参数都被正确处理
                    for k, v in params.items():
                        if k != 'operation':
                            kwargs[k] = v
                except json.JSONDecodeError:
                    pass  # 如果解析失败，继续使用原始参数
            
            # 如果kwargs中包含JSON字符串参数，也进行解析
            if 'query_text' in kwargs and isinstance(kwargs['query_text'], str) and kwargs['query_text'].startswith('{'):
                try:
                    params = json.loads(kwargs['query_text'])
                    kwargs.update(params)
                except json.JSONDecodeError:
                    pass  # 如果解析失败，继续使用原始参数
                    
            # 处理直接传递的参数
            if 'query_text' not in kwargs and 'pollutant_name' in kwargs:
                kwargs['query_text'] = kwargs['pollutant_name']
            if 'pollutant_name' not in kwargs and 'query_text' in kwargs:
                kwargs['pollutant_name'] = kwargs['query_text']
            
            # 如果kwargs中的值是JSON字符串，也进行解析
            for key, value in list(kwargs.items()):
                if isinstance(value, str) and value.startswith('{'):
                    try:
                        params = json.loads(value)
                        kwargs.update(params)
                        print(f"[DEBUG] 解析kwargs中的JSON参数: {params}")
                    except json.JSONDecodeError:
                        pass  # 如果解析失败，继续使用原始参数
            
            
            # 支持中文操作名称映射
            operation_mapping = {
                "query_required_data": ["查询必需数据", "查询本地数据目录中与aldrin相关的微生物和基因数据"],
                "get_available_pollutants_summary": ["获取可用污染物摘要"],
                "get_organism_data": ["获取微生物数据", "查询微生物数据", "读取微生物数据"],
                "get_gene_data": ["获取基因数据", "查询基因数据", "读取基因数据"],
                "assess_data_integrity": ["评估数据完整性", "检查数据完整性"]
            }
            
            # 将中文操作名称映射到英文操作名称
            actual_operation = operation
            for eng_op, chi_ops in operation_mapping.items():
                if operation == eng_op or operation in chi_ops:
                    actual_operation = eng_op
                    break
            
            if actual_operation == "query_required_data":
                try:
                    # 从kwargs中获取查询文本
                    query_text = kwargs.get("query_text") or kwargs.get("query")
                    if not query_text:
                        # 尝试从pollutant_name中获取
                        query_text = kwargs.get("pollutant_name")
                    if not query_text:
                        raise ValueError("缺少查询文本参数")
                    data_type = kwargs.get("data_type", "both")
                    # 使用智能数据查询工具
                    smart_query = object.__getattribute__(self, 'smart_query')
                    return smart_query.query_related_data(query_text=query_text, data_type=data_type)
                except ValueError as e:
                    return {"status": "error", "message": str(e)}
                
            elif actual_operation == "get_available_pollutants_summary":
                result = self.get_available_pollutants_summary()
                return {"status": "success", "data": result}
                
            elif actual_operation == "get_organism_data":
                try:
                    # 从kwargs中获取污染物名称
                    pollutant_name = kwargs.get("pollutant_name") or kwargs.get("pollutant")
                    if not pollutant_name:
                        # 尝试从query_text中获取
                        pollutant_name = kwargs.get("query_text")
                    if not pollutant_name:
                        raise ValueError("缺少污染物名称参数")
                    sheet_name = kwargs.get("sheet", 0)
                    # 直接调用本地数据读取工具的方法
                    local_data_retriever = object.__getattribute__(self, 'local_data_retriever')
                    data = local_data_retriever.get_organism_data(pollutant_name, sheet_name)
                    if data is not None:
                        return {
                            "status": "success",
                            "data": {
                                "shape": data.shape,
                                "columns": list(data.columns),
                                "sample_data": data.head(5).to_dict('records')
                            },
                            "pollutant_name": pollutant_name
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"未找到污染物 '{pollutant_name}' 的微生物数据",
                            "pollutant_name": pollutant_name
                        }
                except ValueError as e:
                    return {"status": "error", "message": str(e)}
                
            elif actual_operation == "get_gene_data":
                try:
                    # 从kwargs中获取污染物名称
                    pollutant_name = kwargs.get("pollutant_name") or kwargs.get("pollutant")
                    if not pollutant_name:
                        # 尝试从query_text中获取
                        pollutant_name = kwargs.get("query_text")
                    if not pollutant_name:
                        raise ValueError("缺少污染物名称参数")
                    sheet_name = kwargs.get("sheet", 0)
                    # 直接调用本地数据读取工具的方法
                    local_data_retriever = object.__getattribute__(self, 'local_data_retriever')
                    data = local_data_retriever.get_gene_data(pollutant_name, sheet_name)
                    if data is not None:
                        return {
                            "status": "success",
                            "data": {
                                "shape": data.shape,
                                "columns": list(data.columns),
                                "sample_data": data.head(5).to_dict('records')
                            },
                            "pollutant_name": pollutant_name
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"未找到污染物 '{pollutant_name}' 的基因数据",
                            "pollutant_name": pollutant_name
                        }
                except ValueError as e:
                    return {"status": "error", "message": str(e)}
                
            elif actual_operation == "assess_data_integrity":
                try:
                    # 从kwargs中获取查询文本
                    query_text = kwargs.get("query_text") or kwargs.get("query")
                    if not query_text:
                        # 尝试从pollutant_name中获取
                        query_text = kwargs.get("pollutant_name")
                    if not query_text:
                        raise ValueError("缺少查询文本参数")
                    return self.assess_data_integrity(query_text)
                except ValueError as e:
                    return {"status": "error", "message": str(e)}
                
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
        smart_query = object.__getattribute__(self, 'smart_query')
        result = smart_query.query_related_data(query_text, data_type)
        
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
        local_data_retriever = object.__getattribute__(self, 'local_data_retriever')
        pollutants = local_data_retriever.list_available_pollutants()
        return {
            "genes_pollutants_count": len(pollutants["genes_pollutants"]),
            "organism_pollutants_count": len(pollutants["organism_pollutants"]),
            "genes_pollutants_sample": pollutants["genes_pollutants"][:5],  # 前5个示例
            "organism_pollutants_sample": pollutants["organism_pollutants"][:5]  # 前5个示例
        }
    
    def assess_data_integrity(self, query_text):
        """
        评估数据完整性，检查本地数据和外部数据的可用性
        
        Args:
            query_text (str): 查询文本
            
        Returns:
            dict: 包含数据完整性评估结果的字典
        """
        # 使用object.__getattribute__获取实例属性
        local_data_retriever = object.__getattribute__(self, 'local_data_retriever')
        smart_query = object.__getattribute__(self, 'smart_query')
        
        # 本地数据查询
        local_result = smart_query.query_related_data(query_text=query_text)
        
        # 外部数据查询
        external_result = smart_query.query_external_databases(query_text=query_text)
        
        # 评估数据完整性
        assessment = {
            "status": "success",
            "query_text": query_text,
            "local_data": {
                "available": local_result.get("status") == "success",
                "matched_pollutants": local_result.get("matched_pollutants", []),
                "gene_data_count": len(local_result.get("gene_data", {})),
                "organism_data_count": len(local_result.get("organism_data", {}))
            },
            "external_data": {
                "available": external_result.get("status") == "success",
                "kegg_data_count": len(external_result.get("kegg_data", {})),
                "envipath_data_count": len(external_result.get("envipath_data", {}))
            }
        }
        
        # 计算完整性评分
        local_score = 0
        if assessment["local_data"]["gene_data_count"] > 0:
            local_score += 50
        if assessment["local_data"]["organism_data_count"] > 0:
            local_score += 50
            
        external_score = 0
        if assessment["external_data"]["kegg_data_count"] > 0:
            external_score += 50
        if assessment["external_data"]["envipath_data_count"] > 0:
            external_score += 50
            
        assessment["data_integrity_score"] = (local_score + external_score) / 2
        assessment["recommendations"] = []
        
        # 根据数据完整性提供推荐
        if local_score < 100:
            assessment["recommendations"].append("本地数据不完整，建议补充相关基因或微生物数据")
        if external_score < 100:
            assessment["recommendations"].append("外部数据库数据不完整，建议查询更多相关条目")
        if assessment["data_integrity_score"] < 70:
            assessment["recommendations"].append("数据完整性较低，建议使用更具体的查询关键词")
            
        return assessment