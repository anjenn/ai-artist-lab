from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.models import Base
from app.db.seed import seed_demo_data
from app.db.session import _engine_kwargs
from app.services.rag_service import RagService


def reset_database(engine: Engine, session_factory: sessionmaker) -> dict[str, Any]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with session_factory() as db:
        ids = seed_demo_data(db)
    return {"database_reset": True, "seed_ids": ids}


def reset_dev_database(
    *,
    database_url: str | None = None,
    kb_dir: str | Path = "../knowledge_base",
    chroma_path: str | Path | None = None,
    reindex: bool = True,
) -> dict[str, Any]:
    settings = get_settings()
    url = database_url or settings.database_url
    engine = create_engine(url, **_engine_kwargs(url))
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    result = reset_database(engine, session_factory)
    if reindex:
        result["rag_index"] = RagService(chroma_path=str(chroma_path) if chroma_path else None).index_knowledge_base(str(kb_dir))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset the local dev database, reseed demo data, and optionally reindex the KB.")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--kb-dir", default="../knowledge_base")
    parser.add_argument("--chroma-path", default=None)
    parser.add_argument("--skip-reindex", action="store_true")
    args = parser.parse_args()
    result = reset_dev_database(
        database_url=args.database_url,
        kb_dir=args.kb_dir,
        chroma_path=args.chroma_path,
        reindex=not args.skip_reindex,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
