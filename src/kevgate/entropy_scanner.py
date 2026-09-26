"""
Fast pre-filter: Shannon entropy scanner and regex secret detector.

Runs in <2ms on typical diffs. Catches hardcoded secrets and high-entropy
strings before dispatching to the LM Studio decision engine.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from kevgate.schema import SecretFinding

# ---------------------------------------------------------------------------
# Secret regex patterns
# ---------------------------------------------------------------------------

_SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key",      re.compile(r"AKIA[0-9A-Z]{16}")),
    ("aws_secret_key",      re.compile(r"(?i)aws.{0,20}secret.{0,20}['\"][0-9A-Za-z/+]{40}['\"]")),
    ("github_pat_classic",  re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("github_pat_fine",     re.compile(r"github_pat_[A-Za-z0-9_]{82}")),
    ("github_oauth",        re.compile(r"gho_[A-Za-z0-9]{36}")),
    ("private_key_header",  re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----")),
    ("generic_api_key",     re.compile(r"(?i)(api[_-]?key|api[_-]?secret|access[_-]?token)\s*[=:]\s*['\"][A-Za-z0-9+/\-_]{20,}['\"]")),
    ("slack_token",         re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,48}")),
    ("stripe_key",          re.compile(r"sk_(live|test)_[0-9A-Za-z]{24,}")),
    ("dotenv_secret",       re.compile(r"(?m)^[+]\s*[A-Z_]+(SECRET|TOKEN|KEY|PASSWORD|PASSWD|PWD)\s*=\s*.{8,}")),
    ("bearer_token",        re.compile(r"(?i)authorization\s*[:=]\s*['\"]?Bearer\s+[A-Za-z0-9\-._~+/]{20,}['\"]?")),
    ("hex_secret_40plus",   re.compile(r"(?<![a-fA-F0-9])[0-9a-fA-F]{40,}(?![a-fA-F0-9])")),
]


# ---------------------------------------------------------------------------
# Shannon entropy
# ---------------------------------------------------------------------------

def shannon_entropy(data: str) -> float:
    """
    Calculate Shannon entropy of a string in bits per character.
    Returns 0.0 for empty or single-character strings.
    """
    if len(data) < 2:
        return 0.0
    freq: dict[str, int] = {}
    for ch in data:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


# ---------------------------------------------------------------------------
# Diff scanning
# ---------------------------------------------------------------------------

def scan_diff(diff: str, entropy_threshold: float = 4.5) -> list[SecretFinding]:
    """
    Scan a unified diff string for potential secrets and high-entropy strings.

    Only added lines (lines starting with '+' but not '+++') are evaluated,
    since removed lines are being deleted and pose no forward risk.

    Args:
        diff: Raw unified diff text.
        entropy_threshold: Strings with entropy above this are flagged.

    Returns:
        List of SecretFinding objects. Empty list means no findings.
    """
    findings: list[SecretFinding] = []

    for line_number, line in enumerate(diff.splitlines(), start=1):
        # Only scan added lines
        if not line.startswith("+") or line.startswith("+++"):
            continue

        content = line[1:]  # strip leading '+'

        # Pattern matching
        for pattern_name, pattern in _SECRET_PATTERNS:
            match = pattern.search(content)
            if match:
                matched = match.group(0)
                entropy = shannon_entropy(matched)
                findings.append(
                    SecretFinding(
                        line_number=line_number,
                        pattern_name=pattern_name,
                        matched_text=matched[:80],  # truncate for safety
                        entropy_score=entropy,
                        is_high_entropy=entropy >= entropy_threshold,
                    )
                )

        # High-entropy token scan (catches secrets not covered by patterns)
        # Split on common delimiters and check each token
        for token in re.split(r"""[\s'"=:,(){}\[\]<>]""", content):
            if len(token) >= 20:
                entropy = shannon_entropy(token)
                if entropy >= entropy_threshold:
                    # Avoid duplicate with pattern findings
                    already_found = any(
                        f.matched_text == token[:80] for f in findings
                        if f.line_number == line_number
                    )
                    if not already_found:
                        findings.append(
                            SecretFinding(
                                line_number=line_number,
                                pattern_name="high_entropy_token",
                                matched_text=token[:80],
                                entropy_score=round(entropy, 3),
                                is_high_entropy=True,
                            )
                        )

    return findings


def has_critical_secret(findings: list[SecretFinding]) -> bool:
    """Returns True if any finding is a pattern match or high-entropy string."""
    return any(f.pattern_name != "high_entropy_token" or f.is_high_entropy for f in findings)
