#!/usr/bin/env python3
import subprocess
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/leonard/Downloads/Claude-edb-Project-V3")
DEPLOY_REPO_ROOT = Path.home() / "Documents" / "EDB-AI-Circular-System"

def run(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise

def main():
    if not DEPLOY_REPO_ROOT.exists():
        print(f"Error: {DEPLOY_REPO_ROOT} not found")
        return

    # 1. Abort failed rebase
    try:
        run(["git", "rebase", "--abort"], cwd=DEPLOY_REPO_ROOT)
        print("Rebase aborted.")
    except Exception:
        print("No active rebase to abort.")

    # 2. Pull latest from remote to get new circulars.json
    # 2. Reset to remote main to clear divergent history
    run(["git", "fetch", "origin", "main"], cwd=DEPLOY_REPO_ROOT)
    run(["git", "reset", "--hard", "origin/main"], cwd=DEPLOY_REPO_ROOT)
    print("Reset deploy repo to origin/main.")
    print("Pulled latest remote state.")

    # 3. Re-sync code from workspace (v3.0.38)
    # Note: This will overwrite circulars.json in deploy repo with the workspace version.
    # Since we prioritize v3.0.38 logic, we will then trigger a workflow to refresh data anyway.
    from publish_release import sync_workspace_to_repo
    import sys
    sys.path.append(str(WORKSPACE_ROOT / "dev/tools"))
    
    synced = sync_workspace_to_repo()
    print(f"Re-synced {len(synced)} paths.")

    # 4. Commit and Push
    run(["git", "add", "."], cwd=DEPLOY_REPO_ROOT)
    run(["git", "commit", "-m", "chore: publish v3.0.38 (manual fix)"], cwd=DEPLOY_REPO_ROOT)
    run(["git", "push", "origin", "main"], cwd=DEPLOY_REPO_ROOT)
    print("v3.0.38 pushed successfully.")

if __name__ == "__main__":
    main()
