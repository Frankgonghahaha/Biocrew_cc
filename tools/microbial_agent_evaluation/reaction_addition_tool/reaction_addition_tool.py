#!/usr/bin/env python3
"""
代谢反应填充工具
用于批量为SBML模型添加代谢反应
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import pandas as pd
import os
import tempfile
import shutil
import logging
from pathlib import Path

# 尝试导入COBRApy
try:
    from cobra.io import read_sbml_model, write_sbml_model
    import cobra
    COBRA_AVAILABLE = True
except ImportError:
    COBRA_AVAILABLE = False
    print("警告: COBRApy库未安装，将无法使用代谢反应填充工具")

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReactionAdditionToolInput(BaseModel):
    models_path: str = Field(..., description="代谢模型目录路径")
    reactions_csv: str = Field(..., description="包含代谢反应定义的CSV文件路径")
    output_path: str = Field(..., description="输出目录路径")
    only_models: Optional[List[str]] = Field(None, description="仅处理指定的模型文件名列表")
    auto_extrans: bool = Field(False, description="是否自动补齐EX/TRANS反应")

class ReactionAdditionTool(BaseTool):
    name: str = "ReactionAdditionTool"
    description: str = "用于批量为SBML模型添加代谢反应的工具"
    args_schema = ReactionAdditionToolInput
    
    def _run(self, **kwargs) -> Dict[str, Any]:
        """
        运行代谢反应填充工具
        
        Args:
            models_path: 代谢模型目录路径
            reactions_csv: 包含代谢反应定义的CSV文件路径
            output_path: 输出目录路径
            only_models: 仅处理指定的模型文件名列表
            auto_extrans: 是否自动补齐EX/TRANS反应
            
        Returns:
            包含操作结果的字典
        """
        try:
            # 获取参数
            models_path = kwargs.get('models_path')
            reactions_csv = kwargs.get('reactions_csv')
            output_path = kwargs.get('output_path')
            only_models = kwargs.get('only_models')
            auto_extrans = kwargs.get('auto_extrans', False)
            
            # 检查参数
            if not models_path or not reactions_csv or not output_path:
                return {
                    "status": "error",
                    "message": "缺少必要参数：models_path, reactions_csv, 或 output_path"
                }
            
            # 检查COBRApy是否可用
            if not COBRA_AVAILABLE:
                return {
                    "status": "error",
                    "message": "COBRApy库未安装，无法执行代谢反应填充"
                }
            
            # 执行反应添加过程
            logger.info(f"开始执行代谢反应填充，模型目录: {models_path}")
            result = self._execute_reaction_addition(models_path, reactions_csv, output_path, only_models, auto_extrans)
            
            logger.info("代谢反应填充完成")
            return result
            
        except Exception as e:
            logger.error(f"代谢反应填充工具执行出错: {str(e)}")
            return {
                "status": "error",
                "message": f"执行代谢反应填充时发生错误: {str(e)}"
            }
    
    def _execute_reaction_addition(self, models_path: str, reactions_csv: str, 
                                 output_path: str, only_models: Optional[List[str]], 
                                 auto_extrans: bool) -> Dict[str, Any]:
        """执行反应添加过程"""
        try:
            # 创建输出目录
            os.makedirs(output_path, exist_ok=True)
            
            # 读取反应CSV文件
            reactions_df = pd.read_csv(reactions_csv)
            logger.info(f"读取到 {len(reactions_df)} 个反应")
            
            # 查找模型文件
            model_files = self._discover_models(models_path, only_models)
            logger.info(f"找到 {len(model_files)} 个模型文件")
            
            if not model_files:
                return {
                    "status": "error",
                    "message": f"在目录 {models_path} 中未找到SBML模型文件"
                }
            
            # 处理每个模型
            results = []
            for model_file in model_files:
                try:
                    result = self._process_single_model(model_file, reactions_df, output_path, auto_extrans)
                    results.append(result)
                except Exception as e:
                    logger.error(f"处理模型 {model_file} 时出错: {str(e)}")
                    results.append({
                        "model": os.path.basename(model_file),
                        "status": "error",
                        "message": str(e)
                    })
            
            # 统计结果
            successful = sum(1 for r in results if r.get("status") == "success")
            failed = len(results) - successful
            
            return {
                "status": "success",
                "data": {
                    "total_models": len(results),
                    "successful": successful,
                    "failed": failed,
                    "details": results
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行反应添加过程时发生错误: {str(e)}"
            }
    
    def _discover_models(self, models_path: str, only_models: Optional[List[str]]) -> List[str]:
        """查找模型文件"""
        model_files = []
        
        # 递归搜索.xml和.sbml文件
        for root, _, files in os.walk(models_path):
            for file in files:
                if file.lower().endswith(('.xml', '.sbml')):
                    full_path = os.path.join(root, file)
                    if only_models is None or file in only_models:
                        model_files.append(full_path)
        
        return sorted(model_files)
    
    def _process_single_model(self, model_file: str, reactions_df: pd.DataFrame, 
                            output_path: str, auto_extrans: bool) -> Dict[str, Any]:
        """处理单个模型"""
        try:
            model_name = os.path.basename(model_file)
            logger.info(f"处理模型: {model_name}")
            
            # 读取模型
            model = read_sbml_model(model_file)
            
            # 为模型添加反应
            added_reactions = self._add_reactions_to_model(model, reactions_df)
            
            # 如果启用自动EX/TRANS补齐
            if auto_extrans:
                self._add_extrans_reactions(model)
            
            # 保存修改后的模型
            output_file = os.path.join(output_path, model_name)
            write_sbml_model(model, output_file)
            
            return {
                "model": model_name,
                "status": "success",
                "added_reactions": added_reactions,
                "output_file": output_file
            }
            
        except Exception as e:
            return {
                "model": model_name,
                "status": "error",
                "message": str(e)
            }
    
    def _add_reactions_to_model(self, model, reactions_df: pd.DataFrame) -> List[str]:
        """为模型添加反应"""
        added_reactions = []
        
        for _, row in reactions_df.iterrows():
            try:
                # 解析反应方程
                equation = row.get('Reaction equation') or row.get('equation')
                if not equation:
                    continue
                
                # 生成反应ID
                reaction_id = row.get('id') or row.get('Reaction id')
                if not reaction_id:
                    reaction_id = f"RXN_{len(model.reactions) + 1:05d}"
                
                # 获取反应名称
                reaction_name = row.get('name', '')
                
                # 解析上下界
                lb = row.get('lb')
                ub = row.get('ub')
                
                # 根据箭头类型设置默认上下界
                if '->' in equation and '<->' not in equation:
                    # 不可逆反应
                    default_lb, default_ub = 0, 1000
                else:
                    # 可逆反应
                    default_lb, default_ub = -1000, 1000
                
                lb = lb if pd.notna(lb) else default_lb
                ub = ub if pd.notna(ub) else default_ub
                
                # 创建反应对象
                reaction = cobra.Reaction(reaction_id)
                reaction.name = reaction_name
                reaction.lower_bound = float(lb)
                reaction.upper_bound = float(ub)
                
                # 将反应方程解析为COBRA格式
                # 这里简化处理，实际应该更复杂地解析方程
                reaction.build_reaction_from_string(equation)
                
                # 添加反应到模型
                model.add_reactions([reaction])
                added_reactions.append(reaction_id)
                
            except Exception as e:
                logger.warning(f"添加反应时出错: {str(e)}")
                continue
        
        return added_reactions
    
    def _add_extrans_reactions(self, model) -> None:
        """自动添加EX/TRANS反应"""
        try:
            # 收集模型中的代谢物
            metabolites = set()
            for metabolite in model.metabolites:
                # 获取代谢物基础名称（去除舱室后缀）
                base_name = self._get_metabolite_base_name(metabolite.id)
                metabolites.add(base_name)
            
            # 为每个代谢物添加EX和TRANS反应
            for base_name in metabolites:
                # 添加TRANS反应（胞外 ↔ 胞质）
                trans_id = f"TRANS_{base_name}"
                if trans_id not in model.reactions:
                    trans_reaction = cobra.Reaction(trans_id)
                    trans_reaction.name = f"Transport of {base_name}"
                    trans_reaction.lower_bound = -1000
                    trans_reaction.upper_bound = 1000
                    # 这里简化处理，实际应该正确设置反应方程
                    model.add_reactions([trans_reaction])
                
                # 添加EX反应（与外界交换）
                ex_id = f"EX_{base_name}_e"
                if ex_id not in model.reactions:
                    ex_reaction = cobra.Reaction(ex_id)
                    ex_reaction.name = f"Exchange of {base_name}"
                    ex_reaction.lower_bound = -1000
                    ex_reaction.upper_bound = 1000
                    # 这里简化处理，实际应该正确设置反应方程
                    model.add_reactions([ex_reaction])
            
            # 特殊处理o2
            if "o2" in metabolites:
                o2_trans_id = "TRANS_o2"
                o2_ex_id = "EX_o2_e"
                
                if o2_trans_id not in model.reactions:
                    o2_trans_reaction = cobra.Reaction(o2_trans_id)
                    o2_trans_reaction.name = "Transport of oxygen"
                    o2_trans_reaction.lower_bound = -1000
                    o2_trans_reaction.upper_bound = 1000
                    model.add_reactions([o2_trans_reaction])
                
                if o2_ex_id not in model.reactions:
                    o2_ex_reaction = cobra.Reaction(o2_ex_id)
                    o2_ex_reaction.name = "Exchange of oxygen"
                    o2_ex_reaction.lower_bound = -1000
                    o2_ex_reaction.upper_bound = 1000
                    model.add_reactions([o2_ex_reaction])
                    
        except Exception as e:
            logger.warning(f"添加EX/TRANS反应时出错: {str(e)}")
    
    def _get_metabolite_base_name(self, metabolite_id: str) -> str:
        """获取代谢物基础名称（去除舱室后缀）"""
        # 移除常见的舱室后缀
        suffixes = ['_c', '_e', '_m', '_p', '_n', '_g', '_l', '_r', '_s', '_v', '_x', '_y', '_z']
        base_name = metabolite_id
        for suffix in suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        return base_name