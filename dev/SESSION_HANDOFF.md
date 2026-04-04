# Session Handoff

## Current Baseline
1. Version: **Workspace files show v3.0.5** (detected 2026-04-04) ← **治理文件尚未有對應產品 session 記錄；推送前必須先對帳**
2. Core commands / features:
   - `edb-dashboard.html` — on-disk version marker = v3.0.5（供應商統計與採購類別顯示仍在）
   - `edb_scraper.py` — banner version marker = v3.0.5（KnowledgeStore 語義搜尋 + 增強供應商 Schema 仍在）
   - `circulars.json` — EDB 通告 + gpt-5-nano AI 分析（待更新 push ✅）
   - `knowledge.json` — 從 edb-knowledge 獲取的語義事實來源（v1.2.2，107 facts ✅）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具
   - `requirements.txt` — Python 依賴清單
   - `dev/knowledge/role_facts.json` — K1 基線知識庫（存檔）
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` — K1 接口合約規格
3. Regression baseline: Latest documented product verification = v3.0.4 JS syntax PASS；workspace version markers currently show v3.0.5 but are not yet reconciled in SESSION_LOG
4. Release / merge status: **Do not push/deploy until v3.0.5 drift is reconciled and documented**
5. Active branch / environment: GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git；GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/ ✅
6. External platforms / dependencies in scope:
   - EDB 網站：https://applications.edb.gov.hk/circular/circular.aspx?langno=2（ASP.NET WebForms）
   - OpenAI gpt-5-nano API（temperature=1, max_completion_tokens=16000, developer role）
   - Python: requests, beautifulsoup4, PyMuPDF (fitz), openai
   - Frontend: 純 HTML/CSS/JS（無框架）

## Layer Map
1. Product / System Layer: EDB 通告爬蟲 + AI 分析 + Dashboard 前端
2. Development Governance Layer: AGENTS.md 規則、SESSION 管理、Root Safety Check
3. Current task belongs to which layer: Development Governance Layer（startup verification + deployment state confirmation）
4. Known layer-boundary risks: workspace `v3.0.5` 與 GitHub Pages live `v3.0.4` 不一致；不可把本地版本誤當已部署版本

## Mandatory Start Checklist
1. ✅ Read `dev/SESSION_HANDOFF.md`
2. ✅ Read `dev/SESSION_LOG.md`
3. ✅ Read `dev/CODEBASE_CONTEXT.md`（若存在；2026-03-17 已建立）
4. Confirm working tree / file status
5. Run baseline checks: 在瀏覽器開啟 GitHub Pages 目視驗證 UI
6. Confirm environment / dependency state: Python venv + OPENAI_API_KEY（後端開發時需要）
7. Confirm whether external platform alignment is required: 開始後端開發前需確認 EDB 網站 ViewState 格式
8. Search for related SSOT / spec / runbook before change

## ⚠️ Session Close 必做保障（每次 Session 結束前強制執行）
> 目的：確保每個版本有快照，可隨時回退，不依賴 VM 環境

**每個 session 結束前，必須在 Mac Terminal 完成以下兩項：**

### 保障 A：打 Git Tag（版本快照）
```bash
# 1. Commit session close 文件更新
git add .
git commit -m "chore: session close — <本 session 簡述>"

# 2. 打版本 tag
git tag v2.1.0-dashboard

# 3. 推送（先 pull --rebase，再 push）
git pull --rebase origin main
git push origin main
git push origin --tags
```

### ⚠️ git pull --rebase 風險提示（2026-03-22 確認）
- GitHub Actions 定時 commit circulars.json，所以本地 push 前幾乎必須先 pull --rebase
- rebase 時，若 circulars.json / SESSION_HANDOFF.md 有衝突，**本地版本可能被遠端舊版覆蓋**
- 建議：push 前先確認 `git status` 和 `git log --oneline -3`，確保本地版本正確

### 保障 B：複製資料夾（本機備份）
```bash
cp -r "<PROJECT_PATH>" "<PROJECT_PATH>-snapshot-v2.1.0"
```

### 如需從舊版本回退
```bash
git checkout v2.1.0-dashboard
```

## Open Priorities
1. **[下一步 ⭐]** 先把 workspace `v3.0.5` 發布到 deploy repo / GitHub Pages；目前 live site 經實測仍是 `v3.0.4`
2. **[重要]** 若要繼續產品開發，先補寫 `v3.0.5` 的產品層 SESSION_LOG 記錄，避免版本與驗證證據脫節
3. **[其後]** 若用戶提供新版 `role_facts.json`，整合取代 `dev/knowledge/role_facts.json`，並同步驗證 K1 接口
4. **[繼續]** 發布後 hard refresh 驗證 GitHub Pages 是否顯示 `v3.0.5`
5. **[長期]** K1 第二階段：PDF 提取真實 EDB 知識（另立項目）
6. **[選做]** LLM 引擎切換機制

## v2.1.0 Key Changes（2026-03-22）
- 新增 🏠 首頁 tab（panel-home），首頁與通告總覽正式分離
- Stats buttons（本月通告/需關注/即將截止）加入 toggle 行為，再按返回首頁
- 通告總覽每次進入重置篩選，顯示全部通告
- 搜尋結果獨立 dropdown panel，不影響通告總覽
- 全面 LLM→AI 改名 + AI 分析免責聲明
- 詳情面板重構：PDF 連結置頂 + AI 分析/角色/比較三分頁
- 月曆通告標題改用 EDBC 格式（EDBC046）
- 移除預設釘選通告
- 系統說明精簡
- 供應商 tab：圖表佔位 + 廉政公署/EDB 法規參考連結

## v0.2.0-frontend Key Decisions（用戶已確認 2026-03-10）
- 所有設定存 localStorage（角色/主題/佈局/色調/字體/狀態/收藏）
- 供應商 Tab 條件顯示（選供應商角色才出現）
- 金額分兩類：💰可申請（直接撥款）vs 📦資源（政府提供，非直接申請）
- 截止類型三分：apply_deadline / submission_deadline / awareness_deadline
- 截止提示配合角色（非所有角色都顯示同等緊急）
- 常備參考通告（📌）與一般收藏（⭐）分開
- 文件包下載 = ZIP（摘要PDF + ics + JSON）
- Dev 頁面觸發：URL ?dev=1 或版本號連按 5 次
- Mobile 優化列為最後批次（A6），先桌面版完成後再優化

## Known Risks / Blockers
1. gpt-5-nano 必須 temperature=1，否則 400 Bad Request
   - `max_tokens` → 必須用 `max_completion_tokens`（推理模型）
   - `"system"` role → 必須用 `"developer"` role（推理模型）
   - `max_completion_tokens` 最少 16000
2. EDB 網站需 POST + ViewState（GET 無效），解析用位置式（非 CSS class）
3. ✅ ~~days-3 覆蓋問題~~ **已修復（2026-03-23）：** PHASE 4 現在 load existing JSON → merge raw → sort by date desc → save
4. **⚠️ git rebase 治理文件覆蓋風險（2026-03-22 確認）：**
   - GitHub Actions 定時 commit 導致遠端常領先本地
   - `git pull --rebase` 可能覆蓋 SESSION_HANDOFF.md / SESSION_LOG.md
   - 緩解：push 前手動 cp 最新版本到 git repo；或在 `.gitattributes` 設 merge strategy
5. **⚠️ VM workspace ≠ git repo（2026-03-15 確認）：**
   - VM workspace: `Claude-edb-Project-V3`（前端文件在此，以此為主）
   - Git repo: `EDB-Circular-AI-analysis-system`（後端文件必須寫到這裏）
   - Mac git repo 路徑：`/Users/leonard/Library/Application Support/Claude/local-agent-mode-sessions/f52b21f7-e7c9-49a3-80dc-00ab322afbcf/51c234d2-cb9f-4b55-bb07-b71de9e93c27/local_e454964f-74da-4734-9a60-bf4b4362ca65/outputs/EDB-Circular-AI-analysis-system`
6. **⚠️ EDB 表單字段已確認（2026-03-10 實測）：**
   - PlaceholderID = `MainContentPlaceHolder`
   - 日期字段：`txtPeriodFrom` / `txtPeriodTo`
   - 搜尋按鈕：`btnSearch2`（JS 觸發）
7. PyMuPDF (fitz) 已替換 pdfplumber/pdfminer（2026-03-15）— school-year workflow 全綠
8. **⚠️ Workspace 文檔漂移（2026-04-04 確認）：**
   - `edb-dashboard.html` 與 `edb_scraper.py` 均顯示 v3.0.5
   - `dev/SESSION_LOG.md` 最新產品條目僅記錄到 v3.0.4
   - 緩解：下一 session 先比對 diff / 驗證 / 補文檔，再部署
9. **⚠️ Live deployment state（2026-04-04 實測）：**
   - GitHub Pages `edb-dashboard.html` 仍顯示 v3.0.4
   - live site 尚未包含已確認的 v3.0.5 workspace 狀態
   - 緩解：先 deploy / trigger workflow，再用 live HTML 重新驗證版本

## Regression / Verification Notes
1. v2.1.0 QC: 24/24 structural checks 通過；JS syntax check 通過
2. GitHub Pages 部署：需 workflow 執行（不是 push 自動觸發）
3. school-year 最後成功：1h 23m（16 hours ago as of 2026-03-22）

## Consolidation Watchlist
1. SESSION_HANDOFF.md 被 rebase 覆蓋：下次 session 開始需確認版本（push 前先 cp）
2. ✅ ~~days-3 覆蓋 school-year 數據~~ 已修復（2026-03-23 PHASE 4 merge）

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.

### ⚡ Version Bump Rule (Mandatory — Key Decision #10, 2026-03-26)
Every session that modifies `edb-dashboard.html` or `edb_scraper.py` **must** increment the version before closing.

Increment scheme:
- **Patch** `v3.0.x` — bug fixes, minor tweaks, copy changes
- **Minor** `v3.x.0` — new features, significant UI additions or layout changes
- **Major** `vx.0.0` — complete redesign (user-initiated only)

6 locations to update in `edb-dashboard.html`:
1. `<title>` tag
2. `id="brandVersion"` span
3. `id="devVersion"` span
4. `id="versionLabel"` span
5. Footer text (`EDB 通告智能分析系統 vX.X.X`)
6. `const VERSION = 'vX.X.X';`

Do not close a session with code changes without completing the version bump.

## Last Session Record
1. UTC date: 2026-04-04
2. Session ID: Codex_20260404_0003
3. Completed:
   - ✅ 依 AGENTS.md §1 完成 startup reads：`AGENTS.md` → `SESSION_HANDOFF.md` → `SESSION_LOG.md` → `CODEBASE_CONTEXT.md`
   - ✅ 驗證 workspace 確為 `v3.0.5`，且 supplier schema / UI 已包含 `eligibility`、`contact_unit`、`procurement_cat`
   - ✅ 實測 GitHub Pages live `edb-dashboard.html` 仍為 `v3.0.4`
   - ✅ 確認目前不能宣稱 `v3.0.5` 已上線
   - ✅ 在 `README.md` 新增 K1 API spec 外部連結
4. Pending:
   - 發布 workspace `v3.0.5` 到 deploy repo / GitHub Pages
   - 補寫 `v3.0.5` 的產品層 session documentation（若要延續當前 workspace 狀態）
   - 等待用戶提供新版 `role_facts.json`
5. Next priorities (max 3):
   - deploy 並驗證 GitHub Pages v3.0.5
   - 補齊 v3.0.5 產品 session 記錄
   - 等待 / 整合新版 role_facts.json
6. Risks / blockers: live site 仍是 v3.0.4；若跳過 deploy 驗證或文檔同步，容易誤報版本狀態
7. Files materially changed:
   - `README.md`（新增 K1 API spec 連結）
   - `dev/SESSION_HANDOFF.md`（Last Session Record 更新）
   - `dev/SESSION_LOG.md`（新增本 session entry）
   - `dev/DOC_SYNC_CHECKLIST.md`（新增 README link/reference row）
8. Validation summary: startup reads PASS；workspace v3.0.5 markers confirmed；live GitHub Pages fetched and confirmed at v3.0.4；README link insertion verified
9. Git commits: 未執行
