# djanbee/managers/os_manager/base.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from .command import CommandResult


class BaseOSManager(ABC):
    """Abstract interface for low‐level, OS‐specific operations."""

    @abstractmethod
    def run_command(
            self,
            args: List[str],
            cwd: Optional[Path] = None,
            sudo: bool = False
    ) -> CommandResult:
        """Run any shell command; return structured success/stdout/stderr."""

    @abstractmethod
    def run_python_command(
            self,
            command_args: List[str]
    ) -> CommandResult:
        """Run a Python interpreter command (e.g. `python -m venv …`)."""

    @abstractmethod
    def get_current_directory(self) -> Path:
        """Return current working directory."""

    def get_dir(self) -> Path:
        """Return current working directory."""

    @abstractmethod
    def change_directory(self, path: Path) -> None:
        """Chdir into given path (or raise)."""

    @abstractmethod
    def get_pip_path(self, venv_path: Path) -> Path:
        """Return the pip executable inside a virtualenv."""

    @abstractmethod
    def check_package_installed(self, name: str) -> bool:
        """Check if a system package/binary is available in PATH."""

    @abstractmethod
    def install_package(self, name: str) -> CommandResult:
        """Install a system package (e.g. apt, winget, etc.)."""

    @abstractmethod
    def check_service_status(self, service: str) -> bool:
        """Return True if the given service is running."""

    @abstractmethod
    def start_service(self, service: str) -> CommandResult:
        """Start a system service."""

    @abstractmethod
    def stop_service(self, service: str) -> CommandResult:
        """Stop a system service."""

    @abstractmethod
    def restart_service(self, service: str) -> CommandResult:
        """Restart a system service."""

    @abstractmethod
    def enable_service(self, service: str) -> CommandResult:
        """Enable a service to start on boot."""

    @abstractmethod
    def reload_daemon(self) -> CommandResult:
        """Reload the OS’s service daemon (e.g. systemd)."""

    @abstractmethod
    def file_exists(self, path: Path) -> bool:
        """Return True if `path` points to an existing file."""

    @abstractmethod
    def directory_exists(self, path: Path) -> bool:
        """Return True if `path` points to an existing directory."""

    @abstractmethod
    def get_username(self) -> str:
        """Return the current user’s username."""

    @abstractmethod
    def is_admin(self) -> bool:
        """Return True if running with elevated privileges."""

    @abstractmethod
    def user_exists(self, username: str) -> bool:
        """Check if a local system user exists."""

    @abstractmethod
    def is_venv_directory(self, path: Path) -> bool:
        """Detect if `path` is a Python virtualenv (pyvenv.cfg present)."""
