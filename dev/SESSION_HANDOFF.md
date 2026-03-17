# Session Handoff

## Current Baseline
1. Version: **v2.0.0** (2026-03-16) ← **當前版本（待 push）**
2. Core commands / features:
   - `edb-dashboard.html` — v2.0.0 全面改版 Dashboard（~2,766 行；37 項改進，含版本管理/主題/圖標/詳情面板/日曆/搜尋/篩選/手機適配/統計/分享等）
   - `edb_scraper.py` — 後端爬蟲 + LLM 分析管線（PyMuPDF 引擎 + K1 知識注入 + R1-v2 角色精確度：few-shot + postprocess filter）
   - `circulars.json` — school-year 全量 EDB 通告 + gpt-5-nano LLM 分析（GitHub Pages 已部署 ✅）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具
   - `requirements.txt` — Python 依賴清單（PyMuPDF 替換 pdfplumber）
   - `dev/knowledge/role_facts.json` — K1 基線知識庫（6 主題 × 7 角色，人工整理版）
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` — K1 獨立項目接口合約規格
3. Regression baseline: school-year workflow 全綠 1h25m；days-3 workflow 33s；v2.0.0 HTML 驗證 OK（14/14 checks）；R1-v2 postprocess simulation supplier 49%→21%
4. Release / merge status: **v2.0.0 + R1-v2 已推送至 GitHub** ✅（`7151ed7` + `dbd997e`）；GitHub Pages v2.0.0 已部署 ✅；days-3 workflow 8m9s 成功
5. Active branch / environment: GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git；GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/（school-year 數據已上線 ✅）
6. External platforms / dependencies in scope:
   - EDB 網站：https://applications.edb.gov.hk/circular/circular.aspx?langno=2 （ASP.NET WebForms）
   - OpenAI gpt-5-nano API
   - Python: requests, beautifulsoup4, PyMuPDF (fitz), openai
   - Frontend: 純 HTML/CSS/JS（無框架），SheetJS CDN

## Layer Map
1. Product / System Layer: EDB 通告爬蟲 + LLM 分析 + Dashboard 前端
2. Development Governance Layer: AGENTS.md 規則、SESSION 管理、Root Safety Check
3. Current task belongs to which layer: Product / System Layer（後端管線開發）
4. Known layer-boundary risks: 暫無

## Mandatory Start Checklist
1. ✅ Read `dev/SESSION_HANDOFF.md`
2. ✅ Read `dev/SESSION_LOG.md`
3. Read `dev/v0.2.0-FRONTEND-SPEC.md`（前端規格 SSOT，後端需參照 circulars.json schema）
4. Confirm working tree / file status
5. Run baseline checks: 在瀏覽器開啟 `edb-dashboard.html` 目視驗證 UI
6. Confirm environment / dependency state: Python venv + OPENAI_API_KEY（後端開發時需要）
7. Confirm whether external platform alignment is required: 開始後端開發前需確認 EDB 網站 ViewState 格式
8. Search for related SSOT / spec / runbook before change: 後端規格參閱 `EDB-項目需求及規則總覽.docx` 第五節（LLM）+ 第六節（爬蟲）
9. Search for duplicate rule / duplicate term / prior related fixes: 見 SESSION_LOG

## ⚠️ Session Close 必做保障（每次 Session 結束前強制執行）
> 目的：確保每個版本有快照，可隨時回退，不依賴 VM 環境

**每個 session 結束前，必須在 Mac Terminal 完成以下兩項：**

### 保障 A：打 Git Tag（版本快照）
```bash
# 1. Commit session close 文件更新
git add .
git commit -m "chore: session close — <本 session 簡述>"

# 2. 打版本 tag（格式：v主版本.次版本.修訂-說明）
git tag v0.x.x-<說明>          # 例：v0.3.0-backend, v1.0.0-release

# 3. 推送（按 dev/GIT_PUSH_MANUAL.md 操作）
git push --force origin main
git push origin --tags
```
> GitHub 有 tag 就等同快照，任何時候可 `git checkout <tag>` 取回

### 保障 B：複製資料夾（本機備份）
```bash
# 在 Mac Terminal 執行
cp -r "<PROJECT_PATH>" "<PROJECT_PATH>-snapshot-v0.x.x"
# 例：cp -r ".../EDB-Circular-AI-analysis-system" ".../EDB-Circular-AI-analysis-system-snapshot-v0.3.0"
```
> 本機有副本，即使 git 歷史因 force push 被覆蓋仍可還原

### 如需從舊版本回退
```bash
# 方法 A：從 GitHub 取回特定版本
cd /tmp && git clone https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git EDB-old
cd EDB-old && git checkout v0.2.1-frontend

# 方法 B：直接使用本機快照副本
cp -r "<PROJECT_PATH>-snapshot-v0.x.x" "<PROJECT_PATH>-restored"
```

## Open Priorities
1. ✅ ~~開發正式 `edb-dashboard.html`（v0.2.0-frontend）~~ **已完成（2026-03-10）**
2. ✅ ~~v0.2.1-frontend 13 項 UI 修訂~~ **已完成（2026-03-10）**
3. ✅ ~~建立 `edb_scraper.py` 後端管線框架~~ **已完成（2026-03-10）**
4. ✅ ~~診斷 EDB POST 表單字段錯誤~~ **已修正（2026-03-10）**
5. ✅ ~~pdfplumber→PyMuPDF 遷移~~ **已完成（2026-03-15）；school-year 全綠**
6. ✅ ~~Issue 4：Dashboard 官方摘要空白~~ **UI fallback 已修復（2026-03-16 v1.1.2）**
7. ✅ ~~K1 知識注入基線框架~~ **已完成（2026-03-16）；role_facts.json + 注入函數 + 接口規格**
8. ✅ ~~R1 全角色職責精確度~~ **R1-v2 已完成（2026-03-16）；few-shot + postprocess filter + commit `dbd997e`**
9. ✅ ~~v2.0.0 Dashboard 37 項改版~~ **已完成（2026-03-16）；commit `7151ed7`，14/14 驗證通過**
10. ✅ ~~Mac push v2.0.0 + R1-v2~~ **已推送 + workflow 成功（2026-03-16）**
11. **[下一步 ⭐]** GitHub Pages v2.0.0 視覺驗證 + school-year workflow re-run（R1-v2 效果驗證）
12. **[長期]** K1 第二階段：PDF 提取真實 EDB 知識（另立項目，通過 role_facts.json 接口交付）
13. **[選做]** LLM 引擎切換機制
14. **[選做]** 後端 #35/#36：上年度爬蟲分析 + 年末預算預測（HTML 已預留 placeholder）

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
- 功能規格 SSOT：`dev/v0.2.0-FRONTEND-SPEC.md`

## Knowledge Base Usage Rules ⚠️ MANDATORY
1. **使用時機：** 知識庫文件 **只在分析通告時使用**，不用於一般對話或其他任務
2. **文件範圍：** `ROLE_KNOWLEDGE_INDEX.md` 只列出每角色 **top 5 文件**，並非完整知識庫清單
3. **查閱方式（Index → Link → Fetch）：**
   - Step 1：先查閱 `ROLE_KNOWLEDGE_INDEX.md`，找出與通告相關角色對應的知識文件
   - Step 2：根據 index 中的 URL/路徑，**直接連結至對應文件的相關章節**
   - Step 3：只讀取與通告內容直接相關的段落，避免全文載入
4. **目的：** 以知識文件補充角色背景，提高分析精準度（例如：教師的 CPD 要求、採購門檻、意外通報規則等），而非取代通告本身的判讀
5. **禁止：** 不可因知識庫未覆蓋某範疇而拒絕分析；知識庫只是輔助資料

## Known Risks / Blockers
1. gpt-5-nano 必須 temperature=1，否則 400 Bad Request（已記錄於需求文件第五節）
   **⚠️ 額外已確認規則（2026-03-10 實測）：**
   - `max_tokens` → 必須用 `max_completion_tokens`（推理模型）
   - `"system"` role → 必須用 `"developer"` role（推理模型）
   - `max_completion_tokens` 最少 16000（推理 tokens 消耗大）
2. EDB 網站需 POST + ViewState（GET 無效），解析用位置式（非 CSS class）
3. `--llm-only` 必須搭配 `--output ./circulars.json`（避免路徑錯誤）
4. **⚠️ EDB 表單字段已確認（2026-03-10 實測）：**
   - PlaceholderID = `MainContentPlaceHolder`（非 `ContentPlaceHolder1`）
   - 日期字段：`txtPeriodFrom` / `txtPeriodTo`（非 `txtFromDate` / `txtToDate`）
   - 搜尋按鈕：`btnSearch2`（JS 觸發，非 `btnSearch`）
   - 無 `ddlYear` / `ddlMonth` 字段；改用 `ddlSchoolType2` + `ddlCircularType`
   - 必須包含：`ctl00$currentSection = "2"` + `lbltab_circular = "通告"`
   - `edb_scraper.py` 已修正並通過 dry-run 驗證 ✅
5. **⚠️ EDB HTML 通告結構已確認（2026-03-10 實測）：**
   - 每條通告 = `<tr>` 含 3× `<td class="circularResultRow circulartRow">`
   - Cell[0] 日期：`<div class="table_text_mobile_app">` 文字格式 `日期DD/MM/YYYY`
   - Cell[1] 主題：`<div class="table_text_mobile_app">` 直接文字節點=標題；`<div class="circulars_result_remark">` = 通告號
   - Cell[2] 語言：`<a href="../circular/upload/EDBCM/EDBCMyyNNNC.pdf">繁體中文</a>` 等3個連結
   - **無 detail_url**（列表頁沒有通告詳情連結）
   - PDF 優先順序：C.pdf（繁中）> E.pdf（英文）> S.pdf（簡體）
6. ✅ **pdfminer/pdfplumber 問題已解決（2026-03-15）** — 完全替換為 PyMuPDF (fitz)
   - 歷史記錄：pdfminer C 擴展 DEBUG 洪流（107K+ 行），6 種補丁方案全部失敗
   - 最終方案：移除 pdfplumber/pdfminer，替換為 PyMuPDF (fitz)，零 DEBUG 輸出
   - school-year workflow 首次成功：1h 25m，全綠 ✅
   - **安全的 workflow 模式**：`days-3`（增量，33 秒）/ `school-year`（全量，~1h25m）
7. **⚠️ VM workspace ≠ git repo（2026-03-15 確認）：**
   - VM workspace: `Claude-edb-Project-V3`（前端文件在此）
   - Git repo: `EDB-Circular-AI-analysis-system`（後端文件必須寫到這裏）
   - 修改後端文件時必須先 `request_cowork_directory` mount git repo 再寫入
   - Mac git repo 路徑：`/Users/leonard/Library/Application Support/Claude/local-agent-mode-sessions/f52b21f7-e7c9-49a3-80dc-00ab322afbcf/51c234d2-cb9f-4b55-bb07-b71de9e93c27/local_e454964f-74da-4734-9a60-bf4b4362ca65/outputs/EDB-Circular-AI-analysis-system`

## Regression / Verification Notes
1. Required checks: 後端驗收（見需求文件 8.1）、前端驗收（見需求文件 8.2）
2. Current failing checks: N/A（Mockup 階段）
3. Release / merge blocking conditions: 前後端聯調通過後方可發布

## Consolidation Watchlist
1. Rules currently duplicated across files: 暫無
2. Areas showing accretive drift: 暫無
3. Candidate items for consolidation / retirement: 待正式開發後評估

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.
If the session's changes affect specifications, runbooks, regression thresholds, release conditions, or external platform integrations, the corresponding documents must also be updated.
If the session's fix involves adding a new rule, first check whether the existing definition should be integrated or outdated wording retired — avoid stacking without consolidating.

## Last Session Record
1. UTC date: 2026-03-17
2. Session ID: Claude_20260317_0800（AGENTS.md v2 升級 + CODEBASE_CONTEXT.md 生成）
3. Completed:
   - ✅ **AGENTS.md v2 升級**：整合 INIT.md 7 項新增（§0a Note / §0b API Safety / §1 CODEBASE_CONTEXT / §2 優先級 / §3d Test Plan / §4 Close 擴充 / §10 Active trigger）；兩個 repo 同步（622 行）
   - ✅ **dev/CODEBASE_CONTEXT.md 首次生成**：177 行，7 section，3 External Services（全部有 Doc-reviewed + Test-verified），8 Key Decisions
   - ✅ **Root Safety Check + 備份**：INSTALL_ROOT_OK + INSTALL_WRITE_OK；`dev/init_backup/20260317_081952_UTC/`
4. Pending：
   - school-year workflow re-run 進行中（R1-v2 效果驗證）
   - GitHub Pages v2.0.0 視覺驗證
   - Mac push 本次治理文件更新
   - README.md / CHANGELOG.md 內容過時（非阻塞）
   - K1 第二階段（另立項目）
   - LLM 引擎切換機制
5. Next priorities (max 3):
   - school-year workflow 結果 + R1-v2 角色分佈驗證
   - GitHub Pages v2.0.0 視覺驗證
   - K1 PDF 提取項目（另立）
6. Risks / blockers: school-year re-run 進行中，結果未知；README.md/CHANGELOG.md 過時但非阻塞
7. Files materially changed:
   - `AGENTS.md`（兩個 repo，395→622 行）
   - `dev/CODEBASE_CONTEXT.md`（新建，177 行）
   - `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`
8. Validation summary: AGENTS.md 兩個 repo 完全一致；CODEBASE_CONTEXT.md 7 section 完整；備份快照完整
9. Git commits: 待 Mac push

## Previous Session Record (RE05)
1. UTC date: 2026-03-14
2. Session ID: Claude_20260314_RE05（PDF timeout 修復嘗試 — 未成功）
3. Completed:
   - ❌ PDF timeout 三種方案全部失敗（SIGALRM / multiprocessing+SIGTERM）
   - git push 成功（87c9e08）；3 次 workflow 全部卡死
4. Files: `edb_scraper.py`、`dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`

## Previous Session Record (RE04)
1. UTC date: 2026-03-11
2. Session ID: Claude_20260311_RE04（8 項功能實作：匯出、列印、多選、排序、主題、狀態同步）
3. Completed:
   - **F1 — 排序持久化**：`lsLoad()` 讀取 `edb_sort_field`/`edb_sort_asc`；`sortList()` 寫入 localStorage；預設按日期降序 ✅
   - **F2 — 時段自動主題**：`applyTheme()` 改用 `new Date().getHours()`（07:00–18:00=淺色，其餘=深色）；`setInterval` 每 60 秒重評 ✅
   - **C1 — 狀態互通**：`updateBmBadge()`（書籤 tab badge 即時更新）+ `syncStatusBtns(id,status)`（多處狀態按鈕即時同步，無需重繪）；所有狀態按鈕加 `data-sid` ✅
   - **C2 — 資源狀態有意義**：row 顏色 CSS（`.res-applying/applied/closed/na`）；`setApplyStatus()` 改寫（即時 DOM 行顏色更新 + 申請日期記錄 + toast 通知）；新增 `edb_apply_dates` localStorage key ✅
   - **B5 — CSV 增強**：`exportExcel()` 新增「行動數」+「AI摘要（前200字）」欄位 ✅
   - **B7 — .ics 日曆匯出**：新增 `exportICS()` 函數（iCalendar 格式，含所有截止日期）；工具列新增 📅 日曆按鈕 ✅
   - **B6 — 格式化列印**：`printDetail()` 改寫（在新視窗開啟結構化 HTML 報告，含列印/關閉按鈕）；移除舊 `window.print()` 版本（避免重複函數） ✅
   - **B8 — 多選批量匯出**：`toggleMultiSelect()`/`cardClick()`/`exportSelected()` 新增；浮動批量操作列（#batchBar）；卡片選中框和 CSS；工具列 ☑️ 多選按鈕 ✅
   - **HTML 驗證**：`html.parser` 確認標籤平衡（HTML OK）；所有 11 個新函數 grep 確認存在 ✅
   - **git push 診斷**：
     * `fatal: no upstream branch` → `git push --set-upstream origin main`
     * `fatal: not a git repository` → 需先 `cd` 至項目目錄
     * `[rejected] fetch first` → `git pull --rebase origin main && git push`（GitHub Actions 有衝突）
4. Pending：
   - ⭐ **edb_scraper.py 加 PDF 解析 timeout**（pdfminer 在某 PDF 卡死 1 小時以上，workflow 被取消）
   - ⭐ GitHub Pages 仍是舊版本（無 📅 日曆 / ☑️ 多選按鈕）；修復 timeout 後重新觸發 workflow 才能部署
   - 討論（下個 session）：K1 知識庫參考文件框架、R1 全角色職責精確度、LLM 引擎切換機制
   - 選做：次要缺陷（D8/D9 月曆篩選、F4 badge 計數、H5 天數選擇器、H6 已跟進切換）
5. Next priorities (max 3):
   - ⭐ 修復 `edb_scraper.py` PDF timeout（signal.alarm 60秒），push → 觸發 workflow → 確認 Pages 部署
   - K1/R1 知識框架討論
   - 次要缺陷修復 + 響應式設計測試
6. Risks / blockers: ⚠️ pdfminer 無 timeout 保護 → 某些 PDF 令 workflow 卡死超過 1 小時（已記錄於 Known Risks #6）
7. Files materially changed:
   - `edb-dashboard.html`（2453→2796 行；8 項新功能）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（更新）
8. Validation summary: HTML parser「HTML OK」✅；11 函數 grep 全找到 ✅；edb-dashboard.html 2796 行
9. New localStorage keys added: `edb_sort_field`、`edb_sort_asc`、`edb_apply_dates`（共現 12 個 keys）
10. Consolidation actions taken: 移除舊 `printDetail()` 重複函數（`window.print()` 版本）

## Previous Session Record
1. UTC date: 2026-03-11
2. Session ID: Claude_20260311_RE03（自動化驗收測試 + grantChip null 修復）
3. Completed:
   - 自動化驗收測試：73/80（91%）通過 ✅；Live site 105 條通告，PDF 連結 ✅
   - Bug 修復：`grantChip()` applicable 類型加 `||'資助'` ✅（影響 10+ 張卡片）
   - git push upstream 診斷：`fatal: no upstream branch` → `git push --set-upstream origin main`
4. Files materially changed:
   - `edb-dashboard.html`（修復：grantChip null fallback）
   - `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`

## Previous Session Record
1. UTC date: 2026-03-11
2. Session ID: Claude_20260311_RE02（PDF 連結修復 + 導航修復 + 系統說明 + 驗收清單）
3. Completed:
   - **PDF 連結修復**：
     * `edb_scraper.py` 輸出 record 新增 `pdf_urls` 欄位（之前只在內部處理，未寫入 JSON）✅
     * `edb-dashboard.html` 新增 `buildPdfLinks(d)` helper function ✅
     * PDF 按鈕使用真實 EDB URL；無 pdf_urls 時以通告號推算 URL；最終 fallback 連至 EDB 通告列表頁 ✅
   - **導航 Bug 修復**：
     * Stats Bar「即將截止」chip — 現先切換至通告總覽頁，再滾動至 dlBar（原本不切換 tab）✅
     * 供應商 Tab Disclaimer Note 重複插入 bug — 加入 `id='supplierNote'` guard ✅
   - **系統功能說明**：
     * 設定頁新增全寬「📖 系統功能說明」卡片 ✅
     * 涵蓋 8 個功能模組：通告總覽、截止追蹤、角色視圖、資源申請、收藏/常備、自動更新、PDF原文件、本機儲存 ✅
   - **驗收清單**：
     * 新建 `dev/ACCEPTANCE_CHECKLIST.md` ✅
     * 涵蓋 A–K 11 個類別，共 80+ 個測試項目 ✅
4. Files materially changed:
   - `edb_scraper.py`（更新：輸出 record 加入 pdf_urls）
   - `edb-dashboard.html`（更新：buildPdfLinks + 導航修復 + 系統說明卡）
   - `dev/ACCEPTANCE_CHECKLIST.md`（新建）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（更新）

---

## Previous Session Record
1. UTC date: 2026-03-09
2. Session ID: Claude_20260309_1943
3. Completed:
   - 治理框架安裝（AGENTS.md / CLAUDE.md / GEMINI.md / SESSION_HANDOFF / SESSION_LOG）
   - 讀取需求文件 `EDB-項目需求及規則總覽.docx`（全文 + 表格）
   - 製作互動式 HTML Mockup `edb-dashboard-mockup.html`（1452行，20項 QC 全通過）
4. Files materially changed:
   - `AGENTS.md`（新建）、`CLAUDE.md`（新建）、`GEMINI.md`（新建）
   - `dev/SESSION_HANDOFF.md`（新建→更新）、`dev/SESSION_LOG.md`（新建→更新）
   - `edb-dashboard-mockup.html`（新建）
