"""
Git pre-commit hook installer and manager.

Writes/removes the .git/hooks/pre-commit file and handles
existing hook detection gracefully.
"""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

_HOOK_MARKER = "# installed-by: kevgate"

_HOOK_SCRIPT = """\
#!/bin/sh
# installed-by: kevgate
# KevGate pre-commit hook — https://github.com/WilliamAxelC/IBM-hackathon
kevgate check
"""

_HOOK_SCRIPT_PYTHON = """\
#!/bin/sh
# installed-by: kevgate
# KevGate pre-commit hook — https://github.com/WilliamAxelC/IBM-hackathon
"{python}" -m kevgate.cli check
"""


def _find_git_root(start: Path) -> Path:
    """Walk up from start until we find a .git directory."""
    current = start.resolve()
    while True:
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            raise FileNotFoundError(
                f"Not inside a git repository (searched from {start})"
            )
        current = parent


def _hooks_dir(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks"


def _hook_file(repo_root: Path) -> Path:
    return _hooks_dir(repo_root) / "pre-commit"


def _is_kevgate_hook(hook_file: Path) -> bool:
    """Return True if the hook was installed by kevgate."""
    try:
        return _HOOK_MARKER in hook_file.read_text()
    except OSError:
        return False


def install_hook(repo_root: Path | None = None) -> Path:
    """
    Install the KevGate pre-commit hook.

    Args:
        repo_root: Path to the repository root. Auto-detected from cwd if None.

    Returns:
        Path to the installed hook file.

    Raises:
        FileExistsError: If a non-KevGate pre-commit hook already exists.
        FileNotFoundError: If not in a git repository.
    """
    root = repo_root or _find_git_root(Path.cwd())
    hooks_dir = _hooks_dir(root)
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = _hook_file(root)

    if hook_file.exists() and not _is_kevgate_hook(hook_file):
        raise FileExistsError(
            f"A pre-commit hook already exists at {hook_file} and was not installed by KevGate. "
            "Remove it manually or back it up, then re-run `kevgate hook install`."
        )

    # Prefer calling kevgate directly if on PATH; fall back to python -m
    python_exe = sys.executable
    if _kevgate_on_path():
        script = _HOOK_SCRIPT
    else:
        script = _HOOK_SCRIPT_PYTHON.format(python=python_exe)

    hook_file.write_text(script)
    # Make executable
    current_mode = hook_file.stat().st_mode
    hook_file.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return hook_file


def uninstall_hook(repo_root: Path | None = None) -> bool:
    """
    Remove the KevGate pre-commit hook.

    Args:
        repo_root: Path to the repository root. Auto-detected from cwd if None.

    Returns:
        True if the hook was removed, False if no KevGate hook was found.

    Raises:
        PermissionError: If the hook exists but was not installed by KevGate.
    """
    root = repo_root or _find_git_root(Path.cwd())
    hook_file = _hook_file(root)

    if not hook_file.exists():
        return False

    if not _is_kevgate_hook(hook_file):
        raise PermissionError(
            f"Pre-commit hook at {hook_file} was not installed by KevGate. "
            "Remove it manually if intended."
        )

    hook_file.unlink()
    return True


def _kevgate_on_path() -> bool:
    """Check if the `kevgate` command is available on PATH."""
    import shutil
    return shutil.which("kevgate") is not None
