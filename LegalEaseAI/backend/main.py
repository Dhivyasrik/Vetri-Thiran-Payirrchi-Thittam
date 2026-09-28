from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from backend.config import get_settings

from backend.routes import router


settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    version=settings.app_version,

    description=(
        "AI-powered legal document "
        "drafting API."
    ),
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=(
        settings.cors_origin_list
    ),

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST"
    ],

    allow_headers=["*"],
)


app.include_router(router)