# Session Handoff

## Current Baseline
1. Version: v0.2.1-frontend + v0.3.0-backend(進行中) (2026-03-10) ← **當前版本**
2. Core commands / features:
   - `edb-dashboard.html` — 正式版單頁 Dashboard（2,453 行，13 項修訂 ✅ **已完成**）
   - `edb_scraper.py` — 後端爬蟲 + LLM 分析管線（v0.3.0-backend，已建立，待測試）
   - `fetch_knowledge.py` — EDB / ICAC 知識庫抓取工具（已建立）
   - `requirements.txt` — Python 依賴清單（已更新）
   - `edb-dashboard-mockup.html` — 互動式 UI Mockup（保留作參考）
3. Regression baseline: 26/26 QC 功能驗證通過（2026-03-10）；v0.2.1 13/13 修訂
4. Release / merge status: v0.2.1-frontend 已完成，待 GitHub 推送（需 Mac Terminal，tag: v0.2.1-frontend）
5. Active branch / environment: 本地輸出目錄 `mnt/outputs/EDB-Circular-AI-analysis-system/`（GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git，最新 tag: v0.1.0-mockup，待推送 v0.2.1-frontend）
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
7. **[下一步 ⭐]** 完整 LLM 執行：
   ```bash
   export OPENAI_API_KEY="sk-..."
   python3 edb_scraper.py --days 30 --output ./circulars.json -v
   ```
8. **[下一步]** 在瀏覽器開啟 `edb-dashboard.html` → 手動載入 `circulars.json`（Dev 頁面或直接同目錄放置），確認真實數據顯示正常
9. **[下一步]** Mac Terminal：`push-to-github.sh`（tag: v0.3.0-backend）
10. 整合測試：`circulars.json` 與 Dashboard 聯調，驗收標準見需求文件第八節

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
2. Session ID: Claude_20260310_BE03（HTML 結構解析 + _parse_list 修正 + dry-run ✅）
3. Completed:
   - `debug_edb_html.py` 第二次執行（修正後）：POST 成功找到 14 條通告號碼 ✅
   - 建立 `parse_structure.py`：分析通告號碼的實際 DOM 位置
   - 建立 `parse_row.py`：解析完整 row 結構（所有 cells + links）
   - 確認真實 HTML 結構（見 Known Risks #5）
   - 完整重寫 `_parse_list()`：按真實結構解析（3 cells，circulars_result_remark，PDF 連結）
   - 修正 `_abs_url()`：改用 `urljoin` 正確解析 `../` 相對路徑
   - 修正 `datetime.utcnow()` deprecation warning → `datetime.now(timezone.utc)`
   - **Dry-run 完全通過**：14 條通告 + PDF 提取 + circulars.json 38.4KB ✅
4. Pending：
   - 設定 `export OPENAI_API_KEY="sk-..."` 後執行完整 LLM 分析
   - 在瀏覽器確認真實 circulars.json 載入 Dashboard 正常顯示
   - GitHub 推送（tag: v0.3.0-backend）
5. Next priorities (max 3):
   - ⭐ 完整 LLM 執行：`python3 edb_scraper.py --days 30 --output ./circulars.json -v`
   - 瀏覽器確認真實數據顯示
   - GitHub 推送
6. Risks / blockers: LLM 分析速度（14條 × ~30s/條 ≈ 7分鐘）；OPENAI_API_KEY 必須設定
7. Files materially changed:
   - `edb_scraper.py`（更新：_parse_list 完整重寫 + _abs_url 修正 + timezone fix）
   - `parse_structure.py`（新建：DOM 結構診斷）
   - `parse_row.py`（新建：完整 row 結構解析）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（更新）
8. Validation summary: **dry-run 通過：14 circulars, PDF text extracted, 38.4KB JSON** ✅
9. Consolidation actions taken: EDB HTML 結構記錄於 Known Risks #5（SSOT）

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
