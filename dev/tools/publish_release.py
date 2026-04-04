#!/usr/bin/env python3
"""Bump the project version, sync the workspace into the deploy repo, and publish."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


WORKSPACE_ROOT = Path("/Users/leonard/Downloads/Claude-edb-Project-V3")
DEPLOY_REPO_ROOT = Path.home() / "Documents" / "EDB-AI-Circular-System"
REPO_SLUG = "Leonard-Wong-Git/EDB-AI-Circular-System"

SYNC_EXCLUDES = {
    ".git",
    ".edb_cache",
    "__pycache__",
    ".DS_Store",
    "dev/init_backup",
    "dev/archive",
}


def run(cmd: list[str], cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=capture,
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def detect_version() -> str:
    dashboard = read_text(WORKSPACE_ROOT / "edb-dashboard.html")
    scraper = read_text(WORKSPACE_ROOT / "edb_scraper.py")

    dashboard_match = re.search(r"const VERSION = '(v\d+\.\d+\.\d+)';", dashboard)
    scraper_match = re.search(r"EDB Circular Scraper \+ Analyzer  (v\d+\.\d+\.\d+)", scraper)
    if not dashboard_match or not scraper_match:
        raise RuntimeError("Could not detect current version markers")
    if dashboard_match.group(1) != scraper_match.group(1):
        raise RuntimeError(
            f"Version mismatch: dashboard={dashboard_match.group(1)} scraper={scraper_match.group(1)}"
        )
    return dashboard_match.group(1)


def bump_patch(version: str) -> str:
    major, minor, patch = [int(part) for part in version[1:].split(".")]
    return f"v{major}.{minor}.{patch + 1}"


def replace_or_fail(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise RuntimeError(f"Expected {label} marker not found: {old}")
    return content.replace(old, new)


def update_versions(old_version: str, new_version: str) -> None:
    dashboard_path = WORKSPACE_ROOT / "edb-dashboard.html"
    scraper_path = WORKSPACE_ROOT / "edb_scraper.py"

    dashboard = read_text(dashboard_path)
    replacements = [
        (f"<title>EDB 通告智能分析系統 {old_version}</title>", f"<title>EDB 通告智能分析系統 {new_version}</title>", "title"),
        (f'id="devVersion">{old_version}</span>', f'id="devVersion">{new_version}</span>', "devVersion"),
        (f'id="brandVersion"> {old_version}</span>', f'id="brandVersion"> {new_version}</span>', "brandVersion"),
        (f'id="versionLabel" style="font-size:12px;cursor:pointer;color:var(--text-muted)" onclick="devVersionClick()" title="連按5次開啟開發者工具">{old_version}</span>',
         f'id="versionLabel" style="font-size:12px;cursor:pointer;color:var(--text-muted)" onclick="devVersionClick()" title="連按5次開啟開發者工具">{new_version}</span>',
         "versionLabel"),
        (f"EDB 通告智能分析系統 {old_version} &nbsp;|&nbsp; &copy; 2026", f"EDB 通告智能分析系統 {new_version} &nbsp;|&nbsp; &copy; 2026", "footer"),
        (f"const VERSION = '{old_version}';", f"const VERSION = '{new_version}';", "const VERSION"),
    ]
    for old, new, label in replacements:
        dashboard = replace_or_fail(dashboard, old, new, label)
    write_text(dashboard_path, dashboard)

    scraper = read_text(scraper_path)
    scraper = replace_or_fail(
        scraper,
        f"EDB Circular Scraper + Analyzer  {old_version}",
        f"EDB Circular Scraper + Analyzer  {new_version}",
        "scraper banner",
    )
    write_text(scraper_path, scraper)


def should_sync(relative_path: Path) -> bool:
    rel = relative_path.as_posix()
    if rel in SYNC_EXCLUDES:
        return False
    return not any(rel == prefix or rel.startswith(prefix + "/") for prefix in SYNC_EXCLUDES)


def sync_workspace_to_repo() -> list[str]:
    synced: list[str] = []
    for source in WORKSPACE_ROOT.rglob("*"):
        if source == WORKSPACE_ROOT:
            continue
        relative = source.relative_to(WORKSPACE_ROOT)
        if not should_sync(relative):
            continue
        destination = DEPLOY_REPO_ROOT / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        synced.append(relative.as_posix())
    return synced


def git_commit_exists(message: str) -> bool:
    result = run(["git", "status", "--short"], cwd=DEPLOY_REPO_ROOT, capture=True)
    return bool(result.stdout.strip())


def trigger_workflow_hint() -> None:
    print("Note: GitHub Pages workflow in this repo runs on push only if workflow config supports it.")
    print("If the site does not update automatically, trigger the workflow manually in GitHub Actions.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a new release from workspace to deploy repo.")
    parser.add_argument("--no-bump", action="store_true", help="Do not increment the patch version before syncing.")
    parser.add_argument("--skip-push", action="store_true", help="Stop after local commit in the deploy repo.")
    parser.add_argument("--dry-run", action="store_true", help="Show the intended actions without writing anything.")
    args = parser.parse_args()

    if not DEPLOY_REPO_ROOT.exists():
        raise RuntimeError(f"Deploy repo not found: {DEPLOY_REPO_ROOT}")

    current_version = detect_version()
    next_version = current_version if args.no_bump else bump_patch(current_version)

    print(f"Workspace root : {WORKSPACE_ROOT}")
    print(f"Deploy repo    : {DEPLOY_REPO_ROOT}")
    print(f"Current version: {current_version}")
    print(f"Target version : {next_version}")

    if args.dry_run:
        print("Dry run only. No files changed.")
        return 0

    if not args.no_bump:
        update_versions(current_version, next_version)

    synced = sync_workspace_to_repo()
    print(f"Synced {len(synced)} paths into deploy repo.")

    run(["git", "add", "."], cwd=DEPLOY_REPO_ROOT)
    if git_commit_exists(f"chore: publish {next_version}"):
        run(["git", "commit", "-m", f"chore: publish {next_version}"], cwd=DEPLOY_REPO_ROOT)
    else:
        print("No deploy-repo changes detected after sync.")
        return 0

    if args.skip_push:
        print("Commit created locally; push skipped by request.")
        return 0

    run(["git", "pull", "--rebase", "origin", "main"], cwd=DEPLOY_REPO_ROOT)
    run(["git", "push", "origin", "main"], cwd=DEPLOY_REPO_ROOT)

    print(f"Published {next_version} to https://github.com/{REPO_SLUG}")
    trigger_workflow_hint()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
