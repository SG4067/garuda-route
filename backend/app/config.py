"""Environment-backed application settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GARUDAROUTE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "GarudaRoute API"
    environment: str = "development"
    debug: bool = False
    risk_roads_file: Path | None = None
    risk_road_to_location_json: str = "{}"


settings = Settings()
