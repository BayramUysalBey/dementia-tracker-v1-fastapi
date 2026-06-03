from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, field_validator

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
    
    @field_validator("DATABASE_URL")
    @classmethod
    def check_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "DATABASE_URL is missing! If you are deploying to a cloud provider "
                "(like Railway, Render, etc.), you MUST set the DATABASE_URL environment "
                "variable in their dashboard. The .env file is NOT uploaded to the cloud."
            )
        if v.startswith('"') or v.startswith("'"):
            raise ValueError(
                "DATABASE_URL should NOT start with quotation marks. "
                "Remove the quotes from your environment variables in your cloud dashboard."
            )
        return v
    
settings = Settings()
