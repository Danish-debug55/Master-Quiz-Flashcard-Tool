from pathlib import Path

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.service import (
    get_next_card,
    review_card,
    get_dashboard,
    search_cards,
)


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Mastery Flashcards")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ReviewRequest(BaseModel):
    card_id: str
    rating: str


@app.get("/")
def home():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/next-card")
def next_card(topic: str = "All", x_user_id: str = Header(default="")):
    try:
        return get_next_card(x_user_id, topic)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/api/review")
def review_card_route(payload: ReviewRequest, x_user_id: str = Header(default="")):
    try:
        return review_card(x_user_id, payload.card_id, payload.rating)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/api/dashboard")
def dashboard_route(x_user_id: str = Header(default="")):
    try:
        return get_dashboard(x_user_id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/api/search")
def search_route(query: str = "", topic: str = "All"):
    try:
        return {"results": search_cards(query, topic)}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
