#!/usr/bin/env python3
"""
统一数据访问工具
整合本地数据库和外部数据库的数据访问功能
"""

from crewai.tools import BaseTool
from config.config import Config
from sqlalchemy import create_engine, text
from typing import Dict, Any, List, Optional
import requests
import json

class UnifiedDataTool(BaseTool):
    name: str = "统一数据访问工具"
    description: str = "整合本地数据库和外部数据库的数据访问功能，提供一站式数据查询服务"
    
    def __init__(self):
        """
        初始化统一数据访问工具
        """
        super().__init__()
        # 初始化数据库连接
        object.__setattr__(self, 'db_engine', self._get_database_connection())
        
    def _get_database_connection(self):
        """
        创建数据库连接
        """
        db_type = Config.DB_TYPE
        db_host = Config.DB_HOST
        db_port = Config.DB_PORT
        db_name = Config.DB_NAME
        db_user = Config.DB_USER
        db_password = Config.DB_PASSWORD
        
        if db_type == 'postgresql':
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type == 'mysql':
            database_url = f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        engine = create_engine(database_url)
        return engine
    
    def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的数据访问操作
        
        Args:
            operation (str): 要执行的操作名称
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            # 支持的操作映射
            operation_mapping = {
                "query_pollutant_data": ["查询污染物数据", "获取aldrin相关的基因和微生物数据"],
                "query_gene_data": ["查询基因数据"],
                "query_organism_data": ["查询微生物数据"],
                "query_external_data": ["查询外部数据库数据", "查询KEGG和EnviPath数据库"],
                "get_pollutant_summary": ["获取污染物摘要"],
                "search_pollutants": ["搜索污染物"]
            }
            
            # 将操作名称标准化
            actual_operation = self._normalize_operation(operation, operation_mapping)
            
            # 执行相应操作
            if actual_operation == "query_pollutant_data":
                return self.query_pollutant_data(**kwargs)
            elif actual_operation == "query_gene_data":
                return self.query_gene_data(**kwargs)
            elif actual_operation == "query_organism_data":
                return self.query_organism_data(**kwargs)
            elif actual_operation == "query_external_data":
                return self.query_external_data(**kwargs)
            elif actual_operation == "get_pollutant_summary":
                return self.get_pollutant_summary(**kwargs)
            elif actual_operation == "search_pollutants":
                return self.search_pollutants(**kwargs)
            else:
                return {"status": "error", "message": f"不支持的操作: {actual_operation}"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
            }
    
    def _normalize_operation(self, operation: str, mapping: Dict) -> str:
        """
        标准化操作名称
        
        Args:
            operation (str): 原始操作名称
            mapping (dict): 操作映射表
            
        Returns:
            str: 标准化后的操作名称
        """
        # 直接匹配
        if operation in mapping:
            return operation
            
        # 中文映射匹配
        for eng_op, chi_ops in mapping.items():
            if operation in chi_ops:
                return eng_op
                
        return operation
    
    def query_pollutant_data(self, pollutant_name: str, data_type: str = "both") -> Dict[Any, Any]:
        """
        查询指定污染物的所有相关数据
        
        Args:
            pollutant_name (str): 污染物名称
            data_type (str): 数据类型 ("gene", "organism", "both")
            
        Returns:
            dict: 查询结果
        """
        try:
            results = {
                "status": "success",
                "pollutant_name": pollutant_name,
                "gene_data": None,
                "organism_data": None
            }
            
            # 查询基因数据
            if data_type in ["gene", "both"]:
                gene_data = self._query_gene_data_from_db(pollutant_name)
                if gene_data:
                    results["gene_data"] = gene_data
            
            # 查询微生物数据
            if data_type in ["organism", "both"]:
                organism_data = self._query_organism_data_from_db(pollutant_name)
                if organism_data:
                    results["organism_data"] = organism_data
            
            return results
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询污染物数据时出错: {str(e)}",
                "pollutant_name": pollutant_name
            }
    
    def _query_gene_data_from_db(self, pollutant_name: str) -> Optional[List[Dict]]:
        """
        从数据库查询基因数据
        
        Args:
            pollutant_name (str): 污染物名称
            
        Returns:
            list: 基因数据列表
        """
        try:
            with self.db_engine.connect() as connection:
                # 查询基因数据
                result = connection.execute(text("""
                    SELECT *
                    FROM genes_data
                    WHERE pollutant_name = :pollutant_name
                    LIMIT 100
                """), {"pollutant_name": pollutant_name.lower().replace(' ', '_')})
                
                # 转换为字典列表
                columns = result.keys()
                rows = result.fetchall()
                
                gene_data = []
                for row in rows:
                    gene_data.append(dict(zip(columns, row)))
                
                return gene_data if gene_data else None
                
        except Exception as e:
            print(f"查询基因数据时出错: {e}")
            return None
    
    def _query_organism_data_from_db(self, pollutant_name: str) -> Optional[List[Dict]]:
        """
        从数据库查询微生物数据
        
        Args:
            pollutant_name (str): 污染物名称
            
        Returns:
            list: 微生物数据列表
        """
        try:
            with self.db_engine.connect() as connection:
                # 查询微生物数据
                result = connection.execute(text("""
                    SELECT *
                    FROM organism_data
                    WHERE pollutant_name = :pollutant_name
                    LIMIT 100
                """), {"pollutant_name": pollutant_name.lower().replace(' ', '_')})
                
                # 转换为字典列表
                columns = result.keys()
                rows = result.fetchall()
                
                organism_data = []
                for row in rows:
                    organism_data.append(dict(zip(columns, row)))
                
                return organism_data if organism_data else None
                
        except Exception as e:
            print(f"查询微生物数据时出错: {e}")
            return None
    
    def query_gene_data(self, pollutant_name: str, enzyme_type: Optional[str] = None) -> Dict[Any, Any]:
        """
        查询基因数据
        
        Args:
            pollutant_name (str): 污染物名称
            enzyme_type (str, optional): 酶类型
            
        Returns:
            dict: 基因数据
        """
        try:
            with self.db_engine.connect() as connection:
                if enzyme_type:
                    result = connection.execute(text("""
                        SELECT *
                        FROM genes_data
                        WHERE pollutant_name = :pollutant_name
                        AND enzyme_type = :enzyme_type
                        LIMIT 50
                    """), {
                        "pollutant_name": pollutant_name.lower().replace(' ', '_'),
                        "enzyme_type": enzyme_type
                    })
                else:
                    result = connection.execute(text("""
                        SELECT *
                        FROM genes_data
                        WHERE pollutant_name = :pollutant_name
                        LIMIT 50
                    """), {"pollutant_name": pollutant_name.lower().replace(' ', '_')})
                
                # 转换为字典列表
                columns = result.keys()
                rows = result.fetchall()
                
                gene_data = []
                for row in rows:
                    gene_data.append(dict(zip(columns, row)))
                
                return {
                    "status": "success",
                    "data": gene_data,
                    "count": len(gene_data)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询基因数据时出错: {str(e)}",
                "pollutant_name": pollutant_name
            }
    
    def query_organism_data(self, pollutant_name: str, organism_type: Optional[str] = None) -> Dict[Any, Any]:
        """
        查询微生物数据
        
        Args:
            pollutant_name (str): 污染物名称
            organism_type (str, optional): 微生物类型
            
        Returns:
            dict: 微生物数据
        """
        try:
            with self.db_engine.connect() as connection:
                if organism_type:
                    result = connection.execute(text("""
                        SELECT *
                        FROM organism_data
                        WHERE pollutant_name = :pollutant_name
                        AND organism_type = :organism_type
                        LIMIT 50
                    """), {
                        "pollutant_name": pollutant_name.lower().replace(' ', '_'),
                        "organism_type": organism_type
                    })
                else:
                    result = connection.execute(text("""
                        SELECT *
                        FROM organism_data
                        WHERE pollutant_name = :pollutant_name
                        LIMIT 50
                    """), {"pollutant_name": pollutant_name.lower().replace(' ', '_')})
                
                # 转换为字典列表
                columns = result.keys()
                rows = result.fetchall()
                
                organism_data = []
                for row in rows:
                    organism_data.append(dict(zip(columns, row)))
                
                return {
                    "status": "success",
                    "data": organism_data,
                    "count": len(organism_data)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询微生物数据时出错: {str(e)}",
                "pollutant_name": pollutant_name
            }
    
    def query_external_data(self, query_text: str) -> Dict[Any, Any]:
        """
        查询外部数据库数据
        
        Args:
            query_text (str): 查询文本
            
        Returns:
            dict: 外部数据库查询结果
        """
        results = {
            "status": "success",
            "query_text": query_text,
            "kegg_data": {},
            "envipath_data": {}
        }
        
        try:
            # 查询KEGG数据
            kegg_results = self._query_kegg_data(query_text)
            results["kegg_data"] = kegg_results
            
            # 查询EnviPath数据
            envipath_results = self._query_envipath_data(query_text)
            results["envipath_data"] = envipath_results
            
        except Exception as e:
            results["status"] = "partial_success"
            results["error"] = str(e)
        
        return results
    
    def _query_kegg_data(self, query_text: str) -> Dict[Any, Any]:
        """
        查询KEGG数据库数据
        
        Args:
            query_text (str): 查询文本
            
        Returns:
            dict: KEGG数据
        """
        try:
            # 这里可以实现实际的KEGG API调用
            # 为简化示例，返回模拟数据
            return {
                "status": "success",
                "query": query_text,
                "pathways": [],
                "genes": []
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询KEGG数据时出错: {str(e)}"
            }
    
    def _query_envipath_data(self, query_text: str) -> Dict[Any, Any]:
        """
        查询EnviPath数据库数据
        
        Args:
            query_text (str): 查询文本
            
        Returns:
            dict: EnviPath数据
        """
        try:
            # 这里可以实现实际的EnviPath API调用
            # 为简化示例，返回模拟数据
            return {
                "status": "success",
                "query": query_text,
                "compounds": [],
                "pathways": []
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"查询EnviPath数据时出错: {str(e)}"
            }
    
    def get_pollutant_summary(self, pollutant_name: str) -> Dict[Any, Any]:
        """
        获取污染物数据摘要
        
        Args:
            pollutant_name (str): 污染物名称
            
        Returns:
            dict: 数据摘要
        """
        try:
            with self.db_engine.connect() as connection:
                # 获取基因数据统计
                gene_result = connection.execute(text("""
                    SELECT COUNT(*) as count, COUNT(DISTINCT enzyme_type) as enzyme_types
                    FROM genes_data
                    WHERE pollutant_name = :pollutant_name
                """), {"pollutant_name": pollutant_name.lower().replace(' ', '_')})
                
                gene_stats = gene_result.fetchone()
                
                # 获取微生物数据统计
                organism_result = connection.execute(text("""
                    SELECT COUNT(*) as count, COUNT(DISTINCT organism_type) as organism_types
                    FROM organism_data
                    WHERE pollutant_name = :pollutant_name
                """), {"pollutant_name": pollutant_name.lower().replace(' ', '_')})
                
                organism_stats = organism_result.fetchone()
                
                return {
                    "status": "success",
                    "pollutant_name": pollutant_name,
                    "gene_data": {
                        "total_records": gene_stats[0] if gene_stats else 0,
                        "enzyme_types": gene_stats[1] if gene_stats else 0
                    },
                    "organism_data": {
                        "total_records": organism_stats[0] if organism_stats else 0,
                        "organism_types": organism_stats[1] if organism_stats else 0
                    }
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取污染物摘要时出错: {str(e)}",
                "pollutant_name": pollutant_name
            }
    
    def search_pollutants(self, keyword: str) -> Dict[Any, Any]:
        """
        搜索污染物
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            dict: 搜索结果
        """
        try:
            with self.db_engine.connect() as connection:
                # 搜索基因数据中的污染物
                gene_result = connection.execute(text("""
                    SELECT DISTINCT pollutant_name
                    FROM genes_data
                    WHERE pollutant_name ILIKE :keyword
                    LIMIT 20
                """), {"keyword": f"%{keyword}%"})
                
                gene_pollutants = [row[0] for row in gene_result.fetchall()]
                
                # 搜索微生物数据中的污染物
                organism_result = connection.execute(text("""
                    SELECT DISTINCT pollutant_name
                    FROM organism_data
                    WHERE pollutant_name ILIKE :keyword
                    LIMIT 20
                """), {"keyword": f"%{keyword}%"})
                
                organism_pollutants = [row[0] for row in organism_result.fetchall()]
                
                # 合并结果并去重
                all_pollutants = list(set(gene_pollutants + organism_pollutants))
                
                return {
                    "status": "success",
                    "keyword": keyword,
                    "pollutants": all_pollutants,
                    "count": len(all_pollutants)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索污染物时出错: {str(e)}",
                "keyword": keyword
            }

# 使用示例
if __name__ == "__main__":
    # 创建统一数据访问工具实例
    unified_tool = UnifiedDataTool()
    
    # 示例1: 查询污染物数据
    result = unified_tool.query_pollutant_data("aldrin")
    print("查询污染物数据结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 示例2: 获取污染物摘要
    summary = unified_tool.get_pollutant_summary("aldrin")
    print("\n污染物摘要:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))