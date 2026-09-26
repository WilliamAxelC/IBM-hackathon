"""KevGate configuration — loaded from .kevgate.toml or environment variables."""

from __future__ import annotations

from typing import Any, Literal, Tuple, Type

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class KevGateConfig(BaseSettings):
    """
    KevGate runtime configuration.

    Resolution order (highest to lowest priority):
      1. Environment variables prefixed with KEVGATE_
      2. .kevgate.toml in the current working directory
      3. Defaults defined here
    """

    model_config = SettingsConfigDict(
        env_prefix="KEVGATE_",
        toml_file=".kevgate.toml",
        toml_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )

    # LM Studio connection
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="Base URL of the LM Studio OpenAI-compatible API.",
    )
    lmstudio_model: str = Field(
        default="kev-4b",
        description="Model identifier to pass in the chat completion request.",
    )
    request_timeout_ms: int = Field(
        default=500,
        description="HTTP request timeout in milliseconds. Requests exceeding this raise LMStudioUnavailableError.",
    )

    # Gate thresholds
    block_threshold: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Risk score at or above which commits are hard-blocked (exit 1).",
    )
    warn_threshold: int = Field(
        default=30,
        ge=0,
        le=100,
        description="Risk score at or above (but below block_threshold) which a warning is printed but the commit is allowed.",
    )

    # Entropy scanner
    entropy_threshold: float = Field(
        default=4.5,
        description="Shannon entropy threshold above which a string is flagged as a potential secret.",
    )

    # Offline behaviour
    offline_behavior: Literal["pass", "fail", "warn"] = Field(
        default="warn",
        description=(
            "What to do when LM Studio is unreachable: "
            "'pass' silently allows the commit, "
            "'fail' hard-blocks with exit 1, "
            "'warn' prints a warning and allows the commit."
        ),
    )

    # MCP server
    mcp_server_name: str = Field(
        default="kevgate",
        description="MCP server name advertised to clients.",
    )
