# Session Log

## 2026-03-09

1. Agent & Session ID: Claude_20260309_1943
2. Task summary: 治理框架安裝 + 讀取需求文件 + 製作互動式 HTML Mockup
3. Layer classification: Product / System Layer（Mockup 設計） + Development Governance Layer（框架安裝）
4. Source triage: 需求來源 = `EDB-項目需求及規則總覽.docx`（v2.0，2026-03-09），屬文件驅動設計
5. Files read:
   - `/sessions/.../mnt/uploads/EDB-項目需求及規則總覽.docx`（全文段落 + 10張表格）
   - `dev/SESSION_HANDOFF.md`（初始化空白模板）
   - `dev/SESSION_LOG.md`（初始化空白模板）
6. Files changed:
   - `AGENTS.md`（新建，完整治理規則）
   - `CLAUDE.md`（新建，@AGENTS.md 橋接）
   - `GEMINI.md`（新建，@./AGENTS.md 橋接）
   - `dev/SESSION_HANDOFF.md`（新建→本 session 更新）
   - `dev/SESSION_LOG.md`（新建→本 session 更新）
   - `edb-dashboard-mockup.html`（新建，1452行）
7. Completed:
   - Root Safety Check（pwd=/sessions/kind-eager-pasteur，git root=none）
   - 用戶確認 PROJECT_ROOT（Mac 本機路徑對應 mnt/outputs/EDB-Circular-AI-analysis-system）
   - INSTALL_ROOT_OK + INSTALL_WRITE_OK 雙重確認通過
   - 備份快照建立：`dev/init_backup/20260309_194343_UTC/`（無舊檔，備份為空）
   - 5 個治理檔案建立完成
   - 需求文件完整解析（8節 + 10張表格）
   - 互動式 HTML Mockup 完成：
     * 4 主分頁（通告總覽 / 月曆 / 供應商 / 設定）
     * 詳情面板（右側滑入，5 個內部分頁：總結/行動/截止/角色/版本比較）
     * 4 條 Mock 通告（含完整 llm 欄位、role_relevance、diff）
     * 搜尋建議下拉清單
     * 角色選擇器
     * 截止倒數列
     * 月曆（藍/紅點標記，點擊查看事件）
     * 主題切換（深色/淺色/自動）
     * 字體大小滑桿
     * 設定頁（LLM模型資訊 / 使用指南）
8. Validation / QC:
   - HTML 語法驗證：0 unclosed tags（python html.parser）
   - 20/20 UI 組件驗證全通過（grep 檢查）
   - 文件大小：1452 行
9. Pending: 正式 Dashboard 開發、後端 edb_scraper.py 開發
10. Next priorities:
    - 確認 Mockup UI 方向，收集修改意見
    - 開發正式 `edb-dashboard.html`（功能完整版）
    - 開發 `edb_scraper.py` 後端管線
11. Risks / blockers:
    - gpt-5-nano 必須 temperature=1
    - EDB 網站需 POST + ViewState
    - `--llm-only` 必須搭配 `--output`
12. Notes: 首次 session，專案從零開始

### Problem -> Root Cause -> Fix -> Verification
1. Problem: N/A（首次 session，無 bug）
2. Root Cause: —
3. Fix: —
4. Verification: —
5. Regression / rule update: —

### Consolidation / Retirement Record
1. Duplicate / drift found: 無
2. Single source of truth chosen: `EDB-項目需求及規則總覽.docx` 為本階段 SSOT
3. What was merged: —
4. What was retired / superseded: —
5. Why consolidation was needed: —

---

## 2026-03-09（續）

1. Agent & Session ID: Claude_20260309_KB01
2. Task summary: 知識庫文件建立 + GitHub 推送腳本 + fetch_knowledge.py
3. Layer classification: Product / System Layer（知識庫基礎建設）
4. Source triage: 用戶提供 8 個 EDB/ICAC URL；VM 網絡封鎖，以底稿 + 本地執行腳本代替
5. Files read:
   - `dev/SESSION_HANDOFF.md`（更新前版本）
   - `dev/SESSION_LOG.md`（更新前版本）
6. Files changed:
   - `dev/knowledge/sch_admin_guide.md`（新建）
   - `dev/knowledge/fin_management.md`（新建）
   - `dev/knowledge/curriculum_guides.md`（新建）
   - `dev/knowledge/sch_activities.md`（新建）
   - `dev/knowledge/press_releases.md`（新建）
   - `dev/knowledge/kpm.md`（新建）
   - `dev/knowledge/icac_reference.md`（新建）
   - `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`（新建）
   - `fetch_knowledge.py`（新建）
   - `push-to-github.sh`（新建）
   - `README.md`（新建）、`CHANGELOG.md`（新建）、`.gitignore`（新建）
7. Completed:
   - 8 個角色知識庫底稿（預填內容，清楚標示「底稿」）
   - `ROLE_KNOWLEDGE_INDEX.md`（角色→文件對照，使用說明）
   - `fetch_knowledge.py`（requests + BeautifulSoup4，支援 depth 子頁面抓取，自動生成 index）
   - `push-to-github.sh`（安全 PAT 輸入，re-init git，stage + commit + tag + push，自動清理 token）
   - `README.md`（完整架構圖、資料夾結構、CLI 參數、成本估算、Roadmap）
   - `CHANGELOG.md`（Keep-a-Changelog，v0.1.0-mockup 正式記錄）
   - `.gitignore`（Python/Data/Secrets/macOS/IDE）
8. Validation / QC:
   - 8 個知識文件結構一致（標題/來源/角色/狀態/主要章節）
   - ROLE_KNOWLEDGE_INDEX 對照表完整（6 角色 × 相關文件）
   - push-to-github.sh 安全設計驗證（read -s 隱藏輸入，push 後清理 token URL）
9. Pending: Mac Terminal 執行 `push-to-github.sh`，Mac Terminal 執行 `fetch_knowledge.py`
10. Next priorities:
    - 在 Mac Terminal 執行 push 腳本（需新 GitHub PAT）
    - 在 Mac Terminal 執行 fetch_knowledge.py 更新知識庫
    - 開發正式 `edb-dashboard.html`（v0.2.0-frontend）
11. Risks / blockers:
    - VM 網絡封鎖 edb.gov.hk + github.com（已 workaround：Mac Terminal 腳本）
    - EDB 部分頁面為 ASP.NET WebForms，requests GET 可能只獲取部分內容
12. Notes: 接續 Claude_20260309_1943 session，於新 session 中因 context window 用盡而分段處理

### Problem -> Root Cause -> Fix -> Verification
1. Problem: VM 網絡封鎖，無法直接抓取 EDB/ICAC URL 或推送 GitHub
2. Root Cause: VM egress proxy 封鎖外部請求（edb.gov.hk, icac.org.hk, github.com）
3. Fix: 建立底稿知識文件 + fetch_knowledge.py（Mac 執行）+ push-to-github.sh（Mac 執行）
4. Verification: 腳本邏輯審閱通過，用戶需在 Mac 端執行驗證
5. Regression / rule update: 已記錄「VM 網絡限制」於 SESSION_HANDOFF Known Risks

### Consolidation / Retirement Record
1. Duplicate / drift found: 無
2. Single source of truth chosen: 知識庫以官方 URL 為 SSOT，底稿為臨時替代
3. What was merged: —
4. What was retired / superseded: —
5. Why consolidation was needed: —

---

### Next Session Handoff Prompt (Verbatim)
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：Mockup v1.0 完成，進入正式開發階段

已完成：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）安裝完畢
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）已全文解析
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行）已完成並通過 QC

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard-mockup.html   ← 本 session 產出，請先瀏覽確認 UI 方向
  ├── AGENTS.md / CLAUDE.md / GEMINI.md
  └── dev/SESSION_HANDOFF.md + SESSION_LOG.md

待處理優先事項（按序）：
1. 用戶確認 Mockup UI 方向後，開發正式 edb-dashboard.html（功能完整版）
2. 開發 edb_scraper.py 後端（ASP.NET POST 抓取 → pdfplumber → gpt-5-nano）
3. 整合測試：circulars.json 與 Dashboard 聯調，按需求文件第八節驗收

關鍵技術規則（必讀，開發前對齊）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
- gpt-5-nano：temperature=1 固定，Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- Dashboard：單檔案 HTML（無建構工具），內嵌 CSS+JS

第一個具體行動：
  在瀏覽器開啟 edb-dashboard-mockup.html，確認 UI 設計方向，
  提供修改意見後即可開始正式 edb-dashboard.html 開發。
```

---

## 2026-03-09（SESSION CLOSE — Claude_20260309_KB02）

1. Agent & Session ID: Claude_20260309_KB02
2. Task summary: 知識庫使用規則澄清 + Session Close
3. Layer classification: Development Governance Layer（規則補充）
4. Source triage: 用戶口頭指示，補充知識庫使用約束條件
5. Files changed:
   - `dev/SESSION_HANDOFF.md`：新增「Knowledge Base Usage Rules」章節（5條強制規則）
   - `dev/SESSION_LOG.md`：本條目（session close 記錄）
6. Key clarifications recorded:
   - **知識庫只在分析通告時使用**（非一般對話）
   - **ROLE_KNOWLEDGE_INDEX 只列 top 5**，並非完整知識庫
   - **查閱方式：Index → Link → Fetch**（動態連結至相關章節，不全文載入）
   - 知識庫是輔助資料，不可因未覆蓋某範疇而拒絕分析
   - `fetch_knowledge.py` 已在 Mac 成功執行（20:48 UTC），9/9 來源成功，知識庫已含官網真實內容
7. Validation: SESSION_HANDOFF.md 規則章節結構正確，Next Session Handoff Prompt v3 已更新

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 知識庫使用邊界不清晰（何時用、如何查閱、覆蓋範圍）
2. Root Cause: 上兩個 session 只建立了文件，未明文定義使用協議
3. Fix: 在 SESSION_HANDOFF.md 新增 Knowledge Base Usage Rules（5條）
4. Verification: 規則已寫入 SSOT（SESSION_HANDOFF.md），下個 session 讀取時自動生效
5. Regression / rule update: 無

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: SESSION_HANDOFF.md Knowledge Base Usage Rules 章節
3. Merged: 知識庫使用規則集中至 SESSION_HANDOFF.md
4. Retired: Next Session Handoff Prompt v1、v2（由 v3 取代，見下方）
5. Why: 減少跨文件查閱，確保下個 agent 只需讀 SESSION_HANDOFF 即可對齊

---

---

## 2026-03-10

1. Agent & Session ID: Claude_20260310_FE01
2. Task summary: 正式版 `edb-dashboard.html` 開發（v0.2.0-frontend），全功能實作
3. Layer classification: Product / System Layer（正式前端開發）
4. Source triage: 需求來源 = `dev/v0.2.0-FRONTEND-SPEC.md`（用戶已確認 SSOT），補充用戶口頭反饋 A1–A10 + 助手提案 B1–B8
5. Files read:
   - `dev/SESSION_HANDOFF.md`
   - `dev/v0.2.0-FRONTEND-SPEC.md`
   - `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`
   - `dev/knowledge/icac_reference.md`
   - `edb-dashboard.html`（QC 驗證時）
6. Files changed:
   - `edb-dashboard.html`（新建，2,292 行）
   - `CHANGELOG.md`（新增 v0.2.0-frontend 記錄）
   - `dev/SESSION_HANDOFF.md`（本 session 記錄更新）
   - `dev/SESSION_LOG.md`（本 session 記錄，本條目）
7. Completed:
   - 用戶 UI 反饋整理：A1–A10（用戶提供）+ B1–B8（助手提案）共 18 項確認
   - `dev/v0.2.0-FRONTEND-SPEC.md` 建立（17 節完整規格，用戶確認為 SSOT）
   - `edb-dashboard.html` 全功能實作：
     * 6 主分頁（通告總覽 / 月曆 / 資源與申請 / 收藏清單 / 供應商 / 設定）
     * 詳情面板 5 個內部分頁（總結 / 行動方案 / 截止日期 / 角色分析 / 版本比較）
     * 4 色調 × 2 主題系統（Spring/Summer/Autumn/Winter × 深色/淺色）
     * localStorage 14 個 key 持久化
     * 角色條件顯示（供應商 Tab 僅在 supplier 角色出現）
     * Grant info 雙類型（💰可申請 vs 📦資源）
     * 截止日期三類型（apply/submission/awareness）
     * 狀態三態循環 + 書籤雙軌（⭐ + 📌）
     * 統計列（角色適配）+ 篩選列（6 維度，可收摺）
     * 月曆（Notion 風格，格內顯示標題）
     * Dev 頁面（?dev=1 或版本號連按 5 次）
     * 鍵盤快捷鍵（1–6 / / / T / Esc / ?）
     * Print 支援（@media print）
     * Mock 數據 4 條（完整 schema）
   - CHANGELOG.md 更新（v0.2.0-frontend 正式記錄）
8. Validation / QC:
   - HTML 語法驗證：0 unclosed tags（python html.parser）
   - 26/26 功能驗證全通過（grep 檢查）
   - 文件大小：2,292 行
9. Pending:
   - 用戶在瀏覽器視覺確認 `edb-dashboard.html`
   - Mac Terminal 執行 `push-to-github.sh`（更新 CHANGELOG 後推送，tag: v0.2.0-frontend）
   - 開發 `edb_scraper.py` 後端管線（v0.3.0-backend）
10. Next priorities:
    - 用戶瀏覽器開啟 `edb-dashboard.html` 目視驗收
    - GitHub 推送 v0.2.0-frontend tag
    - 開發 `edb_scraper.py`（v0.3.0-backend）
11. Risks / blockers:
    - 同前（VM 網絡封鎖，GitHub 推送需 Mac Terminal + 新 PAT）
12. Notes:
    - 本 session 因 context window 限制分為兩段（context compaction 後接續）
    - 大型 HTML 寫入分兩步驟（Write CSS+HTML → Edit JS 替換佔位符）解決 token 限制問題

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 單次 Write 工具輸出過長，HTML 被截斷
2. Root Cause: Output token 限制
3. Fix: 先 Write CSS+HTML（含 JS 佔位符），再 Edit 替換 JS 佔位符為完整 JavaScript
4. Verification: HTML 語法驗證通過，26/26 功能 grep 驗證通過
5. Regression / rule update: 大型單檔案寫入技巧記錄於本條目，可供後續 session 參考

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: `dev/v0.2.0-FRONTEND-SPEC.md` 為前端功能規格 SSOT
3. Merged: 用戶反饋 A1–A10 + 助手提案 B1–B8 統整至 SPEC
4. Retired: edb-dashboard-mockup.html 功能已被 edb-dashboard.html 取代（mockup 保留作參考）
5. Why: 正式版取代 mockup，規格 SSOT 集中管理

---

### Next Session Handoff Prompt — v5（最終版本 ✅，請用此版本）
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.2.0-frontend ✅ 完成，準備進入 v0.3.0-backend 開發

已完成（全部 ✅）：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）✅
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）全文解析 ✅
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行，QC 通過）✅
- 角色知識庫 9 個文件（dev/knowledge/）建立，官網內容已抓取 ✅
- 知識庫使用規則寫入 SESSION_HANDOFF.md ✅
- GitHub 推送完成（tag: v0.1.0-mockup）✅
- 正式 Dashboard（edb-dashboard.html，2292行，QC 26/26 通過）✅ ← NEW
- v0.2.0-FRONTEND-SPEC.md（規格 SSOT）✅ ← NEW

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html           ← 正式版 Dashboard（目視確認後推送 GitHub）
  ├── edb-dashboard-mockup.html   ← 保留作 UI 參考
  ├── fetch_knowledge.py
  ├── push-to-github.sh
  ├── AGENTS.md / CLAUDE.md / GEMINI.md
  ├── README.md / CHANGELOG.md / .gitignore
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      ├── v0.2.0-FRONTEND-SPEC.md     ← 前端規格 SSOT
      └── knowledge/
          ├── ROLE_KNOWLEDGE_INDEX.md
          └── [9 個知識庫文件]

待處理優先事項（按序）：
1. 用戶在瀏覽器開啟 edb-dashboard.html 目視驗收
2. Mac Terminal 執行 push-to-github.sh 推送 v0.2.0-frontend tag
3. 開發 edb_scraper.py 後端（ASP.NET POST 抓取 → pdfplumber → gpt-5-nano，v0.3.0-backend）
4. 整合測試：circulars.json 與 Dashboard 聯調（v1.0.0-release）

關鍵技術規則（必讀）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
- gpt-5-nano：temperature=1 固定，Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- Dashboard：單檔案 HTML（無建構工具），內嵌 CSS+JS
- VM 網絡封鎖 edb.gov.hk + github.com，所有外部操作必須在 Mac Terminal 執行

知識庫使用規則（必須遵守）：
- 只在「分析通告」時使用，不用於一般對話
- ROLE_KNOWLEDGE_INDEX.md 只列每角色 top 5，非完整清單
- 查閱方式：Index → Link → Fetch（只讀相關章節，不全文載入）
- 知識庫是輔助資料，不可因未覆蓋而拒絕分析通告

第一個具體行動：
  在瀏覽器開啟 edb-dashboard.html，確認 UI + 所有功能正常，
  然後在 Mac Terminal 執行 push-to-github.sh 推送 v0.2.0-frontend，
  再開始 edb_scraper.py 後端開發。
```

---

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE01
2. Task summary: v0.2.1-frontend 13 項 UI 修訂 + v0.3.0-backend 後端管線啟動
3. Layer classification: Product / System Layer（UI 修訂 + 後端開發）
4. Source triage: 用戶口頭列舉 13 項修訂；後端規格來自需求文件第五/六節
5. Files read:
   - `dev/SESSION_HANDOFF.md`（v0.2.0-frontend 版本）
   - `CHANGELOG.md`（v0.2.0-frontend 版本）
   - `edb_scraper.py`（新建後驗證）
6. Files changed:
   - `edb-dashboard.html`（更新，2,292→2,453 行，13 項修訂）
   - `edb_scraper.py`（新建，v0.3.0-backend，450+ 行）
   - `requirements.txt`（新建）
   - `CHANGELOG.md`（更新，新增 v0.2.1-frontend 記錄）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - v0.2.1-frontend 13 項 UI 修訂（完整清單見 CHANGELOG.md v0.2.1-frontend 節）：
     * Fix 1：4 個統計 Tag 改為可點擊連結
     * Fix 2：視圖工具列加「卡片」「列表」文字 + 🖨️ 列印按鈕
     * Fix 3：收藏頁指引橫幅 + Tab 徽章
     * Fix 4：月曆顏色邏輯（紅=高影響+必須，藍=一般，綠=截止）+ isAttention()
     * Fix 5：REFERENCE_CIRCULARS 3 條預設常備通告（自動首次釘選）
     * Fix 6：4 色調 × 2 主題 CSS 組合選擇器（surface/border 也變色）
     * Fix 7：數據來源卡片移至 Dev 頁
     * Fix 8：使用指南移至 Dev 頁（標示「開發者」）
     * Fix 9a：快捷鍵 T→D（避免衝突）
     * Fix 9b：Header 角色指示器徽章 + updateRoleIndicator()
     * Fix 10：行動角色名稱改中文 + 當前角色高亮
     * Fix 11：頁腳免責聲明（EDB 數據來源）
     * Fix 12：系統設計者 Leonard Wong
     * Fix 13：供應商頁移除政策指引 chip，加外部連結注釋
   - `edb_scraper.py` v0.3.0-backend 建立（ASP.NET ViewState POST + 位置式表格 + pdfplumber + gpt-5-nano json_schema，temperature=1 固定）
   - `requirements.txt` 建立（requests / beautifulsoup4 / pdfplumber / openai / lxml）
   - `edb_scraper.py` py_compile 語法驗證通過
8. Validation / QC:
   - edb_scraper.py：`python3 -m py_compile` ✅ Syntax OK
   - edb-dashboard.html：2,453 行（+161 行 vs v0.2.0）
   - CHANGELOG.md v0.2.1-frontend 記錄完整
9. Pending:
   - Mac Terminal：`pip install -r requirements.txt`
   - Mac Terminal：`python3 edb_scraper.py --days 7 --dry-run -v`（EDB 網絡測試）
   - Mac Terminal：`push-to-github.sh`（tag: v0.2.1-frontend）
   - 設定 `export OPENAI_API_KEY="sk-..."`
   - 完整後端執行：`python3 edb_scraper.py --days 30 --output ./circulars.json -v`
10. Next priorities:
    - dry-run 測試驗證 EDB ViewState POST 有效
    - 完整 LLM 分析執行，生成真實 circulars.json
    - 整合測試：circulars.json 載入 Dashboard（v1.0.0-release）
11. Risks / blockers:
    - gpt-5-nano temperature=1 固定（不可更改）
    - EDB 網站位置式表格（Col 0=通告號，Col 1=標題，Col 2=日期，Col 3+=PDF）
    - VM 網絡封鎖，所有外部操作需 Mac Terminal
12. Notes:
    - 本 session 因 context compaction 從摘要接續，所有設計決定見上方摘要
    - 大型 HTML 修改分多次 Edit（而非整體重寫）以維持穩定性

### Problem -> Root Cause -> Fix -> Verification
1. Problem: QC「Fix3 instructions visible」字串比對失敗
2. Root Cause: QC 查找字串帶逗號（`'釘選），永久保存'`），HTML 實際無逗號
3. Fix: 確認 HTML 內容正確（無逗號版本），QC 邏輯調整
4. Verification: 目視確認 Fix 3 橫幅文字正確
5. Regression / rule update: QC grep 字串需與實際 HTML 完全一致

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: CHANGELOG.md 記錄 v0.2.1-frontend 修訂；需求文件後端規格保持不變
3. Merged: 13 項修訂統整至 CHANGELOG v0.2.1-frontend
4. Retired: v5 Handoff Prompt（由 v6 取代，見下方）
5. Why: 版本進度更新，後端管線啟動

---

### Next Session Handoff Prompt — v6（已由 v7 取代）
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.2.1-frontend ✅ 完成，v0.3.0-backend 管線已建立，待 Mac Terminal 測試

已完成（全部 ✅）：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）✅
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）全文解析 ✅
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行）✅
- 角色知識庫 9 個文件（dev/knowledge/）+ 官網內容已抓取 ✅
- GitHub 推送（tag: v0.1.0-mockup）✅
- 正式 Dashboard（edb-dashboard.html，v0.2.0，2292行，QC 26/26）✅
- v0.2.1-frontend 13 項 UI 修訂（2453行）✅ ← NEW
- edb_scraper.py 後端管線建立（v0.3.0-backend，450+行，syntax OK）✅ ← NEW
- requirements.txt 更新 ✅ ← NEW

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html           ← 正式版 Dashboard（v0.2.1，2453行）
  ├── edb_scraper.py               ← 後端管線（v0.3.0-backend，待測試）
  ├── fetch_knowledge.py           ← 知識庫抓取工具
  ├── requirements.txt             ← Python 依賴（已更新）
  ├── push-to-github.sh            ← GitHub 推送腳本
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      ├── v0.2.0-FRONTEND-SPEC.md  ← 前端規格 SSOT
      └── knowledge/[9 個知識庫文件]

待處理優先事項（按序，Mac Terminal 執行）：
1. cd ~/path/to/EDB-Circular-AI-analysis-system
2. pip install -r requirements.txt
3. export OPENAI_API_KEY="sk-..."
4. python3 edb_scraper.py --days 7 --output ./circulars.json --dry-run -v  # 測試網絡
5. python3 edb_scraper.py --days 30 --output ./circulars.json -v           # 完整執行
6. bash push-to-github.sh  # 推送 tag v0.2.1-frontend
7. 在瀏覽器開啟 edb-dashboard.html，確認真實 circulars.json 已載入

關鍵技術規則（必讀）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
  表格欄位：Col 0=通告號，Col 1=標題+URL，Col 2=日期，Col 3+=PDF 連結
- gpt-5-nano：temperature=1 固定（不可更改），Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- VM 網絡封鎖 edb.gov.hk + github.com，所有外部操作必須在 Mac Terminal 執行

知識庫使用規則（必須遵守）：
- 只在「分析通告」時使用，不用於一般對話
- ROLE_KNOWLEDGE_INDEX.md 只列每角色 top 5，非完整清單
- 查閱方式：Index → Link → Fetch（只讀相關章節，不全文載入）

第一個具體行動：
  在 Mac Terminal 執行 dry-run 測試，確認 EDB 網站連通 + ViewState POST 有效：
  python3 edb_scraper.py --days 7 --output ./circulars.json --dry-run -v
  若成功：執行完整版 python3 edb_scraper.py --days 30 --output ./circulars.json -v
```

---

### Next Session Handoff Prompt — v5（已由 v7 取代）
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.1.0-mockup ✅ 全數完成，準備進入 v0.2.0-frontend 開發

已完成（v0.1.0-mockup 里程碑，全部 ✅）：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）✅
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）全文解析 ✅
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行，QC 通過）✅
- 角色知識庫 9 個文件（dev/knowledge/）建立，官網內容已抓取（2026-03-09 20:48 UTC）✅
- 知識庫使用規則寫入 SESSION_HANDOFF.md ✅
- GitHub 推送完成（tag: v0.1.0-mockup，repo: Leonard-Wong-Git/EDB-AI-Circular-System）✅

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard-mockup.html   ← 請先在瀏覽器開啟確認 UI 方向
  ├── fetch_knowledge.py
  ├── push-to-github.sh
  ├── AGENTS.md / CLAUDE.md / GEMINI.md
  ├── README.md / CHANGELOG.md / .gitignore
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      └── knowledge/
          ├── ROLE_KNOWLEDGE_INDEX.md     ← 角色→知識文件對照（top 5）
          ├── sch_admin_guide.md          ← 所有角色
          ├── fin_management.md           ← 所有角色
          ├── curriculum_guides.md        ← 所有角色
          ├── sch_activities.md           ← 所有角色
          ├── press_releases.md           ← 所有角色
          ├── kpm.md                      ← 所有角色
          ├── fin_management_supplier.md  ← supplier 專屬
          ├── icac_reference.md           ← supplier 專屬
          └── press_releases_supplier.md  ← supplier 專屬

待處理優先事項（按序）：
1. 用戶確認 Mockup UI 方向後，開發正式 edb-dashboard.html（v0.2.0-frontend）
2. 開發 edb_scraper.py 後端（ASP.NET POST 抓取 → pdfplumber → gpt-5-nano，v0.3.0-backend）
3. 整合測試：circulars.json 與 Dashboard 聯調，按需求文件第八節驗收（v1.0.0-release）

關鍵技術規則（必讀）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
- gpt-5-nano：temperature=1 固定，Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- Dashboard：單檔案 HTML（無建構工具），內嵌 CSS+JS
- VM 網絡封鎖 edb.gov.hk + github.com，所有外部操作必須在 Mac Terminal 執行

知識庫使用規則（必須遵守）：
- 只在「分析通告」時使用，不用於一般對話
- ROLE_KNOWLEDGE_INDEX.md 只列每角色 top 5，非完整清單
- 查閱方式：Index → Link → Fetch（只讀相關章節，不全文載入）
- 知識庫是輔助資料，不可因未覆蓋而拒絕分析通告

第一個具體行動：
  在瀏覽器開啟 edb-dashboard-mockup.html，確認 UI 設計方向，
  提供修改意見後即可開始正式 edb-dashboard.html 開發（v0.2.0-frontend）。
```

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE02
2. Task summary: EDB POST 表單字段診斷 + 修正
3. Layer classification: Product / System Layer（後端調試）
4. Source triage: Mac Terminal 實測輸出（parse_form.py 解析 debug_edb_GET.html），屬實測驅動修正
5. Files read: edb_scraper.py（查閱舊字段）; debug_edb_GET.html（Mac 存檔，parse_form.py 解析）
6. Files changed:
   - `edb_scraper.py`（更新：POST data 字段全部修正）
   - `debug_edb_html.py`（新建→更新：POST 字段同步修正）
   - `parse_form.py`（新建：表單結構解析工具）
   - `dev/SESSION_HANDOFF.md`（更新：Known Risks #4 + Open Priorities）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - Mac Terminal：pip install 成功 ✅
   - dry-run 執行：HTTP 200 但表格找不到（字段全錯）
   - parse_form.py 解析揭示實際字段，完成以下修正：
     * ContentPlaceHolder1 → MainContentPlaceHolder
     * txtFromDate → txtPeriodFrom
     * txtToDate → txtPeriodTo
     * btnSearch → btnSearch2
     * 移除不存在的 ddlYear/ddlMonth
     * 新增 ctl00$currentSection="2" + lbltab_circular="通告"
8. Validation / QC: parse_form.py 輸出確認實際字段；修正後待 Mac Terminal 驗證
9. Pending: python3 debug_edb_html.py（驗證修正）→ dry-run → 完整 LLM 執行
10. Next priorities:
    - ⭐ python3 debug_edb_html.py 確認 POST 找到通告號碼
    - 完整 dry-run → LLM 分析 → circulars.json
    - push-to-github.sh（tag: v0.2.1-frontend）
11. Risks / blockers: _parse_list() 表格格式未知，可能仍需調整；通告號正則待確認

### Problem -> Root Cause -> Fix -> Verification
1. Problem: POST 後找不到通告表格
2. Root Cause: 所有 POST 字段名稱錯誤（假設了錯誤的 ContentPlaceHolder1）
3. Fix: parse_form.py 解析實際 HTML，全部修正至真實字段名稱
4. Verification: 待執行 debug_edb_html.py（下個 session）
5. Regression / rule update: 記錄於 SESSION_HANDOFF Known Risks #4（SSOT）

### Consolidation / Retirement Record
1. SSOT: SESSION_HANDOFF Known Risks #4 = EDB 表單字段唯一正確記錄
2. Retired: 舊 POST data（ContentPlaceHolder1 版本）已替換

---

### Next Session Handoff Prompt — v7（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.2.1-frontend ✅，後端 POST 字段已修正，待 Mac Terminal 驗證

已完成（全部 ✅）：
- 治理框架 ✅ | 需求文件解析 ✅ | Mockup ✅ | 知識庫 ✅
- Dashboard v0.2.1（2453行，13修訂）✅
- edb_scraper.py v0.3.0-backend 建立 + POST 字段修正 ✅
- pip install 成功 ✅

⚠️ EDB 表單字段（已從實測確認，見 SESSION_HANDOFF Known Risks #4）：
  PlaceholderID : MainContentPlaceHolder（非 ContentPlaceHolder1）
  日期字段      : txtPeriodFrom / txtPeriodTo
  搜尋按鈕      : btnSearch2
  必要字段      : ctl00$currentSection="2", lbltab_circular="通告"
  下拉字段      : ddlSchoolType2 + ddlCircularType（無 ddlYear/ddlMonth）

主要檔案：outputs/EDB-Circular-AI-analysis-system/
  edb_scraper.py, debug_edb_html.py, parse_form.py, requirements.txt
  push-to-github.sh, edb-dashboard.html（v0.2.1）

⭐ 立即執行（Mac Terminal）：
  cd "<EDB 項目路徑>"
  python3 debug_edb_html.py
  # 成功標誌：EDB CIRCULAR NUMBERS FOUND 列出通告號碼

確認成功後：
  python3 edb_scraper.py --days 30 --output ./circulars.json --dry-run -v
  export OPENAI_API_KEY="sk-..."
  python3 edb_scraper.py --days 30 --output ./circulars.json -v
  bash push-to-github.sh  # tag: v0.2.1-frontend

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE03
2. Task summary: EDB HTML 結構解析 + _parse_list 完整重寫 + dry-run 通過 ✅
3. Layer classification: Product / System Layer（後端調試 + 驗證）
4. Source triage: Mac Terminal 執行 parse_structure.py + parse_row.py 輸出，屬實測驅動修正
5. Files read: edb_scraper.py（多次）
6. Files changed:
   - `edb_scraper.py`（更新：_parse_list 完整重寫 + _abs_url urljoin + timezone fix）
   - `parse_structure.py`（新建：DOM 結構診斷）
   - `parse_row.py`（新建：完整 row 解析）
   - `dev/SESSION_HANDOFF.md`（更新：Known Risks #5 + Open Priorities + Last Session）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - debug_edb_html.py（修正後）確認 POST 找到 14 條通告號碼 ✅
   - parse_structure.py：確認通告號在 <div class="circulars_result_remark"> 內
   - parse_row.py：確認完整 row 結構（3 cells，PDF 3個連結，無 detail_url，日期格式 "日期DD/MM/YYYY"）
   - _parse_list() 完整重寫（基於實測結構，移除舊假設）
   - _abs_url() 修正為 urljoin（正確處理 ../）
   - datetime.utcnow() → datetime.now(timezone.utc)（消除 DeprecationWarning）
   - **Dry-run 完全通過：**
     * 14 條通告爬取並解析 ✅
     * PDF 下載並文字提取（pdfplumber，最大 7310 chars）✅
     * circulars.json 38.4KB 儲存成功 ✅
     * 零錯誤，只剩 datetime 警告（已修正）
8. Validation / QC:
   - py_compile OK ✅
   - dry-run: 14/14 circulars parsed, PDFs extracted, JSON saved ✅
9. Pending: export OPENAI_API_KEY → 完整 LLM 執行
10. Next priorities:
    - ⭐ python3 edb_scraper.py --days 30 --output ./circulars.json -v（真實 LLM）
    - 瀏覽器確認 circulars.json 載入 Dashboard
    - push-to-github.sh（tag: v0.3.0-backend）
11. Risks / blockers:
    - LLM 分析 14條 × ~30s = 約 7分鐘，正常
    - OPENAI_API_KEY 必須在 Mac Terminal export

### Problem -> Root Cause -> Fix -> Verification
1. Problem: _parse_list() 找不到表格（表格存在但結構與假設完全不符）
2. Root Cause: EDB 用非標準結構（td.circularResultRow + div.circulars_result_remark），非簡單表格列
3. Fix: 完整重寫 _parse_list()，基於 parse_row.py 確認的真實結構
4. Verification: dry-run 通過（14 circulars parsed）✅
5. Regression / rule update: 記錄於 SESSION_HANDOFF Known Risks #5（SSOT）

### Consolidation / Retirement Record
1. Duplicate / drift: 舊 _parse_list 假設（col0=通告號，col1=標題，col2=日期）已替換
2. SSOT: SESSION_HANDOFF Known Risks #5 = EDB HTML 通告結構唯一正確記錄
3. Merged: HTML 結構知識集中於 Known Risks
4. Retired: 舊 _parse_list 邏輯（基於不存在的表格結構）
5. Why: 防止未來 session 重複分析相同結構

---

### Next Session Handoff Prompt — v8（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：Dry-run ✅ 通過，準備執行完整 LLM 分析

已完成（全部 ✅）：
- Dashboard v0.2.1（2453行）✅ | edb_scraper.py v0.3.0 ✅
- pip install ✅ | EDB POST 字段修正 ✅ | HTML 解析修正 ✅
- Dry-run: 14 circulars + PDF text + 38.4KB JSON ✅

⭐ 立即執行（Mac Terminal）：
  export OPENAI_API_KEY="sk-..."
  python3 edb_scraper.py --days 30 --output ./circulars.json -v
  # 預計時間：約 7-10 分鐘（14條 × LLM 分析）

完成後：
  在瀏覽器開啟 edb-dashboard.html，確認真實 circulars.json 顯示正常
  bash push-to-github.sh  # tag: v0.3.0-backend

關鍵規則：gpt-5-nano temperature=1 固定（不可更改）
EDB HTML 結構：見 SESSION_HANDOFF Known Risks #5
```
