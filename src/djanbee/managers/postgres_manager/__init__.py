from pathlib import Path
from typing import Tuple, List

from ..pip_manager import PipManager
from ..os_manager.command import CommandResult


class PostgresManager:
    """Ensure Python Postgres drivers are present in a virtual environment."""

    def __init__(self, pip_mgr: PipManager):
        self._pip = pip_mgr

    def check_dependencies(self, venv_path: Path) -> Tuple[bool, List[str]]:
        """Return (all_present, missing_list)."""
        required = ["psycopg2", "psycopg2-binary"]
        missing: List[str] = []
        for pkg in required:
            if not self._pip.is_installed(pkg, venv_path):
                missing.append(pkg)
        return (len(missing) == 0, missing)

    def ensure_dependencies(self, venv_path: Path) -> CommandResult:
        """Install any missing Postgres drivers, one by one."""
        all_ok, missing = self.check_dependencies(venv_path)
        if all_ok:
            return CommandResult(success=True, stdout="All Postgres deps installed", stderr="")
        for pkg in missing:
            res = self._pip.install(pkg, venv_path)
            if not res.success:
                return CommandResult(
                    success=False,
                    stdout="",
                    stderr=f"Failed to install {pkg}: {res.stderr}"
                )
        return CommandResult(success=True, stdout="Installed missing Postgres deps", stderr="")
