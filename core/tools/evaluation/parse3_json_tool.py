#!/usr/bin/env python3
"""
DesignAgent 结果解析工具
解析 `test_results/DesignAgent/DesignAgent.json`，抽取指定 consortium 的成员列表。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from crewai.tools import BaseTool  # type: ignore
from pydantic import BaseModel, Field


DEFAULT_DESIGN_RESULT = (
    Path(__file__).resolve().parents[3]
    / "test_results"
    / "DesignAgent"
    / "DesignAgent.json"
)


class ParseConsortiaInput(BaseModel):
    """解析 DesignAgent JSON 的输入"""

    json_path: Optional[str] = Field(
        default=None,
        description="DesignAgent 结果 JSON 路径，默认读取 test_results/DesignAgent/DesignAgent.json",
    )
    consortium_id: str = Field(
        default="1",
        description="需要解析的 consortium_id（可传入字符串或数字字符串）。",
    )


class ParseDesignConsortiaTool(BaseTool):
    """解析 DesignAgent 结果的工具"""

    name: str = "ParseDesignConsortiaTool"
    description: str = (
        "读取 DesignAgent 输出 JSON，提取指定 consortium 的成员列表，"
        "为后续 FAA 构建或评估步骤提供输入。"
    )
    args_schema: type[BaseModel] = ParseConsortiaInput

    def _run(
        self,
        json_path: Optional[str] = None,
        consortium_id: str = "1",
    ) -> Dict[str, Any]:
        try:
            path = Path(json_path or DEFAULT_DESIGN_RESULT).expanduser()
            if not path.is_file():
                raise FileNotFoundError(f"未找到 DesignAgent 结果文件：{path}")

            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

            records = data.get("records") or []
            if not isinstance(records, list):
                raise ValueError("DesignAgent JSON 中的 records 字段格式不正确。")

            target_id = str(consortium_id).strip()
            matched_record: Optional[Dict[str, Any]] = None
            for record in records:
                record_id = str(record.get("consortium_id", "")).strip()
                if record_id == target_id:
                    matched_record = record
                    break

            if matched_record is None:
                raise ValueError(f"在 {path} 中未找到 consortium_id={target_id} 的记录。")

            members = matched_record.get("members") or []
            if not isinstance(members, list) or not all(isinstance(item, str) for item in members):
                raise ValueError("目标记录的 members 字段格式不正确，需为字符串列表。")

            return {
                "status": "success",
                "json_path": str(path),
                "consortium_id": target_id,
                "members": members,
                "record": matched_record,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"DesignAgent 结果解析失败: {exc}",
            }


__all__ = ["ParseDesignConsortiaTool", "ParseConsortiaInput"]
