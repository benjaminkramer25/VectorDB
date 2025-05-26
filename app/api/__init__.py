from fastapi import APIRouter
from .v1 import libraries, chunks

api_router = APIRouter()
api_router.include_router(libraries.router)
api_router.include_router(chunks.router)
