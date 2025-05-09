# djanbee/managers/file_system_manager/__init__.py

from pathlib import Path
from typing import Callable, List, Optional

class FileSystemManager:
    """Pure-Python filesystem utilities."""

    def set_dir(self, path: Path) -> None:
        """Change working directory to `path`."""
        if not path.exists():
            raise FileNotFoundError(f"No such directory: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        Path.chdir(path)

    def get_path_basename(self, path: Path) -> str:
        """Return last component of a path."""
        return path.name

    def search_subfolders(
        self,
        root: Path,
        validator: Callable[[Path], bool],
        max_depth: int = 1
    ) -> List[Path]:
        results: List[Path] = []
        def recurse(current: Path, depth: int):
            if depth > max_depth:
                return
            for child in current.iterdir():
                if child.is_dir():
                    if validator(child):
                        results.append(child)
                    recurse(child, depth + 1)
        recurse(root, 1)
        return results

    def search_folder(
        self,
        folder: Path,
        validator: Callable[[Path], bool]
    ) -> Optional[Path]:
        return folder if validator(folder) else None

    def write_text_file(self, path: Path, content: str) -> None:
        """Write text to `path`, creating parent dirs as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
