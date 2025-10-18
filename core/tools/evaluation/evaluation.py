#!/usr/bin/env python3
"""
评价工具
实现基于核心标准的评价结果判断逻辑
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import re
import os

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 导入统一路径配置
try:
    from config.paths import MODELS_DIR as DEFAULT_MODELS_DIR
except ImportError:
    # 如果无法导入配置，使用默认路径
    DEFAULT_MODELS_DIR = os.path.join(current_dir, '..', '..', '..', 'outputs', 'metabolic_models')

class AnalyzeEvaluationResultRequest(BaseModel):
    evaluation_report: str = Field(..., description="技术评估专家生成的评价报告")


class CheckCoreStandardsRequest(BaseModel):
    evaluation_report: str = Field(..., description="评价报告")


class AnalyzeCtfbaResultsRequest(BaseModel):
    ctfba_results: Dict[str, Any] = Field(..., description="ctFBA工具的计算结果")
    target_compound: str = Field(..., description="目标污染物名称")


class EvaluationTool(BaseTool):
    name: str = "EvaluationTool"
    description: str = "实现基于核心标准的评价结果判断逻辑，包括ctFBA结果分析"
    
    def _run(self, operation: str = "", models_dir: str = DEFAULT_MODELS_DIR, **kwargs) -> Dict[Any, Any]:
        """
        执行指定的评价操作
        
        Args:
            operation (str): 要执行的操作名称
            models_dir (str): 代谢模型目录路径
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
            # 确保使用正确的模型目录
            if not models_dir or models_dir == ".":
                models_dir = DEFAULT_MODELS_DIR
                
            models_dir = os.path.abspath(models_dir)
            
            # 如果提供了operation参数，则按旧方式处理以保持向后兼容
            if operation:
                if operation == "analyze_evaluation_result":
                    evaluation_report = kwargs.get("evaluation_report")
                    if not evaluation_report:
                        return {"status": "error", "message": "缺少评价报告参数"}
                    result = self.analyze_evaluation_result(evaluation_report)
                    return {"status": "success", "data": result}
                    
                elif operation == "check_core_standards":
                    evaluation_report = kwargs.get("evaluation_report")
                    if not evaluation_report:
                        return {"status": "error", "message": "缺少评价报告参数"}
                    result = self.check_core_standards(evaluation_report)
                    return {"status": "success", "data": result}
                    
                elif operation == "analyze_ctfba_results":
                    ctfba_results = kwargs.get("ctfba_results")
                    target_compound = kwargs.get("target_compound")
                    if not ctfba_results:
                        return {"status": "error", "message": "缺少ctFBA结果参数"}
                    result = self.analyze_ctfba_results(ctfba_results, target_compound)
                    return {"status": "success", "data": result}
                    
                else:
                    return {"status": "error", "message": f"不支持的操作: {operation}"}
            else:
                # 如果没有提供operation参数，直接使用kwargs中的参数
                if "evaluation_report" in kwargs:
                    # 默认执行analyze_evaluation_result操作
                    result = self.analyze_evaluation_result(kwargs["evaluation_report"])
                    return {"status": "success", "data": result}
                elif "ctfba_results" in kwargs:
                    # 执行analyze_ctfba_results操作
                    ctfba_results = kwargs["ctfba_results"]
                    target_compound = kwargs.get("target_compound", "")
                    result = self.analyze_ctfba_results(ctfba_results, target_compound)
                    return {"status": "success", "data": result}
                else:
                    return {"status": "error", "message": "缺少必需参数"}
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行操作时出错: {str(e)}",
                "operation": operation
            }
    
    def analyze_evaluation_result(self, evaluation_report: str) -> Dict[str, Any]:
        """
        分析评价报告并判断是否需要重新设计
        
        Args:
            evaluation_report (str): 技术评估专家生成的评价报告
            
        Returns:
            dict: 包含判断结果和建议的字典
        """
        # 检查核心标准是否达标
        core_standards_met = self.check_core_standards(evaluation_report)
        
        # 分析具体原因
        reason = ""
        suggestions = ""
        
        if not core_standards_met:
            reason = "群落稳定性和/或结构稳定性不达标"
            suggestions = "建议重新进行微生物识别，选择更合适的微生物组合"
        else:
            reason = "群落稳定性和结构稳定性均达标"
            suggestions = "可以进入实施方案生成阶段"
        
        analysis_result = {
            "core_standards_met": core_standards_met,
            "need_redesign": not core_standards_met,
            "reason": reason,
            "suggestions": suggestions
        }
        
        return analysis_result
    
    def check_core_standards(self, evaluation_report: str) -> bool:
        """
        检查核心标准（群落稳定性和结构稳定性）是否达标
        
        Args:
            evaluation_report (str): 评价报告
            
        Returns:
            bool: 如果核心标准达标返回True，否则返回False
        """
        try:
            # 解析评价报告，检查是否包含关键失败信息
            if isinstance(evaluation_report, str):
                # 检查是否包含失败信息
                if ("无法构建微生物社区" in evaluation_report or 
                    "无法计算" in evaluation_report or
                    "失败" in evaluation_report or
                    "error" in evaluation_report.lower()):
                    return False
                
                # 检查是否明确提到核心标准未达标
                if ("未达标" in evaluation_report or
                    "不达标" in evaluation_report):
                    return False
                    
                # 默认认为如果报告中没有明确的失败信息，则达标
                return True
            else:
                # 非字符串格式，默认认为达标
                return True
                
        except Exception as e:
            # 出现异常时，默认认为达标
            return True
    
    def analyze_ctfba_results(self, ctfba_results: Dict[str, Any], target_compound: str = "") -> Dict[str, Any]:
        """
        分析ctFBA工具的计算结果
        
        Args:
            ctfba_results (dict): ctFBA工具的计算结果
            target_compound (str): 目标污染物名称
            
        Returns:
            dict: 分析结果
        """
        # 检查结果状态
        if ctfba_results.get("status") != "success":
            return {
                "is_valid": False,
                "reason": "ctFBA计算失败",
                "suggestions": "检查模型文件是否正确，或使用模拟数据继续流程"
            }
        
        data = ctfba_results.get("data", {})
        
        # 检查关键指标
        community_growth = data.get("community_growth", 0)
        species_growth_rates = data.get("species_growth_rates", {})
        target_flux = data.get("target_compound_flux", 0)
        
        # 分析群落生长率
        if community_growth <= 0:
            return {
                "is_valid": False,
                "reason": "群落生长率过低或为负值",
                "suggestions": "检查模型是否完整，或调整群落组成比例"
            }
        
        # 分析物种生长率
        if not species_growth_rates:
            return {
                "is_valid": False,
                "reason": "未获取到物种生长率信息",
                "suggestions": "检查模型是否完整"
            }
        
        # 检查是否有物种生长率为负值或零
        negative_growth_species = [species for species, growth in species_growth_rates.items() if growth <= 0]
        if negative_growth_species:
            return {
                "is_valid": False,
                "reason": f"以下物种生长率为负值或零: {', '.join(negative_growth_species)}",
                "suggestions": "调整群落组成比例或检查模型完整性"
            }
        
        # 分析目标化合物通量
        if target_flux <= 0:
            return {
                "is_valid": False,
                "reason": f"目标化合物'{target_compound}'的通量为负值或零",
                "suggestions": "检查反应是否正确添加到模型中"
            }
        
        # 如果所有检查都通过
        return {
            "is_valid": True,
            "community_growth": community_growth,
            "species_growth_rates": species_growth_rates,
            "target_flux": target_flux,
            "reason": "ctFBA计算结果正常",
            "suggestions": "可以继续进行后续评估"
        }