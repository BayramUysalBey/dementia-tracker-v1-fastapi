from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    API_KEY: str = ""
    VERSION: str = "1.0.0"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = ""
    TEST_DB_NAME: str = ""
    @computed_field
    def BASE_URL(self) -> str:
        return self.DATABASE_URL.rsplit('/', 1)[0] if self.DATABASE_URL else ""
    
	
settings = Settings()
