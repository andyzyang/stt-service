from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VOSK_MODEL_PATH: str = "/model"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"


settings = Settings()
