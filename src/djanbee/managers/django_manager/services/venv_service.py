# djanbee/services/venv_service.py

from pathlib import Path
import sys
import venv
from typing import Optional, List, Union
from collections import namedtuple

from ....managers.os_manager import OSManager
from ....managers.file_system_manager import FileSystemManager
from ..state import DjangoManagerState
from .venv_service_display import DjangoEnvironmentServiceDisplay

Result = namedtuple("Result", ["valid", "object"])


class DjangoEnvironmentService:
    """Service for detecting and creating Python virtual environments"""

    def __init__(
        self,
        os_manager: OSManager,
        display: DjangoEnvironmentServiceDisplay,
        fs_manager: FileSystemManager,
    ):
        self.os_manager = os_manager
        self.display = display
        self.state = DjangoManagerState.get_instance()
        self.fs_manager = fs_manager

    def get_active_venv(self) -> Optional[Result]:
        """Detects the currently active venv via VIRTUAL_ENV + sys.prefix check."""
        virtual_env = self.os_manager.get_environment_variable("VIRTUAL_ENV")
        if not virtual_env:
            return None

        # Confirm we’re actually inside a venv
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_name = self.os_manager.get_path_basename(virtual_env)
            self.state.active_venv_path = virtual_env
            return Result(
                True,
                {"virtual_env": Path(virtual_env), "virtual_env_name": venv_name},
            )
        return None

    def is_venv(self, path: Union[str, Path]) -> bool:
        """Validator: True if `path` looks like a Python virtualenv."""
        path = Path(path)
        return self.os_manager.is_venv_directory(path)

    def find_envs(self) -> List[Result]:
        """Search current directory one level deep for virtual environments."""
        cwd = self.os_manager.get_current_directory()
        paths = self.fs_manager.search_subfolders(cwd, self.is_venv)
        return [Result(True, p) for p in paths]

    def create_environment(self, path: Union[str, Path] = ".venv") -> Optional[Result]:
        """
        Create a new virtual environment on-demand.
        Returns Result(valid, {"virtual_env": Path, "virtual_env_name": str})
        or None on failure.
        """
        try:
            self.display.print_progress(f"Creating virtual environment at {path}...")
            venv_path = Path(path)
            venv.create(venv_path, with_pip=True)
            self.display.print_success(f"Virtual environment created at {venv_path}")
            env_info = {"virtual_env": venv_path, "virtual_env_name": venv_path.name}
            return Result(True, env_info)
        except Exception as e:
            self.display.print_error(f"Failed to create virtual environment: {e}")
            return None

    def find_or_create_venv(self) -> Optional[dict]:
        """
        Ensure we have an active venv: detect it, or prompt to find/create one.
        Returns the venv info dict or None.
        """
        self.display.lookup_venv()
        active = self.get_active_venv()
        if active:
            self.display.success_lookup_venv()
            return active.object

        self.display.failure_lookup_venv("No active virtual environment")
        candidates = self.find_envs()
        if not candidates:
            self.display.failure_lookup_venvs()
            if self.display.prompt_create_environment():
                new_env = self.create_environment()
                if new_env:
                    self.display.success_locate_env(
                        new_env.object["virtual_env_name"],
                        new_env.object["virtual_env"],
                    )
                    return new_env.object
            return None

        # If multiple found, prompt selection
        choices = [(r.object.name, r.object) for r in candidates]
        selection = self.display.prompt_env_selection(choices)
        if not selection:
            return None

        _, chosen_path = selection
        env_info = {
            "virtual_env": chosen_path,
            "virtual_env_name": self.os_manager.get_path_basename(chosen_path),
        }
        self.state.active_venv_path = chosen_path
        self.display.success_locate_env(env_info["virtual_env_name"], chosen_path)
        return env_info
