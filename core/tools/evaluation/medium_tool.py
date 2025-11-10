#!/usr/bin/env python3
"""
推荐培养基构建工具
依托 MICOM 与 COBRA，扫描模型目录，输出 recommended_medium.csv。
"""

from __future__ import annotations

import os
import tempfile
import shutil
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field, validator

try:
    from cobra.io import read_sbml_model, write_sbml_model
except Exception as exc:  # pragma: no cover - import guards
    read_sbml_model = None
    write_sbml_model = None
    COBRA_IMPORT_ERROR = exc
else:
    COBRA_IMPORT_ERROR = None

HAVE_WORKFLOW = False
try:  # pragma: no cover - 环境判定
    from micom.workflows.media import complete_community_medium as wf_complete

    HAVE_WORKFLOW = True
except Exception:
    try:
        from micom.media import complete_medium as single_complete
    except Exception as exc:  # pragma: no cover
        single_complete = None
        MICOM_IMPORT_ERROR = exc
    else:
        MICOM_IMPORT_ERROR = None
else:
    MICOM_IMPORT_ERROR = None

warnings.filterwarnings("ignore", category=FutureWarning)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "Model"
DEFAULT_MEDIUM_DIR = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "Medium"
DEFAULT_OUTPUT_CSV = DEFAULT_MEDIUM_DIR / "recommended_medium.csv"
EXTERNAL_COMPARTMENT_SYNONYMS = {"C_e", "ext", "external", "extracellular"}
TARGET_EXTERNAL = "e"


class MediumBuildInput(BaseModel):
    model_dir: str = Field(
        default=str(DEFAULT_MODEL_DIR),
        description="代谢模型目录（递归搜索 .xml/.sbml）",
    )
    output_csv: str = Field(
        default=str(DEFAULT_OUTPUT_CSV),
        description="推荐培养基输出 CSV（reaction, flux）",
    )
    community_growth: float = Field(default=0.1, description="community growth 参数")
    min_growth: float = Field(default=0.1, description="成员最小生长率要求")
    max_import: float = Field(default=20.0, description="单一底物最大进口上界")
    candidate_ex: Optional[List[str]] = Field(
        default=None,
        description="候选 EX 列表（示例：['EX_glc__D_m=10','EX_o2_m=20'])",
    )

    @validator("community_growth", "min_growth", "max_import")
    def positive_values(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("相关参数必须为正数")
        return value


class MediumBuildTool(BaseTool):
    name: str = "MediumBuildTool"
    description: str = (
        "扫描模型目录，使用 MICOM complete_medium/complete_community_medium 生成推荐培养基 CSV"
    )
    args_schema: type[BaseModel] = MediumBuildInput

    def _run(
        self,
        model_dir: str,
        output_csv: str,
        community_growth: float = 0.1,
        min_growth: float = 0.1,
        max_import: float = 20.0,
        candidate_ex: Optional[List[str]] = None,
    ) -> Dict[str, Optional[str]]:
        if COBRA_IMPORT_ERROR:
            return {
                "status": "error",
                "message": f"导入 cobra 失败: {COBRA_IMPORT_ERROR}",
            }
        if MICOM_IMPORT_ERROR:
            return {
                "status": "error",
                "message": f"导入 micom 失败: {MICOM_IMPORT_ERROR}",
            }

        model_path = Path(model_dir).expanduser()
        if not model_path.is_dir():
            return {
                "status": "error",
                "message": f"模型目录不存在: {model_path}",
            }

        models = self._discover_models(model_path)
        if not models:
            return {
                "status": "error",
                "message": f"未在目录下发现 SBML 模型: {model_path}",
            }

        candidate_df = self._parse_candidate_ex(candidate_ex)
        all_rows: List[pd.DataFrame] = []
        for sbml in models:
            try:
                df = self._run_for_model(
                    sbml,
                    community_growth,
                    min_growth,
                    max_import,
                    candidate_df,
                )
                all_rows.append(df)
            except Exception as exc:  # noqa: BLE001
                return {
                    "status": "error",
                    "message": f"模型 {sbml} 计算失败: {exc}",
                }

        if not all_rows:
            return {
                "status": "error",
                "message": "没有可汇总的结果。",
            }

        merged = pd.concat(all_rows, ignore_index=True)
        medium_df = self._recommend_medium(merged, max_import)
        if medium_df.empty:
            return {
                "status": "error",
                "message": "无正需求通量，无法输出推荐培养基。",
            }

        output_path = Path(output_csv).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        medium_df.rename(columns={"suggested_upper_bound": "flux"}).to_csv(output_path, index=False)

        return {
            "status": "success",
            "output_csv": str(output_path),
            "model_count": len(models),
            "recommendation_count": len(medium_df),
            "workflow_mode": "workflow" if HAVE_WORKFLOW else "single_api",
        }

    @staticmethod
    def _discover_models(model_dir: Path) -> List[str]:
        paths: List[str] = []
        for root, _dirs, files in os.walk(model_dir):
            for fn in files:
                if fn.lower().endswith((".xml", ".sbml")):
                    paths.append(os.path.join(root, fn))
        paths.sort()
        return paths

    @staticmethod
    def _parse_candidate_ex(candidate_ex: Optional[List[str]]) -> pd.DataFrame:
        pairs: List[tuple[str, float]] = []
        if candidate_ex:
            for item in candidate_ex:
                if "=" in item:
                    rid, val = item.split("=", 1)
                    try:
                        pairs.append((rid.strip(), float(val)))
                    except Exception:
                        continue
        if not pairs:
            pairs = [("EX_glc__D_m", 10.0), ("EX_o2_m", 20.0)]
        return pd.DataFrame(pairs, columns=["reaction", "flux"])

    def _run_for_model(
        self,
        sbml_path: str,
        community_growth: float,
        min_growth: float,
        max_import: float,
        candidate_ex: pd.DataFrame,
    ) -> pd.DataFrame:
        name = os.path.splitext(os.path.basename(sbml_path))[0]
        tmpd = tempfile.mkdtemp(prefix=f"cm_sbml_{name}_")
        try:
            model = read_sbml_model(sbml_path)
            model = self._normalize_external_compartment(model)
            tmp_sbml = os.path.join(tmpd, f"{name}.xml")
            write_sbml_model(model, tmp_sbml)

            com = self._build_singleton_community(tmp_sbml, name)
            if HAVE_WORKFLOW:
                df = self._run_with_workflow(
                    com,
                    name,
                    community_growth,
                    min_growth,
                    max_import,
                    candidate_ex,
                )
            else:
                df = self._run_with_single_api(
                    com,
                    name,
                    community_growth,
                    min_growth,
                    max_import,
                    candidate_ex,
                )
            return df
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)

    @staticmethod
    def _normalize_external_compartment(model):
        changed = 0
        for met in model.metabolites:
            comp = (met.compartment or "").strip()
            if comp in EXTERNAL_COMPARTMENT_SYNONYMS:
                met.compartment = TARGET_EXTERNAL
                changed += 1
        if changed:
            print(f" · 统一外液舱室：修正 {changed} 个代谢物 compartment → 'e'")
        return model

    @staticmethod
    def _build_singleton_community(sbml_path: str, name: str):
        tax = (
            pd.DataFrame(
                {
                    "id": [name],
                    "file": [sbml_path],
                    "abundance": [1.0],
                    "biomass": [None],
                }
            )
            .set_index("id", drop=False)
        )
        from micom import Community

        return Community(tax, name=f"COMM_{name}")

    @staticmethod
    def _run_with_workflow(
        com,
        name: str,
        community_growth: float,
        min_growth: float,
        max_import: float,
        candidate_ex: pd.DataFrame,
    ) -> pd.DataFrame:
        tmpd = tempfile.mkdtemp(prefix=f"cm_wf_{name}_")
        try:
            pickle_name = f"{name}.pickle"
            pickle_path = os.path.join(tmpd, pickle_name)
            com.to_pickle(pickle_path)
            manifest = pd.DataFrame(
                {
                    "sample_id": [name],
                    "file": [pickle_name],
                }
            )
            fixed = wf_complete(
                manifest=manifest,
                model_folder=tmpd,
                medium=candidate_ex,
                community_growth=community_growth,
                min_growth=min_growth,
                max_import=max_import,
                summarize=True,
                threads=1,
            )
            out = fixed[["reaction", "flux"]].copy()
            out.insert(0, "model", name)
            return out
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)

    @staticmethod
    def _run_with_single_api(
        com,
        name: str,
        community_growth: float,
        min_growth: float,
        max_import: float,
        candidate_ex: pd.DataFrame,
    ) -> pd.DataFrame:
        med_series = pd.Series({r: float(v) for r, v in candidate_ex.values})
        fixed = single_complete(
            model=com,
            medium=med_series,
            growth=community_growth,
            min_growth=min_growth,
            max_import=max_import,
        )
        df = pd.DataFrame({"reaction": fixed.index, "flux": fixed.values})
        df.insert(0, "model", name)
        return df

    @staticmethod
    def _recommend_medium(all_rows: pd.DataFrame, max_import: float) -> pd.DataFrame:
        df_pos = all_rows[all_rows["flux"] > 1e-12].copy()
        if df_pos.empty:
            return pd.DataFrame(columns=["reaction", "suggested_upper_bound"])

        grp = df_pos.groupby("reaction")["flux"]
        summary = pd.DataFrame(
            {
                "models_with_need": grp.size(),
                "mean_flux": grp.mean(),
                "p50_flux": grp.quantile(0.5),
                "p75_flux": grp.quantile(0.75),
                "max_flux": grp.max(),
            }
        ).sort_values(
            ["models_with_need", "p75_flux", "mean_flux"],
            ascending=False,
        )

        v = summary["p75_flux"].astype(float)
        sug = v.copy()
        sug = sug.where(v >= 0.01, 0.01)
        sug = sug.mask((v >= 0.01) & (v < 0.1), 0.1)
        sug = sug.mask((v >= 0.1) & (v < 1.0), 1.0)
        sug = sug.mask((v >= 1.0) & (v < 10.0), 10.0)
        summary["suggested_upper_bound"] = sug.clip(upper=max_import)
        return summary.reset_index()[["reaction", "suggested_upper_bound"]]


__all__ = ["MediumBuildTool", "MediumBuildInput"]
