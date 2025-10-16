#!/usr/bin/env python3
"""
培养基推荐工具
用于生成推荐培养基组分
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

# 尝试导入MICOM和COBRApy
try:
    from micom import Community
    from cobra.io import read_sbml_model, write_sbml_model
    MICOM_AVAILABLE = True
    COBRA_AVAILABLE = True
except ImportError:
    MICOM_AVAILABLE = False
    COBRA_AVAILABLE = False
    print("警告: MICOM或COBRApy库未安装，将无法使用培养基推荐工具")

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediumRecommendationToolInput(BaseModel):
    models_path: str = Field(..., description="代谢模型目录路径")
    output_path: str = Field(..., description="输出CSV文件路径")
    community_growth: float = Field(0.1, description="社区生长率参数")
    min_growth: float = Field(0.1, description="最小生长率参数")
    max_import: float = Field(20.0, description="单一底物最大进口上界")
    candidate_ex: Optional[List[str]] = Field(None, description="候选EX列表，形如EX_id=value")

class MediumRecommendationTool(BaseTool):
    name: str = "MediumRecommendationTool"
    description: str = "用于生成推荐培养基组分的工具"
    args_schema = MediumRecommendationToolInput
    
    def _run(self, **kwargs) -> Dict[str, Any]:
        """
        运行培养基推荐工具
        
        Args:
            models_path: 代谢模型目录路径
            output_path: 输出CSV文件路径
            community_growth: 社区生长率参数
            min_growth: 最小生长率参数
            max_import: 单一底物最大进口上界
            candidate_ex: 候选EX列表，形如EX_id=value
            
        Returns:
            包含操作结果的字典
        """
        try:
            # 获取参数
            models_path = kwargs.get('models_path')
            output_path = kwargs.get('output_path')
            community_growth = kwargs.get('community_growth', 0.1)
            min_growth = kwargs.get('min_growth', 0.1)
            max_import = kwargs.get('max_import', 20.0)
            candidate_ex = kwargs.get('candidate_ex')
            
            # 检查参数
            if not models_path or not output_path:
                return {
                    "status": "error",
                    "message": "缺少必要参数：models_path 或 output_path"
                }
            
            # 检查依赖库是否可用
            if not MICOM_AVAILABLE or not COBRA_AVAILABLE:
                return {
                    "status": "error",
                    "message": "MICOM或COBRApy库未安装，无法执行培养基推荐"
                }
            
            # 解析候选EX
            candidate_ex_df = self._parse_candidate_ex(candidate_ex)
            
            # 执行培养基推荐过程
            logger.info(f"开始执行培养基推荐，模型目录: {models_path}")
            result = self._execute_medium_recommendation(
                models_path, output_path, community_growth, min_growth, max_import, candidate_ex_df
            )
            
            logger.info("培养基推荐完成")
            return result
            
        except Exception as e:
            logger.error(f"培养基推荐工具执行出错: {str(e)}")
            return {
                "status": "error",
                "message": f"执行培养基推荐时发生错误: {str(e)}"
            }
    
    def _parse_candidate_ex(self, candidate_ex: Optional[List[str]]) -> pd.DataFrame:
        """解析候选EX列表"""
        if not candidate_ex:
            # 默认候选EX
            cand_pairs = [("EX_glc__D_m", 10.0), ("EX_o2_m", 20.0)]
        else:
            cand_pairs = []
            for item in candidate_ex:
                if "=" in item:
                    rid, val = item.split("=", 1)
                    try:
                        cand_pairs.append((rid.strip(), float(val)))
                    except Exception:
                        pass
        
        if not cand_pairs:
            cand_pairs = [("EX_glc__D_m", 10.0), ("EX_o2_m", 20.0)]
        
        return pd.DataFrame(cand_pairs, columns=["reaction", "flux"])
    
    def _execute_medium_recommendation(self, models_path: str, output_path: str,
                                     community_growth: float, min_growth: float, 
                                     max_import: float, candidate_ex: pd.DataFrame) -> Dict[str, Any]:
        """执行培养基推荐过程"""
        try:
            # 查找模型文件
            model_paths = self._discover_models(models_path)
            logger.info(f"找到 {len(model_paths)} 个模型文件")
            
            if not model_paths:
                return {
                    "status": "error",
                    "message": f"在目录 {models_path} 中未找到SBML模型文件"
                }
            
            # 处理每个模型并收集结果
            all_rows = []
            for model_path in model_paths:
                try:
                    df = self._process_single_model(
                        model_path, community_growth, min_growth, max_import, candidate_ex
                    )
                    if df is not None and not df.empty:
                        all_rows.append(df)
                except Exception as e:
                    logger.error(f"处理模型 {model_path} 时出错: {str(e)}")
            
            if not all_rows:
                return {
                    "status": "error",
                    "message": "没有可汇总的结果"
                }
            
            # 合并所有结果
            out = pd.concat(all_rows, ignore_index=True)
            
            # 生成推荐培养基
            medium_df = self._recommend_medium(out, max_import)
            
            if medium_df.empty:
                return {
                    "status": "error",
                    "message": "没有正需求通量，无法给出建议"
                }
            
            # 保存推荐培养基到CSV
            try:
                medium_df.rename(columns={"suggested_upper_bound": "flux"}).to_csv(output_path, index=False)
                logger.info(f"已导出推荐培养基到: {output_path}")
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"推荐培养基导出失败: {str(e)}"
                }
            
            # 返回前几行预览
            preview = medium_df.head(20).to_dict('records')
            
            return {
                "status": "success",
                "data": {
                    "output_file": output_path,
                    "total_reactions": len(medium_df),
                    "preview": preview
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行培养基推荐过程时发生错误: {str(e)}"
            }
    
    def _discover_models(self, models_path: str) -> List[str]:
        """查找模型文件"""
        model_paths = []
        
        # 递归搜索.xml和.sbml文件
        for root, _, files in os.walk(models_path):
            for file in files:
                if file.lower().endswith(('.xml', '.sbml')):
                    model_paths.append(os.path.join(root, file))
        
        return sorted(model_paths)
    
    def _process_single_model(self, model_path: str, community_growth: float, 
                            min_growth: float, max_import: float, 
                            candidate_ex: pd.DataFrame) -> Optional[pd.DataFrame]:
        """处理单个模型"""
        try:
            # 获取模型名称
            name = os.path.splitext(os.path.basename(model_path))[0]
            logger.info(f"处理模型: {name}")
            
            # 创建临时目录和社区
            tmp_dir = tempfile.mkdtemp(prefix=f"cm_sbml_{name}_")
            try:
                # 读取模型
                model = read_sbml_model(model_path)
                model = self._normalize_external_compartment(model)
                
                # 保存临时SBML
                tmp_sbml = os.path.join(tmp_dir, f"{name}.xml")
                write_sbml_model(model, tmp_sbml)
                
                # 构建单菌社区
                community = self._build_singleton_community(tmp_sbml, name)
                
                # 使用MICOM计算完整培养基
                result_df = self._run_with_micom(community, name, community_growth, min_growth, max_import, candidate_ex)
                
                return result_df
                
            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"处理模型 {model_path} 时出错: {str(e)}")
            return None
    
    def _normalize_external_compartment(self, model):
        """统一外液舱室标记"""
        EXTERNAL_COMPARTMENT_SYNONYMS = {"C_e", "ext", "external", "extracellular"}
        TARGET_EXTERNAL = "e"
        
        changed = 0
        for met in model.metabolites:
            comp = (met.compartment or "").strip()
            if comp in EXTERNAL_COMPARTMENT_SYNONYMS:
                met.compartment = TARGET_EXTERNAL
                changed += 1
        
        if changed:
            logger.info(f"统一外液舱室：修正 {changed} 个代谢物 compartment → 'e'")
        
        return model
    
    def _build_singleton_community(self, sbml_path: str, name: str) -> Community:
        """构建单菌社区"""
        tax = pd.DataFrame({
            "id": [name],
            "file": [sbml_path],
            "abundance": [1.0],
            "biomass": [None],
        }).set_index("id", drop=False)
        
        return Community(tax, name=f"COMM_{name}")
    
    def _run_with_micom(self, community, name: str, community_growth: float, 
                       min_growth: float, max_import: float, candidate_ex: pd.DataFrame) -> pd.DataFrame:
        """使用MICOM计算完整培养基"""
        try:
            # 尝试使用workflows API
            try:
                from micom.workflows.media import complete_community_medium as wf_complete
                
                tmp_dir = tempfile.mkdtemp(prefix=f"cm_wf_{name}_")
                try:
                    # 保存社区到pickle
                    pickle_name = f"{name}.pickle"
                    pickle_path = os.path.join(tmp_dir, pickle_name)
                    community.to_pickle(pickle_path)
                    
                    # 创建清单
                    manifest = pd.DataFrame({
                        "sample_id": [name],
                        "file": [pickle_name],
                    })
                    
                    # 计算完整培养基
                    fixed = wf_complete(
                        manifest=manifest,
                        model_folder=tmp_dir,
                        medium=candidate_ex,
                        community_growth=community_growth,
                        min_growth=min_growth,
                        max_import=max_import,
                        summarize=True,
                        threads=1,
                    )
                    
                    result_df = fixed[["reaction", "flux"]].copy()
                    result_df.insert(0, "model", name)
                    return result_df
                    
                finally:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                    
            except Exception:
                # 回退到单模型API
                from micom.media import complete_medium as single_complete
                
                med_series = pd.Series({r: float(v) for r, v in candidate_ex.values})
                fixed = single_complete(
                    model=community,
                    medium=med_series,
                    growth=community_growth,
                    min_growth=min_growth,
                    max_import=max_import,
                )
                
                result_df = pd.DataFrame({"reaction": fixed.index, "flux": fixed.values})
                result_df.insert(0, "model", name)
                return result_df
                
        except Exception as e:
            logger.error(f"使用MICOM计算培养基时出错: {str(e)}")
            return pd.DataFrame()
    
    def _recommend_medium(self, all_rows: pd.DataFrame, max_import: float) -> pd.DataFrame:
        """基于全部单菌结果生成推荐培养基"""
        try:
            df_pos = all_rows[all_rows["flux"] > 1e-12].copy()
            if df_pos.empty:
                return pd.DataFrame(columns=["reaction", "suggested_upper_bound"])
            
            # 按反应名聚合统计
            grp = df_pos.groupby("reaction")["flux"]
            summary = pd.DataFrame({
                "models_with_need": grp.size(),
                "mean_flux": grp.mean(),
                "p50_flux": grp.quantile(0.5),
                "p75_flux": grp.quantile(0.75),
                "max_flux": grp.max(),
            }).sort_values(["models_with_need", "p75_flux", "mean_flux"], ascending=False)
            
            # 分档映射
            v = summary["p75_flux"].astype(float)
            sug = v.copy()
            sug = sug.where(v >= 0.01, 0.01)
            sug = sug.mask((v >= 0.01) & (v < 0.1), 0.1)
            sug = sug.mask((v >= 0.1) & (v < 1.0), 1.0)
            sug = sug.mask((v > 1.0) & (v < 10.0), 10.0)
            summary["suggested_upper_bound"] = sug.clip(upper=max_import)
            
            medium_df = summary.reset_index()[["reaction", "suggested_upper_bound"]].copy()
            return medium_df
            
        except Exception as e:
            logger.error(f"生成推荐培养基时出错: {str(e)}")
            return pd.DataFrame()