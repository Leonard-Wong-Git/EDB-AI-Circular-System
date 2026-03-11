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
2. Session ID: Claude_20260310_RE01（v1.0.0 整合修復 + --school-year + GitHub Pages 部署配置）
3. Completed:
   - **整合 Bug 修復**：
     * `edb_scraper.py` title 污染修復（`摘要：` 截斷）✅
     * `edb-dashboard.html` REFERENCE_CIRCULARS ID 碰撞修復（9001/9002/9003）✅
   - **--school-year 新功能**：
     * `school_year_start()` helper（9月1日學年定義，4個邊界條件測試通過）✅
     * `get_circular_list()` 新增 `date_from` 參數 ✅
     * circulars.json 輸出新增 `range` / `date_from` / `date_to` 欄位 ✅
     * `--days 365` 全面支援 ✅
   - **GitHub Pages 部署配置**：
     * `.github/workflows/update-circulars.yml` 新建（每天 HKT 07:00 自動更新）✅
     * `index.html` 新建（根 URL 自動跳轉 edb-dashboard.html）✅
     * `.gitignore` 更新（移除 circulars.json 排除，加入 .edb_cache/）✅
   - **用戶教育**：說明 folder snapshot + git tag 兩層保障策略 ✅
   - **版本更新**：`edb_scraper.py` 版本號更新至 v1.0.0 ✅
   - **✅ 學年爬蟲完成**：`python3 edb_scraper.py --school-year --output ./circulars.json -v` → **104 條通告，834.5KB** ✅
4. Pending：
   - ⭐ 在瀏覽器開啟 `edb-dashboard.html`，確認 104 條學年通告正確顯示
   - **GitHub Pages 一次性設定**（見 CHANGELOG v1.0.1-hosting）：
     1. push 所有文件至 GitHub
     2. 設定 GitHub Secret：`OPENAI_API_KEY`
     3. Settings → Pages → Source: GitHub Actions
     4. 手動觸發第一次 workflow
   - Dashboard 目視確認（學年數據載入後）
5. Next priorities (max 3):
   - ⭐ 完成 GitHub Pages 一次性設定，取得公開 URL
   - 確認學年爬蟲 circulars.json 在 Dashboard 正常顯示
   - 推送 tag `v1.0.1-hosting`
6. Risks / blockers:
   - 學年爬蟲通告數量未知（估計 50–100+），LLM 費用需留意
   - GitHub Pages 首次設定需要手動操作（Settings → Pages → Source: GitHub Actions）
7. Files materially changed:
   - `edb_scraper.py`（更新：title fix + school_year_start + date_from + v1.0.0）
   - `edb-dashboard.html`（更新：REFERENCE_CIRCULARS id 9001/9002/9003）
   - `.github/workflows/update-circulars.yml`（新建）
   - `index.html`（新建）
   - `.gitignore`（更新）
   - `CHANGELOG.md`（更新：v1.0.0-release + v1.0.1-hosting）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（更新）
8. Validation summary: `py_compile` OK ✅；`school_year_start()` 4 邊界條件 ✅；學年爬蟲執行中 ⏳
9. Consolidation actions taken: 無新規則；部署架構記錄於 CHANGELOG v1.0.1-hosting

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
