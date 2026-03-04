from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    database_url: str = "postgresql+asyncpg://agent_user:agent_pass@localhost:5432/agent_db"
    redis_url: str = "redis://localhost:6379"

    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    max_agent_steps: int = 10
    session_ttl_seconds: int = 86400

settings = Settings()

