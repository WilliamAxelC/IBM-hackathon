"""S1Gate exception hierarchy."""


class S1GateError(Exception):
    """Base exception for all S1Gate errors."""


# Backwards compatibility alias
KevGateError = S1GateError


class LMStudioUnavailableError(S1GateError):
    """Raised when the LM Studio server cannot be reached within the timeout."""

    def __init__(self, url: str, timeout_ms: int) -> None:
        super().__init__(
            f"LM Studio unreachable at {url} (timeout: {timeout_ms}ms). "
            "Ensure LM Studio is running and a model is loaded. "
            "Set KEVGATE_OFFLINE_BEHAVIOR=pass to skip the gate when offline."
        )
        self.url = url
        self.timeout_ms = timeout_ms


class GeminiUnavailableError(S1GateError):
    """Raised when the Gemini API cannot be reached or API key is missing."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message



class DecisionParseError(S1GateError):
    """Raised when the model response cannot be parsed into a DecisionPayload."""

    def __init__(self, raw_response: str, cause: Exception) -> None:
        super().__init__(
            f"Failed to parse model response into DecisionPayload: {cause}\n"
            f"Raw response: {raw_response!r}"
        )
        self.raw_response = raw_response
        self.cause = cause


class GateBlockedError(S1GateError):
    """Raised (optionally) when the gate decision is BLOCK."""

    def __init__(self, summary: str, risk_score: int) -> None:
        super().__init__(
            f"Gate BLOCKED — risk_score={risk_score}: {summary}"
        )
        self.summary = summary
        self.risk_score = risk_score
