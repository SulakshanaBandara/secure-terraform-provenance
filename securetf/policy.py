# securetf/policy.py
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class VerificationPolicy:
    require_signature: bool
    require_attestation: bool
    signature_suffix: str
    attestation_bundle_suffix: str


@dataclass(frozen=True)
class TerraformPolicy:
    init_before_plan: bool
    allow_apply: bool


@dataclass(frozen=True)
class GitPolicy:
    require_clean_worktree: bool


@dataclass(frozen=True)
class Policy:
    artifact_path: str
    verification: VerificationPolicy
    terraform: TerraformPolicy
    git: GitPolicy


def load_policy(path: str) -> Policy:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))

    v = data["verification"]
    t = data["terraform"]
    g = data["git"]

    return Policy(
        artifact_path=data["artifact"]["path"],
        verification=VerificationPolicy(
            require_signature=bool(v["require_signature"]),
            require_attestation=bool(v["require_attestation"]),
            signature_suffix=str(v["signature_file_suffix"]),
            attestation_bundle_suffix=str(v["attestation_bundle_suffix"]),
        ),
        terraform=TerraformPolicy(
            init_before_plan=bool(t["init_before_plan"]),
            allow_apply=bool(t["allow_apply"]),
        ),
        git=GitPolicy(
            require_clean_worktree=bool(g["require_clean_worktree"]),
        ),
    )

