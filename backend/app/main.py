from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import get_settings
from backend.app.core.logging_config import configure_logging
from backend.app.api.routes import router

s = get_settings()
configure_logging()

app = FastAPI(title=s.APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=s.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=s.API_PREFIX)