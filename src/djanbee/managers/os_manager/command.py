from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import subprocess

@dataclass
class CommandResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int

class CommandRunner:
    def run(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        sudo: bool = False
    ) -> CommandResult:
        cmd = (["sudo"] if sudo else []) + args
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return CommandResult(
            success=(proc.returncode == 0),
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            exit_code=proc.returncode
        )
