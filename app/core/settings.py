from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_KEY: str = ""
    VERSION: str = "1.0.0"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = ""
    TEST_DB_NAME: str = "test_dementia_db"
    BASE_URL: str = DATABASE_URL.rsplit('/', 1)[0]
	
settings = Settings()
