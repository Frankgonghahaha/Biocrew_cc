#!/usr/bin/env python3
"""
针对 ScoreMetabolicInteractionTool 的定向测试。
仅展示 “Patescibacteria sp. GCA-016699975 sp016699875” 与
“Pseudomonadota sp. SphingorhabdusB sp016721875” 之间的互作指标与数据库原始记录。
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import and_, func, or_

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TARGET_FUNCTIONAL = "Pseudomonadota sp. SphingorhabdusB sp016721875"
TARGET_COMPLEMENT = "Patescibacteria sp. GCA-016699975 sp016699875"

from core.tools.database.complementarity_model import (  # noqa: E402
    MicrobialComplementarity,
)
from core.tools.design.score_metabolic_tool import (  # noqa: E402
    ScoreMetabolicInteractionTool,
)


def main() -> None:
    json_path = (
        PROJECT_ROOT
        / "test_results"
        / "IdentificationAgent_Result_2025-06-21T12-45-33.json"
    )
    if not json_path.exists():
        raise FileNotFoundError(f"找不到识别阶段 JSON：{json_path}")

    tool = ScoreMetabolicInteractionTool()
    result = tool._run(
        identification_json_path=str(json_path),
        include_complements=True,
        only_positive_delta=False,
        top_n=None,
    )

    if result.get("status") != "success":
        raise RuntimeError(f"互作评分失败: {result}")

    print("互作评分成功，以下为目标物种对的详细计算过程：\n")

    pairs = result.get("pairs", [])
    target_pairs = [
        pair
        for pair in pairs
        if _is_target_pair(
            pair.get("functional_species"),
            pair.get("complement_species"),
        )
    ]

    if not target_pairs:
        print("未在互作结果中找到指定的物种组合。")
        return

    csv_rows: list[dict[str, Any]] = []

    for pair in target_pairs:
        cleaned = _clean_pair(pair)
        print("互作指标：")
        print(json.dumps(cleaned, indent=2, ensure_ascii=False))
        db_rows = _print_database_details(tool, pair)
        csv_rows.extend(
            _rows_for_csv(cleaned, db_rows)
        )
        print("-" * 80)

    _write_csv(csv_rows)


def _is_target_pair(functional: str | None, complement: str | None) -> bool:
    """判断物种对是否为目标组合（忽略顺序）。"""
    names = {functional or "", complement or ""}
    return names == {TARGET_FUNCTIONAL, TARGET_COMPLEMENT}


def _clean_pair(data: dict[str, Any]) -> dict[str, Any]:
    """将 SQLAlchemy 返回的 Decimal / None 等类型转换为 JSON 友好的形式。"""
    cleaned: dict[str, Any] = {}
    for key, value in data.items():
        if value is None:
            cleaned[key] = None
        elif isinstance(value, (int, float, str)):
            cleaned[key] = value
        else:
            cleaned[key] = float(value)
    return cleaned


def _print_database_details(
    tool: ScoreMetabolicInteractionTool, pair: dict[str, Any]
) -> list[MicrobialComplementarity]:
    """补充展示互补性数据库中的原始记录。"""
    session_factory = getattr(tool, "_Session", None)
    if session_factory is None:
        print("  [警告] 无法访问数据库会话工厂。")
        return
    session = session_factory()
    try:
        rows = _fetch_pair_rows(
            session,
            pair.get("functional_species", ""),
            pair.get("complement_species", ""),
        )
        if not rows:
            print("  [提示] 数据库中未找到匹配记录。")
            return []
        print("数据库原始记录：")
        for row in rows:
            print(
                json.dumps(
                    {
                        "degrading_microorganism": row.degrading_microorganism,
                        "complementary_microorganism": row.complementary_microorganism,
                        "competition_index": row.competition_index,
                        "complementarity_index": row.complementarity_index,
                        "delta_index": float(row.complementarity_index)
                        - float(row.competition_index),
                    },
                    ensure_ascii=False,
                )
            )
        return rows
    except Exception as exc:  # noqa: BLE001
        print(f"  [错误] 查询数据库时出现异常: {exc}")
        return []
    finally:
        session.close()


def _fetch_pair_rows(
    session,
    species_a: str,
    species_b: str,
) -> Iterable[MicrobialComplementarity]:
    table = MicrobialComplementarity
    norm_a = " ".join(species_a.split()).strip()
    norm_b = " ".join(species_b.split()).strip()
    pattern_a = f"%{norm_a}%"
    pattern_b = f"%{norm_b}%"
    return (
        session.query(table)
        .filter(
            or_(
                and_(
                    func.lower(table.degrading_microorganism).like(
                        func.lower(pattern_a)
                    ),
                    func.lower(table.complementary_microorganism).like(
                        func.lower(pattern_b)
                    ),
                ),
                and_(
                    func.lower(table.degrading_microorganism).like(
                        func.lower(pattern_b)
                    ),
                    func.lower(table.complementary_microorganism).like(
                        func.lower(pattern_a)
                    ),
                ),
            )
        )
        .all()
    )


def _rows_for_csv(
    result_pair: dict[str, Any],
    db_rows: Iterable[MicrobialComplementarity],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    result_delta = result_pair.get("delta_index")
    for row in db_rows:
        comp_idx = float(row.competition_index)
        compmt_idx = float(row.complementarity_index)
        rows.append(
            {
                "result_functional_species": result_pair.get("functional_species"),
                "result_complement_species": result_pair.get("complement_species"),
                "result_competition_index": result_pair.get("competition_index"),
                "result_complementarity_index": result_pair.get("complementarity_index"),
                "result_delta_index": result_delta,
                "db_degrading_microorganism": row.degrading_microorganism,
                "db_complementary_microorganism": row.complementary_microorganism,
                "db_competition_index": comp_idx,
                "db_complementarity_index": compmt_idx,
                "db_delta_index": compmt_idx - comp_idx,
            }
        )
    return rows


def _write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("未生成任何 CSV 数据。")
        return
    output_dir = PROJECT_ROOT / "test_results" / "DesignAgent"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "metabolic_pair_details.csv"
    fieldnames = list(rows[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"已将互作详细数据写入: {output_path}")


if __name__ == "__main__":
    main()
