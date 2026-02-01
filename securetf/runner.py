# securetf/runner.py
import subprocess
from typing import List, Optional


class CommandError(RuntimeError):
    pass


def run(cmd: List[str], *, cwd: Optional[str] = None) -> str:
    """
    Run a command and return stdout. Raise CommandError on failure.
    """
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        msg = (
            f"Command failed: {' '.join(cmd)}\n"
            f"Exit code: {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}\n"
        )
        raise CommandError(msg)
    return proc.stdout

