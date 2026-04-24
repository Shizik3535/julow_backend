from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.core.config import settings


def add_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allowed_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allowed_methods,
        allow_headers=settings.cors.allowed_headers,
    )
