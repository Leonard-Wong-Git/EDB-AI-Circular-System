# Session Handoff

## Current Baseline
1. Version: **v3.0.18** (2026-04-08) ← **git commit d52ae17 已完成；等待用戶 push + 觸發 workflow backfill**
2. Core commands / features:
   - `edb-dashboard.html` — v3.0.18（月曆 dlLabel fix + apply-ext 互動表單 + K1 版本同步）
   - `edb_scraper.py` — v3.0.18（K1 三部分修復：carry-forward + Phase 4.5 backfill + post-LLM re-detect）
   - `circulars.json` — EDB 通告 + gpt-5-nano AI 分析（live 目前 117 records，k1_* 仍待 backfill）
   - `knowledge.json` — 從 edb-knowledge 獲取的語義事實來源（v1.2.2，107 facts ✅）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具
   - `requirements.txt` — Python 依賴清單
   - `dev/knowledge/role_facts.json` — K1 基線知識庫（目前 workspace 缺檔，待接收新版交付）
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` — K1 接口合約規格（已對齊至 v2.0.0 角色契約）
3. Regression baseline: py_compile PASS；dashboard JS syntax PASS；4/4 K1 logic tests PASS；version markers v3.0.18 confirmed in all 6 dashboard locations + scraper print；git commit d52ae17 in Documents/EDB-AI-Circular-System
4. Release / merge status: **v3.0.18 已 commit（d52ae17）；尚未 push；live GitHub Pages 仍為 v3.0.17**
5. Active branch / environment: GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git；GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/ ✅
6. External platforms / dependencies in scope:
   - EDB 網站：https://applications.edb.gov.hk/circular/circular.aspx?langno=2（ASP.NET WebForms）
   - OpenAI gpt-5-nano API（temperature=1, max_completion_tokens=16000, developer role）
   - K1 Knowledge: https://leonard-wong-git.github.io/edb-knowledge/（knowledge.json / guidelines.json）
   - Python: requests, beautifulsoup4, PyMuPDF (fitz), openai
   - Frontend: 純 HTML/CSS/JS（無框架）

## Layer Map
1. Product / System Layer: EDB 通告爬蟲 + AI 分析 + Dashboard 前端
2. Development Governance Layer: AGENTS.md 規則、SESSION 管理、Root Safety Check
3. Current task belongs to which layer: Product / System Layer（K1 backfill pipeline fix + dashboard UI fix）
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
# 1. 進入正確 git repo（Documents 目錄下的那個）
cd ~/Documents/EDB-AI-Circular-System

# 2. Pull rebase 先（GitHub Actions 可能已更新 circulars.json）
git pull --rebase origin main

# 3. Push v3.0.18 commit
git push origin main

# 4. 打版本 tag
git tag v3.0.18

# 5. 推送 tag
git push origin --tags

# 6. 觸發 school-year workflow（手動，GitHub Actions UI）
#    → 這樣才會用 v3.0.18 的 scraper backfill 所有 117 records
```

### ⚠️ git pull --rebase 風險提示（2026-03-22 確認）
- GitHub Actions 定時 commit circulars.json，所以本地 push 前幾乎必須先 pull --rebase
- rebase 時，若 circulars.json / SESSION_HANDOFF.md 有衝突，**本地版本可能被遠端舊版覆蓋**
- 建議：push 前先確認 `git status` 和 `git log --oneline -3`，確保本地版本正確

### 保障 B：複製資料夾（本機備份）
```bash
cp -r ~/Documents/EDB-AI-Circular-System ~/Documents/EDB-AI-Circular-System-snapshot-v3.0.18
```

### 如需從舊版本回退
```bash
git checkout v3.0.18
```

## Open Priorities
1. **[立即 ⭐ 用戶行動]** 在 Mac Terminal：`cd ~/Documents/EDB-AI-Circular-System && git pull --rebase && git push`，然後在 GitHub Actions 手動觸發 school-year workflow
2. **[驗證]** Workflow 完成後，fetch live circulars.json，抽樣 3-5 records 確認 k1_topics / k1_facts / k1_guidelines 非空
3. **[重要]** 修正 topic-aware review cross-topic 污染：supplier/finance links 跑入 curriculum/student 通告
4. **[待接收]** 新版 `role_facts.json` 從 K1 project 交付後，驗證符合 K1 v2.0.0 契約再接入
5. **[長期]** K1 第二階段：PDF 提取真實 EDB 知識（另立項目）
6. **[選做]** LLM 引擎切換機制

## Known Risks / Blockers
1. gpt-5-nano 必須 temperature=1，否則 400 Bad Request
   - `max_tokens` → 必須用 `max_completion_tokens`（推理模型）
   - `"system"` role → 必須用 `"developer"` role（推理模型）
   - `max_completion_tokens` 最少 16000
2. EDB 網站需 POST + ViewState（GET 無效），解析用位置式（非 CSS class）
3. ✅ ~~days-3 覆蓋問題~~ **已修復（2026-03-23）**
4. **⚠️ git rebase 治理文件覆蓋風險（2026-03-22 確認）：**
   - GitHub Actions 定時 commit 導致遠端常領先本地
   - `git pull --rebase` 可能覆蓋 SESSION_HANDOFF.md / SESSION_LOG.md
   - 緩解：push 前手動 cp 最新版本到 git repo；或在 `.gitattributes` 設 merge strategy
5. **⚠️ 正確 git repo 路徑（2026-04-08 確認）：**
   - ✅ 正確：`~/Documents/EDB-AI-Circular-System`（已與 GitHub origin 同步，commit d52ae17 在此）
   - ❌ 不要用：`EDB-Circular-AI-analysis-system` 掛載資料夾（舊 clone，停留在 v3.0.3，已過時）
6. **⚠️ EDB 表單字段已確認（2026-03-10 實測）：**
   - PlaceholderID = `MainContentPlaceHolder`
   - 日期字段：`txtPeriodFrom` / `txtPeriodTo`
   - 搜尋按鈕：`btnSearch2`（JS 觸發）
7. PyMuPDF (fitz) 已替換 pdfplumber/pdfminer（2026-03-15）— school-year workflow 全綠
8. **⚠️ Publish conflict note（2026-04-04 實測）：**
   - remote `circulars.json` 可能在 code/docs 發布期間被 GitHub Actions 更新
   - rebase 時若只衝突在 `circulars.json`，應保留較新的 remote 版本，再繼續推送
9. **⚠️ Knowledge review boundary（2026-04-04 確認）：**
   - 第二輪 review 現時只針對 supplier + curriculum + finance 場景做 deterministic enrichment
   - 不應改寫 deadline、金額、編號、scope 等硬事實
10. **⚠️ Role contract migration watch（2026-04-06 確認）：**
    - K1 接口規格已更新為 `subject_head` / `panel_chair` / `eo_admin=EO`
    - 新版 `role_facts.json` 尚未交付；接入前仍需按 K1 v2.0.0 契約驗證
11. **⚠️ K1 public API drift watch（2026-04-08 確認）：**
    - public `knowledge.json` live payload 目前是 topic → role-arrays 形態，不是舊 task brief 的 entry-list 形態
    - public `guidelines.json` 與 task brief 一致
    - 整合層已做雙 schema 兼容處理
12. **⚠️ K1 backfill — school-year workflow 必須手動觸發（2026-04-08 確認）：**
    - GitHub Pages 只在 workflow run 時更新；不會因 git push 自動執行
    - backfill 效果要在下次 school-year workflow 完成後才能在 live circulars.json 看到
    - PROJECT_MASTER_SPEC suggestion issued: Claude_20260408_1400 2026-04-08.

## Regression / Verification Notes
1. v2.1.0 QC: 24/24 structural checks 通過；JS syntax check 通過
2. GitHub Pages 部署：push 至 `main` 現已自動觸發 Pages deployment；仍可保留 manual/schedule workflow 用於 scraper
3. school-year 最後成功：1h 23m（16 hours ago as of 2026-03-22）
4. v3.0.18 QC: py_compile PASS；4/4 K1 logic tests PASS；dashboard JS version markers confirmed

## Consolidation Watchlist
1. SESSION_HANDOFF.md 被 rebase 覆蓋：下次 session 開始需確認版本（push 前先 cp）
2. ✅ ~~days-3 覆蓋 school-year 數據~~ 已修復（2026-03-23 PHASE 4 merge）
3. `EDB-Circular-AI-analysis-system` 掛載資料夾已過時（v3.0.3）— 不可用於後端開發

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
1. UTC date: 2026-04-08
2. Session ID: Claude_20260408_1400
3. Completed:
   - ✅ 月曆 dlLabel fix：calendar cells 現顯示類型標籤（`⏰ EDBC042 申請`）
   - ✅ apply-ext interactive form：已申請 → date-picker + notes；申請中 → notes；localStorage 持久化
   - ✅ K1 Phase 3 skip-block carry-forward：保留 existing records 的 k1_* fields
   - ✅ K1 Phase 4.5 backfill pass：merge-sort 後批量補填所有 k1_topics=[] records
   - ✅ analyze() post-LLM K1 re-detect：LLM 返回後重新偵測 K1 topics（更準確）
   - ✅ 版本升至 v3.0.18（scraper + dashboard 6 locations，git repo + workspace）
   - ✅ git commit d52ae17（Documents/EDB-AI-Circular-System）
4. Pending:
   - 用戶 push v3.0.18 並手動觸發 school-year workflow
   - 驗證 live circulars.json k1_* fields 非空
   - 修正 topic-aware review cross-topic 污染
   - 接收新版 role_facts.json
5. Next priorities (max 3):
   - 用戶 push + 觸發 school-year workflow（立即行動）
   - 驗證 live k1_topics/k1_facts/k1_guidelines
   - 修正 topic-aware review cross-topic 污染
6. Risks / blockers:
   - push 前必須 git pull --rebase（GitHub Actions 可能已更新 circulars.json）
   - school-year workflow 需手動觸發；不自動 backfill
   - EDB-Circular-AI-analysis-system 掛載資料夾已過時，不可用於後端工作
7. Files materially changed:
   - `edb_scraper.py`（Documents/EDB-AI-Circular-System + Claude-edb-Project-V3 workspace）
   - `edb-dashboard.html`（Documents/EDB-AI-Circular-System + Claude-edb-Project-V3 workspace）
   - `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`
8. Validation summary: py_compile PASS；dashboard JS syntax PASS；4/4 logic tests PASS；version v3.0.18 confirmed；commit d52ae17 confirmed
9. Git commits: d52ae17 feat: v3.0.18 — K1 backfill + calendar label fix + apply-ext form
