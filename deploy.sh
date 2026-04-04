#!/bin/bash
# EDB Dashboard — 自動版本升級 + 同步 deploy repo + 推送 GitHub
# 用法：bash ~/Downloads/Claude-edb-Project-V3/deploy.sh

set -euo pipefail

python3 ~/Downloads/Claude-edb-Project-V3/dev/tools/publish_release.py "$@"
