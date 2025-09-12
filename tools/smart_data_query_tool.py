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
            if operation == "query_related_data":
                query_text = kwargs.get("query_text")
                data_type = kwargs.get("data_type", "both")
                sheet_name = kwargs.get("sheet_name", 0)
                if not query_text:
                    return {"status": "error", "message": "缺少查询文本参数"}
                return self.query_related_data(query_text, data_type, sheet_name)
                
            elif operation == "get_data_summary":
                pollutant_name = kwargs.get("pollutant_name")
                data_type = kwargs.get("data_type", "both")
                if not pollutant_name:
                    return {"status": "error", "message": "缺少污染物名称参数"}
                return self.get_data_summary(pollutant_name, data_type)
                
            else:
                return {"status": "error", "message": f"不支持的操作: {operation}"}
                
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
                    gene_data = self.data_retriever.get_gene_data(pollutant, sheet_name)
                    if gene_data is not None:
                        results["gene_data"][pollutant] = {
                            "shape": gene_data.shape,
                            "columns": list(gene_data.columns)[:10],  # 只显示前10列
                            "sample_data": gene_data.head(3).to_dict('records')  # 显示前3行示例
                        }
                except Exception as e:
                    results["gene_data"][pollutant] = {
                        "error": str(e)
                    }
        
        # 查询微生物数据
        if data_type in ["organism", "both"]:
            for pollutant in pollutant_names:
                try:
                    organism_data = self.data_retriever.get_organism_data(pollutant, sheet_name)
                    if organism_data is not None:
                        results["organism_data"][pollutant] = {
                            "shape": organism_data.shape,
                            "columns": list(organism_data.columns)[:10],  # 只显示前10列
                            "sample_data": organism_data.head(3).to_dict('records')  # 显示前3行示例
                        }
                except Exception as e:
                    results["organism_data"][pollutant] = {
                        "error": str(e)
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
