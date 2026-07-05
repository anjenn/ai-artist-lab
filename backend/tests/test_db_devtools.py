from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.devtools import reset_database
from app.db.models import Artist, Base


def test_reset_database_drops_recreates_and_seeds_demo_data():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_factory() as db:
        db.add(Artist(name="TEMP"))
        db.commit()

    result = reset_database(engine, session_factory)

    with session_factory() as db:
        artists = list(db.scalars(select(Artist)).all())

    assert result["database_reset"] is True
    assert result["seed_ids"]["artist_id"] == 1
    assert [artist.name for artist in artists] == ["LUMI NOA"]
