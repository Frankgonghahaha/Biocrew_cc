#!/usr/bin/env python3
"""
FAA 构建工具
依据成员列表，从 protein_sequences 数据库表中提取氨基酸序列，生成以物种命名的 .faa 文件。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from crewai.tools import BaseTool  # type: ignore
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

load_dotenv()

DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[3]
    / "test_results"
    / "EvaluateAgent"
    / "faa"
)


class FaaBuildInput(BaseModel):
    """FAA 构建工具输入"""

    species: List[str] = Field(..., description="需要构建 FAA 的物种名称列表")
    output_dir: Optional[str] = Field(
        default=None,
        description="FAA 文件输出目录，默认 test_results/EvaluateAgent/faa",
    )
    sequences_per_species: int = Field(
        default=3000,
        description="每个物种写入的最大序列条数",
    )

    @validator("species")
    def ensure_species(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value if str(item).strip()]
        if not cleaned:
            raise ValueError("species 列表不能为空")
        return cleaned

    @validator("sequences_per_species")
    def validate_limit(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("sequences_per_species 必须 > 0")
        return value


class FaaBuildTool(BaseTool):
    """根据成员列表构建 FAA 的工具"""

    name: str = "FaaBuildTool"
    description: str = (
        "针对指定物种列表，查询 protein_sequences 表中的氨基酸序列，"
        "并输出以物种名称命名的 .faa 文件，供 EvaluateAgent 使用。"
    )
    args_schema: type[BaseModel] = FaaBuildInput

    def __init__(self) -> None:
        super().__init__()
        self._engine: Engine = self._init_engine()
        self._Session = sessionmaker(bind=self._engine)

    def _init_engine(self) -> Engine:
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        if not all([db_host, db_port, db_name, db_user, db_password]):
            raise RuntimeError("数据库配置不完整，请在环境变量中设置 DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD。")
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return create_engine(database_url)

    def _run(
        self,
        species: List[str],
        output_dir: Optional[str] = None,
        sequences_per_species: int = 200,
    ) -> Dict[str, Any]:
        session = None
        try:
            target_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
            target_dir.mkdir(parents=True, exist_ok=True)

            unique_species = []
            seen = set()
            for name in species:
                normalized = self._normalize_name(name)
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    unique_species.append(normalized)

            if not unique_species:
                raise ValueError("未能从输入中识别到有效的物种名称。")

            session = self._Session()
            generated_files: List[str] = []
            missing_species: List[str] = []
            skipped_species: List[str] = []

            for name in unique_species:
                file_path = target_dir / f"{self._sanitize_filename(name)}.faa"
                if file_path.exists():
                    skipped_species.append(name)
                    generated_files.append(str(file_path))
                    continue

                sequences = self._fetch_sequences(session, name, sequences_per_species)
                if not sequences:
                    missing_species.append(name)
                    continue
                with file_path.open("w", encoding="utf-8") as fh:
                    for entry in sequences:
                        header = f">{entry['sequence_id']}|{name}"
                        fh.write(f"{header}\n")
                        fh.write(f"{self._wrap_sequence(entry['aa_sequence'])}\n")
                generated_files.append(str(file_path))

            return {
                "status": "success",
                "output_dir": str(target_dir),
                "generated_files": generated_files,
                "missing_species": missing_species,
                "skipped_species": skipped_species,
            }

        except SQLAlchemyError as exc:
            return {
                "status": "error",
                "message": f"数据库查询失败: {exc}",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"FAA 构建失败: {exc}",
            }
        finally:
            if session is not None:
                session.close()

    def _fetch_sequences(
        self,
        session,
        species_name: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        sql = text(
            """
            SELECT sequence_id, aa_sequence
            FROM protein_sequences
            WHERE lower(species_name) = lower(:species)
            ORDER BY sequence_length DESC
            LIMIT :limit
            """
        )
        rows = session.execute(sql, {"species": species_name, "limit": limit}).fetchall()
        sequences: List[Dict[str, Any]] = []
        for row in rows:
            seq_id = row[0]
            aa_seq = row[1]
            if not aa_seq:
                continue
            sequences.append(
                {"sequence_id": str(seq_id), "aa_sequence": str(aa_seq).replace("\r", "").replace("\n", "")}
            )
        return sequences

    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join(name.replace("（", "(").replace("）", ")").split()).strip()

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        cleaned = "".join(ch if ch.isalnum() or ch in ("_", "-", ".") else "_" for ch in name)
        return cleaned.strip("_") or "unknown_species"

    @staticmethod
    def _wrap_sequence(sequence: str, width: int = 70) -> str:
        return "\n".join(sequence[i : i + width] for i in range(0, len(sequence), width))


__all__ = ["FaaBuildTool", "FaaBuildInput"]
