from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Water Monitor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Threshold (cm)
    THRESHOLD_WASPADA: int = 50
    THRESHOLD_BAHAYA: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
