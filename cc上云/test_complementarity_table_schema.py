#!/usr/bin/env python3
"""Schema check for the microbial_complementarity table."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

from dotenv import load_dotenv


class TestMicrobialComplementarityTableSchema(unittest.TestCase):
    """Validate the schema of the microbial_complementarity table."""

    @classmethod
    def setUpClass(cls) -> None:
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()

        required_env = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")
        missing = [var for var in required_env if not os.getenv(var)]
        if missing:
            raise unittest.SkipTest(f"数据库环境变量缺失: {', '.join(missing)}")

        try:
            from sqlalchemy import create_engine, inspect
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest("未安装 SQLAlchemy，跳过数据库结构检查") from exc

        cls._create_engine = create_engine
        cls._inspect = inspect

        db_url = (
            f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
            f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
        )

        try:
            cls.engine = cls._create_engine(db_url)
            cls.inspector = cls._inspect(cls.engine)
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest("未安装 psycopg2，无法连接数据库") from exc

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "inspector"):
            cls.engine.dispose()

    def test_table_schema_contains_expected_columns(self) -> None:
        """Ensure all required columns exist in the target table."""
        columns = {
            column["name"]: column for column in self.inspector.get_columns("microbial_complementarity")
        }

        expected_columns = {
            "id",
            "degrading_microorganism",
            "complementary_microorganism",
            "competition_index",
            "complementarity_index",
        }

        self.assertTrue(expected_columns.issubset(columns.keys()), columns.keys())

        float_columns = {"competition_index", "complementarity_index"}
        for name in float_columns:
            type_str = str(columns[name]["type"]).upper()
            self.assertTrue(
                any(marker in type_str for marker in ("FLOAT", "DOUBLE", "NUMERIC", "DECIMAL")),
                msg=f"列 {name} 的类型不是浮点数: {type_str}",
            )

        string_columns = {"degrading_microorganism", "complementary_microorganism"}
        for name in string_columns:
            type_str = str(columns[name]["type"]).upper()
            self.assertTrue(
                any(marker in type_str for marker in ("CHAR", "TEXT", "STRING", "VARCHAR")),
                msg=f"列 {name} 的类型不是字符串: {type_str}",
            )

        self.assertFalse(columns["degrading_microorganism"]["nullable"])
        self.assertFalse(columns["complementary_microorganism"]["nullable"])

        from sqlalchemy import text
        query = text(
            """
            SELECT degrading_microorganism,
                   complementary_microorganism,
                   competition_index,
                   complementarity_index
            FROM microbial_complementarity
            WHERE complementarity_index > competition_index
            ORDER BY (complementarity_index - competition_index) DESC
            LIMIT 5
            """
        )
        with self.engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        print("\n互补关系示例（Top 5，Complementarity > Competition）：")
        if not rows:
            print("未找到满足补偿条件的记录。")
        else:
            for row in rows:
                delta = row.complementarity_index - row.competition_index
                print(
                    f"- 降解菌: {row.degrading_microorganism} | 互补菌: {row.complementary_microorganism} "
                    f"| Competition: {row.competition_index:.4f} | Complementarity: {row.complementarity_index:.4f} "
                    f"| Δ: {delta:.4f}"
                )


if __name__ == "__main__":
    unittest.main()
