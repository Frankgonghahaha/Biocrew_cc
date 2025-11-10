#!/usr/bin/env python3
"""
AddPathwayTool
为已有代谢模型批量添加污染物降解路径（DBP → phthalate + Butanol），
并输出到指定目录，供后续评估使用。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field

try:
    from cobra import Model, Reaction, Metabolite
    from cobra.io import read_sbml_model, write_sbml_model
except Exception as exc:  # pragma: no cover - cobra 未安装
    COBRA_IMPORT_ERROR = exc
else:
    COBRA_IMPORT_ERROR = None

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "Model"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "test_results" / "EvaluateAgent" / "Model_pathway"

NEW_METABOLITES: Dict[str, Tuple[str, Iterable[str], Optional[str]]] = {
    "dbp": ("Dibutyl phthalate", ["c", "e"], "C16H22O4"),
    "phthalate": ("Phthalic acid", ["c", "e"], "C8H6O4"),
    "btoh": ("Butanol", ["c", "e"], "C4H10O"),
    "h2o": ("Water", ["c", "e"], "H2O"),
    "o2": ("Oxygen", ["c", "e"], "O2"),
    "nadh": ("NADH", ["c"], None),
    "nad": ("NAD+", ["c"], None),
    "h": ("Proton", ["c", "e"], "H"),
}


class AddPathwayInput(BaseModel):
    """AddPathwayTool 输入参数"""

    model_dir: str = Field(
        default=str(DEFAULT_MODEL_DIR),
        description="原始代谢模型目录（默认 test_results/EvaluateAgent/Model）",
    )
    output_dir: str = Field(
        default=str(DEFAULT_OUTPUT_DIR),
        description="添加路径后的模型输出目录（默认 test_results/EvaluateAgent/Model_pathway）",
    )
    only_files: Optional[List[str]] = Field(
        default=None,
        description="仅处理指定文件名（相对 model_dir）",
    )


class AddPathwayTool(BaseTool):
    """批量为模型添加 DBP 降解通路"""

    name: str = "AddPathwayTool"
    description: str = "为模型目录下的 SBML 模型添加 DBP→phthalate + butanol 的降解路径"
    args_schema: type[BaseModel] = AddPathwayInput

    def _run(
        self,
        model_dir: str,
        output_dir: str,
        only_files: Optional[List[str]] = None,
    ) -> Dict[str, Optional[str]]:
        if COBRA_IMPORT_ERROR:
            return {
                "status": "error",
                "message": f"导入 cobra 失败: {COBRA_IMPORT_ERROR}",
            }

        src = Path(model_dir).expanduser()
        dst = Path(output_dir).expanduser()
        if not src.is_dir():
            return {
                "status": "error",
                "message": f"模型目录不存在: {src}",
            }
        dst.mkdir(parents=True, exist_ok=True)

        if only_files:
            targets = [src / f for f in only_files]
        else:
            targets = sorted(p for p in src.iterdir() if p.suffix.lower() in {".xml", ".sbml"})

        if not targets:
            return {
                "status": "error",
                "message": f"未在目录下发现 SBML 模型: {src}",
            }

        generated = []
        for file_path in targets:
            if not file_path.is_file():
                continue
            out_file = dst / file_path.name
            if out_file.exists():
                generated.append(str(out_file))
                continue
            try:
                model = read_sbml_model(str(file_path))
                self._ensure_metabolites(model)
                self._add_dbp_reactions(model)
                write_sbml_model(model, str(out_file))
                generated.append(str(out_file))
            except Exception as exc:  # noqa: BLE001
                return {
                    "status": "error",
                    "message": f"处理模型 {file_path.name} 失败: {exc}",
                }

        return {
            "status": "success",
            "output_dir": str(dst),
            "generated_files": generated,
            "model_count": len(generated),
        }

    def _ensure_metabolites(self, model: Model) -> None:
        for base_id, (name, compartments, formula) in NEW_METABOLITES.items():
            for comp in compartments:
                met_id = f"{base_id}_{comp}"
                if met_id in model.metabolites:
                    continue
                met = Metabolite(id=met_id, name=name or met_id, compartment=comp)
                if formula:
                    met.formula = formula
                model.add_metabolites([met])

    def _ensure_simple_metabolite(self, model: Model, met_id: str) -> Metabolite:
        if met_id in model.metabolites:
            return model.metabolites.get_by_id(met_id)
        comp = met_id.split("_")[-1] if "_" in met_id else "c"
        met = Metabolite(id=met_id, name=met_id, compartment=comp)
        model.add_metabolites([met])
        return met

    def _ensure_reaction(
        self,
        model: Model,
        rxn_id: str,
        stoich: Dict[str, float],
        lower_bound: float,
        upper_bound: float,
        rxn_name: Optional[str] = None,
    ) -> Reaction:
        if rxn_id in model.reactions:
            return model.reactions.get_by_id(rxn_id)
        for met_id in stoich.keys():
            if met_id not in {m.id for m in model.metabolites}:
                self._ensure_simple_metabolite(model, met_id)
        rxn = Reaction(rxn_id, name=rxn_name or rxn_id, lower_bound=lower_bound, upper_bound=upper_bound)
        rxn.add_metabolites({model.metabolites.get_by_id(k): v for k, v in stoich.items()})
        model.add_reactions([rxn])
        return rxn

    def _add_dbp_reactions(self, model: Model) -> None:
        self._ensure_reaction(model, "EX_dbp_e", {"dbp_e": -1.0}, -1000.0, 0.0, "DBP exchange (uptake)")
        self._ensure_reaction(model, "EX_phthalate_e", {"phthalate_e": -1.0}, -1000.0, 1000.0, "Phthalate exchange")
        self._ensure_reaction(model, "EX_btoh_e", {"btoh_e": -1.0}, -1000.0, 1000.0, "Butanol exchange")
        self._ensure_reaction(model, "TRANS_o2", {"o2_c": -1.0, "o2_e": 1.0}, -1000.0, 1000.0, "o2 transport c<->e")
        self._ensure_reaction(model, "TRANS_dbp", {"dbp_c": -1.0, "dbp_e": 1.0}, -1000.0, 1000.0, "DBP transport")
        self._ensure_reaction(
            model,
            "TRANS_phthalate",
            {"phthalate_c": -1.0, "phthalate_e": 1.0},
            -1000.0,
            1000.0,
            "Phthalate transport",
        )
        self._ensure_reaction(
            model,
            "TRANS_btoh",
            {"btoh_c": -1.0, "btoh_e": 1.0},
            -1000.0,
            1000.0,
            "Butanol transport",
        )
        self._ensure_reaction(
            model,
            "DBP_HYDRO_BTOH",
            {
                "dbp_c": -1.0,
                "h2o_c": -2.0,
                "nadh_c": -1.0,
                "h_c": -1.0,
                "phthalate_c": 1.0,
                "btoh_c": 2.0,
                "nad_c": 1.0,
            },
            0.0,
            1000.0,
            "DBP hydrolysis to phthalate + 2 butanol (NADH-dependent)",
        )


__all__ = ["AddPathwayTool", "AddPathwayInput"]
