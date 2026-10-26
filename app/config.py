
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Pipeline Guard"
    app_env: Literal["development", "testing", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = "sqlite:///./pipeline_guard.db"

    required_columns: list[str] = ["product", "quantity", "price"]
    negative_value_columns: list[str] = ["quantity", "price"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, value: str) -> str:
        """Reject blank application names."""
        value = value.strip()
        if not value:
            raise ValueError("app_name must not be blank")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Reject blank database URLs."""
        value = value.strip()
        if not value:
            raise ValueError("database_url must not be blank")
        return value

    @field_validator("required_columns", "negative_value_columns")
    @classmethod
    def validate_column_names(cls, value: list[str]) -> list[str]:
        """Reject empty or blank column names."""
        cleaned_columns = [column.strip() for column in value]

        if not cleaned_columns:
            raise ValueError("Column configuration must not be empty")

        if any(not column for column in cleaned_columns):
            raise ValueError("Column names must not be blank")

        if len(cleaned_columns) != len(set(cleaned_columns)):
            raise ValueError("Column names must not contain duplicates")

        return cleaned_columns


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return one cached settings instance."""
    return Settings()
