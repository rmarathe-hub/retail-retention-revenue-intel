"""
Shared PostgreSQL connection helpers for project scripts.

This project connects from the host via localhost:5433 (Docker maps host 5433
to container port 5432).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_HOST = "localhost"
DEFAULT_PORT = "5433"
DEFAULT_DB = "retail_analytics"
DEFAULT_USER = "retail_user"


def normalize_sqlalchemy_url(url: str) -> str:
    """Ensure SQLAlchemy uses the psycopg2 driver."""
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_database_url() -> str:
    """Build SQLAlchemy database URL from DATABASE_URL or POSTGRES_* env vars."""
    load_dotenv(PROJECT_ROOT / ".env")

    explicit_url = os.getenv("DATABASE_URL", "").strip()
    if explicit_url:
        return normalize_sqlalchemy_url(explicit_url)

    host = os.getenv("POSTGRES_HOST") or DEFAULT_HOST
    port = os.getenv("POSTGRES_PORT") or DEFAULT_PORT
    db = os.getenv("POSTGRES_DB") or DEFAULT_DB
    user = os.getenv("POSTGRES_USER") or DEFAULT_USER
    password = os.getenv("POSTGRES_PASSWORD") or ""

    if not password:
        raise ValueError(
            "POSTGRES_PASSWORD is not set. Copy .env.example to .env and configure it."
        )

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def create_db_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    return create_engine(url)
