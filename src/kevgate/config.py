"""S1Gate configuration — loaded from .env, .s1gate.toml, .kevgate.toml, or environment variables."""

from __future__ import annotations

import os
from typing import Any, Literal, Optional, Tuple, Type

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

# Load .env into os.environ if present
load_dotenv(".env")


class S1GateConfig(BaseSettings):
    """
    S1Gate runtime configuration.

    Resolution order (highest to lowest priority):
      1. Environment variables (S1GATE_*, KEVGATE_*, GEMINI_API_KEY)
      2. .env file in the current working directory (NEVER COMMITTED)
      3. .s1gate.toml or .kevgate.toml in the current working directory
      4. Defaults defined here
    """

    model_config = SettingsConfigDict(
        env_prefix="S1GATE_",
        env_file=".env",
        env_file_encoding="utf-8",
        toml_file=".s1gate.toml",
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
        toml_file = ".s1gate.toml" if os.path.exists(".s1gate.toml") else ".kevgate.toml"
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
        )

    # Backend selection: 'gemini' (cloud MVP, sub-150ms) or 'lmstudio' (local offline GPU)
    backend: Literal["gemini", "lmstudio"] = Field(
        default="gemini",
        description="Decision backend: 'gemini' (cloud MVP) or 'lmstudio' (local)",
    )

    # Gemini API configuration (loaded from .env)
    gemini_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY") or os.getenv("S1GATE_GEMINI_API_KEY"),
        description="Google Gemini API key (loaded from GEMINI_API_KEY in .env)",
    )
    gemini_model: str = Field(
        default="gemini-3.1-flash-lite",
        description="Google Gemini model identifier for System-1 triage",
    )

    # LM Studio connection (for offline local GPU mode)
    lmstudio_base_url: str = Field(
        default_factory=lambda: os.getenv("LMSTUDIO_BASE_URL") or os.getenv("KEVGATE_LMSTUDIO_BASE_URL") or "http://localhost:1234/v1",
        description="Base URL of the LM Studio OpenAI-compatible API.",
    )
    lmstudio_model: str = Field(
        default_factory=lambda: os.getenv("LMSTUDIO_MODEL") or os.getenv("KEVGATE_LMSTUDIO_MODEL") or "qwen2.5-coder-3b-instruct",
        description="Model identifier to pass in the chat completion request.",
    )
    request_timeout_ms: int = Field(
        default=2500,
        description="HTTP request timeout in milliseconds.",
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
            "What to do when the backend is unreachable: "
            "'pass' silently allows the commit, "
            "'fail' hard-blocks with exit 1, "
            "'warn' prints a warning and allows the commit."
        ),
    )

    # MCP server
    mcp_server_name: str = Field(
        default="s1gate",
        description="MCP server name advertised to clients.",
    )


# Backwards compatibility alias
KevGateConfig = S1GateConfig
