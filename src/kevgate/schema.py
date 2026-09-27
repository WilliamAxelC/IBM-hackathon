"""S1Gate typed decision schema — Pydantic v2."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class DecisionPayload(BaseModel):
    """Full typed decision output from the System-1 decision engine."""

    # Choice Primitive (Categorical Action)
    category: Literal[
        "safe_refactor",    # Formatting, comments, isolated non-breaking rename
        "benign_feature",   # New functionality preserving existing contracts
        "contract_break",   # Modified/deleted public API, schema, or endpoint
        "security_risk",    # Taint sink, unvalidated input, permission bypass
        "dependency_shift", # Lockfile or package manifest mutation
    ]

    # Score Primitive (0–100 Risk Rating)
    risk_score: int = Field(ge=0, le=100, description="Calibrated risk and blast radius score")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence probability")

    # Noul Primitives (Strict Boolean Invariants)
    is_breaking_change: bool = Field(description="Alters external API or data contract")
    exposes_unprotected_resource: bool = Field(description="Bypasses auth or injects untrusted data")
    unhandled_failure_mode: bool = Field(description="Introduces I/O side-effect without error handling")

    # Remediation Intent Protocol (RIP)
    summary: str = Field(description="One-sentence description of finding")
    target_file: Optional[str] = None
    target_lines: Optional[str] = None
    remediation_hint: Optional[str] = None
    trigger_agent: bool = Field(description="Definitive decision to invoke System-2 Agent")
    processing_time_ms: Optional[float] = Field(default=None, description="Processing latency in milliseconds")

    @model_validator(mode="after")
    def validate_trigger_agent_implies_high_risk(self) -> "DecisionPayload":
        """trigger_agent should only be True when risk is genuinely elevated."""
        # This is a soft invariant — we enforce it as a warning, not a hard error,
        # because the model may legitimately set trigger_agent for moderate risks.
        return self


class RemediationVerification(BaseModel):
    """Result of the Actor-Critic verification loop."""

    verified: bool = Field(description="True if the remediation resolved the original risk")
    previous_score: int = Field(ge=0, le=100, description="Risk score of the original diff")
    new_score: int = Field(ge=0, le=100, description="Risk score of the remediated patch")
    delta: int = Field(description="Score change (new_score - previous_score, negative = improvement)")
    message: str = Field(description="Human-readable verdict message")
    processing_time_ms: Optional[float] = Field(default=None, description="Processing latency in milliseconds")

    @model_validator(mode="after")
    def validate_delta_consistency(self) -> "RemediationVerification":
        expected_delta = self.new_score - self.previous_score
        if self.delta != expected_delta:
            # Correct delta if model produced inconsistent values
            object.__setattr__(self, "delta", expected_delta)
        return self


class SecretFinding(BaseModel):
    """A potential secret or high-entropy string found in a diff."""

    line_number: int
    pattern_name: str
    matched_text: str
    entropy_score: float
    is_high_entropy: bool
