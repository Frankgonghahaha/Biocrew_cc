#!/usr/bin/env python3
"""
ctFBA工具
用于计算微生物群落的代谢通量（协同权衡代谢通量平衡法）
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy.optimize import linprog

class CtfbaToolInput(BaseModel):
    models_path: str = Field(..., description="代谢模型目录路径")
    target_compound: str = Field(..., description="目标污染物名称")
    community_composition: Dict[str, float] = Field(..., description="菌剂群落组成（物种名:比例）")
    tradeoff_coefficient: float = Field(0.5, description="权衡系数（0-1，0=保多样性，1=提降解效率）")

class CtfbaTool(BaseTool):
    name: str = "CtfbaTool"
    description: str = "用于计算微生物群落代谢通量的ctFBA工具（协同权衡代谢通量平衡法）"
    args_schema = CtfbaToolInput
    
    def _run(self, models_path: str, target_compound: str, community_composition: Dict[str, float], 
             tradeoff_coefficient: float = 0.5) -> Dict[str, Any]:
        """
        运行ctFBA算法计算代谢通量
        
        Args:
            models_path: 代谢模型目录路径
            target_compound: 目标污染物名称
            community_composition: 菌剂群落组成（物种名:比例）
            tradeoff_coefficient: 权衡系数（0-1，0=保多样性，1=提降解效率）
            
        Returns:
            dict: 代谢通量计算结果
        """
        try:
            # 验证权衡系数范围
            if not 0 <= tradeoff_coefficient <= 1:
                return {"status": "error", "message": "权衡系数必须在0-1范围内"}
            
            # 模拟ctFBA算法计算过程
            # 实际实现中需要加载代谢模型并进行复杂计算
            # 这里提供一个简化版的示例实现
            
            # 模拟每个物种的降解能力
            species_degradation_rates = {}
            total_degradation_rate = 0
            
            for species, proportion in community_composition.items():
                # 模拟基于Kcat值和环境适应性的降解速率计算
                # 在实际实现中，这里会调用真实的代谢模型计算
                simulated_rate = self._simulate_degradation_rate(species, target_compound, proportion)
                species_degradation_rates[species] = simulated_rate
                total_degradation_rate += simulated_rate
            
            # 计算群落整体的代谢通量
            community_flux = self._calculate_community_flux(
                species_degradation_rates, 
                community_composition, 
                tradeoff_coefficient
            )
            
            # 计算稳定性指标
            stability_metrics = self._calculate_stability_metrics(community_composition)
            
            return {
                "status": "success",
                "data": {
                    "target_compound": target_compound,
                    "community_composition": community_composition,
                    "tradeoff_coefficient": tradeoff_coefficient,
                    "species_degradation_rates": species_degradation_rates,
                    "total_degradation_rate": total_degradation_rate,
                    "community_flux": community_flux,
                    "stability_metrics": stability_metrics
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"执行ctFBA算法时出错: {str(e)}"}
    
    def _simulate_degradation_rate(self, species: str, compound: str, proportion: float) -> float:
        """
        模拟单个物种对目标化合物的降解速率
        
        Args:
            species: 物种名称
            compound: 化合物名称
            proportion: 物种在群落中的比例
            
        Returns:
            float: 降解速率
        """
        # 这是一个简化的模拟函数
        # 实际实现中会基于代谢模型和酶催化数据计算
        import random
        base_rate = random.uniform(0.1, 1.0)  # 基础降解速率
        # 考虑物种比例的影响
        rate = base_rate * proportion
        return round(rate, 4)
    
    def _calculate_community_flux(self, species_rates: Dict[str, float], 
                                 composition: Dict[str, float], 
                                 tradeoff_coeff: float) -> Dict[str, Any]:
        """
        计算群落整体的代谢通量
        
        Args:
            species_rates: 各物种降解速率
            composition: 群落组成
            tradeoff_coeff: 权衡系数
            
        Returns:
            dict: 代谢通量计算结果
        """
        # 计算加权平均降解速率
        weighted_rate = sum(rate * composition[species] for species, rate in species_rates.items())
        
        # 计算多样性指标（香农指数）
        proportions = list(composition.values())
        shannon_diversity = -sum(p * np.log(p) for p in proportions if p > 0)
        
        # 计算权衡后的综合得分
        efficiency_score = weighted_rate  # 降解效率
        diversity_score = shannon_diversity / np.log(len(proportions)) if len(proportions) > 1 else 1.0  # 归一化多样性
        
        # 权衡公式：综合得分 = α × 降解效率 + (1-α) × 多样性
        comprehensive_score = tradeoff_coeff * efficiency_score + (1 - tradeoff_coeff) * diversity_score
        
        return {
            "weighted_degradation_rate": round(weighted_rate, 4),
            "shannon_diversity": round(shannon_diversity, 4),
            "normalized_diversity": round(diversity_score, 4),
            "comprehensive_score": round(comprehensive_score, 4),
            "efficiency_score": round(efficiency_score, 4),
            "diversity_score": round(diversity_score, 4)
        }
    
    def _calculate_stability_metrics(self, composition: Dict[str, float]) -> Dict[str, Any]:
        """
        计算群落稳定性指标
        
        Args:
            composition: 群落组成
            
        Returns:
            dict: 稳定性指标
        """
        proportions = list(composition.values())
        
        # 计算均匀度 (Evenness)
        shannon_diversity = -sum(p * np.log(p) for p in proportions if p > 0)
        max_diversity = np.log(len(proportions))
        evenness = shannon_diversity / max_diversity if max_diversity > 0 else 1.0
        
        # 计算优势度 (Dominance)
        dominance = max(proportions) if proportions else 0
        
        # 计算丰富度 (Richness)
        richness = len([p for p in proportions if p > 0])
        
        return {
            "evenness": round(evenness, 4),
            "dominance": round(dominance, 4),
            "richness": richness
        }