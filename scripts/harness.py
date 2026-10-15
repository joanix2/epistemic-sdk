#!/usr/bin/env python3
"""Lightweight development harness for Epistemic SDK.

Subcommands:
  check      Static checks: imports, public-interface integrity, invariants.
  run        Run the contract test suite, with a dev-cache fingerprint
             (see docs/harness/CACHE.md). Use --no-cache to force execution.

No third-party dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CACHE_DIR = ROOT / ".cache"
CACHE_FILE = CACHE_DIR / "harness.json"

PUBLIC_EXPORTS = (
    "Sort", "Operator", "Variable", "Constant", "Application", "Term",
    "Equation", "Membership", "RewriteRule", "Statement", "Axiom",
    "MetaExecution", "ReflectiveM3", "LanguageM2", "ProgramM1",
    "InferenceMode", "Hypothesis", "Observation", "Sensor", "Belief",
    "Relation", "RelationType", "BeliefGraph", "BeliefUpdater",
    "InferenceEngine", "ProgramTransformation", "TransformationPipeline",
    "ResultTransformation", "ExecutionContext", "Executor", "ExecutionResult",
    "ProgramRunner", "ValidationStatus", "ValidationReport", "Validator",
    "KnowledgeStatus", "Knowledge", "KnowledgeBase", "KnowledgeReviser",
    "EpistemicEngine",
    "ExperimentSelector",
)


def _fingerprint() -> str:
    """Hash of source files, tests and project config (dev-cache layer B)."""
    digest = hashlib.sha256()
    paths = sorted(
        list((ROOT / "epistemic_sdk").rglob("*.py"))
        + list((ROOT / "examples").rglob("*.py"))
        + list((ROOT / "tests").rglob("*.py"))
        + [ROOT / "pyproject.toml"],
    )
    for path in paths:
        if not path.is_file():
            continue
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    digest.update(sys.version.encode())
    return digest.hexdigest()


def _load_cache() -> dict:
    if CACHE_FILE.is_file():
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(entry: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(entry, indent=2))


def _run_unittest() -> int:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
    ).returncode


def cmd_check(_: argparse.Namespace) -> int:
    errors: list[str] = []
    try:
        pkg = importlib.import_module("epistemic_sdk")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: cannot import epistemic_sdk: {exc}")
        return 1

    version = getattr(pkg, "__version__", None)
    print(f"epistemic_sdk version: {version or 'unknown'}")

    missing = [name for name in PUBLIC_EXPORTS if not hasattr(pkg, name)]
    if missing:
        errors.append(f"missing public exports: {', '.join(missing)}")
    else:
        print(f"public interface OK ({len(PUBLIC_EXPORTS)} exports)")

    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        return 1
    print("check OK")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    fingerprint = _fingerprint()
    cache = _load_cache()

    if (
        not args.no_cache
        and cache.get("fingerprint") == fingerprint
        and cache.get("exit_code") == 0
    ):
        print("cache hit: tests already passed for this fingerprint; skipping.")
        print("(use --no-cache to force execution)")
        return 0

    print("running test suite ...")
    code = _run_unittest()
    _save_cache({"fingerprint": fingerprint, "exit_code": code})
    if code != 0:
        print("test suite FAILED")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description="Epistemic SDK dev harness")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="static checks: imports and public interface")

    run_parser = sub.add_parser("run", help="run the test suite (dev-cache aware)")
    run_parser.add_argument(
        "--no-cache", action="store_true", help="force execution, bypass cache"
    )

    args = parser.parse_args()
    if args.command == "check":
        return cmd_check(args)
    if args.command == "run":
        return cmd_run(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
