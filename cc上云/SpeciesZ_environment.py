"""
Utility script for uploading the SpeciesZ environment CSV to PostgreSQL.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError


def load_env() -> None:
    """Load environment variables from a .env file if python-dotenv is available."""
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except ImportError:
        pass


@dataclass
class DatabaseConfig:
    db_type: str = os.getenv("DB_TYPE", "postgresql")
    host: str = os.getenv(
        "DB_HOST", "pgm-bp1ksg5v1lo5z2r8eo.rwlb.rds.aliyuncs.com"
    )
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "Bio_data")
    user: str = os.getenv("DB_USER", "nju_bio")
    password: str = os.getenv("DB_PASSWORD", "980605Hyz")
    sslmode: Optional[str] = os.getenv("DB_SSLMODE")

    def to_sqlalchemy_url(self) -> URL:
        """Build a SQLAlchemy URL with psycopg2 driver."""
        if self.db_type != "postgresql":
            raise ValueError(f"Unsupported DB_TYPE '{self.db_type}'")
        query = {"sslmode": self.sslmode} if self.sslmode else None
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
            query=query,
        )


def default_table_name(csv_path: Path) -> str:
    """Generate a simple snake_case table name from the CSV file name."""
    stem = csv_path.stem
    return stem.lower().replace(" ", "_")


def upload_csv(
    csv_path: Path,
    table_name: str,
    if_exists: str,
    config: Optional[DatabaseConfig] = None,
) -> None:
    """Read the CSV file and upload it to the database."""
    config = config or DatabaseConfig()
    database_url = config.to_sqlalchemy_url()
    df = pd.read_csv(csv_path)

    engine = create_engine(database_url)
    try:
        df.to_sql(table_name, engine, if_exists=if_exists, index=False, method="multi")
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Failed to upload data: {exc}") from exc
    finally:
        engine.dispose()


def show_preview(csv_path: Path, rows: int) -> None:
    """Print the first N rows from the CSV file."""
    df = pd.read_csv(csv_path, nrows=rows)
    print(f"Previewing first {rows} rows from '{csv_path}':")
    print(df.to_string(index=False))


def preview_table(
    table_name: str,
    rows: int,
    config: Optional[DatabaseConfig] = None,
) -> None:
    """Query the database table and print the first N rows."""
    config = config or DatabaseConfig()
    if rows <= 0:
        return
    engine = create_engine(config.to_sqlalchemy_url())
    try:
        metadata = MetaData()
        metadata.reflect(engine, only=[table_name])
        table = metadata.tables[table_name]
        stmt = select(table).limit(rows)
        df = pd.read_sql(stmt, engine)
        if df.empty:
            print(f"Table '{table_name}' is empty.")
        else:
            print(f"Database preview for '{table_name}' (first {rows} rows):")
            print(df.to_string(index=False))
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Failed to preview table '{table_name}': {exc}") from exc
    finally:
        engine.dispose()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Upload the SpeciesZ environment CSV to PostgreSQL."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("Sheet_Species_environment.csv"),
        help="Path to the CSV file (default: Sheet_Species_environment.csv)",
    )
    parser.add_argument(
        "--table",
        type=str,
        default=None,
        help="Target table name (default: derived from CSV file name)",
    )
    parser.add_argument(
        "--if-exists",
        choices=("fail", "replace", "append"),
        default="replace",
        help="Table handling strategy if it already exists (default: replace)",
    )
    parser.add_argument(
        "--sslmode",
        choices=("disable", "allow", "prefer", "require", "verify-ca", "verify-full"),
        default=None,
        help="Override DB SSL mode (default: use DB_SSLMODE env var or no SSL setting).",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=0,
        help="Print the first N rows from the CSV before upload (default: 0, disabled).",
    )
    parser.add_argument(
        "--db-preview",
        type=int,
        default=0,
        help="After upload, show the first N rows from the database table (default: 0, disabled).",
    )
    return parser.parse_args()


def main() -> None:
    load_env()
    args = parse_args()
    csv_path: Path = args.csv.expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    table_name = args.table or default_table_name(csv_path)

    if args.preview > 0:
        show_preview(csv_path, args.preview)

    config = DatabaseConfig()
    if args.sslmode is not None:
        config.sslmode = args.sslmode

    upload_csv(csv_path, table_name, args.if_exists, config=config)
    print(f"Uploaded '{csv_path}' to table '{table_name}'.")

    if args.db_preview > 0:
        preview_table(table_name, args.db_preview, config=config)


if __name__ == "__main__":
    main()
