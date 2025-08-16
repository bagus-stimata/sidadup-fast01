# from pydantic import BaseSettings untuk dibawah <2.0.0
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str = ""
    ALGORITHM: str = ""  # "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0
    DATABASE_URL: str = "sqlite:///./test.db"

    # class Config:
    #     env_file = ".env"
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
