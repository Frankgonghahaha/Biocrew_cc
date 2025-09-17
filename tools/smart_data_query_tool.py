#!/usr/bin/env python3
"""
智能数据查询工具
能够在Agent思考过程中自动识别和查询相关基因或微生物数据
"""

from crewai.tools import BaseTool
import pandas as pd
import re
from pathlib import Path
from tools.local_data_retriever import LocalDataRetriever
from typing import Dict, Any

class SmartDataQueryTool(BaseTool):
    name: str = "智能数据查询工具"
    description: str = "能够在Agent思考过程中自动识别和查询相关基因或微生物数据"
    
    def __init__(self, base_path="."):
        """
        初始化智能数据查询工具
        
        Args:
            base_path (str): 项目根路径，默认为当前目录
        """
        super().__init__()  # 调用父类构造函数
        # 使用object.__setattr__来设置实例属性，避免Pydantic验证错误
        object.__setattr__(self, 'data_retriever', LocalDataRetriever(base_path))
        object.__setattr__(self, 'base_path', base_path)
    
    def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的智能数据查询操作
        
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
            print(f"[DEBUG] SmartDataQueryTool._run 调用参数: {json.dumps(params_log, ensure_ascii=False)}")
            
            # 如果operation是JSON字符串，解析它
            if isinstance(operation, str) and operation.startswith('{'):
                import json
                try:
                    params = json.loads(operation)
                    operation = params.get('operation', operation)
                    # 合并参数
                    kwargs.update({k: v for k, v in params.items() if k != 'operation'})
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
                "query_related_data": ["查询相关数据", "识别与aldrin降解相关的微生物和基因"],
                "get_data_summary": ["获取数据摘要"],
                "query_external_databases": ["查询外部数据库", "查询KEGG和EnviPath数据库"]
            }
            
            # 将中文操作名称映射到英文操作名称
            actual_operation = operation
            for eng_op, chi_ops in operation_mapping.items():
                if operation == eng_op or operation in chi_ops:
                    actual_operation = eng_op
                    break
            
            # 直接执行操作
            if actual_operation == "query_related_data":
                query_text = kwargs.get("query_text") or kwargs.get("query")
                if not query_text:
                    # 尝试从pollutant_name中获取
                    query_text = kwargs.get("pollutant_name")
                data_type = kwargs.get("data_type", "both")
                return self.query_related_data(query_text, data_type)
            elif actual_operation == "get_data_summary":
                pollutant_name = kwargs.get("pollutant_name") or kwargs.get("pollutant")
                if not pollutant_name:
                    # 尝试从query_text中获取
                    pollutant_name = kwargs.get("query_text")
                data_type = kwargs.get("data_type", "both")
                return self.get_data_summary(pollutant_name, data_type)
            elif actual_operation == "query_external_databases":
                query_text = kwargs.get("query_text") or kwargs.get("query")
                if not query_text:
                    # 尝试从pollutant_name中获取
                    query_text = kwargs.get("pollutant_name")
                return self.query_external_databases(query_text)
            else:
                return {"status": "error", "message": f"不支持的操作: {actual_operation}"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
            }
    
    def _extract_pollutant_names(self, text):
        """
        从文本中提取可能的污染物名称
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: 提取到的污染物名称列表
        """
        # 检查输入文本是否为None
        if text is None:
            return []
        
        # 获取所有可用的污染物名称
        available_pollutants = self.data_retriever.list_available_pollutants()
        all_pollutants = (available_pollutants["genes_pollutants"] + 
                         available_pollutants["organism_pollutants"])
        
        # 清理污染物名称，移除文件后缀等
        clean_pollutants = []
        for pollutant in all_pollutants:
            # 移除可能的文件后缀
            clean_name = re.sub(r'_Genes$|_genes$|_Organism$|_organism$|_organisms$', '', pollutant)
            clean_pollutants.append(clean_name)
        
        # 在文本中查找匹配的污染物名称
        found_pollutants = []
        for pollutant in clean_pollutants:
            # 使用更灵活的匹配方式
            if (pollutant.lower() in text.lower() or 
                text.lower() in pollutant.lower() or
                self._fuzzy_match(pollutant, text)):
                # 避免重复添加
                if pollutant not in found_pollutants:
                    found_pollutants.append(pollutant)
        
        # 如果没有找到精确匹配，尝试更宽松的关键词匹配
        if not found_pollutants:
            # 定义常见污染物的关键词映射
            keyword_mapping = {
                'sulfamethoxazole': ['smx', 'sulfamethoxazole', '磺胺甲恶唑'],
                'endosulfan': ['endosulfan'],
                'pfos': ['pfos', 'perfluorooctane sulfonate'],
                'pfoa': ['pfoa', 'perfluorooctanoic acid'],
                'ddt': ['ddt', 'dichlorodiphenyltrichloroethane'],
                'pcbs': ['pcb', 'polychlorinated biphenyls'],
                'smx': ['smx', 'sulfamethoxazole', '磺胺甲恶唑']
            }
            
            text_lower = text.lower()
            for pollutant in clean_pollutants:
                pollutant_lower = pollutant.lower()
                # 检查是否有关键词匹配
                for key, keywords in keyword_mapping.items():
                    if key in pollutant_lower:
                        for keyword in keywords:
                            if keyword in text_lower:
                                if pollutant not in found_pollutants:
                                    found_pollutants.append(pollutant)
                                    break
        
        return found_pollutants
    
    def _fuzzy_match(self, pollutant_name, text):
        """
        模糊匹配污染物名称和文本
        
        Args:
            pollutant_name (str): 污染物名称
            text (str): 文本
            
        Returns:
            bool: 是否匹配
        """
        # 检查输入参数是否为None
        if pollutant_name is None or text is None:
            return False
            
        # 移除空格和特殊字符进行比较
        clean_pollutant = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', pollutant_name.lower())
        clean_text = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', text.lower())
        
        # 检查是否包含关系
        return (clean_pollutant in clean_text or 
                clean_text in clean_pollutant or
                # 检查是否有共同的子串（长度至少为3）
                self._has_common_substring(clean_pollutant, clean_text, min_length=3))
    
    def _has_common_substring(self, str1, str2, min_length=3):
        """
        检查两个字符串是否有共同的子串
        
        Args:
            str1 (str): 第一个字符串
            str2 (str): 第二个字符串
            min_length (int): 最小子串长度
            
        Returns:
            bool: 是否有共同子串
        """
        # 简单的子串匹配
        for i in range(len(str1) - min_length + 1):
            substring = str1[i:i + min_length]
            if substring in str2:
                return True
        return False
    
    def query_related_data(self, query_text, data_type="both", sheet_name=0):
        """
        根据查询文本自动识别并查询相关数据
        
        Args:
            query_text (str): 查询文本，可以是用户输入或Agent的思考内容
            data_type (str): 数据类型，"gene"、"organism" 或 "both"
            sheet_name (str or int): 工作表名称或索引，默认为0
            
        Returns:
            dict: 包含查询结果的字典
        """
        # 提取污染物名称
        pollutant_names = self._extract_pollutant_names(query_text)
        
        if not pollutant_names:
            return {
                "status": "no_match",
                "message": "未在文本中找到匹配的污染物名称",
                "data": None
            }
        
        results = {
            "status": "success",
            "matched_pollutants": pollutant_names,
            "gene_data": {},
            "organism_data": {}
        }
        
        # 查询基因数据
        if data_type in ["gene", "both"]:
            for pollutant in pollutant_names:
                try:
                    # 先检查文件是否存在
                    file_path = self.data_retriever._find_file_by_pollutant(
                        self.data_retriever.genes_path, pollutant)
                    if file_path is not None:
                        gene_data = self.data_retriever.get_gene_data(pollutant, sheet_name)
                        if gene_data is not None:
                            results["gene_data"][pollutant] = {
                                "shape": gene_data.shape,
                                "columns": list(gene_data.columns)[:10],  # 只显示前10列
                                "sample_data": gene_data.head(3).to_dict('records')  # 显示前3行示例
                            }
                        else:
                            results["gene_data"][pollutant] = {
                                "error": "无法读取基因数据"
                            }
                    else:
                        # 文件不存在，跳过
                        pass
                except Exception as e:
                    results["gene_data"][pollutant] = {
                        "error": str(e)
                    }
        
        # 查询微生物数据
        if data_type in ["organism", "both"]:
            for pollutant in pollutant_names:
                try:
                    # 先检查文件是否存在
                    file_path = self.data_retriever._find_file_by_pollutant(
                        self.data_retriever.organism_path, pollutant)
                    if file_path is not None:
                        organism_data = self.data_retriever.get_organism_data(pollutant, sheet_name)
                        if organism_data is not None:
                            results["organism_data"][pollutant] = {
                                "shape": organism_data.shape,
                                "columns": list(organism_data.columns)[:10],  # 只显示前10列
                                "sample_data": organism_data.head(3).to_dict('records')  # 显示前3行示例
                            }
                        else:
                            results["organism_data"][pollutant] = {
                                "error": "无法读取微生物数据"
                            }
                    else:
                        # 文件不存在，跳过
                        pass
                except Exception as e:
                    results["organism_data"][pollutant] = {
                        "error": str(e)
                    }
        
        # 如果本地数据查询结果不完整，自动查询外部数据库获取补充信息
        if results.get("status") == "success":
            # 检查是否有数据缺失
            has_gene_data = len(results.get("gene_data", {})) > 0
            has_organism_data = len(results.get("organism_data", {})) > 0
            
            # 对于某些特定污染物（如Aldrin），可能只有微生物数据而没有基因数据，这是正常情况
            # 在这种情况下，仍然查询外部数据库以获取补充信息
            if not has_gene_data or not has_organism_data:
                external_results = self.query_external_databases(query_text)
                results["external_data"] = external_results
                
            # 添加数据完整性信息
            results["data_completeness"] = {
                "has_gene_data": has_gene_data,
                "has_organism_data": has_organism_data,
                "total_pollutants_matched": len(pollutant_names),
                "gene_data_pollutants_count": len(results.get("gene_data", {})),
                "organism_data_pollutants_count": len(results.get("organism_data", {}))
            }
        
        return results
    
    def query_all_sheets_for_pollutant(self, pollutant_name, data_type="both"):
        """
        查询指定污染物的所有工作表数据
        
        Args:
            pollutant_name (str): 污染物名称
            data_type (str): 数据类型，"gene"、"organism" 或 "both"
            
        Returns:
            dict: 包含所有工作表数据的字典
        """
        results = {
            "status": "success",
            "pollutant": pollutant_name,
            "gene_sheets": {},
            "organism_sheets": {}
        }
        
        # 查询基因数据的所有工作表
        if data_type in ["gene", "both"]:
            try:
                all_gene_sheets = self.data_retriever.get_gene_data_all_sheets(pollutant_name)
                if all_gene_sheets is not None:
                    for sheet_name, df in all_gene_sheets.items():
                        results["gene_sheets"][sheet_name] = {
                            "shape": df.shape,
                            "columns": list(df.columns)[:10],
                            "sample_data": df.head(2).to_dict('records')
                        }
            except Exception as e:
                results["gene_sheets"]["error"] = str(e)
        
        # 查询微生物数据的所有工作表
        if data_type in ["organism", "both"]:
            try:
                all_organism_sheets = self.data_retriever.get_organism_data_all_sheets(pollutant_name)
                if all_organism_sheets is not None:
                    for sheet_name, df in all_organism_sheets.items():
                        results["organism_sheets"][sheet_name] = {
                            "shape": df.shape,
                            "columns": list(df.columns)[:10],
                            "sample_data": df.head(2).to_dict('records')
                        }
            except Exception as e:
                results["organism_sheets"]["error"] = str(e)
        
        return results
    
    def get_data_summary(self, pollutant_name, data_type="both"):
        """
        获取指定污染物的数据摘要
        
        Args:
            pollutant_name (str): 污染物名称
            data_type (str): 数据类型，"gene"、"organism" 或 "both"
            
        Returns:
            dict: 数据摘要信息
        """
        summary = {
            "pollutant": pollutant_name,
            "gene_summary": None,
            "organism_summary": None
        }
        
        # 获取基因数据摘要
        if data_type in ["gene", "both"]:
            try:
                gene_data = self.data_retriever.get_gene_data(pollutant_name)
                if gene_data is not None:
                    summary["gene_summary"] = {
                        "shape": gene_data.shape,
                        "columns_count": len(gene_data.columns),
                        "rows_count": len(gene_data),
                        "sheet_names": self.data_retriever.list_sheet_names(pollutant_name, "gene")
                    }
            except Exception as e:
                summary["gene_summary"] = {"error": str(e)}
        
        # 获取微生物数据摘要
        if data_type in ["organism", "both"]:
            try:
                organism_data = self.data_retriever.get_organism_data(pollutant_name)
                if organism_data is not None:
                    summary["organism_summary"] = {
                        "shape": organism_data.shape,
                        "columns_count": len(organism_data.columns),
                        "rows_count": len(organism_data),
                        "sheet_names": self.data_retriever.list_sheet_names(pollutant_name, "organism")
                    }
            except Exception as e:
                summary["organism_summary"] = {"error": str(e)}
        
        return summary
    
    def query_external_databases(self, query_text):
        """
        查询外部数据库(KEGG和EnviPath)获取补充信息
        
        Args:
            query_text (str): 查询文本
            
        Returns:
            dict: 包含外部数据库查询结果的字典
        """
        # 导入外部数据库工具
        from tools.kegg_tool import KeggTool
        from tools.envipath_tool import EnviPathTool
        
        # 创建外部数据库工具实例
        kegg_tool = KeggTool()
        envipath_tool = EnviPathTool()
        
        results = {
            "status": "success",
            "query_text": query_text,
            "kegg_data": {},
            "envipath_data": {}
        }
        
        # 提取污染物名称用于外部数据库查询
        pollutant_names = self._extract_pollutant_names(query_text)
        search_keywords = pollutant_names if pollutant_names else [query_text]
        
        try:
            # 查询KEGG数据库
            kegg_results = {}
            for keyword in search_keywords:
                # 查询相关基因
                genes_result = kegg_tool.find_entries("genes", keyword)
                if genes_result.get("status") == "success" and genes_result.get("count", 0) > 0:
                    kegg_results[f"{keyword}_genes"] = {
                        "count": genes_result["count"],
                        "sample_data": genes_result["data"][:5]  # 只取前5个结果
                    }
                
                # 查询相关pathway
                pathway_result = kegg_tool.find_entries("pathway", keyword)
                if pathway_result.get("status") == "success" and pathway_result.get("count", 0) > 0:
                    kegg_results[f"{keyword}_pathway"] = {
                        "count": pathway_result["count"],
                        "sample_data": pathway_result["data"][:5]  # 只取前5个结果
                    }
            
            results["kegg_data"] = kegg_results
            
            # 查询EnviPath数据库
            envipath_results = {}
            for keyword in search_keywords:
                # 搜索化合物
                compound_result = envipath_tool.search_compound(keyword)
                if compound_result.get("status") == "success":
                    envipath_results[f"{keyword}_compound"] = {
                        "query": compound_result.get("query", keyword),
                        "status": "success"
                    }
                
                # 根据关键词搜索pathway
                pathway_result = envipath_tool.search_pathways_by_keyword(keyword)
                if pathway_result.get("status") == "success":
                    envipath_results[f"{keyword}_pathway"] = {
                        "keyword": pathway_result.get("keyword", keyword),
                        "status": "success"
                    }
            
            results["envipath_data"] = envipath_results
            
        except Exception as e:
            results["status"] = "partial_success"  # 即使部分查询失败，也返回已获取的数据
            results["error"] = str(e)
        
        return results

# 使用示例
if __name__ == "__main__":
    # 创建智能数据查询工具实例
    smart_query = SmartDataQueryTool()
    
    # 示例1: 根据用户输入查询相关数据
    user_input = "我们需要处理Alpha-hexachlorocyclohexane污染问题"
    print("用户输入:", user_input)
    result = smart_query.query_related_data(user_input)
    print("查询结果:")
    print(f"  匹配的污染物: {result.get('matched_pollutants', [])}")
    print(f"  基因数据项数: {len(result.get('gene_data', {}))}")
    print(f"  微生物数据项数: {len(result.get('organism_data', {}))}")
    
    # 示例2: 获取数据摘要
    print("\n数据摘要:")
    summary = smart_query.get_data_summary("Alpha-hexachlorocyclohexane")
    if summary["gene_summary"]:
        print(f"  基因数据: {summary['gene_summary']['shape']}")
    if summary["organism_summary"]:
        print(f"  微生物数据: {summary['organism_summary']['shape']}")
