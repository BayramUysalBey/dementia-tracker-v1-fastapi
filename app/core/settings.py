from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    VERSION: str = "1.0.0"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = ""
    TEST_DB_NAME: str = ""
    SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENTRY_DSN: str | None = None
    BASE_URL: str = ""
    BASE_URL_FRONT_ONE: str = ""
    BASE_URL_FRONT_TWO: str = ""
    
    MEDIA_UPLOAD_DIR: str = "static/uploads/media"
    
    
settings = Settings()
