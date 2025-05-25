from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "TodoApp"
    PROJECT_VERSION: str = "0.1.0"
    SECRET_KEY: str = "your-secret-key-here"
    DATABASE_URL: str = "sqlite:///./todos.db"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
