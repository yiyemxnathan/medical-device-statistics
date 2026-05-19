from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_version: str = "0.1.0"
    algorithm_version: str = "sampling-statistics-0.1.0"
    database_url: str = "sqlite:///./statistics.db"


settings = Settings()
