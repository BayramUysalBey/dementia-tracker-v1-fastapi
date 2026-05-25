from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    VERSION: str = "1.0.0"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = ""
    TEST_DB_NAME: str = ""
    SECRET_KEY: str = " "
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENTRY_DSN: str | None = None
    
    MEDIA_UPLOAD_DIR: str = "static/uploads/media"
    
    MAIL_USERNAME: EmailStr | None = None
    MAIL_PASSWORD: str = ""
    MAIL_FROM: EmailStr | None = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    

settings = Settings()
