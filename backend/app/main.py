from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routers import assignments, auth, gifts, groups, invitations, notifications, participants, wishlists
from app.config import get_settings
from app.database import Base, engine

WEB_DIR = Path(__file__).parent / "web"

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SecretSanta API",
    version="1.0.0",
    description="Gift exchange platform API used by the SecretSanta Android app.",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_origins = settings.cors_origin_list or ["*"]
_wildcard = _origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _wildcard else _origins,
    allow_credentials=not _wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(invitations.router)
app.include_router(participants.router)
app.include_router(wishlists.router)
app.include_router(assignments.router)
app.include_router(gifts.router)
app.include_router(notifications.router)


@app.on_event("startup")
def on_startup() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "secretsanta"}


@app.get("/api/public/how-it-works")
def how_it_works() -> dict:
    return {
        "title": "How Secret Santa works",
        "steps": [
            {"title": "Create a group", "body": "Name the exchange, set a budget, date and privacy mode."},
            {"title": "Invite people", "body": "Share a unique join link over WhatsApp, email or messages."},
            {"title": "Collect wishlists", "body": "Everyone adds gift ideas. Only their Secret Santa can see them."},
            {"title": "Draw names", "body": "The organizer starts a fair random draw. Nobody gets themselves."},
            {"title": "Give the gift", "body": "Track shopping, shipping and delivery until the reveal."},
        ],
    }


@app.get("/api/public/gift-ideas")
def gift_ideas() -> dict:
    return {
        "title": "Secret Santa gift ideas",
        "collections": [
            {
                "slug": "office",
                "title": "Office Secret Santa",
                "ideas": ["Desk plant", "Good notebook", "Coffee sampler", "Noise-cancelling earplugs"],
            },
            {
                "slug": "family",
                "title": "Family gift exchange",
                "ideas": ["Photo book", "Board game", "Hot chocolate kit", "Cozy socks"],
            },
            {
                "slug": "christmas",
                "title": "Christmas 2026",
                "ideas": ["Fairy lights", "Recipe journal", "Reusable wrap kit", "Local artisan chocolate"],
            },
        ],
    }


@app.get("/")
def homepage():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/{full_path:path}")
def spa_pages(full_path: str):
    blocked = ("api/", "docs", "redoc", "openapi.json", "health", "web/")
    if full_path.startswith(blocked) or full_path in {"docs", "redoc", "openapi.json", "health"}:
        raise HTTPException(status_code=404, detail="Not found")
    page = WEB_DIR / full_path
    if page.is_file():
        return FileResponse(page)
    return FileResponse(WEB_DIR / "index.html")


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        raise exc
    if settings.app_env == "development":
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Something went wrong"})
