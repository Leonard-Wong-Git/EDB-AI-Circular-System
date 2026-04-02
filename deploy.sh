#!/bin/bash
# EDB Dashboard — 一鍵推送
# 用法：bash ~/Downloads/Claude-edb-Project-V3/deploy.sh

cd ~/Documents/EDB-AI-Circular-System || { echo "❌ 找不到 repo，請先 clone"; exit 1; }
echo "📦 同步遠端..."
git pull --rebase origin main
echo "🚀 推送至 GitHub..."
git push origin main
echo "✅ 完成！約1分鐘後生效"
echo "   請按 Cmd+Shift+R 強制刷新"
echo "   https://leonard-wong-git.github.io/EDB-AI-Circular-System/"
