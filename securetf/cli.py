# securetf/cli.py
from __future__ import annotations

import argparse
from pathlib import Path

from securetf.runner import run, CommandError
from securetf.policy import load_policy
from securetf.provenance import write_default_predicate


def git_is_clean() -> bool:
    out = run(["git", "status", "--porcelain"])
    return out.strip() == ""


def git_head_commit() -> str:
    return run(["git", "rev-parse", "HEAD"]).strip()


def cosign_attest_blob(
    artifact: str,
    key: str,
    predicate: str,
    bundle_out: str,
    attestation_type: str,
) -> None:
    run([
        "cosign", "attest-blob",
        "--key", key,
        "--predicate", predicate,
        "--type", attestation_type,
        "--bundle", bundle_out,
        artifact,
    ])


def cosign_verify_blob_attestation(
    artifact: str,
    pubkey: str,
    bundle_path: str,
) -> None:
    run([
        "cosign", "verify-blob-attestation",
        "--key", pubkey,
        "--bundle", bundle_path,
        artifact,
    ])


def terraform_init() -> None:
    run(["terraform", "init", "-input=false"])


def terraform_plan() -> None:
    run(["terraform", "plan"])


def terraform_apply() -> None:
    run(["terraform", "apply", "-auto-approve"])


def cmd_attest(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    artifact = args.artifact or policy.artifact_path

    predicate = args.predicate
    if predicate is None:
        predicate = "provenance.generated.json"
        commit = git_head_commit() if Path(".git").exists() else None
        write_default_predicate(artifact, predicate, git_commit=commit)

    bundle_out = f"{artifact}{policy.verification.attestation_bundle_suffix}"

    cosign_attest_blob(
        artifact=artifact,
        key=args.key,
        predicate=predicate,
        bundle_out=bundle_out,
        attestation_type=args.type,
    )

    print(f"Attestation created for: {artifact}")
    print(f"Predicate file: {predicate}")
    print(f"Bundle file: {bundle_out}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    artifact = args.artifact or policy.artifact_path

    if policy.git.require_clean_worktree and Path(".git").exists():
        if not git_is_clean():
            print("Verification failed: git worktree is not clean.")
            return 2

    bundle_path = f"{artifact}{policy.verification.attestation_bundle_suffix}"
    cosign_verify_blob_attestation(artifact, args.pubkey, bundle_path)

    print("Verification OK.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    artifact = args.artifact or policy.artifact_path

    # Enforce verification before Terraform execution
    v = argparse.Namespace(
        artifact=artifact,
        pubkey=args.pubkey,
        policy=args.policy,
    )

    rc = cmd_verify(v)
    if rc != 0:
        return rc

    if policy.terraform.init_before_plan:
        terraform_init()

    terraform_plan()

    if policy.terraform.allow_apply:
        terraform_apply()

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="securetf",
        description="Secure Terraform enforcement using Sigstore DSSE attestations.",
    )
    parser.add_argument(
        "--policy",
        default="policy.yml",
        help="Path to policy.yml",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_att = sub.add_parser(
        "attest",
        help="Create a DSSE attestation bundle for a Terraform artifact.",
    )
    p_att.add_argument(
        "artifact",
        nargs="?",
        help="Path to Terraform file (default from policy).",
    )
    p_att.add_argument(
        "--key",
        default="cosign.key",
        help="Cosign private key path.",
    )
    p_att.add_argument(
        "--predicate",
        help="Predicate JSON file. If omitted, a default one is generated.",
    )
    p_att.add_argument(
        "--type",
        default="application/vnd.terrasign.provenance+json",
        help="Attestation type.",
    )
    p_att.set_defaults(func=cmd_attest)

    p_ver = sub.add_parser(
        "verify",
        help="Verify DSSE attestation for a Terraform artifact.",
    )
    p_ver.add_argument(
        "artifact",
        nargs="?",
        help="Path to Terraform file (default from policy).",
    )
    p_ver.add_argument(
        "--pubkey",
        default="cosign.pub",
        help="Cosign public key path.",
    )
    p_ver.set_defaults(func=cmd_verify)

    p_apply = sub.add_parser(
        "apply",
        help="Verify attestation, then run terraform plan/apply according to policy.",
    )
    p_apply.add_argument(
        "artifact",
        nargs="?",
        help="Path to Terraform file (default from policy).",
    )
    p_apply.add_argument(
        "--pubkey",
        default="cosign.pub",
        help="Cosign public key path.",
    )
    p_apply.set_defaults(func=cmd_apply)

    args = parser.parse_args()

    try:
        raise SystemExit(args.func(args))
    except CommandError as e:
        print(str(e))
        raise SystemExit(1)

