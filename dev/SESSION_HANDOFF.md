# Session Handoff

## Current Baseline
1. Version: **v0.3.0-backend** (2026-03-10) ← **當前版本** 🎉
2. Core commands / features:
   - `edb-dashboard.html` — 正式版單頁 Dashboard（2,453 行，v0.2.1 ✅）
   - `edb_scraper.py` — 後端爬蟲 + LLM 分析管線（v0.3.0-backend ✅ **已完成並通過測試**）
   - `circulars.json` — 14 條真實 EDB 通告 + gpt-5-nano LLM 分析（已生成 ✅）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具
   - `requirements.txt` — Python 依賴清單
3. Regression baseline: dry-run 14/14 通告通過；LLM 分析成功（EDBCM030 high/721chars, EDBCM026 mid/462chars）
4. Release / merge status: **v0.3.0-backend tag 已推送至 GitHub** ✅（52 objects, 11.35 MiB）
5. Active branch / environment: GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git，最新 tag: **v0.3.0-backend** ✅
6. External platforms / dependencies in scope:
   - EDB 網站：https://applications.edb.gov.hk/circular/circular.aspx?langno=2 （ASP.NET WebForms）
   - OpenAI gpt-5-nano API
   - Python: requests, beautifulsoup4, pdfplumber, openai
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

## Open Priorities
1. ✅ ~~開發正式 `edb-dashboard.html`（v0.2.0-frontend）~~ **已完成（2026-03-10）**
2. ✅ ~~v0.2.1-frontend 13 項 UI 修訂~~ **已完成（2026-03-10）**
3. ✅ ~~建立 `edb_scraper.py` 後端管線框架~~ **已完成（2026-03-10）**
4. ✅ ~~診斷 EDB POST 表單字段錯誤~~ **已修正（2026-03-10）**
5. ✅ ~~`_parse_list()` 修正為真實 EDB HTML 結構~~ **已完成（2026-03-10）**
6. ✅ ~~Dry-run 測試通過~~ **14 條通告 + PDF 提取 + 38.4KB circulars.json ✅ 已完成（2026-03-10）**
7. ✅ ~~完整 LLM 執行~~ **14 條通告 LLM 分析成功（2026-03-10）**
8. ✅ ~~GitHub 推送 v0.3.0-backend~~ **已完成（2026-03-10）**
9. **[下一步 ⭐]** 在瀏覽器開啟 `edb-dashboard.html`，確認真實 `circulars.json` 正確顯示
10. **[下一步]** 整合調整：根據真實數據微調 Dashboard 顯示（如有需要）
11. v1.0.0-release：整合測試通過後正式發布，驗收標準見需求文件第八節

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
1. UTC date: 2026-03-10
2. Session ID: Claude_20260310_BE04（LLM 修正 + 完整管線通過 + Dashboard 真實數據驗證 + GitHub 推送 + Session Close）
3. Completed:
   - 修正 `max_tokens` → `max_completion_tokens`（gpt-5-nano 推理模型要求）✅
   - 修正 `"system"` → `"developer"` role（gpt-5-nano 推理模型要求）✅
   - 修正 `max_completion_tokens` 4096 → 16000（推理 tokens 消耗大）✅
   - 建立 `test_llm.py`：3 階段診斷，Test 3 通過（finish_reason=stop，1675 chars）✅
   - **完整 LLM 執行成功**：EDBCM030/2026 high/721chars，EDBCM026/2026 mid/462chars ✅
   - Dashboard 真實數據確認：EDBCM030（HK$800,000 今天截止）正確顯示 ✅
   - GitHub force push + tag `v0.3.0-backend` 推送成功（52 objects，11.35 MiB）✅
   - **Session Close**：
     * `CHANGELOG.md` 更新（v0.3.0-backend 完整記錄）✅
     * 診斷工具移至 `dev/tools/`（debug_edb_html.py, parse_form.py, parse_structure.py, parse_row.py, test_llm.py）✅
     * `dev/GIT_PUSH_MANUAL.md` 新建（完整手動 git 推送指南 + PAT 方法）✅
     * `dev/SESSION_HANDOFF.md` + `dev/SESSION_LOG.md` 更新（本記錄）✅
4. Pending：
   - ⭐ 瀏覽器整合確認：在瀏覽器開啟 `edb-dashboard.html`，目視確認真實 circulars.json 顯示
   - 根據真實數據微調 Dashboard（如有需要）
   - **需在 Mac Terminal 執行最終 git push**（將 dev/tools/, GIT_PUSH_MANUAL.md, CHANGELOG 更新推送 GitHub）
5. Next priorities (max 3):
   - ⭐ v1.0.0-release 整合測試（前後端聯調驗收，見需求文件第八節）
   - Dashboard 微調（如真實數據顯示有任何問題）
   - 定期更新排程（cron / 排程，見 CHANGELOG Planned 節）
6. Risks / blockers: 無新風險；舊風險已記錄於 Known Risks #1–#5
7. Files materially changed:
   - `edb_scraper.py`（更新：LLM 三項修正）
   - `test_llm.py`（新建 → 移至 dev/tools/）
   - `dev/tools/debug_edb_html.py`（移動）
   - `dev/tools/parse_form.py`（移動）
   - `dev/tools/parse_structure.py`（移動）
   - `dev/tools/parse_row.py`（移動）
   - `dev/GIT_PUSH_MANUAL.md`（新建）
   - `CHANGELOG.md`（更新：v0.3.0-backend 完整記錄）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（更新）
8. Validation summary: **完整管線通過：14 circulars + PDF + LLM 分析 + GitHub v0.3.0-backend tag** ✅
9. Consolidation actions taken: gpt-5-nano 三項規則記錄於 Known Risks #1（SSOT）；診斷工具集中於 dev/tools/

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
