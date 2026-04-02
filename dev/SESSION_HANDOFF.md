# Session Handoff

## Current Baseline
1. Version: **v3.0.3** (2026-04-02) ← **當前版本；已 commit 至 git repo；待 push 至 GitHub**
2. Core commands / features:
   - `edb-dashboard.html` — v3.0.1 Dashboard（3,061 行；設定佈局修復 + 篩選導航修復 + UX 整合）
   - `edb_scraper.py` — 後端爬蟲 + AI 分析管線（PyMuPDF 引擎 + K1 知識注入 + R1-v2）
   - `circulars.json` — EDB 通告 + gpt-5-nano AI 分析（GitHub Pages 已部署 ✅）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具
   - `requirements.txt` — Python 依賴清單（PyMuPDF 替換 pdfplumber）
   - `dev/knowledge/role_facts.json` — K1 基線知識庫
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` — K1 接口合約規格
3. Regression baseline: v3.0.1 JS syntax PASS；3 bugs 修復已驗證；v3.0.0 已部署 ✅
4. Release / merge status: **v3.0.1 待推送**；v3.0.0 commit `3f54cc2` 已部署 ✅
5. Active branch / environment: GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git；GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/ ✅
6. External platforms / dependencies in scope:
   - EDB 網站：https://applications.edb.gov.hk/circular/circular.aspx?langno=2（ASP.NET WebForms）
   - OpenAI gpt-5-nano API（temperature=1, max_completion_tokens=16000, developer role）
   - Python: requests, beautifulsoup4, PyMuPDF (fitz), openai
   - Frontend: 純 HTML/CSS/JS（無框架）

## Layer Map
1. Product / System Layer: EDB 通告爬蟲 + AI 分析 + Dashboard 前端
2. Development Governance Layer: AGENTS.md 規則、SESSION 管理、Root Safety Check
3. Current task belongs to which layer: Product / System Layer（前端 UI 修復）
4. Known layer-boundary risks: 暫無

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
1. **[下一步 ⭐]** 執行 `bash ~/Downloads/Claude-edb-Project-V3/deploy.sh` → push v3.0.3 → Cmd+Shift+R 確認上線
2. **[已建立]** git repo 已掛載 VM，Claude 今後自動 commit；用戶只需 push
3. **[繼續]** 繼續收集並修復 dashboard bugs（每次修復遵守 Version Bump Rule）
4. **[下一步]** 供應商統計新數據字段（scraper 修改，目前圖表為 placeholder）
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
1. UTC date: 2026-04-02
2. Session ID: Claude_20260402_0000
3. Completed:
   - ✅ 修復「角色及資源」tab 行動清單顯示 JSON 亂碼（新增 `actText()` helper）
   - ✅ v3.0.1 → v3.0.2（6 處）
   - ✅ JS syntax PASS；4/4 unit tests PASS
4. Pending:
   - cp files → commit → push v3.0.2 到 git repo
   - 確認 GitHub Pages 顯示 v3.0.2
5. Next priorities (max 3):
   - Push v3.0.2 到 git repo 並確認 GitHub Pages 部署
   - 繼續 dashboard bug fixes（待用戶報告）
   - 供應商圖表數據字段（scraper）
6. Risks / blockers: push 前先 cp governance files 防 rebase 覆蓋
7. Files materially changed:
   - `edb-dashboard.html`（actText helper + render fix + v3.0.2）
   - `dev/SESSION_HANDOFF.md`（版本 + Open Priorities + Last Session 更新）
   - `dev/SESSION_LOG.md`（新增 2026-04-02 session entry）
8. Validation summary: JS syntax PASS；4 unit tests PASS
9. Git commits: 待用戶在 Mac Terminal 推送
