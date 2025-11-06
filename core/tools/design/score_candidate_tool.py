#!/usr/bin/env python3
"""
候选微生物综合评分工具（新版）
串联 JSON 解析、酶降解评分、环境适应性评分与单菌综合评分，
输出与历史 Result2_candidate_scores.csv 对应的记录。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from crewai.tools import BaseTool
except ImportError:  # pragma: no cover - fallback
    class BaseTool:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()

    print("Warning: crewai 未安装，ScoreCandidateTool 将使用简化 BaseTool。")

from pydantic import BaseModel, Field, root_validator

from core.tools.design.parse1_json_tool import ParseDegradationJSONTool
from core.tools.design.parse2_json_tool import ParseEnvironmentJSONTool
from core.tools.design.score_environment_tool import (
    ScoreEnvironmentTool,
    SpeciesEnvironmentRequest,
    TargetEnvironment,
)
from core.tools.design.score_enzyme_degradation_tool import (
    ScoreEnzymeDegradationTool,
    SpeciesEnzymePayload,
)
from core.tools.design.score_single_species_tool import (
    EnvironmentScoreEntry,
    EnzymeScoreEntry,
    ScoreSingleSpeciesTool,
    SpeciesEntry,
)


class ScoreCandidateInput(BaseModel):
    """综合评分工具的输入"""

    json_path: Optional[str] = Field(
        default=None,
        description="IdentificationAgent 输出 JSON 文件路径。",
    )
    parsed_degradation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="ParseDegradationJSONTool 的结果，可避免重复解析。",
    )
    parsed_environment: Optional[Dict[str, Any]] = Field(
        default=None,
        description="ParseEnvironmentJSONTool 的结果，可避免重复解析。",
    )
    weight_kcat: float = Field(default=0.5, description="kcat 归一化分量权重")
    weight_env: float = Field(default=0.4, description="环境软评分权重")
    weight_enzyme_diversity: float = Field(
        default=0.1,
        description="酶多样性归一化分量权重",
    )
    max_records: Optional[int] = Field(
        default=10,
        description="返回前 N 条记录；None 表示不过滤。",
    )
    trim_details: bool = Field(
        default=True,
        description="是否精简中间结果（移除冗长字段，如序列、全部环境记录等）。",
    )

    @root_validator
    def ensure_source(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("json_path") and (
            values.get("parsed_degradation") is None
            or values.get("parsed_environment") is None
        ):
            raise ValueError(
                "必须提供 json_path，或同时提供 parsed_degradation 与 parsed_environment 数据。"
            )
        return values


class ScoreCandidateTool(BaseTool):
    """功能菌与互补菌综合评分工具（新版管线）"""

    name: str = "ScoreCandidateTool"
    description: str = (
        "综合 ParseDegradationJSONTool、ParseEnvironmentJSONTool、"
        "ScoreEnzymeDegradationTool、ScoreEnvironmentTool 与 ScoreSingleSpeciesTool，"
        "输出菌株的 S_microbe 评分及中间数据。"
    )
    args_schema: type[BaseModel] = ScoreCandidateInput

    def __init__(self) -> None:
        super().__init__()
        self._parse_degradation = ParseDegradationJSONTool()
        self._parse_environment = ParseEnvironmentJSONTool()
        self._enzyme_tool = ScoreEnzymeDegradationTool()
        self._environment_tool = ScoreEnvironmentTool()
        self._single_tool = ScoreSingleSpeciesTool()

    def _run(
        self,
        json_path: Optional[str] = None,
        parsed_degradation: Optional[Dict[str, Any]] = None,
        parsed_environment: Optional[Dict[str, Any]] = None,
        weight_kcat: float = 0.5,
        weight_env: float = 0.4,
        weight_enzyme_diversity: float = 0.1,
        max_records: Optional[int] = 10,
        trim_details: bool = True,
    ) -> Dict[str, Any]:
        try:
            degradation_payload = parsed_degradation
            environment_payload = parsed_environment

            if json_path:
                if degradation_payload is None:
                    degradation_payload = self._parse_degradation._run(json_path=json_path)
                if environment_payload is None:
                    environment_payload = self._parse_environment._run(json_path=json_path)

            if not degradation_payload or degradation_payload.get("status") != "success":
                raise ValueError("ParseDegradationJSONTool 未成功返回数据。")
            if not environment_payload or environment_payload.get("status") != "success":
                raise ValueError("ParseEnvironmentJSONTool 未成功返回数据。")

            pollutant_smiles = (
                degradation_payload.get("pollutant_smiles")
                or environment_payload.get("pollutant_smiles")
            )
            if not pollutant_smiles:
                raise ValueError("缺少污染物 SMILES，无法执行酶降解评分。")

            species_entries = environment_payload.get("species") or []
            if not species_entries:
                raise ValueError("环境解析结果中缺少物种清单。")

            target_env_data = environment_payload.get("target_environment") or {}
            target_env = TargetEnvironment(**target_env_data)

            degradation_map = {
                self._normalize(item.get("strain", "")): item
                for item in degradation_payload.get("functional_records", [])
            }

            species_payload_raw = degradation_payload.get("species_payload") or []
            species_payload_map = {
                self._normalize(item.get("strain", "")): item for item in species_payload_raw
            }

            species_payload: List[SpeciesEnzymePayload] = []
            for item in species_entries:
                strain = self._normalize(item.get("strain", ""))
                if not strain:
                    continue
                payload_dict = species_payload_map.get(strain)
                if payload_dict:
                    payload = SpeciesEnzymePayload.parse_obj(
                        {
                            **payload_dict,
                            "strain": item.get("strain", strain),
                            "source": payload_dict.get("source") or item.get("source"),
                        }
                    )
                else:
                    deg_entry = degradation_map.get(strain, {})
                    enzyme_list = deg_entry.get("enzymes", []) or []
                    payload = SpeciesEnzymePayload(
                        strain=item.get("strain", strain),
                        sequences=deg_entry.get("enzyme_sequences") or [],
                        source=item.get("source"),
                        enzyme_names=[enzyme.get("name") for enzyme in enzyme_list if enzyme.get("name")] or None,
                        enzyme_diversity=deg_entry.get("enzyme_diversity"),
                    )
                species_payload.append(payload)

            enzyme_result = self._enzyme_tool._run(
                pollutant_smiles=pollutant_smiles,
                species=species_payload,
            )
            if enzyme_result.get("status") != "success":
                raise ValueError(enzyme_result.get("message", "酶降解评分失败"))

            env_requests = [
                SpeciesEnvironmentRequest(
                    strain=self._normalize(item.get("strain", "")),
                    source=item.get("source"),
                )
                for item in species_entries
                if item.get("strain")
            ]
            environment_result = self._environment_tool._run(
                species=env_requests,
                target_environment=target_env,
            )
            if environment_result.get("status") != "success":
                raise ValueError(environment_result.get("message", "环境评分失败"))

            single_result = self._single_tool._run(
                species=[
                    SpeciesEntry(
                        strain=self._normalize(item.get("strain", "")),
                        source=item.get("source"),
                    )
                    for item in species_entries
                    if item.get("strain")
                ],
                enzyme_results=[
                    EnzymeScoreEntry.parse_obj(record)
                    for record in enzyme_result.get("results", [])
                ],
                environment_results=[
                    EnvironmentScoreEntry.parse_obj(record)
                    for record in environment_result.get("results", [])
                ],
                weight_kcat=weight_kcat,
                weight_env=weight_env,
                weight_enzyme_diversity=weight_enzyme_diversity,
                top_n=max_records,
            )
            if single_result.get("status") != "success":
                raise ValueError(single_result.get("message", "单菌综合评分失败"))

            trimmed_single = self._trim_single_result(single_result, max_records)
            trimmed_enzyme = self._trim_enzyme_results(enzyme_result, max_records, trim_details)
            trimmed_environment = self._trim_environment_results(environment_result, max_records, trim_details)

            return {
                "status": "success",
                "pollutant_smiles": pollutant_smiles,
                "target_environment": target_env.dict(),
                "single_species": trimmed_single,
                "enzyme_results": trimmed_enzyme,
                "environment_results": trimmed_environment,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"候选菌评分失败: {exc}",
            }

    @staticmethod
    def _normalize(name: str) -> str:
        return " ".join(name.replace("（", "(").replace("）", ")").split()).strip()

    @staticmethod
    def _trim_single_result(
        result: Dict[str, Any],
        max_records: Optional[int],
    ) -> Dict[str, Any]:
        records = result.get("records") or []
        if max_records is not None and max_records > 0:
            records = records[:max_records]
        trimmed_summary = dict(result.get("summary") or {})
        trimmed_summary["returned_count"] = len(records)
        trimmed_summary.setdefault("total_count", trimmed_summary.get("total_count", len(records)))
        return {
            "status": result.get("status"),
            "records": records,
            "summary": trimmed_summary,
        }

    @staticmethod
    def _trim_enzyme_results(
        result: Dict[str, Any],
        max_records: Optional[int],
        trim_details: bool,
    ) -> Dict[str, Any]:
        records = result.get("results") or []
        if trim_details:
            for item in records:
                item.pop("entries", None)
        if max_records is not None and max_records > 0:
            records = records[:max_records]
        summary = dict(result.get("summary") or {})
        summary["returned_count"] = len(records)
        summary.setdefault("total_count", summary.get("total_count", len(records)))
        return {
            "status": result.get("status"),
            "pollutant_smiles": result.get("pollutant_smiles"),
            "reference_kcat": result.get("reference_kcat"),
            "results": records,
            "summary": summary,
        }

    @staticmethod
    def _trim_environment_results(
        result: Dict[str, Any],
        max_records: Optional[int],
        trim_details: bool,
    ) -> Dict[str, Any]:
        records = result.get("results") or []
        trimmed_records: List[Dict[str, Any]] = []
        for item in records:
            if trim_details:
                record_copy = dict(item)
                env_records = record_copy.get("records") or []
                if env_records:
                    record_copy["records"] = [env_records[0]]
            else:
                record_copy = item
            trimmed_records.append(record_copy)
        if max_records is not None and max_records > 0:
            trimmed_records = trimmed_records[:max_records]
        return {
            "status": result.get("status"),
            "target_environment": result.get("target_environment"),
            "results": trimmed_records,
        }


__all__ = ["ScoreCandidateTool", "ScoreCandidateInput"]
