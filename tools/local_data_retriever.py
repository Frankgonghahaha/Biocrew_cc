#!/usr/bin/env python3
"""
本地数据读取工具类
用于从data/Genes和data/Organism目录中获取表格数据
"""

from crewai.tools import BaseTool
import os
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any

class LocalDataRetriever(BaseTool):
    name: str = "本地数据读取工具"
    description: str = "用于从data/Genes和data/Organism目录中获取表格数据"
    
    def __init__(self, base_path="."):
        """
        初始化本地数据读取工具
        
        Args:
            base_path (str): 项目根路径，默认为当前目录
        """
        super().__init__()  # 调用父类构造函数
        # 使用object.__setattr__来设置实例属性，避免Pydantic验证错误
        object.__setattr__(self, 'base_path', Path(base_path))
        object.__setattr__(self, 'genes_path', Path(base_path) / "data" / "Genes")
        object.__setattr__(self, 'organism_path', Path(base_path) / "data" / "Organism")
        
        # 验证路径是否存在
        genes_path = object.__getattribute__(self, 'genes_path')
        organism_path = object.__getattribute__(self, 'organism_path')
        if not genes_path.exists():
            raise FileNotFoundError(f"基因数据路径不存在: {genes_path}")
        if not organism_path.exists():
            raise FileNotFoundError(f"微生物数据路径不存在: {organism_path}")
    
    def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的本地数据读取操作
        
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
            print(f"[DEBUG] LocalDataRetriever._run 调用参数: {json.dumps(params_log, ensure_ascii=False)}")
            
            # 如果operation是JSON字符串，解析它
            if isinstance(operation, str) and operation.startswith('{'):
                import json
                try:
                    params = json.loads(operation)
                    operation = params.get('operation', operation)
                    # 合并参数，确保pollutant_name也被正确处理
                    for k, v in params.items():
                        if k != 'operation':
                            kwargs[k] = v
                    print(f"[DEBUG] 解析JSON后的参数: {kwargs}")
                except json.JSONDecodeError:
                    pass  # 如果解析失败，继续使用原始参数
            
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
                "get_gene_data": ["获取基因数据", "查询基因数据", "读取基因数据"],
                "get_organism_data": ["获取微生物数据", "查询微生物数据", "读取微生物数据", "查询data/Organism目录下与aldrin相关的微生物数据"],
                "list_available_pollutants": ["列出可用污染物", "查询可用污染物"],
                "list_sheet_names": ["列出工作表名称", "获取工作表名称"]
            }
            
            # 将中文操作名称映射到英文操作名称
            actual_operation = operation
            for eng_op, chi_ops in operation_mapping.items():
                if operation == eng_op or operation in chi_ops:
                    actual_operation = eng_op
                    break
            
            if actual_operation == "get_gene_data":
                try:
                    # 从kwargs中获取污染物名称
                    pollutant_name = kwargs.get("pollutant_name") or kwargs.get("pollutant")
                    if not pollutant_name:
                        # 尝试从query_text中获取
                        pollutant_name = kwargs.get("query_text")
                    if not pollutant_name:
                        raise ValueError("缺少污染物名称参数")
                    sheet_name = kwargs.get("sheet", 0)
                    data = self.get_gene_data(pollutant_name, sheet_name)
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
                
            elif actual_operation == "get_organism_data":
                try:
                    print(f"[DEBUG] get_organism_data - kwargs: {kwargs}")
                    # 从kwargs中获取污染物名称
                    pollutant_name = kwargs.get("pollutant_name") or kwargs.get("pollutant")
                    if not pollutant_name:
                        # 尝试从query_text中获取
                        pollutant_name = kwargs.get("query_text")
                    if not pollutant_name:
                        raise ValueError("缺少污染物名称参数")
                    print(f"[DEBUG] get_organism_data - 获取到的pollutant_name: {pollutant_name}")
                    sheet_name = kwargs.get("sheet", 0)
                    data = self.get_organism_data(pollutant_name, sheet_name)
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
                    print(f"[DEBUG] get_organism_data - ValueError: {e}")
                    return {"status": "error", "message": str(e)}
                
            elif actual_operation == "list_available_pollutants":
                result = self.list_available_pollutants()
                return {"status": "success", "data": result}
                
            elif actual_operation == "list_sheet_names":
                try:
                    # 从kwargs中获取污染物名称
                    pollutant_name = kwargs.get("pollutant_name") or kwargs.get("pollutant")
                    if not pollutant_name:
                        # 尝试从query_text中获取
                        pollutant_name = kwargs.get("query_text")
                    if not pollutant_name:
                        raise ValueError("缺少污染物名称参数")
                    data_type = kwargs.get("data_type", "gene")
                    return self.list_sheet_names(pollutant_name, data_type)
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
    
    def _normalize_filename(self, filename):
        """
        标准化文件名，处理特殊字符和空格
        
        Args:
            filename (str): 原始文件名
            
        Returns:
            str: 标准化后的文件名
        """
        # 移除末尾的:Zone.Identifier（Windows文件系统标记）
        if ":Zone.Identifier" in filename:
            filename = filename.replace(":Zone.Identifier", "")
        return filename
    
    def _find_file_by_pollutant(self, directory, pollutant_name):
        """
        根据污染物名称查找对应的文件
        
        Args:
            directory (Path): 数据目录路径
            pollutant_name (str): 污染物名称
            
        Returns:
            Path: 找到的文件路径，如果未找到返回None
        """
        # 清理污染物名称，移除特殊字符
        clean_name = re.sub(r'[^\w\s\u4e00-\u9fff\-_()]', '', pollutant_name)
        
        # 遍历目录中的所有文件
        for file_path in directory.iterdir():
            if file_path.is_file():
                filename = self._normalize_filename(file_path.name)
                # 检查文件名是否包含污染物名称（不区分大小写）
                if clean_name.lower() in filename.lower():
                    return file_path
        
        # 如果精确匹配失败，尝试模糊匹配
        for file_path in directory.iterdir():
            if file_path.is_file():
                filename = self._normalize_filename(file_path.name)
                # 移除文件扩展名进行匹配
                name_without_ext = filename.rsplit('.', 1)[0]
                if clean_name.lower() in name_without_ext.lower() or name_without_ext.lower() in clean_name.lower():
                    return file_path
        
        return None
    
    def get_gene_data(self, pollutant_name, sheet_name=0):
        """
        根据污染物名称获取基因数据
        
        Args:
            pollutant_name (str): 污染物名称
            sheet_name (str or int): 工作表名称或索引，默认为0（第一个工作表）
            
        Returns:
            pandas.DataFrame: 基因数据，如果未找到返回None
        """
        try:
            file_path = self._find_file_by_pollutant(self.genes_path, pollutant_name)
            if file_path is None:
                raise FileNotFoundError(f"未找到污染物 '{pollutant_name}' 对应的基因数据文件")
            
            # 读取Excel文件的指定工作表，指定engine参数
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            elif file_path.suffix.lower() == '.xls':
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df
        except Exception as e:
            print(f"读取基因数据时出错: {e}")
            return None
    
    def get_organism_data(self, pollutant_name, sheet_name=0):
        """
        根据污染物名称获取微生物数据
        
        Args:
            pollutant_name (str): 污染物名称
            sheet_name (str or int): 工作表名称或索引，默认为0（第一个工作表）
            
        Returns:
            pandas.DataFrame: 微生物数据，如果未找到返回None
        """
        try:
            file_path = self._find_file_by_pollutant(self.organism_path, pollutant_name)
            if file_path is None:
                raise FileNotFoundError(f"未找到污染物 '{pollutant_name}' 对应的微生物数据文件")
            
            # 读取Excel文件的指定工作表，指定engine参数
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            elif file_path.suffix.lower() == '.xls':
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df
        except Exception as e:
            print(f"读取微生物数据时出错: {e}")
            return None
    
    def get_gene_data_all_sheets(self, pollutant_name):
        """
        根据污染物名称获取基因数据（所有工作表）
        
        Args:
            pollutant_name (str): 污染物名称
            
        Returns:
            dict: 包含所有工作表数据的字典，键为工作表名称，值为DataFrame
        """
        try:
            file_path = self._find_file_by_pollutant(self.genes_path, pollutant_name)
            if file_path is None:
                raise FileNotFoundError(f"未找到污染物 '{pollutant_name}' 对应的基因数据文件")
            
            # 读取Excel文件的所有工作表，指定engine参数
            if file_path.suffix.lower() == '.xlsx':
                all_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
            elif file_path.suffix.lower() == '.xls':
                all_sheets = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
            else:
                all_sheets = pd.read_excel(file_path, sheet_name=None)
            return all_sheets
        except Exception as e:
            print(f"读取基因数据时出错: {e}")
            return None
    
    def get_organism_data_all_sheets(self, pollutant_name):
        """
        根据污染物名称获取微生物数据（所有工作表）
        
        Args:
            pollutant_name (str): 污染物名称
            
        Returns:
            dict: 包含所有工作表数据的字典，键为工作表名称，值为DataFrame
        """
        try:
            file_path = self._find_file_by_pollutant(self.organism_path, pollutant_name)
            if file_path is None:
                raise FileNotFoundError(f"未找到污染物 '{pollutant_name}' 对应的微生物数据文件")
            
            # 读取Excel文件的所有工作表，指定engine参数
            if file_path.suffix.lower() == '.xlsx':
                all_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
            elif file_path.suffix.lower() == '.xls':
                all_sheets = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
            else:
                all_sheets = pd.read_excel(file_path, sheet_name=None)
            return all_sheets
        except Exception as e:
            print(f"读取微生物数据时出错: {e}")
            return None
    
    def list_sheet_names(self, pollutant_name, data_type="gene"):
        """
        列出指定数据文件的所有工作表名称
        
        Args:
            pollutant_name (str): 污染物名称
            data_type (str): 数据类型，"gene" 或 "organism"
            
        Returns:
            list: 工作表名称列表
        """
        try:
            if data_type == "gene":
                file_path = self._find_file_by_pollutant(self.genes_path, pollutant_name)
            else:
                file_path = self._find_file_by_pollutant(self.organism_path, pollutant_name)
            
            if file_path is None:
                raise FileNotFoundError(f"未找到污染物 '{pollutant_name}' 对应的数据文件")
            
            # 获取所有工作表名称，指定engine参数
            if file_path.suffix.lower() == '.xlsx':
                sheet_names = pd.ExcelFile(file_path, engine='openpyxl').sheet_names
            elif file_path.suffix.lower() == '.xls':
                sheet_names = pd.ExcelFile(file_path, engine='xlrd').sheet_names
            else:
                sheet_names = pd.ExcelFile(file_path).sheet_names
            return sheet_names
        except Exception as e:
            print(f"获取工作表名称时出错: {e}")
            return None
    
    def list_available_pollutants(self):
        """
        列出所有可用的污染物名称
        
        Returns:
            dict: 包含基因数据和微生物数据污染物名称的字典
        """
        genes_pollutants = []
        organism_pollutants = []
        
        # 获取基因数据中的污染物名称
        if self.genes_path.exists():
            for file_path in self.genes_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.xlsx', '.xls']:
                    filename = self._normalize_filename(file_path.name)
                    # 移除文件扩展名
                    name_without_ext = filename.rsplit('.', 1)[0]
                    genes_pollutants.append(name_without_ext)
        
        # 获取微生物数据中的污染物名称
        if self.organism_path.exists():
            for file_path in self.organism_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.xlsx', '.xls']:
                    filename = self._normalize_filename(file_path.name)
                    # 移除文件扩展名
                    name_without_ext = filename.rsplit('.', 1)[0]
                    organism_pollutants.append(name_without_ext)
        
        return {
            "genes_pollutants": genes_pollutants,
            "organism_pollutants": organism_pollutants
        }
    
    def search_files_by_keyword(self, keyword):
        """
        根据关键词搜索相关数据文件
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            dict: 包含匹配文件的字典
        """
        matching_genes = []
        matching_organisms = []
        
        # 在基因数据中搜索
        if self.genes_path.exists():
            for file_path in self.genes_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.xlsx', '.xls']:
                    filename = self._normalize_filename(file_path.name)
                    if keyword.lower() in filename.lower():
                        matching_genes.append(filename)
        
        # 在微生物数据中搜索
        if self.organism_path.exists():
            for file_path in self.organism_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.xlsx', '.xls']:
                    filename = self._normalize_filename(file_path.name)
                    if keyword.lower() in filename.lower():
                        matching_organisms.append(filename)
        
        return {
            "matching_genes": matching_genes,
            "matching_organisms": matching_organisms
        }

# 使用示例
if __name__ == "__main__":
    # 创建数据读取工具实例
    data_retriever = LocalDataRetriever()
    
    # 列出所有可用的污染物
    pollutants = data_retriever.list_available_pollutants()
    print("可用的基因数据污染物:")
    for pollutant in pollutants["genes_pollutants"][:5]:  # 只显示前5个
        print(f"  - {pollutant}")
    
    print("\n可用的微生物数据污染物:")
    for pollutant in pollutants["organism_pollutants"][:5]:  # 只显示前5个
        print(f"  - {pollutant}")
    
    # 示例：获取特定污染物的数据（如果文件存在）
    # gene_data = data_retriever.get_gene_data("Alpha-hexachlorocyclohexane")
    # if gene_data is not None:
    #     print("\n基因数据示例:")
    #     print(gene_data.head())
    
    # organism_data = data_retriever.get_organism_data("Alpha-hexachlorocyclohexane")
    # if organism_data is not None:
    #     print("\n微生物数据示例:")
    #     print(organism_data.head())
