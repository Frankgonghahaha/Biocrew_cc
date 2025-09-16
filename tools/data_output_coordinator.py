#!/usr/bin/env python3
"""
数据输出协调器
帮助Agent生成完整、结构化和多元化的数据输出
"""

from crewai.tools import BaseTool
from typing import Dict, Any, List, Union
import json
import pandas as pd

class DataOutputCoordinator(BaseTool):
    name: str = "数据输出协调器"
    description: str = "帮助Agent生成完整、结构化和多元化的数据输出"
    
    def __init__(self):
        """
        初始化数据输出协调器
        """
        super().__init__()  # 调用父类构造函数
    
    def _run(self, operation: str, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的数据输出协调操作
        
        Args:
            operation (str): 要执行的操作名称
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            # 支持中文操作名称映射
            operation_mapping = {
                "format_output": ["格式化输出", "结构化输出"],
                "combine_data": ["整合数据", "合并数据"],
                "generate_report": ["生成报告", "创建报告"],
                "assess_completeness": ["评估完整性", "检查完整性"]
            }
            
            # 将中文操作名称映射到英文操作名称
            actual_operation = operation
            for eng_op, chi_ops in operation_mapping.items():
                if operation == eng_op or operation in chi_ops:
                    actual_operation = eng_op
                    break
            
            if actual_operation == "format_output":
                return self.format_output(**kwargs)
            elif actual_operation == "combine_data":
                return self.combine_data(**kwargs)
            elif actual_operation == "generate_report":
                return self.generate_report(**kwargs)
            elif actual_operation == "assess_completeness":
                return self.assess_completeness(**kwargs)
            else:
                return {"status": "error", "message": f"不支持的操作: {operation}"}
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
            }
    
    def format_output(self, data: Union[Dict, List, str], format_type: str = "json") -> Dict[Any, Any]:
        """
        格式化输出数据
        
        Args:
            data (Union[Dict, List, str]): 要格式化的数据
            format_type (str): 格式类型，支持"json", "table", "list"
            
        Returns:
            dict: 格式化后的数据
        """
        try:
            if format_type == "json":
                formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
            elif format_type == "table":
                if isinstance(data, dict):
                    # 转换为表格格式
                    formatted_data = self._dict_to_table(data)
                else:
                    formatted_data = str(data)
            elif format_type == "list":
                if isinstance(data, dict):
                    # 转换为列表格式
                    formatted_data = self._dict_to_list(data)
                else:
                    formatted_data = data if isinstance(data, list) else [data]
            else:
                formatted_data = str(data)
            
            return {
                "status": "success",
                "formatted_data": formatted_data,
                "format_type": format_type
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"格式化数据时出错: {str(e)}",
                "data": str(data)
            }
    
    def combine_data(self, *args, **kwargs) -> Dict[Any, Any]:
        """
        整合多个数据源的数据
        
        Args:
            *args: 要整合的数据列表
            **kwargs: 命名数据源
            
        Returns:
            dict: 整合后的数据
        """
        try:
            combined_data = {}
            
            # 处理位置参数
            for i, data in enumerate(args):
                if isinstance(data, dict):
                    combined_data[f"data_source_{i}"] = data
                else:
                    combined_data[f"data_source_{i}"] = {"content": data}
            
            # 处理关键字参数
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    combined_data[key] = value
                else:
                    combined_data[key] = {"content": value}
            
            return {
                "status": "success",
                "combined_data": combined_data,
                "sources_count": len(combined_data)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"整合数据时出错: {str(e)}",
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            }
    
    def generate_report(self, title: str, sections: List[Dict], metadata: Dict = None) -> Dict[Any, Any]:
        """
        生成结构化报告
        
        Args:
            title (str): 报告标题
            sections (List[Dict]): 报告章节列表，每个章节包含title和content
            metadata (Dict): 报告元数据
            
        Returns:
            dict: 生成的报告
        """
        try:
            report = {
                "title": title,
                "sections": sections,
                "metadata": metadata or {},
                "generated_at": pd.Timestamp.now().isoformat()
            }
            
            # 计算报告统计信息
            stats = {
                "section_count": len(sections),
                "total_characters": sum(len(str(section.get("content", ""))) for section in sections),
                "has_metadata": metadata is not None
            }
            
            return {
                "status": "success",
                "report": report,
                "statistics": stats
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成报告时出错: {str(e)}",
                "title": title
            }
    
    def assess_completeness(self, data: Dict, required_fields: List[str] = None) -> Dict[Any, Any]:
        """
        评估数据完整性
        
        Args:
            data (Dict): 要评估的数据
            required_fields (List[str]): 必需字段列表
            
        Returns:
            dict: 完整性评估结果
        """
        try:
            if not isinstance(data, dict):
                return {
                    "status": "error",
                    "message": "数据必须是字典格式"
                }
            
            required_fields = required_fields or []
            
            # 检查必需字段
            missing_fields = []
            present_fields = []
            
            for field in required_fields:
                if field in data and data[field] is not None and data[field] != "":
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            # 计算完整性评分
            total_fields = len(required_fields)
            present_fields_count = len(present_fields)
            
            if total_fields > 0:
                completeness_score = (present_fields_count / total_fields) * 100
            else:
                completeness_score = 100
            
            assessment = {
                "status": "success",
                "completeness_score": completeness_score,
                "present_fields": present_fields,
                "missing_fields": missing_fields,
                "total_required_fields": total_fields,
                "present_fields_count": present_fields_count
            }
            
            # 添加建议
            if completeness_score < 70:
                assessment["recommendations"] = [
                    "数据完整性较低，建议补充缺失字段",
                    "考虑使用外部数据源获取更多信息"
                ]
            elif completeness_score < 90:
                assessment["recommendations"] = [
                    "数据基本完整，可考虑补充部分字段以提高质量"
                ]
            else:
                assessment["recommendations"] = [
                    "数据完整性良好"
                ]
            
            return assessment
        except Exception as e:
            return {
                "status": "error",
                "message": f"评估数据完整性时出错: {str(e)}",
                "data_type": type(data).__name__
            }
    
    def _dict_to_table(self, data: Dict) -> str:
        """
        将字典转换为表格格式
        
        Args:
            data (Dict): 要转换的字典数据
            
        Returns:
            str: 表格格式的字符串
        """
        if not data:
            return "空数据"
        
        # 创建表格头部
        headers = list(data.keys())
        rows = [list(data.values())]
        
        # 计算每列的最大宽度
        col_widths = []
        for i, header in enumerate(headers):
            max_width = max(len(str(header)), max(len(str(row[i])) for row in rows))
            col_widths.append(min(max_width, 50))  # 限制最大宽度
        
        # 格式化表格
        table_lines = []
        
        # 添加头部
        header_line = "| " + " | ".join(str(header).ljust(col_widths[i]) for i, header in enumerate(headers)) + " |"
        separator_line = "|" + "|".join("-" * (width + 2) for width in col_widths) + "|"
        
        table_lines.append(header_line)
        table_lines.append(separator_line)
        
        # 添加数据行
        for row in rows:
            row_line = "| " + " | ".join(str(cell)[:col_widths[i]].ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
            table_lines.append(row_line)
        
        return "\n".join(table_lines)
    
    def _dict_to_list(self, data: Dict) -> List:
        """
        将字典转换为列表格式
        
        Args:
            data (Dict): 要转换的字典数据
            
        Returns:
            List: 列表格式的数据
        """
        result = []
        for key, value in data.items():
            if isinstance(value, dict):
                result.append({key: value})
            elif isinstance(value, list):
                result.append({key: value})
            else:
                result.append(f"{key}: {value}")
        return result

# 使用示例
if __name__ == "__main__":
    # 创建数据输出协调器实例
    coordinator = DataOutputCoordinator()
    
    # 示例1: 格式化输出
    sample_data = {
        "microorganisms": ["Bacillus subtilis", "Pseudomonas putida"],
        "genes": ["degA", "degB"],
        "complementarity_index": 0.85
    }
    
    print("示例1: 格式化输出")
    result = coordinator.format_output(sample_data, "json")
    print(result)
    
    # 示例2: 整合数据
    print("\n示例2: 整合数据")
    local_data = {"organism": "Bacillus subtilis", "source": "local"}
    external_data = {"pathway": "degradation pathway", "source": "KEGG"}
    result = coordinator.combine_data(local_data, external_data, metadata={"query": "aldrin"})
    print(result)
    
    # 示例3: 生成报告
    print("\n示例3: 生成报告")
    sections = [
        {"title": "微生物识别结果", "content": "识别到2种功能微生物"},
        {"title": "基因数据分析", "content": "发现相关降解基因"}
    ]
    result = coordinator.generate_report("功能微生物组识别报告", sections)
    print(result)
    
    # 示例4: 评估完整性
    print("\n示例4: 评估完整性")
    data_to_assess = {
        "microorganisms": ["Bacillus subtilis"],
        "genes": None,
        "complementarity_index": 0.85
    }
    required_fields = ["microorganisms", "genes", "complementarity_index"]
    result = coordinator.assess_completeness(data_to_assess, required_fields)
    print(result)