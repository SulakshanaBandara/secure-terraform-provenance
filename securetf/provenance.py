# securetf/provenance.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import time
from typing import Dict, Any, Optional


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_default_predicate(artifact: str, out_path: str, *, git_commit: Optional[str] = None) -> None:
    digest = sha256_file(artifact)
    payload: Dict[str, Any] = {
        "artifact": {
            "path": artifact,
            "sha256": digest,
        },
        "build": {
            "timestamp_utc": utc_now_iso(),
            "builder_id": "securetf-local",
            "tool": "terraform",
        },
        "vcs": {
            "git_commit": git_commit or "",
        },
    }
    Path(out_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

