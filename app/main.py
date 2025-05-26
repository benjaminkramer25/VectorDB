from fastapi import FastAPI
from .api import api_router

def create_app() -> FastAPI:
    app = FastAPI(title="Vector-DB Demo")
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()      # for `uvicorn app.main:app`
