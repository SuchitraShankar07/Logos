from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Any

import psycopg2
from psycopg2.extras import Json, RealDictCursor


@contextmanager
def _get_connection():
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([host, dbname, user, password]):
        raise RuntimeError("Database environment variables are not fully configured")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> bool:
    """Create incidents table if it does not exist. Returns True on success."""
    ddl = """
    CREATE TABLE IF NOT EXISTS incidents (
        id SERIAL PRIMARY KEY,
        logs TEXT,
        code TEXT,
        signals JSONB,
        hypotheses JSONB,
        final_diagnosis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
            conn.commit()
        return True
    except Exception:
        return False


def _extract_keywords(logs: str, max_keywords: int = 5) -> list[str]:
    tokens = set(re.findall(r"[a-zA-Z_]{4,}", logs.lower()))
    priority = [
        "error",
        "exception",
        "timeout",
        "queuepool",
        "connection",
        "operationalerror",
        "failed",
        "unavailable",
        "overloaded",
        "latency",
    ]
    ranked = [k for k in priority if k in tokens]
    if not ranked:
        ranked = ["error", "exception", "timeout"]
    return ranked[:max_keywords]


def retrieve_similar_incidents(logs: str, limit: int = 3) -> list[dict[str, Any]]:
    """Retrieve likely related incidents using keyword ILIKE matching."""
    keywords = _extract_keywords(logs)
    patterns = [f"%{k}%" for k in keywords]

    query = """
    SELECT id, logs, code, signals, hypotheses, final_diagnosis, created_at
    FROM incidents
    WHERE logs ILIKE ANY(%s)
       OR final_diagnosis ILIKE ANY(%s)
    ORDER BY created_at DESC
    LIMIT %s;
    """

    try:
        with _get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (patterns, patterns, limit))
                rows = cur.fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            results.append(
                {
                    "id": row.get("id"),
                    "final_diagnosis": row.get("final_diagnosis"),
                    "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
                    "logs_excerpt": (row.get("logs") or "")[:350],
                    "signals": row.get("signals"),
                    "hypotheses": row.get("hypotheses"),
                }
            )
        return results
    except Exception:
        return []


def store_incident(
    logs: str,
    code: str,
    signals: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    final_diagnosis: str,
) -> bool:
    insert_sql = """
    INSERT INTO incidents (logs, code, signals, hypotheses, final_diagnosis)
    VALUES (%s, %s, %s, %s, %s);
    """

    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    insert_sql,
                    (logs, code, Json(signals), Json(hypotheses), final_diagnosis),
                )
            conn.commit()
        return True
    except Exception:
        return False
