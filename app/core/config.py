from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    embedding_api_key: str = "A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO"  # demo

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
