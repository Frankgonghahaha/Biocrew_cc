"""
测试 SpeciesEnvironmentQueryTool 能否查询数据库中物种的生长环境信息。
"""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DB_SSLMODE", "disable")

from core.tools.database.species_environment_tool import SpeciesEnvironmentQueryTool

MODULE_PATH = Path(__file__).resolve().parent / "SpeciesZ_environment.py"
MODULE_NAME = "species_z_environment"

spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"无法加载模块：{MODULE_PATH}")

module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = module
spec.loader.exec_module(module)

DatabaseConfig = module.DatabaseConfig
default_table_name = module.default_table_name
load_env = module.load_env
upload_csv = module.upload_csv


class TestSpeciesEnvironmentTool(unittest.TestCase):
    """验证 SpeciesEnvironmentQueryTool 可以返回指定物种的生长环境信息。"""

    @classmethod
    def setUpClass(cls) -> None:
        load_env()
        cls.csv_path = PROJECT_ROOT / "Sheet_Species_environment.csv"
        if not cls.csv_path.exists():
            raise unittest.SkipTest(f"CSV 文件不存在：{cls.csv_path}")

        cls.table_name = default_table_name(cls.csv_path)
        cls.config = DatabaseConfig()
        if cls.config.sslmode is None:
            cls.config.sslmode = "disable"

        upload_csv(cls.csv_path, cls.table_name, "replace", config=cls.config)
        cls.tool = SpeciesEnvironmentQueryTool()

    def test_query_species_environment(self) -> None:
        strain = "Pseudomonadota sp."
        result = self.tool._run(
            strain,
            temperature=18.5,
            ph=6.6,
            salinity=0.05,
            oxygen="tolerant",
        )

        self.assertEqual(result.get("status"), "success")
        self.assertGreater(result.get("count", 0), 0, "应至少返回一条生长环境记录")

        records = result.get("records", [])
        first_record = records[0] if records else {}
        print("物种查询结果：")
        print(first_record)
        best = result.get("best_record", {})
        if best:
            score = best.get("adaptability_score")
            self.assertIsNotNone(score)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            print("最佳记录：", best)
            print("最佳适应性评分：", score)

        engine = create_engine(self.config.to_sqlalchemy_url())
        try:
            df = pd.read_sql(
                text(
                    'SELECT * FROM "{}" WHERE strain = :strain LIMIT 5'.format(
                        self.table_name
                    )
                ),
                engine,
                params={"strain": strain},
            )
        except SQLAlchemyError:
            raise
        finally:
            engine.dispose()
        self.assertGreater(len(df), 0)


if __name__ == "__main__":
    unittest.main()
