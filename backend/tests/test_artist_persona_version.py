from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.api.artists import save_persona_version
from app.db.models import Artist, Base, PromptVersion
from app.db.seed import seed_demo_data
from app.schemas.artists import PersonaVersionSave


def test_save_persona_version_updates_artist_and_creates_latest_prompt_version():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    ids = seed_demo_data(db)

    result = save_persona_version(
        ids["artist_id"],
        PersonaVersionSave(
            name="persona-editor-test",
            artist_name="LUMI NOA",
            fan_boundary_level="Warm distance",
            speech_style="Evidence first, then one concrete studio image.",
            personality="Careful, grounded, lightly funny, never possessive.",
            forbidden_statements="No romance, dependency, professional advice, or invented lore.",
            worldview_summary="Blue Garage is a working studio with tape hiss and a blue lamp.",
        ),
        db,
    )

    artist = db.get(Artist, ids["artist_id"])
    prompt_version = db.scalar(select(PromptVersion).where(PromptVersion.name == "persona-editor-test"))

    assert artist.speech_style == "Evidence first, then one concrete studio image."
    assert prompt_version is not None
    assert "Blue Garage is a working studio" in prompt_version.system_prompt
    assert prompt_version.safety_template.startswith("No romance")
    assert result["prompt_version"]["name"] == "persona-editor-test"
