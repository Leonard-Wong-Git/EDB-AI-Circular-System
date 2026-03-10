# GitHub 手動推送指南（Manual Git Push）

每次有新改動需要推送至 GitHub，按以下步驟在 Mac Terminal 執行。

---

## 前置：找到專案路徑

```bash
find ~/Library -type d -name "EDB-Circular-AI-analysis-system" 2>/dev/null
```

複製輸出的完整路徑，下面用 `<PROJECT_PATH>` 代替。

---

## 標準推送流程（每次更新用這個）

```bash
# 1. 進入專案目錄
cd "<PROJECT_PATH>"

# 2. 查看有什麼新改動
git status
git diff --stat

# 3. 加入所有改動
git add .

# 4. 建立 commit（修改訊息）
git commit -m "feat: 描述這次改動的內容"

# 5. 輸入 GitHub PAT 並推送
#    先到 https://github.com/settings/tokens 生成新 PAT（scopes: repo）
git remote set-url origin https://<你的PAT>@github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
git push origin main

# 6. 安全清理：移除 PAT（重要！）
git remote set-url origin https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git

# 7. 加 tag（如是新版本）
git tag v1.0.0-release
git push origin v1.0.0-release
```

---

## 首次設定（若 git 未初始化）

```bash
cd "<PROJECT_PATH>"
git init
git branch -M main
git add .
git commit -m "feat: initial commit"
git remote add origin https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
git remote set-url origin https://<你的PAT>@github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
git push --force origin main
git remote set-url origin https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
```

---

## 生成 GitHub PAT（Personal Access Token）

1. 登入 GitHub → https://github.com/settings/tokens
2. 點「Generate new token (classic)」
3. 填 Note（例如：EDB-push），Expiration 選 30 days
4. Scopes 勾選：✅ **repo**（全部子選項）
5. 點「Generate token」
6. **立即複製**（只顯示一次！）

---

## 常用 git 指令

```bash
git log --oneline -5        # 查看最近 5 個 commit
git tag                     # 查看所有 tag
git status                  # 查看未提交改動
git diff                    # 查看具體改動內容
git stash                   # 暫存未提交改動（切換分支前用）
git stash pop               # 還原暫存
```

---

## 版本號規則（Semantic Versioning）

| 版本 | 意思 | 例子 |
|------|------|------|
| vX.0.0 | 主要里程碑 | v1.0.0-release |
| v0.X.0 | 新功能 | v0.3.0-backend |
| v0.0.X | 修訂/修復 | v0.2.1-frontend |

---

## 專案現有 Tags

| Tag | 內容 |
|-----|------|
| `v0.3.0-backend` ← 最新 | 完整後端管線 + 真實數據 Dashboard ✅ |
| `v0.1.0-mockup` | 初始 Mockup 版本 |

下一個 tag：`v1.0.0-release`（整合測試通過後）
