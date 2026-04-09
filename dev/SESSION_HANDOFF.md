# Session Handoff

## Current Baseline
1. Version: **live v3.0.20 / workspace v3.0.21** (2026-04-09) ← **GitHub Pages + live `circulars.json` 已確認帶出 K1 fields；workspace 已再收緊 deterministic review gating，避免 supplier / finance links 由 AI summary 或 supplier role 自我放大後漏進 curriculum / student 通告**
2. Core commands / features:
   - `edb-dashboard.html` — workspace v3.0.21（版本同步待發佈）
   - `edb_scraper.py` — workspace v3.0.21（K1 prompt injection 與 `v1.3.1` schema consume 已 live；workspace 再把 deterministic review procurement / finance gating 改為 raw-signal 判斷）
   - `circulars.json` — EDB 通告 + gpt-5-nano AI 分析（live 已由 school-year workflow 重生並帶出 `k1_*` 欄位）
   - `knowledge.json` — 從 edb-knowledge 獲取的語義事實來源（v1.3.1，107 facts ✅）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具
   - `requirements.txt` — Python 依賴清單
   - `dev/knowledge/role_facts.json` — K1 基線知識庫（目前 workspace 缺檔，待接收新版交付）
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` — K1 接口合約規格（已對齊至 v2.0.0 角色契約）
3. Regression baseline: scraper Python AST PASS；dashboard JS compile PASS；workspace version markers PASS at v3.0.21；live K1 public SSOT fetch PASS (`knowledge.json`, `guidelines.json`, `K1_API_SPEC.md`, all `v1.3.1`)；live Pages cache-busted 驗證 PASS at `v3.0.20`；public `circulars.json` latest verified `generated_at=2026-04-09T07:04:46Z`, `count=117`；raw-signal gating tests PASS（curriculum/student sample no longer gains procurement links from AI summary wording）
4. Release / merge status: **live site is currently `v3.0.20`; next publish target is workspace `v3.0.21`**
5. Active branch / environment: GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git；GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/ ✅
6. External platforms / dependencies in scope:
   - EDB 網站：https://applications.edb.gov.hk/circular/circular.aspx?langno=2（ASP.NET WebForms）
   - OpenAI gpt-5-nano API（temperature=1, max_completion_tokens=16000, developer role）
   - Python: requests, beautifulsoup4, PyMuPDF (fitz), openai
   - Frontend: 純 HTML/CSS/JS（無框架）

## Layer Map
1. Product / System Layer: EDB 通告爬蟲 + AI 分析 + Dashboard 前端
2. Development Governance Layer: AGENTS.md 規則、SESSION 管理、Root Safety Check
3. Current task belongs to which layer: Product / System Layer（K1 external JSON integration）+ Development Governance Layer（session persistence）
4. Known layer-boundary risks: 第二輪 review 必須只做補充/標準化，不能覆蓋通告硬事實；deploy 時仍要注意 remote `circulars.json` 可能較新；角色契約已更新到 `subject_head` / `panel_chair` / `eo_admin=EO`；K1 public `knowledge.json` live schema 與舊 task brief 不完全一致，整合層現已做雙 schema 兼容

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
1. **[下一步 ⭐]** 發布 workspace `v3.0.21`，再重跑 school-year workflow，驗證 live `knowledge_review.recommended_links` 已不再因 AI summary / supplier role 自我放大而混入 procurement / finance links
2. **[重要]** 針對 curriculum / student 通告抽樣檢查 cross-topic contamination 是否下降；如仍有 supplier / finance links 漏入，再微調 deterministic review gating
3. **[其後]** 接收新版 `role_facts.json`，驗證其符合 K1 v2.0.0 契約後再接入
4. **[其後]** 抽樣檢查 live `subject_head` vs `panel_chair` 輸出質素，必要時微調 topic-aware 分流規則
5. **[觀察]** 視需要再微調「官方原文整理版」對 metadata 行的段落整理規則
6. **[長期]** K1 第二階段：PDF 提取真實 EDB 知識（另立項目）
7. **[選做]** LLM 引擎切換機制

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
8. **⚠️ Publish conflict note（2026-04-04 實測）：**
   - remote `circulars.json` 可能在 code/docs 發布期間被 GitHub Actions 更新
   - `deploy.sh` publish commit rebase 時若只衝突在 `circulars.json`，應保留較新的 remote 版本，再繼續推送 code/docs release
9. **⚠️ Knowledge review boundary（2026-04-04 確認）：**
   - 第二輪 review 現時只針對 supplier + curriculum + finance 場景做 deterministic enrichment
   - 不應改寫 deadline、金額、編號、scope 等硬事實
10. **⚠️ Role contract migration watch（2026-04-06 確認）：**
   - K1 接口規格已更新為 `subject_head` / `panel_chair` / `eo_admin=EO`
   - 產品端已完成第一階段相容層，並已用 workflow 重生 live `circulars.json`
   - 新版 `role_facts.json` 尚未交付；接入前仍需按 K1 v2.0.0 契約驗證
11. **⚠️ K1 public schema watch（2026-04-09 確認）：**
   - public `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md` 現已一致對齊到 `v1.3.1`
   - public `department_head` bucket 已移除；Circular System 必須按 `subject_head + panel_chair + all_roles` 組裝主任層 facts
   - 不應再以 K1 repo 的 local export / backup artifact 當 API truth

## Regression / Verification Notes
1. v2.1.0 QC: 24/24 structural checks 通過；JS syntax check 通過
2. GitHub Pages 部署：push 至 `main` 現已自動觸發 Pages deployment；仍可保留 manual/schedule workflow 用於 scraper；`v3.0.16` live 已驗證
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
1. UTC date: 2026-04-09
2. Session ID: Codex_20260409_0002
3. Completed:
   - ✅ 核實 live Pages 已到 `v3.0.20`，school-year workflow 已重生 `circulars.json`（`generated_at=2026-04-09T07:04:46Z`, `count=117`）
   - ✅ live records 確認 K1 `v1.3.1` schema consume 已生效，且 K1 caps 已落地
   - ✅ 收緊 deterministic review procurement / finance gating，改用 raw circular signals，避免 AI summary / supplier role 自我放大
   - ✅ 版本升至 `v3.0.21`
4. Pending:
   - 推送 / 發布 `v3.0.21`
   - 重跑 school-year workflow，驗證 raw-signal gating 已反映到 live records
   - 如仍有 supplier / finance links 漏入 curriculum / student，繼續微調 deterministic review gating
   - 等待用戶提供新版 `role_facts.json`
5. Next priorities (max 3):
   - 發布 `v3.0.21`
   - 重跑 workflow 並驗證 raw-signal gating
   - 視結果再微調 deterministic review gating
6. Risks / blockers:
   - live HTML 目前是 `v3.0.20`；`v3.0.21` 尚未發布
   - raw-signal gating 目前只做 local deterministic review 驗證，仍需 live workflow 後回歸驗證
   - 等待用戶提供新版 `role_facts.json` 後，才可完成另一條 K1 role-facts 接入驗證
7. Files materially changed:
   - `edb_scraper.py`、`edb-dashboard.html`、`README.md`、`dev/CODEBASE_CONTEXT.md`、`dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`
8. Validation summary: scraper Python AST PASS；dashboard JS compile PASS；raw-signal gating regression PASS（curriculum/student sample no longer gets supplier links; procurement/finance sample keeps procurement+finance links）；full OpenAI LLM call not run because `OPENAI_API_KEY` is absent in this environment
9. Git commits: workspace only; publish pending
