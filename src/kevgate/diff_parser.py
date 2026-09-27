"""
Git diff parser and extractor.

Parses unified diff format into structured DiffChunk objects.
Also provides helpers to extract staged diffs from the current git repo.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DiffChunk:
    """A single file's changes within a unified diff."""

    file_path: str
    """Path of the changed file (relative to repo root)."""

    added_lines: list[str] = field(default_factory=list)
    """Lines that were added (without the leading '+')."""

    removed_lines: list[str] = field(default_factory=list)
    """Lines that were removed (without the leading '-')."""

    context_lines: list[str] = field(default_factory=list)
    """Unchanged context lines (without the leading ' ')."""

    is_new_file: bool = False
    is_deleted_file: bool = False
    is_binary: bool = False

    @property
    def is_lockfile(self) -> bool:
        """True for dependency lock files that should be excluded from LLM analysis."""
        lockfile_names = {
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "poetry.lock",
            "Pipfile.lock",
            "Cargo.lock",
            "composer.lock",
            "go.sum",
            "Gemfile.lock",
            "mix.lock",
        }
        name = Path(self.file_path).name
        return name in lockfile_names

    @property
    def is_build_artifact(self) -> bool:
        """True for generated build output that should be excluded."""
        artifact_dirs = {"dist/", "build/", ".next/", "__pycache__/", "node_modules/", ".git/"}
        return any(self.file_path.startswith(d) or f"/{d}" in self.file_path for d in artifact_dirs)

    @property
    def should_skip(self) -> bool:
        """True if this chunk should be excluded from LLM triage."""
        return self.is_lockfile or self.is_build_artifact or self.is_binary


def parse_unified_diff(raw_diff: str) -> list[DiffChunk]:
    """
    Parse a raw unified diff string into a list of DiffChunk objects.

    Handles standard `git diff` output format including:
    - New file mode
    - Deleted file mode
    - Binary files
    - Multiple hunks per file

    Args:
        raw_diff: Raw unified diff text (e.g. from `git diff --cached`).

    Returns:
        List of DiffChunk objects, one per changed file.
    """
    chunks: list[DiffChunk] = []
    current: DiffChunk | None = None

    for line in raw_diff.splitlines():
        # New file header
        if line.startswith("diff --git "):
            if current is not None:
                chunks.append(current)
            # Extract file path from "diff --git a/<path> b/<path>"
            parts = line.split(" b/", 1)
            file_path = parts[1] if len(parts) == 2 else line.split()[-1]
            current = DiffChunk(file_path=file_path)
            continue
        elif current is None and (line.startswith("--- ") or line.startswith("+++ ")):
            clean = line[4:].strip().split("\t")[0]
            if clean.startswith("a/") or clean.startswith("b/"):
                clean = clean[2:]
            if clean and clean != "/dev/null":
                current = DiffChunk(file_path=clean)
            continue

        if current is None:
            continue

        if line.startswith("new file mode"):
            current.is_new_file = True
        elif line.startswith("deleted file mode"):
            current.is_deleted_file = True
        elif line.startswith("Binary files"):
            current.is_binary = True
        elif line.startswith("+++ ") or line.startswith("--- ") or line.startswith("@@ ") or line.startswith("index "):
            # Skip diff metadata headers
            continue
        elif line.startswith("+"):
            current.added_lines.append(line[1:])
        elif line.startswith("-"):
            current.removed_lines.append(line[1:])
        elif line.startswith(" "):
            current.context_lines.append(line[1:])

    if current is not None:
        chunks.append(current)

    return chunks


def filter_triageable(chunks: list[DiffChunk]) -> list[DiffChunk]:
    """Return only chunks that should be sent to the LM Studio decision engine."""
    return [c for c in chunks if not c.should_skip]


def extract_staged_diff() -> str:
    """
    Run `git diff --cached` and return the unified diff as a string.

    Raises:
        subprocess.CalledProcessError: If git command fails (not in a git repo, etc.)
        FileNotFoundError: If git is not installed.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=3"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract_file_diff(file_path: str) -> str:
    """
    Run `git diff HEAD -- <file_path>` and return the unified diff.

    Used by the MCP `s1gate_inspect_file` tool.
    """
    result = subprocess.run(
        ["git", "diff", "HEAD", "--", file_path],
        capture_output=True,
        text=True,
        check=True,
    )
    if not result.stdout:
        # Fall back to staged diff for the file
        result = subprocess.run(
            ["git", "diff", "--cached", "--", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
    return result.stdout


def chunks_to_condensed_diff(chunks: list[DiffChunk]) -> str:
    """
    Reconstruct a condensed diff string from DiffChunk objects.

    Used to build the prompt payload sent to LM Studio — strips lockfiles
    and binary artifacts before sending.
    """
    parts: list[str] = []
    for chunk in chunks:
        parts.append(f"--- a/{chunk.file_path}")
        parts.append(f"+++ b/{chunk.file_path}")
        for line in chunk.removed_lines:
            parts.append(f"-{line}")
        for line in chunk.added_lines:
            parts.append(f"+{line}")
    return "\n".join(parts)
