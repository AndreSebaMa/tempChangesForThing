import platform
from pathlib import Path
from typing import List, Optional

from .base import BaseOSManager
from .command import CommandResult
from .os_implementations import UnixOSManager, WindowsOSManager

class OSManager:
    """Facade that picks the right OS-specific implementation,
       and exposes only low-level OS calls."""

    def __init__(self):
        system = platform.system().lower()
        if system == "windows":
            self._impl: BaseOSManager = WindowsOSManager()
        else:
            self._impl: BaseOSManager = UnixOSManager()

    def run_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        sudo: bool = False
    ) -> CommandResult:
        """Run any shell command; returns success/stdout/stderr."""
        return self._impl.run_command(args, cwd, sudo)

    def get_current_directory(self) -> Path:
        return self._impl.get_current_directory()

    def install_package(self, package_name: str) -> CommandResult:
        """Installs a system package using appropriate package manager"""
        return self._impl.install_package(package_name)

    def check_package_installed(self, package_name: str) -> bool:
        """Checks if a system package is installed"""
        return self._impl.check_package_installed(package_name)

    get_dir = get_current_directory

    def change_directory(self, path: Path) -> None:
        self._impl.change_directory(path)

    def get_pip_path(self, venv_path: Path) -> Path:
        return self._impl.get_pip_path(venv_path)

    def file_exists(self, path: Path) -> bool:
        return self._impl.file_exists(path)

    def directory_exists(self, path: Path) -> bool:
        return self._impl.directory_exists(path)

    def check_service_status(self, service_name: str) -> bool:
        return self._impl.check_service_status(service_name)

    def start_service(self, service_name: str) -> CommandResult:
        return self._impl.start_service(service_name)

    def stop_service(self, service_name: str) -> CommandResult:
        return self._impl.stop_service(service_name)

    def restart_service(self, service_name: str) -> CommandResult:
        return self._impl.restart_service(service_name)

    def enable_service(self, service_name: str) -> CommandResult:
        return self._impl.enable_service(service_name)

    def get_username(self) -> str:
        return self._impl.get_username()

    def is_admin(self) -> bool:
        return self._impl.is_admin()

    def is_venv_directory(self, path: Path) -> bool:
        return self._impl.is_venv_directory(path)

    def user_exists(self, username: str) -> bool:
        return self._impl.user_exists(username)

    def reload_daemon(self) -> CommandResult:
        return self._impl.reload_daemon()

    def run_python_command(self, args: List[str]) -> CommandResult:
        return self._impl.run_python_command(args)
