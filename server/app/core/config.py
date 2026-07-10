from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # PostgreSQL Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "codeatlas"
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/codeatlas"

    # Cache Configuration
    REDIS_URL: str = "redis://redis:6379/0"

    # Security Configuration
    JWT_SECRET: str = "your-super-secret-key"

    # Third-Party AI Services API keys
    OPENAI_API_KEY: str = ""

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Dynamically adjusts the PostgreSQL database URL to explicitly use 
        the 'psycopg' (psycopg 3) driver for SQLAlchemy 2.0.
        Translates 'postgresql://' to 'postgresql+psycopg://'.
        """
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

# Instantiate the global settings object
settings = Settings()
