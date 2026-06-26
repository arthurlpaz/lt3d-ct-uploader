"""
Application factory
====================
Builds the FastAPI app: global auth dependency, CORS and routers.
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import REALM
from app.routers import api, pages
from app.security import verify

app = FastAPI(title=REALM, dependencies=[Depends(verify)])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages.router)
app.include_router(api.router)
