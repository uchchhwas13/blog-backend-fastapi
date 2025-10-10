from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    JWT_ACCESS_TOKEN_SECRET_KEY: str = ""
    JWT_REFRESH_TOKEN_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Server configuration
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 3000
    
    # Base URL for file resources (can be overridden for production)
    BASE_URL: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    @property
    def server_url(self) -> str:
        """Construct the full server URL."""
        if self.BASE_URL:
            return self.BASE_URL
        return f"http://{self.SERVER_HOST}:{self.SERVER_PORT}"


config = Settings()
