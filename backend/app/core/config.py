import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "local-chatbot"
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5173", "http://127.0.0.1:5500"]

    # Transformers / Model
    HF_MODEL_NAME: str = Field("databricks/dolly-v2-3b", env="HF_MODEL_NAME")
    TRUST_REMOTE_CODE: bool = Field(False, env="TRUST_REMOTE_CODE")
    MAX_NEW_TOKENS: int = Field(512, env="MAX_NEW_TOKENS")
    TEMPERATURE: float = Field(0.7, env="TEMPERATURE")
    TOP_P: float = Field(0.95, env="TOP_P")

    # Performance
    DEVICE_MAP: str = Field("auto", env="DEVICE_MAP")  # e.g. "auto", "cpu", "cuda"
    OFFLOAD_FOLDER: str = Field("./offload", env="OFFLOAD_FOLDER")  # e.g. "auto", "cpu", "cuda"
    TORCH_DTYPE: str = Field("auto", env="TORCH_DTYPE") # e.g. "auto", "float16", "bfloat16"

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()