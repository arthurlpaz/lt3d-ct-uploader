"""
Pages
=====
Static HTML entry point for the web interface.
"""

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import STATIC_DIR

router = APIRouter()


@router.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")
