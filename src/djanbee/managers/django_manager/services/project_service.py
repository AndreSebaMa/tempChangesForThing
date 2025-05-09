# djanbee/services/project_service.py

from pathlib import Path
from typing import Optional, List, Union
from collections import namedtuple

from ....managers.os_manager import OSManager
from ....managers.file_system_manager import FileSystemManager
from ..state import DjangoManagerState
from .project_service_display import DjangoProjectServiceDisplay

Result = namedtuple("Result", ["valid", "object"])


class DjangoProjectService:
    """Service for managing Django project files and structure"""

    def __init__(
        self,
        os_manager: OSManager,
        display: DjangoProjectServiceDisplay,
        fs_manager: FileSystemManager,
    ):
        self.os_manager = os_manager
        self.fs_manager = fs_manager
        self.display = display
        self.state = DjangoManagerState.get_instance()

    def select_project(self) -> Optional[Result]:
        self.display.lookup_django_project()
        projects = self.find_django_project()
        if not projects:
            self.display.failure_lookup_django_project()
            return None

        if isinstance(projects, list):
            project = self._select_and_set_project(projects)
        else:
            # single Result
            project = projects

        if project:
            self.state.current_project_path = project.object
            self.display.success_lookup_project(project)

        return project

    def _select_and_set_project(
        self, projects: List[Result]
    ) -> Optional[Result]:
        # build simple (name, path) list for the prompt
        choices = [(p.object.name, p.object) for p in projects]
        selected = self.display.prompt_project_selection(choices)
        if not selected:
            return None

        _, project_path = selected
        self.initialize_directory(project_path)
        return Result(True, project_path)

    def find_django_project(
        self,
    ) -> Optional[Union[Result, List[Result]]]:
        # try current dir
        single = self.find_django_project_in_current_dir()
        if single:
            return single

        # try subfolders
        many = self.find_django_projects_in_tree()
        return many or None

    def find_django_project_in_current_dir(self) -> Optional[Result]:
        """Return Result if cwd is a Django project, else None."""
        cwd = self.os_manager.get_current_directory()
        path = self.fs_manager.search_folder(cwd, self.is_django_project)
        return Result(True, path) if path else None

    def find_django_projects_in_tree(self) -> List[Result]:
        """Return a list of Results for any Django projects in subfolders."""
        cwd = self.os_manager.get_current_directory()
        paths = self.fs_manager.search_subfolders(cwd, self.is_django_project)
        return [Result(True, p) for p in paths]

    def initialize_directory(self, path: Path) -> None:
        """Change into the given directory, or leave cwd unchanged if None."""
        if path:
            self.os_manager.change_directory(path)

    @staticmethod
    def is_django_project(path: Path) -> bool:
        """Detect whether a directory contains a Django project."""
        if not path.is_dir():
            return False
        manage = path / "manage.py"
        if not manage.exists():
            return False
        return "django" in manage.read_text().lower()

    def find_settings_file(self) -> Optional[Path]:
        """Locate the settings.py file inside the current project."""
        project_root = self.state.current_project_path
        if not project_root:
            return None

        # common locations…
        candidates = [
            project_root / project_root.name / "settings.py",
            project_root / "settings.py",
            project_root / "config" / "settings.py",
            project_root / project_root.name / "settings" / "base.py",
            project_root / "settings" / "base.py",
            project_root / "config" / "settings" / "base.py",
        ]

        # handle DJANGO_SETTINGS_MODULE in manage.py first
        manage = project_root / "manage.py"
        if manage.exists():
            import re

            match = re.search(
                r'DJANGO_SETTINGS_MODULE\s*,\s*["\']([^"\']+)["\']', manage.read_text()
            )
            if match:
                parts = match.group(1).split(".")
                p = project_root
                for part in parts[:-1]:
                    p = p / part
                candidates.insert(0, p / f"{parts[-1]}.py")

        for file in candidates:
            if file.exists() and file.is_file():
                return file

        # fallback: recursive search
        for file in project_root.rglob("settings.py"):
            return file

        return None
