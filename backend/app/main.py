from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import artists, chat, evals, fans, kb
from app.db.seed import seed_demo_data
from app.db.session import SessionLocal, init_db

app = FastAPI(title="Blue Garage AI Artist Lab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(artists.router)
app.include_router(fans.router)
app.include_router(kb.router)
app.include_router(evals.router)


@app.on_event("startup")
def startup() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

