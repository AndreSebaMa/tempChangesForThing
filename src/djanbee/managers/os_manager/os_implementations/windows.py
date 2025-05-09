import os
from pathlib import Path
from typing import List, Optional

from ..base import BaseOSManager
from ..command import CommandRunner, CommandResult

class WindowsOSManager(BaseOSManager):
    def __init__(self):
        self._runner = CommandRunner()

    def get_current_directory(self) -> Path:
        return Path.cwd().resolve()

    def change_directory(self, path: Path) -> None:
        os.chdir(path)

    def get_pip_path(self, venv_path: Path) -> Path:
        return venv_path / "Scripts" / "pip.exe"

    def run_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        sudo: bool = False
    ) -> CommandResult:
        return self._runner.run(args, cwd, sudo=False)

    def run_python_command(
        self,
        command_args: List[str]
    ) -> CommandResult:
        return self.run_command(["python"] + command_args)

    def check_pip_package_installed(self, package_name: str) -> bool:
        res = self.run_command([str(self.get_pip_path(Path("."))), "show", package_name])
        return res.success

    def install_pip_package(self, package_name: str) -> CommandResult:
        return self.run_command([str(self.get_pip_path(Path("."))), "install", package_name])

    def check_package_installed(self, package_name: str) -> bool:
        res = self.run_command(["where", package_name])
        return res.success

    def install_package(self, package_name: str) -> CommandResult:
        return self.run_command([
            "winget", "install", "--exact", package_name,
            "--accept-source-agreements", "--accept-package-agreements"
        ])

    def check_service_status(self, service_name: str) -> bool:
        res = self.run_command(["sc", "query", service_name])
        return res.success and "RUNNING" in res.stdout

    def start_service(self, service_name: str) -> CommandResult:
        return self.run_command(["sc", "start", service_name])

    def stop_service(self, service_name: str) -> CommandResult:
        return self.run_command(["sc", "stop", service_name])

    def restart_service(self, service_name: str) -> CommandResult:
        stop = self.stop_service(service_name)
        if not stop.success:
            return stop
        return self.start_service(service_name)

    def enable_service(self, service_name: str) -> CommandResult:
        return self.run_command(["sc", "config", service_name, "start=auto"])

    def reload_daemon(self) -> CommandResult:
        return CommandResult(True, "", "")

    def file_exists(self, path: Path) -> bool:
        return path.is_file()

    def directory_exists(self, path: Path) -> bool:
        return path.is_dir()

    def get_username(self) -> str:
        res = self.run_command(["whoami"])
        return res.stdout if res.success else ""

    def is_admin(self) -> bool:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def is_venv_directory(self, path: Path) -> bool:
        return (path / "pyvenv.cfg").exists() and (path / "Scripts").is_dir()

    def check_directory_exists(self, dir_path: str) -> bool:
        return Path(dir_path).is_dir()

    def check_file_exists(self, file_path: Path) -> bool:
        return file_path.is_file()

    def user_exists(self, username: str) -> bool:
        res = self.run_command(["net", "user", username])
        return res.success
