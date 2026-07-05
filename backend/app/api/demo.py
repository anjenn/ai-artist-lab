"""Demo interview export/import endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.demo_data import export_demo_data, import_demo_data

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/export")
def export_demo(db: Session = Depends(get_db)) -> dict:
    return export_demo_data(db)


@router.post("/import")
def import_demo(payload: dict, db: Session = Depends(get_db)) -> dict:
    result = import_demo_data(db, payload)
    if not result.get("imported"):
        raise HTTPException(status_code=400, detail=result.get("reason", "import_failed"))
    return result
