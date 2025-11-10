#!/usr/bin/env python3
"""
MICOM 两步优化工具
基于推荐培养基评估微生物群落对污染物（EX_dbp_m）的摄入能力。
"""

from __future__ import annotations

import os
import shutil
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field, validator

try:
    from cobra.io import read_sbml_model, write_sbml_model
except Exception as exc:  # pragma: no cover
    read_sbml_model = None
    write_sbml_model = None
    COBRA_ERROR = exc
else:
    COBRA_ERROR = None

warnings.filterwarnings("ignore", category=FutureWarning)

HAVE_WORKFLOW = False
try:  # pragma: no cover - 环境判定
    from micom.workflows.media import complete_community_medium as wf_complete

    HAVE_WORKFLOW = True
except Exception:
    try:
        from micom.media import complete_medium as single_complete
    except Exception as exc:  # pragma: no cover
        single_complete = None
        MICOM_ERROR = exc
    else:
        MICOM_ERROR = None
else:
    MICOM_ERROR = None

from micom import Community

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "Model_pathway"
DEFAULT_MEDIUM_CSV = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "Medium" / "recommended_medium.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "MICOM"

EXTERNAL_COMPARTMENT_SYNONYMS = {"C_e", "ext", "external", "extracellular"}
TARGET_EXTERNAL = "e"
DBP_EX_ID = "EX_dbp_m"
MAX_IMPORT = 1000.0
EPSILON = 1.0
BIS_TOL = 1e-3
MAX_ITER = 30
MU_TOL = 1e-4


class MicomToolInput(BaseModel):
    model_dir: str = Field(
        default=str(DEFAULT_MODEL_DIR),
        description="代谢模型目录（包含添加通路后的 SBML）",
    )
    medium_csv: str = Field(
        default=str(DEFAULT_MEDIUM_CSV),
        description="推荐培养基 CSV，包含 reaction + flux",
    )
    alpha: float = Field(default=0.7, description="阶段二增长率下界系数 α")
    output_dir: str = Field(
        default=str(DEFAULT_OUTPUT_DIR),
        description="结果输出目录（默认 test_results/EvaluateAgent/MICOM）",
    )
    alpha_scan: bool = Field(default=False, description="是否启用 α 扫描")
    alphas: Optional[str] = Field(
        default=None,
        description="自定义 α 列表，逗号分隔，如 0.5,0.6,0.7；仅在 alpha_scan 为 True 时使用",
    )
    robust: bool = Field(default=False, description="是否启用鲁棒性分析（逐一移除成员）")

    @validator("alpha")
    def validate_alpha(cls, value: float) -> float:
        if not 0 < value <= 1.0:
            raise ValueError("alpha 必须在 (0,1] 范围内")
        return value


class MicomSimulationTool(BaseTool):
    """MICOM 两步优化"""

    name: str = "MicomSimulationTool"
    description: str = "在推荐培养基下执行 MICOM 两阶段优化，评估社区对 DBP 的摄入能力"
    args_schema: type[BaseModel] = MicomToolInput

    def _run(
        self,
        model_dir: str,
        medium_csv: str,
        alpha: float = 0.7,
        output_dir: str = str(DEFAULT_OUTPUT_DIR),
        alpha_scan: bool = False,
        alphas: Optional[str] = None,
        robust: bool = False,
    ) -> Dict[str, Any]:
        if COBRA_ERROR:
            return {"status": "error", "message": f"导入 cobra 失败: {COBRA_ERROR}"}
        if MICOM_ERROR:
            return {"status": "error", "message": f"导入 micom 失败: {MICOM_ERROR}"}

        model_path = Path(model_dir).expanduser()
        medium_path = Path(medium_csv).expanduser()
        out_dir = Path(output_dir).expanduser()
        if not model_path.is_dir():
            return {"status": "error", "message": f"模型目录不存在: {model_path}"}
        if not medium_path.is_file():
            return {"status": "error", "message": f"培养基文件不存在: {medium_path}"}
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            medium = self._read_medium_csv(medium_path)
            medium = self._medium_plus_dbp(medium, dbp_upper=20.0)
            community, tmpd, tax_base, members = self._build_community_from_dir(model_path)
            try:
                applied, missing = self._apply_medium_via_micom(community, medium)
            except Exception as exc:
                shutil.rmtree(tmpd, ignore_errors=True)
                return {"status": "error", "message": f"设置 community.medium 失败: {exc}"}

            biomass_max = self._step1_max_growth(community)
            if biomass_max <= 1e-12:
                shutil.rmtree(tmpd, ignore_errors=True)
                return {"status": "error", "message": "阶段一最大生长为 0，无法执行阶段二。"}

            stage2_growth, dbp_flux, members_df = self._step2_max_dbp_uptake(community, alpha, biomass_max)
            biomass_stage2 = min(stage2_growth, biomass_max + 1e-6)

            summary = pd.DataFrame(
                [
                    {
                        "model_count": len(community.taxa),
                        "Community": ",".join(members),
                        "Biomass": biomass_stage2,
                        "DBP_flux": dbp_flux,
                    }
                ]
            )

            alpha_scan_df = None
            if alpha_scan:
                scan_list = self._parse_alphas(alphas)
                alpha_scan_df = self._run_alpha_scan(community, biomass_max, scan_list)

            robust_df = None
            if robust:
                robust_df = self._run_robust_scan(community, medium, tax_base, alpha)

            output_file = out_dir / "Result_MICOM.xlsx"
            with pd.ExcelWriter(output_file) as writer:
                summary.to_excel(writer, index=False, sheet_name="Simulate result")
                mg_df = members_df if isinstance(members_df, pd.DataFrame) else None
                if mg_df is not None and not mg_df.empty:
                    mg_df.to_excel(writer, index=False, sheet_name="Microbial growth")
                if alpha_scan_df is not None:
                    alpha_scan_df.to_excel(writer, index=False, sheet_name="Alpha scan")
                if robust_df is not None:
                    robust_df.to_excel(writer, index=False, sheet_name="Robust")

            shutil.rmtree(tmpd, ignore_errors=True)
            if alpha_scan_df is not None:
                alpha_scan_df.to_csv(out_dir / "Result_MICOM_alpha_scan.csv", index=False)

            return {
                "status": "success",
                "output_file": str(output_file),
                "alpha": alpha,
                "applied_medium": applied,
                "missing_medium": missing,
                "biomass_max": biomass_max,
                "biomass_stage2": biomass_stage2,
                "dbp_flux": dbp_flux,
                "alpha_scan": str(out_dir / "Result_MICOM_alpha_scan.csv")
                if alpha_scan_df is not None
                else None,
            }
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "message": f"MICOM 计算失败: {exc}"}

    # ---------- helper functions ----------
    def _read_medium_csv(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        if "reaction" not in df.columns:
            raise ValueError("培养基 CSV 必须包含 'reaction' 列")
        if "flux" in df.columns:
            df = df[["reaction", "flux"]].rename(columns={"flux": "upper"})
        elif "suggested_upper_bound" in df.columns:
            df = df[["reaction", "suggested_upper_bound"]].rename(columns={"suggested_upper_bound": "upper"})
        else:
            raise ValueError("培养基 CSV 必须包含 'flux' 或 'suggested_upper_bound' 列")
        df["reaction"] = df["reaction"].astype(str)
        df["upper"] = pd.to_numeric(df["upper"], errors="coerce").fillna(0.0)
        return df

    def _medium_plus_dbp(self, med: pd.DataFrame, dbp_upper: float) -> pd.DataFrame:
        med = med.copy()
        mask = med["reaction"] == DBP_EX_ID
        if mask.any():
            med.loc[mask, "upper"] = med.loc[mask, "upper"].clip(lower=dbp_upper)
        else:
            med = pd.concat(
                [med, pd.DataFrame({"reaction": [DBP_EX_ID], "upper": [dbp_upper]})],
                ignore_index=True,
            )
        return med

    def _discover_models(self, model_dir: Path) -> List[str]:
        paths: List[str] = []
        for root, _dirs, files in os.walk(model_dir):
            for fn in files:
                if fn.lower().endswith((".xml", ".sbml")):
                    paths.append(os.path.join(root, fn))
        paths.sort()
        return paths

    def _build_community_from_dir(self, models_dir: Path) -> Tuple[Community, str, pd.DataFrame, List[str]]:
        model_paths = self._discover_models(models_dir)
        if not model_paths:
            raise FileNotFoundError(f"未在目录下发现 SBML：{models_dir}")

        tmpd = tempfile.mkdtemp(prefix="community_tmp_")
        rows = []
        member_names: List[str] = []
        try:
            for f in model_paths:
                name = os.path.splitext(os.path.basename(f))[0]
                member_names.append(name)
                model = read_sbml_model(f)
                model = self._normalize_external_compartment(model)
                tmp_sbml = os.path.join(tmpd, f"{name}.xml")
                write_sbml_model(model, tmp_sbml)
                rows.append(
                    {
                        "id": name,
                        "file": tmp_sbml,
                        "abundance": 1.0,
                        "biomass": None,
                    }
                )
            tax = pd.DataFrame(rows).set_index("id", drop=False)
            community = Community(tax, name="COMM_DBP")
            return community, tmpd, tax, member_names
        except Exception:
            shutil.rmtree(tmpd, ignore_errors=True)
            raise

    def _normalize_external_compartment(self, model):
        changed = 0
        for met in model.metabolites:
            comp = (met.compartment or "").strip()
            if comp in EXTERNAL_COMPARTMENT_SYNONYMS:
                met.compartment = TARGET_EXTERNAL
                changed += 1
        return model

    def _apply_medium_via_micom(self, comm: Community, medium_df: pd.DataFrame) -> Tuple[int, int]:
        medium_df = medium_df.copy()
        medium_df["upper"] = pd.to_numeric(medium_df["upper"], errors="coerce").fillna(0.0)
        pairs = [(str(rid).strip(), float(up)) for rid, up in medium_df.values]
        applied, missing = 0, 0
        med_dict = {}
        for rid, up in pairs:
            if rid in comm.reactions:
                med_dict[rid] = up
                applied += 1
            else:
                missing += 1
        comm.medium = med_dict
        return applied, missing

    def _step1_max_growth(self, comm: Community) -> float:
        try:
            sol = comm.cooperative_tradeoff(fraction=1.0, fluxes=False)
            return float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)
        except Exception:
            sol = comm.optimize()
            return float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)

    @contextmanager
    def _fixed_bound(self, comm: Community, rxn_id: str, value: float):
        rxn = comm.reactions.get_by_id(rxn_id)
        old_lb, old_ub = rxn.lower_bound, rxn.upper_bound
        try:
            rxn.lower_bound = value
            rxn.upper_bound = value
            yield rxn
        finally:
            eps = 1e-9
            lb, ub = old_lb, old_ub
            if lb > ub:
                if lb - ub <= eps:
                    ub = lb
                else:
                    lb, ub = min(lb, ub), max(lb, ub)
            try:
                rxn.upper_bound = 1e9
                rxn.lower_bound = lb
                rxn.upper_bound = ub
            except Exception:
                rxn.lower_bound = min(lb, ub)
                rxn.upper_bound = max(lb, ub)

    def _ct_max_growth_under_ex(self, comm: Community, ex_id: str, f_value: float) -> float:
        if ex_id not in comm.reactions:
            return float("nan")
        with self._fixed_bound(comm, ex_id, f_value):
            try:
                sol = comm.cooperative_tradeoff(fraction=1.0, fluxes=False)
                return float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)
            except Exception:
                return 0.0

    def _unconstrained_min_ex(self, comm: Community, ex_id: str) -> float:
        if ex_id not in comm.reactions:
            return float("nan")
        rxn = comm.reactions.get_by_id(ex_id)
        old_obj, old_dir = comm.objective, comm.objective_direction
        try:
            comm.objective = rxn
            comm.objective_direction = "min"
            sol = comm.optimize()
            return float(getattr(sol, "objective_value", 0.0) or 0.0)
        finally:
            comm.objective = old_obj
            comm.objective_direction = old_dir

    def _step2_max_dbp_uptake(
        self,
        comm: Community,
        alpha: float,
        biomass_max: float,
    ) -> Tuple[float, float, Optional[pd.DataFrame]]:
        if DBP_EX_ID not in comm.reactions:
            return float("nan"), float("nan"), None

        f_min = self._unconstrained_min_ex(comm, DBP_EX_ID)
        target = alpha * biomass_max
        f_hi = -float(EPSILON)
        mu_hi = self._ct_max_growth_under_ex(comm, DBP_EX_ID, f_hi)

        if mu_hi < target - 1e-12:
            left, right = 0.0, f_hi
            mu_left = self._ct_max_growth_under_ex(comm, DBP_EX_ID, left)
            if mu_left < target - 1e-12:
                with self._fixed_bound(comm, DBP_EX_ID, 0.0):
                    sol = comm.cooperative_tradeoff(fraction=1.0, fluxes=True)
                    g = float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)
                    mg = self._members_growth_table(sol)
                    return g, 0.0, mg
            best_f, best_mu = left, mu_left
            for _ in range(MAX_ITER):
                mid = 0.5 * (left + right)
                mu_mid = self._ct_max_growth_under_ex(comm, DBP_EX_ID, mid)
                if mu_mid >= target:
                    best_f, best_mu = mid, mu_mid
                    right = mid
                else:
                    left = mid
                if abs(right - left) <= BIS_TOL or abs(mu_mid - target) <= MU_TOL:
                    break
            with self._fixed_bound(comm, DBP_EX_ID, best_f):
                sol = comm.cooperative_tradeoff(fraction=1.0, fluxes=True)
                g = float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)
                mg = self._members_growth_table(sol)
                return g, best_f, mg

        f_left = min(f_min, f_hi)
        f_right = max(f_min, f_hi)
        mu_left = self._ct_max_growth_under_ex(comm, DBP_EX_ID, f_left)

        if mu_left < target - 1e-12:
            left, right = f_left, f_hi
            best_f, best_mu = f_hi, mu_hi
            for _ in range(MAX_ITER):
                mid = 0.5 * (left + right)
                mu_mid = self._ct_max_growth_under_ex(comm, DBP_EX_ID, mid)
                if mu_mid >= target:
                    best_f, best_mu = mid, mu_mid
                    right = mid
                else:
                    left = mid
                if abs(right - left) <= BIS_TOL or abs(mu_mid - target) <= MU_TOL:
                    break
            with self._fixed_bound(comm, DBP_EX_ID, best_f):
                sol = comm.cooperative_tradeoff(fraction=1.0, fluxes=True)
                g = float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)
                mg = self._members_growth_table(sol)
                return g, best_f, mg

        with self._fixed_bound(comm, DBP_EX_ID, f_left):
            sol = comm.cooperative_tradeoff(fraction=1.0, fluxes=True)
            g = float(getattr(sol, "growth_rate", getattr(sol, "objective_value", 0.0)) or 0.0)
            mg = self._members_growth_table(sol)
            return g, f_left, mg

    def _members_growth_table(self, sol: Any) -> Optional[pd.DataFrame]:
        if sol is None:
            return None
        df = getattr(sol, "members", None)
        if df is None and hasattr(sol, "solution"):
            df = getattr(sol.solution, "members", None)
        if not isinstance(df, pd.DataFrame) or df.empty:
            return None
        try:
            df = df[~df.index.astype(str).str.lower().eq("medium")]
        except Exception:
            pass
        col = None
        for c in df.columns:
            if "growth" in str(c).lower():
                col = c
                break
        if col is None:
            return None
        out = pd.DataFrame(
            {
                "member": df.index.astype(str),
                "growth_rate": pd.to_numeric(df[col], errors="coerce"),
            }
        ).fillna(0.0)
        return out

    def _run_alpha_scan(self, comm: Community, biomass_max: float, alphas: Iterable[float]) -> pd.DataFrame:
        rows = []
        for a in alphas:
            g, f, _ = self._step2_max_dbp_uptake(comm, float(a), biomass_max)
            rows.append(
                {
                    "alpha": float(a),
                    "biomass_max": biomass_max,
                    "growth_at_f": g,
                    "dbp_flux_f": f,
                }
            )
        return pd.DataFrame(rows)

    def _parse_alphas(self, s: Optional[str]) -> List[float]:
        if not s:
            return [0.5, 0.6, 0.7, 0.8, 0.9]
        vals: List[float] = []
        for tok in s.split(","):
            tok = tok.strip()
            if not tok:
                continue
            try:
                v = float(tok)
                if 0 < v <= 1.0:
                    vals.append(v)
            except Exception:
                continue
        return sorted(set(vals)) or [0.5, 0.6, 0.7, 0.8, 0.9]

    def _run_robust_scan(
        self,
        comm: Community,
        medium: pd.DataFrame,
        tax_base: pd.DataFrame,
        alpha: float,
    ) -> Optional[pd.DataFrame]:
        if not isinstance(tax_base, pd.DataFrame) or tax_base.empty or "id" not in tax_base.columns:
            return None
        results = []
        taxa_ids = tax_base["id"].astype(str).tolist()
        for remove_id in taxa_ids:
            taxa_new = tax_base[tax_base["id"].astype(str) != str(remove_id)].copy()
            if taxa_new.empty:
                results.append({"Removal species": remove_id, "DBP flux": float("nan"), "Biomass": float("nan")})
                continue
            try:
                com_new = Community(taxa_new, name="COMM_DBP_Robust")
                self._apply_medium_via_micom(com_new, medium)
                biomass_rb = self._step1_max_growth(com_new)
                if biomass_rb <= 1e-12:
                    results.append({"Removal species": remove_id, "DBP flux": float("nan"), "Biomass": float("nan")})
                    continue
                stage2_growth_rb, dbp_flux_rb, _ = self._step2_max_dbp_uptake(com_new, alpha, biomass_rb)
                biomass_stage2_rb = min(stage2_growth_rb, biomass_rb + 1e-6)
                results.append(
                    {
                        "Removal species": remove_id,
                        "DBP flux": dbp_flux_rb,
                        "Biomass": biomass_stage2_rb,
                    }
                )
            except Exception:
                results.append({"Removal species": remove_id, "DBP flux": float("nan"), "Biomass": float("nan")})
        return pd.DataFrame(results)


__all__ = ["MicomSimulationTool", "MicomToolInput"]
