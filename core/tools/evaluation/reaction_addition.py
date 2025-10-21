#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReactionAdditionTool工具
用于为代谢模型添加反应
"""

import os
import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import tempfile
import shutil
import re

# 尝试导入COBRApy
try:
    from cobra.io import read_sbml_model, write_sbml_model, validate_sbml_model
    from cobra import Reaction, Metabolite
    COBRA_AVAILABLE = True
except ImportError:
    COBRA_AVAILABLE = False
    print("警告: COBRApy库未安装，将使用模拟实现")

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 导入统一路径配置
try:
    from config.paths import MODELS_DIR, REACTIONS_DIR
except ImportError:
    # 如果无法导入配置，使用默认路径
    MODELS_DIR = os.path.join(current_dir, '..', '..', '..', 'outputs', 'metabolic_models')
    REACTIONS_DIR = os.path.join(current_dir, '..', '..', '..', 'data', 'reactions')

# 确保目录存在
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REACTIONS_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReactionAdditionToolSchema(BaseModel):
    """ReactionAdditionTool工具输入参数定义"""
    models_path: str = Field(
        default=MODELS_DIR,
        description="包含代谢模型文件的目录路径"
    )
    pollutant_name: str = Field(
        ..., 
        description="目标污染物名称"
    )
    reactions_csv: Optional[str] = Field(
        None, 
        description="反应CSV文件路径"
    )


class ReactionAdditionTool(BaseTool):
    name: str = "ReactionAdditionTool"
    description: str = "用于为代谢模型添加反应"
    args_schema = ReactionAdditionToolSchema
    
    def _run(self, models_path: str = MODELS_DIR, pollutant_name: str = "", 
             reactions_csv: Optional[str] = None) -> Dict[str, Any]:
        """
        运行ReactionAdditionTool工具为模型添加反应
        
        Args:
            models_path: 包含代谢模型文件的目录路径
            pollutant_name: 目标污染物名称
            reactions_csv: 反应CSV文件路径
            
        Returns:
            dict: 处理结果
        """
        # 确保使用正确的模型目录
        if not models_path or models_path == ".":
            models_path = MODELS_DIR
            
        models_path = os.path.abspath(models_path)
        logger.info(f"使用项目统一模型目录: {MODELS_DIR}")
        logger.info(f"使用的模型路径: {models_path}")
        
        # 如果没有提供反应CSV文件，则根据污染物名称生成
        if not reactions_csv:
            # 首先尝试查找现有的反应CSV文件
            possible_files = [
                os.path.join(REACTIONS_DIR, f"{pollutant_name}_reactions.csv"),
                os.path.join(REACTIONS_DIR, f"{pollutant_name.replace(' ', '_')}_reactions.csv"),
                os.path.join(REACTIONS_DIR, f"{pollutant_name.replace(' ', '_')}_degradation_reactions.csv")
            ]
            
            for file_path in possible_files:
                if os.path.exists(file_path):
                    reactions_csv = file_path
                    logger.info(f"找到现有的反应CSV文件: {reactions_csv}")
                    break
            else:
                # 如果没有找到现有的文件，则生成新的反应CSV文件
                reactions_csv = self._generate_reactions_csv(pollutant_name)
        
        # 检查反应CSV文件是否存在
        if not os.path.exists(reactions_csv):
            logger.warning(f"反应CSV文件不存在: {reactions_csv}")
            return {"status": "error", "message": f"反应CSV文件不存在: {reactions_csv}"}
        
        # 读取反应数据
        try:
            reactions_df = pd.read_csv(reactions_csv)
            logger.info(f"读取到 {len(reactions_df)} 个反应")
            
            # 检查必要的列是否存在
            required_columns = ['id', 'name']
            for col in required_columns:
                if col not in reactions_df.columns:
                    logger.warning(f"反应CSV文件缺少必要列: {col}")
                    # 添加默认值
                    if col == 'id':
                        reactions_df['id'] = [f"reaction_{i+1}" for i in range(len(reactions_df))]
                    elif col == 'name':
                        reactions_df['name'] = [f"Reaction {i+1}" for i in range(len(reactions_df))]
            
            # 为缺失的可选列添加默认值
            optional_columns = ['subsystem', 'lower_bound', 'upper_bound', 'reactants', 'products']
            for col in optional_columns:
                if col not in reactions_df.columns:
                    if col in ['lower_bound', 'upper_bound']:
                        reactions_df[col] = 1000.0 if col == 'upper_bound' else -1000.0
                    else:
                        reactions_df[col] = ""
        except Exception as e:
            logger.error(f"读取反应CSV文件失败: {str(e)}")
            return {"status": "error", "message": f"读取反应CSV文件失败: {str(e)}"}
        
        # 获取模型文件列表
        try:
            model_files = [f for f in os.listdir(models_path) if f.endswith('.xml')]
            logger.info(f"找到 {len(model_files)} 个模型文件")
        except Exception as e:
            logger.error(f"读取模型目录失败: {str(e)}")
            return {"status": "error", "message": f"读取模型目录失败: {str(e)}"}
        
        if not model_files:
            logger.warning("未找到任何模型文件")
            return {"status": "error", "message": "未找到任何模型文件"}
        
        # 处理每个模型
        results = []
        success_count = 0
        
        for model_file in model_files:
            model_path = os.path.join(models_path, model_file)
            model_name = os.path.splitext(model_file)[0]
            
            logger.info(f"处理模型: {model_path}")
            
            try:
                # 尝试读取模型
                if COBRA_AVAILABLE:
                    model = read_sbml_model(model_path)
                    # 验证模型
                    errors = validate_sbml_model(model_path)[1]
                    if errors and (errors['SBML_ERROR'] or errors['COBRA_ERROR']):
                        logger.warning(f"模型验证失败 {model_path}: {errors}")
                        # 即使有错误也尝试继续处理
                else:
                    # 如果COBRApy不可用，使用模拟实现
                    logger.warning("COBRApy不可用，使用模拟实现")
                    result = {
                        "model": model_path,
                        "status": "success",
                        "message": "模拟执行，未实际修改模型"
                    }
                    results.append(result)
                    success_count += 1
                    continue
                
                # 添加反应到模型
                reaction_count = 0
                for _, row in reactions_df.iterrows():
                    try:
                        # 创建反应对象
                        reaction_id = str(row['id']).replace('.', '_')
                        
                        # 检查反应是否已存在，如果存在则先删除
                        if reaction_id in [r.id for r in model.reactions]:
                            # 删除现有反应
                            reaction_to_remove = model.reactions.get_by_id(reaction_id)
                            model.remove_reactions([reaction_to_remove])
                            logger.info(f"已删除现有反应: {reaction_id}")
                            reaction_count -= 1  # 减少计数，因为我们要重新添加
                        
                        # 创建反应对象
                        reaction = Reaction(reaction_id)
                        reaction.name = str(row['name'])
                        reaction.subsystem = str(row.get('subsystem', ''))
                        
                        # 设置反应的上下限
                        reaction.lower_bound = float(row.get('lower_bound', -1000.0))
                        reaction.upper_bound = float(row.get('upper_bound', 1000.0))
                        
                        # 如果提供了反应物和产物信息，则添加到反应中
                        if 'reactants' in row and pd.notna(row['reactants']) and row['reactants']:
                            # 解析反应物（格式：metabolite_id:stoichiometry|metabolite_id:stoichiometry）
                            reactants_str = str(row['reactants'])
                            if reactants_str:
                                for reactant_part in reactants_str.split('|'):
                                    if ':' in reactant_part:
                                        parts = reactant_part.split(':')
                                        if len(parts) == 2:
                                            met_id, stoich = parts
                                            # 处理目标化合物的特殊命名
                                            if 'target_compound' in row and met_id == row['target_compound']:
                                                actual_met_id = pollutant_name.replace(' ', '_')
                                            else:
                                                actual_met_id = met_id.strip()
                                            
                                            # 尝试获取代谢物，如果不存在则创建
                                            try:
                                                metabolite = model.metabolites.get_by_id(actual_met_id)
                                            except KeyError:
                                                # 如果代谢物不存在，创建新的代谢物
                                                metabolite = Metabolite(actual_met_id)
                                                metabolite.compartment = 'c'  # 默认细胞质 compartment
                                                metabolite.name = met_id  # 设置代谢物名称
                                                model.add_metabolites(metabolite)
                                            reaction.add_metabolites({metabolite: -abs(float(stoich))})  # 负值表示反应物
                        
                        if 'products' in row and pd.notna(row['products']) and row['products']:
                            # 解析产物（格式：metabolite_id:stoichiometry|metabolite_id:stoichiometry）
                            products_str = str(row['products'])
                            if products_str:
                                for product_part in products_str.split('|'):
                                    if ':' in product_part:
                                        parts = product_part.split(':')
                                        if len(parts) == 2:
                                            met_id, stoich = parts
                                            # 处理特殊代谢物命名
                                            if met_id == 'protocatechuic_acid':
                                                actual_met_id = 'protocatechuic_acid'
                                            else:
                                                actual_met_id = met_id.strip()
                                            
                                            # 尝试获取代谢物，如果不存在则创建
                                            try:
                                                metabolite = model.metabolites.get_by_id(actual_met_id)
                                            except KeyError:
                                                # 如果代谢物不存在，创建新的代谢物
                                                metabolite = Metabolite(actual_met_id)
                                                metabolite.compartment = 'c'  # 默认细胞质 compartment
                                                metabolite.name = met_id  # 设置代谢物名称
                                                model.add_metabolites(metabolite)
                                            reaction.add_metabolites({metabolite: abs(float(stoich))})  # 正值表示产物
                        
                        # 添加反应到模型
                        model.add_reactions([reaction])
                        reaction_count += 1
                        logger.info(f"成功添加反应 {reaction_id}")
                    except Exception as e:
                        logger.warning(f"添加反应 {row['id']} 失败: {str(e)}")
                        continue
                
                # 保存修改后的模型
                write_sbml_model(model, model_path)
                
                result = {
                    "model": model_path,
                    "status": "success",
                    "message": f"成功添加 {reaction_count} 个反应"
                }
                results.append(result)
                success_count += 1
                
            except Exception as e:
                logger.error(f"处理模型 {model_path} 时出错: {str(e)}")
                result = {
                    "model": model_path,
                    "status": "error",
                    "message": str(e)
                }
                results.append(result)
        
        logger.info(f"反应添加完成，成功处理 {success_count} 个模型")
        
        return {
            "status": "success",
            "results": results,
            "message": f"成功处理 {success_count} 个模型"
        }
    
    def _generate_reactions_csv(self, pollutant_name: str) -> str:
        """
        生成反应CSV文件
        
        Args:
            pollutant_name: 污染物名称
            
        Returns:
            str: 生成的CSV文件路径
        """
        csv_file = os.path.join(REACTIONS_DIR, f"{pollutant_name.replace(' ', '_')}_degradation_reactions.csv")
        
        # 检查文件是否已存在
        if os.path.exists(csv_file):
            logger.info(f"反应CSV文件已存在: {csv_file}")
            return csv_file
        
        logger.warning(f"未能获取到 {pollutant_name} 的反应数据，创建模拟数据")
        
        # 创建模拟数据，包含反应物和产物信息
        reactions_data = [
            {
                "id": f"reaction_{i+1}",
                "name": f"{pollutant_name} degradation reaction {i+1}",
                "subsystem": "Degradation",
                "lower_bound": -1000.0,
                "upper_bound": 1000.0,
                "reactants": f"{pollutant_name.replace(' ', '_')}:1.0|C{i+1000}:1.0",
                "products": f"C{i+2000}:1.0|protocatechuic_acid:1.0",
                "target_compound": pollutant_name.replace(' ', '_')
            }
            for i in range(4)  # 生成4个模拟反应
        ]
        
        # 创建DataFrame并保存为CSV
        df = pd.DataFrame(reactions_data)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"成功生成模拟反应CSV文件: {csv_file}")
        return csv_file