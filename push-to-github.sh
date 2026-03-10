#!/bin/bash
# ============================================================
# push-to-github.sh
# 一鍵將 EDB-AI-Circular-System 推送至 GitHub
# 使用方法：在 Mac Terminal 執行 bash push-to-github.sh
# ============================================================

set -e  # 遇到錯誤立即停止

# ---------- 設定 ----------
REPO_URL="https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git"
GIT_NAME="Leonard Wong"
GIT_EMAIL="leonard.ai.wong@gmail.com"
TAG="v0.1.0-mockup"
BRANCH="main"

# ---------- 顏色輸出 ----------
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${GREEN}🚀 EDB-AI-Circular-System — GitHub Push Script${NC}"
echo "=================================================="

# ---------- 請輸入 PAT ----------
echo -e "${YELLOW}請貼上你的 GitHub Personal Access Token：${NC}"
read -s -p "Token (輸入後按 Enter，輸入內容不顯示): " TOKEN
echo ""

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Token 不可為空${NC}"; exit 1
fi

# ---------- 取得腳本所在目錄（即專案根目錄）----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "📁 專案目錄：${SCRIPT_DIR}"
cd "$SCRIPT_DIR"

# ---------- 清理舊的 .git（如有損壞）----------
if [ -d ".git" ]; then
  echo -e "${YELLOW}⚠️  發現現有 .git，將重新初始化...${NC}"
  rm -rf .git
fi

# ---------- Git 初始化 ----------
echo -e "\n${GREEN}[1/5] 初始化 Git...${NC}"
git init
git config user.name "$GIT_NAME"
git config user.email "$GIT_EMAIL"
git branch -m "$BRANCH"

# ---------- 加入遠端 ----------
echo -e "${GREEN}[2/5] 設定遠端 origin...${NC}"
git remote add origin "https://Leonard-Wong-Git:${TOKEN}@github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git"

# ---------- Stage 所有檔案 ----------
echo -e "${GREEN}[3/5] 加入所有檔案...${NC}"
git add .gitignore AGENTS.md CHANGELOG.md CLAUDE.md GEMINI.md README.md \
        edb-dashboard-mockup.html dev/SESSION_HANDOFF.md dev/SESSION_LOG.md
git status --short

# ---------- Commit ----------
echo -e "${GREEN}[4/5] 建立 commit...${NC}"
git commit -m "feat: initial release — v0.1.0-mockup

Milestone: UI Mockup + Governance Framework

- AGENTS.md / CLAUDE.md / GEMINI.md — AI agent governance
- edb-dashboard-mockup.html — interactive UI mockup (1452 lines)
  * 4 main tabs: Overview / Calendar / Supplier / Settings
  * Detail panel with 5 inner tabs
  * Dark/light theme, search suggestions, role selector
- dev/SESSION_HANDOFF.md + SESSION_LOG.md — session relay docs
- README.md + CHANGELOG.md — full project documentation

Next: v0.2.0-frontend

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# ---------- Tag ----------
git tag -a "$TAG" -m "v0.1.0-mockup — UI Mockup Release

First milestone: interactive dashboard mockup with full governance framework.
Next milestone: v0.2.0-frontend (production edb-dashboard.html)"

# ---------- Push ----------
echo -e "${GREEN}[5/5] 推送至 GitHub...${NC}"
git push -u origin "$BRANCH"
git push origin "$TAG"

# ---------- 清理 Token（從 remote URL 移除）----------
git remote set-url origin "$REPO_URL"
echo -e "\n${GREEN}✅ Token 已從 remote URL 移除（安全清理完成）${NC}"

echo ""
echo -e "${GREEN}=================================================="
echo -e "🎉 推送成功！"
echo -e "=================================================="
echo -e "📦 Repo：${REPO_URL}"
echo -e "🌿 Branch：${BRANCH}"
echo -e "🏷️  Tag：${TAG}"
echo -e ""
echo -e "🔗 查看 Repo：https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System"
echo -e "🔗 查看 Release：https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System/releases/tag/${TAG}"
echo -e "${NC}"

# 安全提醒
echo -e "${YELLOW}💡 安全提醒：完成後建議到 GitHub 撤銷此 PAT Token${NC}"
echo -e "${YELLOW}   Settings → Developer settings → Personal access tokens → 找到 EDB-AI-Git-token → Delete${NC}"
