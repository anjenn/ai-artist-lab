import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import artists, chat, conversations, demo, evals, fans, kb
from app.core.config import get_settings
from app.db.seed import seed_demo_data
from app.db.session import SessionLocal, init_db
from app.services.observability import log_request_summary, request_id_from_header

app = FastAPI(title="Blue Garage AI Artist Lab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(demo.router)
app.include_router(artists.router)
app.include_router(fans.router)
app.include_router(kb.router)
app.include_router(evals.router)


@app.middleware("http")
async def request_tracing(request: Request, call_next):
    started_at = time.perf_counter()
    request_id = request_id_from_header(request.headers.get("x-request-id"))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    log_request_summary(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        started_at=started_at,
    )
    return response


@app.middleware("http")
async def demo_access_gate(request: Request, call_next):
    settings = get_settings()
    if settings.demo_access_key and request.url.path != "/health" and request.method != "OPTIONS":
        provided = request.headers.get("x-demo-access-key")
        if provided != settings.demo_access_key:
            return JSONResponse({"detail": "Demo access key required"}, status_code=401)
    return await call_next(request)


@app.on_event("startup")
def startup() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
