import os
from pathlib import Path
from typing import List, Optional

from ..base import BaseOSManager
from ..command import CommandRunner, CommandResult

class UnixOSManager(BaseOSManager):
    def __init__(self):
        self._runner = CommandRunner()

    def get_current_directory(self) -> Path:
        return Path.cwd().resolve()

    def change_directory(self, path: Path) -> None:
        os.chdir(path)

    def get_pip_path(self, venv_path: Path) -> Path:
        return venv_path / "bin" / "pip"

    def run_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        sudo: bool = False
    ) -> CommandResult:
        return self._runner.run(args, cwd, sudo)

    def run_python_command(
        self,
        command_args: List[str]
    ) -> CommandResult:
        which3 = self._runner.run(["which", "python3"])
        python_exec = which3.stdout if which3.success else None

        if not python_exec:
            which = self._runner.run(["which", "python"])
            python_exec = which.stdout if which.success else None

        if not python_exec:
            return CommandResult(False, "", "Could not find any python executable")

        return self.run_command([python_exec] + command_args)

    def check_pip_package_installed(self, package_name: str) -> bool:
        res = self.run_command(
            [self.get_pip_path(Path(".")), "show", package_name]
        )
        return res.success

    def install_pip_package(self, package_name: str) -> CommandResult:
        return self.run_command(
            [self.get_pip_path(Path(".")), "install", package_name],
            sudo=False
        )

    def check_package_installed(self, package_name: str) -> bool:
        res = self.run_command(["which", package_name])
        return res.success

    def install_package(self, package_name: str) -> CommandResult:
        update = self.run_command(["apt-get", "update"], sudo=True)
        if not update.success:
            return update

        return self.run_command(
            ["apt-get", "install", "-y", package_name],
            sudo=True
        )

    def check_service_status(self, service_name: str) -> bool:
        res = self.run_command(["systemctl", "is-active", service_name])
        return res.success and res.stdout.strip() == "active"

    def start_service(self, service_name: str) -> CommandResult:
        return self.run_command(["systemctl", "start", service_name], sudo=True)

    def stop_service(self, service_name: str) -> CommandResult:
        return self.run_command(["systemctl", "stop", service_name], sudo=True)

    def restart_service(self, service_name: str) -> CommandResult:
        return self.run_command(["systemctl", "restart", service_name], sudo=True)

    def enable_service(self, service_name: str) -> CommandResult:
        return self.run_command(["systemctl", "enable", service_name], sudo=True)

    def reload_daemon(self) -> CommandResult:
        return self.run_command(["systemctl", "daemon-reload"], sudo=True)

    def file_exists(self, path: Path) -> bool:
        return path.is_file()

    def directory_exists(self, path: Path) -> bool:
        return path.is_dir()

    def get_username(self) -> str:
        res = self.run_command(["whoami"])
        return res.stdout if res.success else ""

    def is_admin(self) -> bool:
        try:
            return os.geteuid() == 0
        except Exception:
            return False

    def is_venv_directory(self, path: Path) -> bool:
        return (path / "pyvenv.cfg").exists() and (path / "bin").is_dir()


    def user_exists(self, username: str) -> bool:
        res = self.run_command(["id", username])
        return res.success
