"""Example service code with intentional defects for debugging demos."""

import logging
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

DB_URL = "postgresql://demo:demo@db:5432/shop"
engine = create_engine(
    DB_URL,
    pool_size=5,
    max_overflow=0,
    pool_timeout=1,
)
SessionLocal = sessionmaker(bind=engine)

# Bug: shared global session object across requests.
global_session = SessionLocal()


def get_user_orders(user_id: int):
    retries = 3
    for attempt in range(retries):
        try:
            rows = global_session.execute(
                text("SELECT id, status FROM orders WHERE user_id = :uid"),
                {"uid": user_id},
            ).fetchall()
            return rows
        except Exception as exc:
            logger.error("db query failed: %s, attempt=%s", exc, attempt + 1)
            # Bug: tight retry loop with fixed sleep can amplify load.
            time.sleep(0.1)

    return []
