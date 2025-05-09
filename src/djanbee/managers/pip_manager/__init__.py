# djanbee/managers/pip_manager/__init__.py

from pathlib import Path
from typing import List

from ..os_manager.main import OSManager
from ..os_manager.command import CommandResult

class PipManager:
    """High-level interface for pip in any venv or system Python."""

    def __init__(self, os_mgr: OSManager):
        self._os = os_mgr

    def install(self, package: str, venv_path: Path) -> CommandResult:
        pip = self._os.get_pip_path(venv_path)
        return self._os.run_command([str(pip), "install", package])

    def uninstall(self, package: str, venv_path: Path) -> CommandResult:
        pip = self._os.get_pip_path(venv_path)
        return self._os.run_command([str(pip), "uninstall", "-y", package])

    def list_installed(self, venv_path: Path) -> CommandResult:
        pip = self._os.get_pip_path(venv_path)
        return self._os.run_command([str(pip), "list", "--format=freeze"])

    def is_installed(self, package: str, venv_path: Path) -> bool:
        res = self.list_installed(venv_path)
        return res.success and any(
            line.split("==")[0] == package for line in res.stdout.splitlines()
        )
