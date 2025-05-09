# djanbee/services/requirements_service.py

from pathlib import Path
from typing import Optional, Tuple
from collections import namedtuple

from ....managers.os_manager import OSManager
from ....managers.file_system_manager import FileSystemManager
from ..state import DjangoManagerState
from .requirements_service_display import DjangoRequirementsServiceDisplay

Result = namedtuple("Result", ["valid", "object"])


class DjangoRequirementsService:
    """Service for managing virtual environment requirements"""

    def __init__(
        self,
        os_manager: OSManager,
        display: DjangoRequirementsServiceDisplay,
        fs_manager: FileSystemManager,
    ):
        self.os_manager = os_manager
        self.fs_manager = fs_manager
        self.state = DjangoManagerState.get_instance()
        self.display = display

    def find_or_extract_requirements(self, venv_path=None):
        """Find existing requirements or extract from virtual environment"""
        self.display.lookup_requirements()
        requirements = self.find_requirements()

        if not requirements:
            self.display.failure_lookup_requirements()
            if self.display.prompt_extract_requirements():
                active_venv = venv_path or self.state.active_venv_path
                if not active_venv:
                    return None, "No active virtual environment found"

                requirements = self.extract_requirements(active_venv)
            else:
                return None

        if requirements:
            # requirements.object is a Path to the requirements.txt
            self.display.success_lookup_requirements(requirements.object)

        return requirements

    def install_requirements_if_confirmed(self, requirements: Result, venv_path=None):
        """Install requirements if user confirms"""
        if self.display.prompt_install_requirements():
            self.display.progress_install_requirements()

            active_venv = venv_path or self.state.active_venv_path
            if not active_venv:
                return False, "No active virtual environment found"

            result = self.install_requirements(active_venv, requirements.object)

            if result[0]:
                self.display.success_install_requirements(
                    requirements.object, active_venv
                )
                return True, "Requirements installed successfully"
            else:
                return result
        else:
            return False, "Installation cancelled by user"

    def find_requirements(self) -> Optional[Result]:
        """
        Look for a requirements file in cwd, then in subfolders.
        Returns Result(valid=True, object=path_to_folder) or None.
        """
        cwd = Path(".")
        # 1) check in cwd
        folder = self.fs_manager.search_folder(cwd, self.has_requirements)
        # 2) if not found, check one level deep
        if not folder:
            folders = self.fs_manager.search_subfolders(cwd, self.has_requirements)
            folder = folders[0] if folders else None

        if folder:
            req_path = folder / "requirements.txt"
            self.state.current_requirements_path = req_path
            return Result(True, req_path)

        return None

    def extract_requirements(self, venv_path: str | Path) -> Tuple[bool, str]:
        """Extracts pip requirements from a virtual environment"""
        venv_path = Path(venv_path)
        requirements_file = "requirements.txt"
        output_path = self.os_manager.get_current_directory() / requirements_file

        success, output = self.os_manager.run_pip_command(venv_path, ["freeze"])
        if not success:
            return False, output

        write_success, message = self.os_manager.write_text_file(
            output_path, output
        )
        if not write_success:
            return False, message

        return Result(True, output_path)

    def install_requirements(
        self, venv_path: str | Path, requirements_path: str | Path
    ) -> Tuple[bool, str]:
        """Installs pip requirements into a virtual environment"""
        venv_path = Path(venv_path)
        requirements_path = Path(requirements_path)

        if not requirements_path.exists():
            return False, f"Requirements file not found: {requirements_path}"

        success, output = self.os_manager.run_pip_command(
            venv_path, ["install", "-r", str(requirements_path)]
        )

        if success:
            return True, "Requirements installed successfully"
        else:
            return False, output

    def has_requirements(self, path: Path) -> bool:
        """
        Validator for folder paths: returns True if folder contains
        a requirements.txt (or -dev/prod variants).
        """
        patterns = ["requirements.txt", "requirements-dev.txt", "requirements-prod.txt"]
        for name in patterns:
            if (path / name).exists():
                return True
        return False
