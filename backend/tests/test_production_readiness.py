from pathlib import Path

from app.db.models import Base


def test_initial_alembic_revision_mentions_all_model_tables():
    root = Path(__file__).resolve().parents[1]
    revision = root / "migrations" / "versions" / "0001_initial_schema.py"
    text = revision.read_text(encoding="utf-8")

    for table_name in Base.metadata.tables:
        assert f'"{table_name}"' in text


def test_deployment_artifacts_exist():
    root = Path(__file__).resolve().parents[2]

    assert (root / "Dockerfile").exists()
    assert (root / "deploy" / "render.yaml").exists()
    assert "DEMO_ACCESS_KEY" in (root / "docs" / "deployment.md").read_text(encoding="utf-8")
