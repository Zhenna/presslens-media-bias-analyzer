"""
Result cache using SQLite + SQLModel.

Caches bias analysis results per (topic, outlet_id, provider) for
settings.cache_ttl_seconds (default 15 min) to avoid redundant LLM calls.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

from backend.core.config import settings
from backend.models.schemas import BiasScores

DATABASE_URL = "sqlite:///./presslens.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class CachedResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cache_key: str = Field(index=True)
    scores_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def _make_key(topic: str, outlet_id: str, provider: str) -> str:
    raw = f"{topic.lower().strip()}|{outlet_id}|{provider}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(topic: str, outlet_id: str, provider: str) -> Optional[BiasScores]:
    key = _make_key(topic, outlet_id, provider)
    cutoff = datetime.utcnow() - timedelta(seconds=settings.cache_ttl_seconds)

    with Session(engine) as session:
        stmt = select(CachedResult).where(
            CachedResult.cache_key == key,
            CachedResult.created_at >= cutoff,
        )
        row = session.exec(stmt).first()
        if row:
            return BiasScores.model_validate_json(row.scores_json)
    return None


def set_cached(topic: str, outlet_id: str, provider: str, scores: BiasScores) -> None:
    key = _make_key(topic, outlet_id, provider)
    with Session(engine) as session:
        # Delete any existing entry for this key
        old = session.exec(select(CachedResult).where(CachedResult.cache_key == key)).first()
        if old:
            session.delete(old)
        session.add(CachedResult(cache_key=key, scores_json=scores.model_dump_json()))
        session.commit()
