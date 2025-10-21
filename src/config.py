from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    JWT_ACCESS_TOKEN_SECRET_KEY: str = ""
    JWT_REFRESH_TOKEN_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""

    # Server configuration
    SERVER_HOST: str = ""
    SERVER_PORT: int = 3000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def server_url(self) -> str:
        return f"http://localhost:{self.SERVER_PORT}"


config = Settings()
