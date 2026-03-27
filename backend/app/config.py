from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./metabuscador.db"
    daily_search_limit: int = 50

    model_config = {"env_file": ".env"}

settings = Settings()
