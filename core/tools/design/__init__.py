#!/usr/bin/env python3
"""
设计工具包初始化文件（采用延迟加载避免不必要的依赖）。
"""

from __future__ import annotations

from importlib import import_module
from typing import Tuple

_LAZY_IMPORTS: dict[str, Tuple[str, str]] = {
    # 数据库工具
    "ProteinSequenceQuerySQLTool": (".protein_sequence_query_sql", "ProteinSequenceQuerySQLTool"),
    "ProteinSequenceQuerySQLToolUpdated": (".protein_sequence_query_sql_updated", "ProteinSequenceQuerySQLToolUpdated"),
    "DegradingMicroorganismIdentificationTool": (
        ".degrading_microorganism_identification_tool",
        "DegradingMicroorganismIdentificationTool",
    ),
    # 预测与评分工具
    "ParseDegradationJSONTool": (".parse1_json_tool", "ParseDegradationJSONTool"),
    "ParseEnvironmentJSONTool": (".parse2_json_tool", "ParseEnvironmentJSONTool"),
    "ScoreEnzymeDegradationTool": (".score_enzyme_degradation_tool", "ScoreEnzymeDegradationTool"),
    "ScoreEnvironmentTool": (".score_environment_tool", "ScoreEnvironmentTool"),
    "ScoreSingleSpeciesTool": (".score_single_species_tool", "ScoreSingleSpeciesTool"),
    "ScoreCandidateTool": (".score_candidate_tool", "ScoreCandidateTool"),
    "ScoreConsortiaTool": (".score_consortia_tool", "ScoreConsortiaTool"),
    "ScoreConsortiaInput": (".score_consortia_tool", "ScoreConsortiaInput"),
    "ConsortiumDefinition": (".score_consortia_tool", "ConsortiumDefinition"),
    # 数据查询工具
    "GeneDataQueryTool": (".gene_query", "GeneDataQueryTool"),
    "OrganismDataQueryTool": (".organism_query", "OrganismDataQueryTool"),
    "PollutantDataQueryTool": (".pollutant_query", "PollutantDataQueryTool"),
    "PollutantSearchTool": (".search", "PollutantSearchTool"),
    "PollutantSummaryTool": (".summary", "PollutantSummaryTool"),
    "standardize_pollutant_name": (".name_utils", "standardize_pollutant_name"),
    "generate_pollutant_name_variants": (".name_utils", "generate_pollutant_name_variants"),
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str):
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = _LAZY_IMPORTS[name]
    module = import_module(module_name, __name__)
    attr = getattr(module, attr_name)
    globals()[name] = attr
    return attr
