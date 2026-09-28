from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    pncp_base_url: str = Field(default="https://pncp.gov.br/api/pncp")
    pncp_query_base_url: str = Field(default="https://pncp.gov.br/api/consulta")
    pncp_timeout_seconds: float = Field(default=30.0, gt=0)
