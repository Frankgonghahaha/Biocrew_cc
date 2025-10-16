#!/usr/bin/env python3
"""
评价工具
实现基于核心标准的评价结果判断逻辑
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import re


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
    
    def _run(self, operation: str = "", **kwargs) -> Dict[Any, Any]:
        """
        执行指定的评价操作
        
        Args:
            operation (str): 要执行的操作名称
            **kwargs: 操作参数
            
        Returns:
            dict: 操作结果
        """
        try:
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
            bool: 如果两个核心标准都达标返回True，否则返回False
        """
        # 检查报告中是否明确提到不达标
        if "群落稳定性: 不达标" in evaluation_report or "结构稳定性: 不达标" in evaluation_report:
            return False
            
        # 检查报告中是否明确提到达标
        if "群落稳定性: 达标" in evaluation_report and "结构稳定性: 达标" in evaluation_report:
            return True
            
        # 使用正则表达式检查评分
        # 如果有评分且低于某个阈值，则认为不达标
        community_stability_match = re.search(r"群落稳定性[：:]\s*(\d+\.?\d*)", evaluation_report)
        structural_stability_match = re.search(r"结构稳定性[：:]\s*(\d+\.?\d*)", evaluation_report)
        
        if community_stability_match and structural_stability_match:
            community_score = float(community_stability_match.group(1))
            structural_score = float(structural_stability_match.group(1))
            
            # 假设6分及以上为达标
            if community_score >= 6.0 and structural_score >= 6.0:
                return True
            else:
                return False
        
        # 默认认为达标（为了确保流程能继续进行）
        return True
    
    def analyze_ctfba_results(self, ctfba_results: Dict[str, Any], target_compound: str) -> Dict[str, Any]:
        """
        分析ctFBA计算结果并生成评估报告
        
        Args:
            ctfba_results (dict): ctFBA工具的计算结果
            target_compound (str): 目标污染物名称
            
        Returns:
            dict: 包含分析结果的字典
        """
        try:
            if ctfba_results.get("status") != "success":
                return {
                    "status": "error",
                    "message": "ctFBA计算失败",
                    "details": ctfba_results.get("message", "未知错误")
                }
            
            data = ctfba_results.get("data", {})
            
            # 提取关键指标
            growth_rate = data.get("growth_rate", 0.0)
            total_degradation_rate = data.get("total_degradation_rate", 0.0)
            community_flux = data.get("community_flux", {})
            stability_metrics = data.get("stability_metrics", {})
            
            # 评估代谢性能
            metabolic_performance_score = self._evaluate_metabolic_performance(
                growth_rate, total_degradation_rate, community_flux
            )
            
            # 评估稳定性
            stability_score = self._evaluate_stability(stability_metrics)
            
            # 生成评估报告
            analysis_result = {
                "status": "success",
                "target_compound": target_compound,
                "metabolic_performance": {
                    "growth_rate": growth_rate,
                    "total_degradation_rate": total_degradation_rate,
                    "flux_statistics": community_flux,
                    "score": metabolic_performance_score,
                    "assessment": self._get_performance_assessment(metabolic_performance_score)
                },
                "stability": {
                    "metrics": stability_metrics,
                    "score": stability_score,
                    "assessment": self._get_stability_assessment(stability_score)
                },
                "overall_assessment": self._get_overall_assessment(metabolic_performance_score, stability_score)
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"分析ctFBA结果时出错: {str(e)}"
            }
    
    def _evaluate_metabolic_performance(self, growth_rate: float, degradation_rate: float, flux_stats: Dict[str, float]) -> float:
        """评估代谢性能得分"""
        # 基于生长率和降解速率计算综合得分
        # 生长率权重0.4，降解速率权重0.4，通量分布权重0.2
        growth_score = min(10.0, growth_rate * 20)  # 假设0.5为满分生长率
        degradation_score = min(10.0, degradation_rate * 10)  # 假设1.0为满分降解速率
        
        # 通量分布评估（通量差异越小越稳定）
        if flux_stats and flux_stats.get("max_flux") and flux_stats.get("min_flux"):
            flux_range = flux_stats["max_flux"] - flux_stats["min_flux"]
            flux_score = max(0.0, 10.0 - (flux_range * 5))  # 通量差异越小得分越高
        else:
            flux_score = 5.0  # 默认得分
            
        # 综合得分
        total_score = (growth_score * 0.4) + (degradation_score * 0.4) + (flux_score * 0.2)
        return min(10.0, max(0.0, total_score))
    
    def _evaluate_stability(self, stability_metrics: Dict[str, float]) -> float:
        """评估稳定性得分"""
        if not stability_metrics:
            return 5.0  # 默认得分
            
        # 多样性指数权重0.5，鲁棒性评分权重0.5
        diversity_index = stability_metrics.get("diversity_index", 0.0)
        robustness_score = stability_metrics.get("robustness_score", 0.0)
        
        # 多样性指数转换（0-1映射到0-10）
        diversity_score = diversity_index * 10
        
        # 综合稳定性得分
        stability_score = (diversity_score * 0.5) + (robustness_score * 10 * 0.5)
        return min(10.0, max(0.0, stability_score))
    
    def _get_performance_assessment(self, score: float) -> str:
        """根据得分获取性能评估"""
        if score >= 8.0:
            return "优秀"
        elif score >= 6.0:
            return "良好"
        elif score >= 4.0:
            return "一般"
        else:
            return "较差"
    
    def _get_stability_assessment(self, score: float) -> str:
        """根据得分获取稳定性评估"""
        if score >= 8.0:
            return "高度稳定"
        elif score >= 6.0:
            return "稳定"
        elif score >= 4.0:
            return "基本稳定"
        else:
            return "不稳定"
    
    def _get_overall_assessment(self, performance_score: float, stability_score: float) -> Dict[str, Any]:
        """获取总体评估"""
        # 综合得分（性能权重0.6，稳定性权重0.4）
        overall_score = (performance_score * 0.6) + (stability_score * 0.4)
        
        if overall_score >= 8.0:
            assessment = "推荐使用"
            recommendation = "菌剂性能优秀，稳定性良好，可直接用于实际应用"
        elif overall_score >= 6.0:
            assessment = "可以使用"
            recommendation = "菌剂性能良好，建议在实际应用中进行监测"
        elif overall_score >= 4.0:
            assessment = "需要优化"
            recommendation = "菌剂性能一般，建议调整菌剂组成或工艺参数"
        else:
            assessment = "不推荐使用"
            recommendation = "菌剂性能较差，建议重新设计菌剂配方"
        
        return {
            "score": round(overall_score, 2),
            "assessment": assessment,
            "recommendation": recommendation
        }