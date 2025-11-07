#!/usr/bin/env python3
"""
功能菌群组合评分工具
依据单菌评分与互作指标，对给定菌群组合计算 S_consort。
参考旧版 Design_pipeline_2 的评分公式。
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, ConfigDict, Field, validator


def _normalize_name(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.replace("（", "(").replace("）", ")").split()).strip()


def _safe_float(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number):
        return None
    return number


def _safe_mean(values: Iterable[Optional[float]]) -> float:
    filtered = [v for v in (_safe_float(x) for x in values) if v is not None]
    if not filtered:
        return 0.0
    return float(sum(filtered) / len(filtered))


@dataclass
class _PairMetrics:
    competition: Optional[float]
    complementarity: Optional[float]
    delta: Optional[float]


class CandidateScoreRecord(BaseModel):
    """单菌评分记录（来自 ScoreSingleSpeciesTool 或 ScoreCandidateTool）。"""

    species: str = Field(..., description="物种名称")
    S_microbe: Optional[float] = Field(
        default=None, description="单菌综合得分，缺失时按 0 处理"
    )
    source: Optional[str] = Field(default=None, description="来源标签，例如 functional/complement")
    kcat_max: Optional[float] = Field(default=None, description="最大 kcat 估计值")
    environment_match: Optional[float] = Field(default=None, description="环境适应评分")

    @validator("species")
    def normalize_species(cls, value: str) -> str:
        normalized = _normalize_name(value)
        if not normalized:
            raise ValueError("species 不能为空")
        return normalized

    @validator("S_microbe", pre=True, always=True)
    def default_s_microbe(cls, value: Optional[float]) -> float:
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


class PairScoreRecord(BaseModel):
    """物种对互作记录（来自 ScoreMetabolicInteractionTool）。"""

    functional_species: str = Field(..., description="功能菌物种名称")
    complement_species: str = Field(..., description="互补菌物种名称")
    competition_index: Optional[float] = Field(default=None, description="竞争指数")
    complementarity_index: Optional[float] = Field(default=None, description="互补指数")
    delta_index: Optional[float] = Field(default=None, description="互补-竞争 Δ")

    @validator("functional_species", "complement_species")
    def normalize_species(cls, value: str) -> str:
        normalized = _normalize_name(value)
        if not normalized:
            raise ValueError("species 名称不能为空")
        return normalized


class ConsortiumDefinition(BaseModel):
    """待评分的菌群组合定义。"""

    members: List[str] = Field(..., description="组合内的物种列表")
    name: Optional[str] = Field(default=None, description="组合名称，可选")

    @validator("members")
    def ensure_members(cls, value: List[str]) -> List[str]:
        normalized = [_normalize_name(item) for item in value if _normalize_name(item)]
        if not normalized:
            raise ValueError("菌群组合成员不能为空")
        return normalized


class ScoreConsortiaInput(BaseModel):
    """菌群评分工具输入参数。"""

    model_config = ConfigDict(populate_by_name=True)

    candidate_records: List[CandidateScoreRecord] = Field(
        ..., description="单菌评分记录列表"
    )
    pair_records: List[PairScoreRecord] = Field(
        default_factory=list,
        description="物种对互作评分记录列表，可为空",
    )
    consortia: List[ConsortiumDefinition] = Field(
        default_factory=list,
        description="待评估的菌群组合；若启用自动生成可留空",
    )
    alpha: float = Field(0.2, description="权重：平均 S_microbe")
    beta: float = Field(0.2, description="权重：平均正向 Δ")
    gamma: float = Field(0.1, description="权重：平均正向 competition（惩罚）")
    lambda_kcat: float = Field(
        0.35, alias="lambda_", description="权重：平均 kcat_max（加分）"
    )
    mu: float = Field(
        -0.05,
        description="规模惩罚权重；最终评分为 score - mu * size，与旧版保持一致",
    )
    require_functional: bool = Field(
        True, description="是否要求组合中至少包含 1 个功能菌"
    )
    min_size: int = Field(2, description="自动生成组合的最小物种数")
    max_size: int = Field(5, description="自动生成组合的最大物种数")
    auto_generate: bool = Field(
        True, description="当未提供 consortia 时，是否根据单菌评分自动生成组合"
    )
    auto_seed_limit: int = Field(
        8,
        description="自动组合时，按 S_microbe 排序后取前 N 个物种作为候选池",
    )
    auto_max_consortia: int = Field(
        100,
        description="自动生成的最大组合数量上限，防止组合爆炸",
    )
    output_timestamp: Optional[str] = Field(
        default=None,
        description="输出 JSON 的时间戳（例如 2025-06-21T12-45-33），用于命名文件；"
        "如果为空则使用当前时间。",
    )

    @validator("min_size")
    def validate_min_size(cls, value: int) -> int:
        if value < 1:
            raise ValueError("min_size 必须 >= 1")
        return value

    @validator("max_size")
    def validate_size_range(cls, value: int, values: Dict[str, Any]) -> int:
        min_size = values.get("min_size", 1)
        if value < min_size:
            raise ValueError("max_size 必须 >= min_size")
        return value

    @validator("consortia", always=True)
    def ensure_consortia(
        cls, value: List[ConsortiumDefinition], values: Dict[str, Any]
    ) -> List[ConsortiumDefinition]:
        auto_generate = values.get("auto_generate", True)
        if not value and not auto_generate:
            raise ValueError("至少需要提供 1 个菌群组合，或启用 auto_generate。")
        return value or []


class ScoreConsortiaTool(BaseTool):
    """菌群组合评分工具。"""

    name: str = "ScoreConsortiaTool"
    description: str = (
        "结合 ScoreSingleSpeciesTool/ScoreCandidateTool 的单菌评分与 "
        "ScoreMetabolicInteractionTool 的互作指标，"
        "对给定菌群组合计算综合评分 S_consort，"
        "评分公式参考 Old_Design_pipeline2："
        "S_consort = α·avg(S_microbe) + β·avg(Δ⁺) - γ·avg(competition⁺) + "
        "λ·avg(kcat_max) - μ·|consortium|。"
    )
    args_schema: type[BaseModel] = ScoreConsortiaInput

    def _run(
        self,
        candidate_records: List[CandidateScoreRecord],
        pair_records: List[PairScoreRecord],
        consortia: List[ConsortiumDefinition],
        alpha: float = 0.2,
        beta: float = 0.2,
        gamma: float = 0.1,
        lambda_kcat: float = 0.35,
        mu: float = -0.05,
        require_functional: bool = True,
        min_size: int = 2,
        max_size: int = 5,
        auto_generate: bool = True,
        auto_seed_limit: int = 8,
        auto_max_consortia: int = 100,
        output_timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            candidate_map = self._build_candidate_lookup(candidate_records)
            pair_lookup = self._build_pair_lookup(pair_records)

            evaluated_consortia = list(consortia or [])
            if auto_generate:
                generated = self._auto_generate_consortia(
                    candidate_records=candidate_records,
                    min_size=min_size,
                    max_size=max_size,
                    require_functional=require_functional,
                    seed_limit=auto_seed_limit,
                    max_count=auto_max_consortia,
                )
                evaluated_consortia.extend(generated)

            if not evaluated_consortia:
                return {
                    "status": "empty",
                    "message": "未提供菌群组合，且自动生成功能未生成有效组合。",
                    "warnings": [],
                }

            results = []
            warnings = []

            for idx, consortium in enumerate(evaluated_consortia, start=1):
                name = consortium.name or f"consortium_{idx}"
                normalized_members = self._unique_members(consortium.members)
                if not normalized_members:
                    warnings.append(f"{name}: 成员为空，跳过。")
                    continue

                member_info = [
                    (member, candidate_map.get(member)) for member in normalized_members
                ]
                missing = [m for m, rec in member_info if rec is None]

                if require_functional and not self._has_functional(member_info):
                    warnings.append(f"{name}: 不包含功能菌，已跳过。")
                    continue

                metrics = self._calculate_metrics(
                    normalized_members,
                    member_info,
                    pair_lookup,
                    alpha,
                    beta,
                    gamma,
                    lambda_kcat,
                    mu,
                )

                results.append(
                    {
                        "name": name,
                        "members": normalized_members,
                        "score": metrics["score"],
                        "avg_S_microbe": metrics["avg_S_microbe"],
                        "avg_delta_pos": metrics["avg_delta_pos"],
                        "avg_comp_pos": metrics["avg_comp_pos"],
                        "avg_kcat_max": metrics["avg_kcat"],
                        "size": metrics["size"],
                        "used_pairs": metrics["used_pairs"],
                        "source_count": metrics["source_count"],
                        "missing_members": missing,
                    }
                )

            if not results:
                return {
                    "status": "empty",
                    "message": "未生成任何菌群评分结果，请检查输入或组合约束。",
                    "warnings": warnings,
                }

            results.sort(key=lambda item: item["score"], reverse=True)
            total_generated = len(results)
            output_file = self._persist_top_consortia(
                results,
                limit=10,
                timestamp_override=output_timestamp,
            )
            best = results[0]
            summary = {
                "count": total_generated,
                "best_name": best["name"],
                "best_score": best["score"],
            }

            return {
                "status": "success",
                "summary": summary,
                "consortia": [best],
                "warnings": warnings,
                "output_file": output_file,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"菌群评分失败: {exc}",
            }

    def _auto_generate_consortia(
        self,
        candidate_records: List[CandidateScoreRecord],
        min_size: int,
        max_size: int,
        require_functional: bool,
        seed_limit: int,
        max_count: int,
    ) -> List[ConsortiumDefinition]:
        if max_size < min_size or not candidate_records:
            return []

        scored_candidates = sorted(
            [record for record in candidate_records if record.species],
            key=lambda item: item.S_microbe if item.S_microbe is not None else float("-inf"),
            reverse=True,
        )
        if seed_limit > 0:
            scored_candidates = scored_candidates[:seed_limit]

        if len(scored_candidates) < min_size:
            return []

        source_map = {
            _normalize_name(record.species): (record.source or "").strip().lower()
            for record in scored_candidates
        }
        species_pool = list(source_map.keys())
        max_size = min(max_size, len(species_pool))

        generated: List[ConsortiumDefinition] = []
        seen: Set[tuple[str, ...]] = set()

        for size in range(min_size, max_size + 1):
            for combo in combinations(species_pool, size):
                if len(generated) >= max_count:
                    return generated
                if require_functional and not any(
                    source_map.get(member) == "functional" for member in combo
                ):
                    continue
                key = tuple(combo)
                if key in seen:
                    continue
                seen.add(key)
                generated.append(ConsortiumDefinition(members=list(combo)))
        return generated

    def _persist_top_consortia(
        self,
        results: List[Dict[str, Any]],
        limit: int = 10,
        timestamp_override: Optional[str] = None,
    ) -> Optional[str]:
        if not results:
            return None

        top_records = results[:limit] if limit and limit > 0 else results
        payload = []
        for entry in top_records:
            payload.append(
                {
                    "consortium_id": entry.get("name"),
                    "members": entry.get("members"),
                    "size": entry.get("size"),
                    "avg_S_microbe": entry.get("avg_S_microbe"),
                    "avg_delta_pos": entry.get("avg_delta_pos"),
                    "avg_comp_pos": entry.get("avg_comp_pos"),
                    "avg_kcat": entry.get("avg_kcat_max"),
                    "S_consort": entry.get("score"),
                    "used_pairs": entry.get("used_pairs"),
                    "source_count": entry.get("source_count"),
                }
            )

        root_dir = Path(__file__).resolve().parents[3]
        output_dir = root_dir / "test_results" / "DesignAgent"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp, safe_ts = self._resolve_output_timestamp(timestamp_override)
        file_path = output_dir / f"DesignAgent_{safe_ts}.json"

        data = {
            "generated_at": timestamp,
            "record_count": len(payload),
            "records": payload,
        }
        with file_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        return str(file_path)

    @staticmethod
    def _resolve_output_timestamp(
        timestamp_override: Optional[str],
    ) -> tuple[str, str]:
        if timestamp_override:
            candidate = timestamp_override.strip()
            if "T" in candidate:
                date_part, time_part = candidate.split("T", 1)
                time_iso = time_part.replace("-", ":")
                iso_candidate = f"{date_part}T{time_iso}"
                try:
                    normalized = datetime.fromisoformat(iso_candidate).isoformat(timespec="seconds")
                    return normalized, candidate.replace(":", "-")
                except ValueError:
                    pass
            try:
                normalized = datetime.fromisoformat(candidate).isoformat(timespec="seconds")
                return normalized, normalized.replace(":", "-")
            except ValueError:
                pass
        now = datetime.now().isoformat(timespec="seconds")
        return now, now.replace(":", "-")

    @staticmethod
    def _unique_members(members: Iterable[str]) -> List[str]:
        seen = set()
        ordered = []
        for member in members:
            normalized = _normalize_name(member)
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered

    @staticmethod
    def _build_candidate_lookup(
        records: Iterable[CandidateScoreRecord],
    ) -> Dict[str, CandidateScoreRecord]:
        lookup: Dict[str, CandidateScoreRecord] = {}
        for record in records:
            lookup[record.species] = record
        return lookup

    @staticmethod
    def _build_pair_lookup(
        records: Iterable[PairScoreRecord],
    ) -> Dict[tuple[str, str], _PairMetrics]:
        best_by_pair: Dict[tuple[str, str], _PairMetrics] = {}

        for record in records:
            a = record.functional_species
            b = record.complement_species
            if not a or not b or a == b:
                continue

            entry = _PairMetrics(
                competition=_safe_float(record.competition_index),
                complementarity=_safe_float(record.complementarity_index),
                delta=_safe_float(record.delta_index),
            )

            key = tuple(sorted((a, b)))
            existing = best_by_pair.get(key)
            if existing is None or ScoreConsortiaTool._is_better_pair(entry, existing):
                best_by_pair[key] = entry

        # 为便于查询，生成双向映射
        pair_lookup: Dict[tuple[str, str], _PairMetrics] = {}
        for (a, b), metrics in best_by_pair.items():
            pair_lookup[(a, b)] = metrics
            pair_lookup[(b, a)] = metrics

        return pair_lookup

    @staticmethod
    def _is_better_pair(candidate: _PairMetrics, current: _PairMetrics) -> bool:
        candidate_delta = candidate.delta if candidate.delta is not None else float("-inf")
        current_delta = current.delta if current.delta is not None else float("-inf")
        if candidate_delta > current_delta:
            return True
        if candidate_delta < current_delta:
            return False
        # 若 Δ 相同，则取互补指数更高者
        candidate_compl = candidate.complementarity if candidate.complementarity is not None else float("-inf")
        current_compl = current.complementarity if current.complementarity is not None else float("-inf")
        return candidate_compl > current_compl

    @staticmethod
    def _has_functional(
        member_info: List[tuple[str, Optional[CandidateScoreRecord]]]
    ) -> bool:
        for _, record in member_info:
            if record and (record.source or "").strip().lower() == "functional":
                return True
        return False

    def _calculate_metrics(
        self,
        members: List[str],
        member_info: List[tuple[str, Optional[CandidateScoreRecord]]],
        pair_lookup: Dict[tuple[str, str], _PairMetrics],
        alpha: float,
        beta: float,
        gamma: float,
        lambda_kcat: float,
        mu: float,
    ) -> Dict[str, Any]:
        s_micro_values = []
        kcat_values = []
        source_count: Dict[str, int] = {}

        for name, record in member_info:
            if record:
                s_micro_values.append(record.S_microbe)
                kcat_values.append(record.kcat_max)
                source = (record.source or "unknown").strip().lower()
            else:
                s_micro_values.append(0.0)
                source = "unknown"

            source_count[source] = source_count.get(source, 0) + 1

        avg_micro = _safe_mean(s_micro_values)
        avg_kcat = _safe_mean(kcat_values)
        avg_delta_pos, avg_comp_pos, used_pairs = self._aggregate_pair_metrics(
            members,
            pair_lookup,
        )

        size = len(members)
        score = (
            alpha * avg_micro
            + beta * avg_delta_pos
            - gamma * avg_comp_pos
            + lambda_kcat * avg_kcat
            - mu * size
        )

        return {
            "score": float(score),
            "avg_S_microbe": avg_micro,
            "avg_delta_pos": avg_delta_pos,
            "avg_comp_pos": avg_comp_pos,
            "avg_kcat": avg_kcat,
            "used_pairs": used_pairs,
            "size": size,
            "source_count": source_count,
        }

    @staticmethod
    def _aggregate_pair_metrics(
        members: List[str],
        pair_lookup: Dict[tuple[str, str], _PairMetrics],
    ) -> tuple[float, float, int]:
        deltas_pos: List[float] = []
        comps_pos: List[float] = []
        used_pairs = 0

        for i, a in enumerate(members):
            for b in members[i + 1 :]:
                metrics = pair_lookup.get((a, b))
                if metrics is None:
                    continue
                used_pairs += 1

                if metrics.delta is not None and metrics.delta > 0:
                    deltas_pos.append(metrics.delta)

                if metrics.competition is not None and metrics.competition > 0:
                    comps_pos.append(metrics.competition)

        return _safe_mean(deltas_pos), _safe_mean(comps_pos), used_pairs


__all__ = ["ScoreConsortiaTool", "ScoreConsortiaInput", "ConsortiumDefinition"]
