#!/bin/bash
# deploy.sh — EDB Dashboard one-command push
# Usage: bash deploy.sh
# Or make executable: chmod +x deploy.sh && ./deploy.sh

cd "$(dirname "$0")"
echo "📦 Pulling latest from remote..."
git pull --rebase origin main
echo "🚀 Pushing to GitHub..."
git push origin main
echo "✅ Done! GitHub Pages will update in ~1 min."
echo "   Hard refresh: Cmd+Shift+R at https://leonard-wong-git.github.io/EDB-AI-Circular-System/"
