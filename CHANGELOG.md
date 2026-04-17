# Changelog

本文件記錄 EDB 通告智能分析系統的所有版本變更。
格式參照 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，版本號遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

---

## [v3.0.46] — 2026-04-17 ✅ 正式完成版

### 里程碑：系統功能全面完成，QC 黃金標準制定

#### Added
- **QC_MASTER.md**：制定正式完成版 QC 規範，12 類 (A–L) 涵蓋開頁、資料載入、篩選欄、詳情面板、月曆、資源申請、收藏、供應商、設定、快捷鍵、CI/CD、後端 scraper，共 70+ 測試項目
- **Landing page gate**：直接訪問 `edb-dashboard.html` 自動跳回 `index.html` 開頁（sessionStorage 機制）；同一瀏覽器 session 內不重複跳轉

#### Changed
- **類型篩選**：新增「通告 (EDBC)」chip，支援篩選純 EDBC 系列通告
- **主題篩選**：新增「安全管理」(safety, 44 條) 及「採購」(procurement, 43 條) 兩個 chip
- **系統功能說明**：重寫為 6 個精簡區塊（含 EDBC 三類說明；AI 模型更正為 gpt-4.1-nano）
- **免責聲明版本號**：修正 v2.0.0 → v3.0.46

#### Removed
- **開發者工具**：從設定頁移除，不再顯示用戶入口

#### Technical
- README.md 版本更新至 v3.0.46；狀態標示「正式完成版」
- CHANGELOG.md 補全 v3.0.44–v3.0.46 完整記錄

---

## [v3.0.45] — 2026-04-17

### 里程碑：知識庫訊號暗盤偵測機制

#### Added
- **知識訊號偵測**（`_detect_knowledge_signal()`）：分析每份通告後靜默偵測是否為政策/框架文件（strong signal：標題含「架構/課程框架/指引（YYYY）」+ curriculum 主題）
- **`_update_policy_signals()`**：去重後寫入 `dev/knowledge/policy_signals.json`，管理員查閱 `pending_review` 條目後手動更新知識庫
- 新增 `_KS_TITLE_STRONG`、`_KS_POLICY_TAGS`、`_KS_SIGNALS_PATH` 常數

#### Technical
- scraper v3.0.43 → v3.0.45
- policy_signals.json 首次生成：待 school-year workflow 後生成（預計 3 份 strong signal）

---

## [v3.0.44] — 2026-04-17

### 里程碑：EDBC 系列支援 + 開頁 index.html

#### Fixed
- **Scraper EDBC 系列漏掉**：`_parse_list()` regex `r"EDB(?:CM|CL)\d{3}/\d{4}"` → `r"EDBC(?:M|L)?\d{3}/\d{4}"`；circ_type 邏輯由 2-way 改為 3-way（EDBCM / EDBCL / EDBC）
- EDBC003/2026、EDBC005/2026 等純 EDBC 系列通告可正確抓取和分析

#### Added
- **開頁 index.html**：Canvas 粒子動畫（游標互動 + 連線效果）、系統名稱、AI 起草功能簡介、3 個功能亮點、進入按鈕（淡出動畫跳轉）；取代原本 redirect
- 系統完成狀態確認（core features done，進入監測維護模式）

#### Technical
- scraper v3.0.43 → v3.0.44；dashboard v3.0.43 → v3.0.44

---

## [v2.1.0] — 2026-03-22

### 里程碑：Dashboard 首頁分離 + 搜尋獨立 + AI 重構 + Scraper Merge 修復 ✅

#### Added
- **🏠 首頁 tab**（新增第一個 tab）：最新 6 條通告 + 需關注項 + 即將截止一覽
- **搜尋結果獨立 panel**：搜尋不再篩選通告總覽，改為 dropdown overlay 顯示結果
- **供應商法規參考連結**：廉政公署學校防貪指引、EDB 學校財務管理、資助學校資助則例
- **供應商圖表佔位**：supplierChartContent（待 scraper 新增數據字段後啟用）

#### Changed
- **Stats buttons toggle 行為**：本月通告/需關注/即將截止 再按一次返回首頁（S._homeFilter 狀態）
- **通告總覽重置**：每次切換至通告總覽 tab 自動 resetOverviewFilters()，顯示全部通告
- **LLM → AI 全面改名**：所有用戶可見文字 LLM 改為 AI
- **詳情面板重構**：PDF 連結置頂（dp-pdf-section），AI 分析/角色/比較三分頁
- **月曆 EDBC 格式**：通告標題由數字改為 EDBC046 格式
- **系統說明精簡**：精簡為 7 行一句式描述
- **edb_scraper.py PHASE 4 Merge 修復**：days-3 模式改為 load 現有 circulars.json 後 merge，不再覆蓋全量數據

#### Fixed
- 移除預設釘選通告（「三個常備參考通告已預設釘選」→「按 📌 釘選長期適用的通告」）
- dpBookmarkBtn null-check（避免 JavaScript 錯誤）
- brand div 多餘引號 HTML 瑕疵

#### Technical
- edb-dashboard.html：2,766 → 3,047 行
- 24/24 structural QC checks 通過；Node.js JS syntax check 通過
- Scraper merge：days-3 run 記錄 `new/updated/kept` 統計；date_from/date_to 反映實際數據範圍
- GitHub Pages v2.1.0 已部署（commit `5b45df0`）

---

## [v2.0.0] — 2026-03-16

### 里程碑：Dashboard 全面改版（37 項改進）+ 後端 R1-v2 角色精確度 ✅

#### Added / Changed（節錄）
- 版本管理系統（VERSION 常數、版本號連按 5 次）
- 4 色調 × 深淺主題系統重構
- 通告號格式改為 EDBCM029/2026
- PDF 連結 buildPdfLinks() helper
- K1 知識注入 + R1-v2 角色精確度（few-shot + postprocess filter）
- school-year workflow 支援（GitHub Actions）
- circulars.json 涵蓋整個學年

---

## [v1.1.1] — 2026-03-14

### 里程碑：PDF timeout 徹底修復 + 版本標籤同步 ✅

#### Fixed
- `edb_scraper.py`：`proc.terminate()` (SIGTERM) → `proc.kill()` (SIGKILL)
  - SIGTERM 被 pdfminer C 擴展忽略（RE01–RE05 五次嘗試均失敗）
  - SIGKILL 由 OS kernel 直接強殺，C 擴展無法攔截
  - GitHub Actions workflow 由卡死 30–60+ 分鐘 → **33 秒完成** ✅
- `edb_scraper.py`：`proc.join()` → `proc.join(2)` 加 2 秒回收安全邊際
- `edb_scraper.py`：pdfminer 所有 sub-logger 設定 ERROR 級別（雙重：worker 子程序 + main process）
  - 修復前：107,000+ 行 DEBUG flood 導致 Actions runner 日誌爆炸
- `edb-dashboard.html`：版本標籤 v0.2.0 → v1.1.0（5 處全部同步）

#### Verified
- GitHub Actions `days-3` workflow 實測：33 秒完成 ✅
- GitHub Pages 顯示 v1.1.0 ✅
- Python `ast.parse` 語法驗證通過 ✅

#### Process Rule Added
- 每次功能 push 後必須同步更新 edb-dashboard.html 的 5 處版本標籤（見 SESSION_HANDOFF.md）

---

## [v1.1.0] — 2026-03-11

### 里程碑：8 項 Dashboard 新功能上線 ✅

#### Added
- **F1 排序持久化**：排序狀態存入 localStorage，重開頁面保留上次排序
- **F2 時段自動主題**：07:00–18:00 自動淺色；其餘時段深色；每 60 秒重評
- **C1 狀態互通**：多處狀態按鈕即時同步（`syncStatusBtns`）；書籤 badge 即時更新
- **C2 資源狀態有意義**：資源申請狀態（申請中/已申請/已截止）驅動 row 背景色
- **B5 CSV 增強**：匯出新增「行動數」+「AI 摘要前 200 字」欄位
- **B6 格式化列印**：新視窗開啟結構化 HTML 報告，含列印/關閉按鈕
- **B7 .ics 日曆匯出**：iCalendar 格式，含所有截止日期；工具列新增 📅 日曆按鈕
- **B8 多選批量匯出**：浮動批量操作列；卡片選中框；工具列新增 ☑️ 多選按鈕

#### Verified
- HTML 語法驗證通過（html.parser，標籤平衡）✅
- 11 個新函數 grep 確認存在 ✅
- edb-dashboard.html：2,453 → 2,796 行 ✅

---

## [v1.0.1-hosting] — 2026-03-10

### 里程碑：GitHub Pages 公開部署配置 ✅

#### Added
- `.github/workflows/update-circulars.yml` — GitHub Actions 自動更新工作流程
  - 定時：每天 HKT 07:00 自動執行（cron `0 23 * * *`）
  - 手動：支援 workflow_dispatch，可選 school-year / days-14 / days-30 / days-365
  - 自動 commit 更新後的 circulars.json 並部署至 GitHub Pages
  - OPENAI_API_KEY 透過 GitHub Secrets 安全注入（不暴露於前端）
- `index.html` — GitHub Pages 根 URL 自動跳轉至 edb-dashboard.html
- `.gitignore` 更新：
  - 移除 `circulars.json` 排除規則（現需 track 以供 Pages 服務）
  - 新增 `.edb_cache/` 排除（PDF 快取，可重新生成，不納入版本控制）
  - 新增 `debug_edb_*.html` 排除（本地診斷文件）

#### Deployment
- 公開 URL：`https://leonard-wong-git.github.io/EDB-AI-Circular-System/`
- 設定步驟：見下方 Hosting Setup 章節（README.md 已更新）
- 所需 GitHub Secret：`OPENAI_API_KEY`

---

## [v1.0.0-release] — 2026-03-10

### 里程碑：前後端整合測試通過 + 學年模式支援 ✅

#### Added
- `edb_scraper.py`：新增 `--school-year` 旗標 — 自動計算本學年9月1日為起始日，抓取本學年全部通告
  - 香港學年定義：9月1日起。若當前日期 < 9月1日，則使用上一年9月1日
  - 例：2026-03-10 → school-year starts 2025-09-01
  - 與 `--days` 互斥，`--school-year` 優先
- `edb_scraper.py`：新增 `school_year_start()` helper 函數
- `edb_scraper.py`：`get_circular_list()` 新增 `date_from` 參數（DD/MM/YYYY，override --days）
- `edb_scraper.py`：circulars.json 輸出新增 `range`、`date_from`、`date_to` 欄位（保留 `days` 向後兼容）
- `--days 365` 已全面支援

#### Fixed
- `edb_scraper.py` `_parse_list()`：修正 title 污染問題 — EDB 頁面的「摘要：」文字段落被誤抓入 title，現以 `re.sub(r"\s*摘要[：:].*$", "", title)` 截斷
- `edb-dashboard.html` REFERENCE_CIRCULARS：修正 ID 碰撞 — 舊 ids 10/11/12 與真實數據重疊，改為 9001/9002/9003

#### Verified
- `school_year_start()` 4 個邊界條件測試通過（學年中、9/1、8/31、10/1）✅
- `py_compile` 語法驗證通過 ✅
- Dashboard 載入真實 circulars.json：14 條通告正確顯示 ✅
- REFERENCE_CIRCULARS 正確釘選，不與真實數據衝突 ✅
- Title 欄位顯示純淨通告標題，無摘要文字污染 ✅

---

## [v0.3.0-backend] — 2026-03-10

### 里程碑：後端管線完成 + 真實數據 Dashboard 驗證 ✅

#### Added
- `edb_scraper.py` — 完整後端管線（v0.3.0，450+ 行）
  - EDB ASP.NET WebForms POST 抓取（ViewState + 實測字段名稱）
  - pdfplumber PDF 全文提取（C.pdf 繁中優先，上限 8,000 chars）
  - gpt-5-nano LLM 分析（json_schema Structured Output，temperature=1 固定）
  - 增量模式（--llm-only 跳過已分析通告）
  - PDF 快取（.edb_cache/）
  - CLI：--days / --output / --llm-only / --model / --dry-run / -v
- `requirements.txt` — Python 依賴（requests / beautifulsoup4 / pdfplumber / openai / lxml）
- `test_llm.py` — LLM API 診斷工具（3 階段測試）
- `debug_edb_html.py` — EDB 網站 POST 診斷工具
- `parse_form.py` — ASP.NET 表單結構解析工具
- `parse_structure.py` — 通告 DOM 結構分析工具
- `parse_row.py` — 完整 row 結構解析工具
- `dev/tools/` — 診斷工具資料夾（保留備用）

#### Fixed（後端調試過程）
- EDB POST 表單字段全部修正（ContentPlaceHolder1 → MainContentPlaceHolder，日期/按鈕字段名稱）
- `_parse_list()` 完整重寫（按真實 HTML 結構：td.circularResultRow + div.circulars_result_remark）
- `_abs_url()` 改用 urljoin 正確解析 `../` 相對路徑
- `max_tokens` → `max_completion_tokens`（gpt-5-nano 推理模型要求）
- `"system"` role → `"developer"` role（gpt-5-nano 推理模型要求）
- `max_completion_tokens` 4096 → 16000（推理 tokens 消耗大）
- `datetime.utcnow()` → `datetime.now(timezone.utc)`（消除 DeprecationWarning）

#### Verified（實測通過）
- Dry-run：14 條真實 EDB 通告（2026-02 至 2026-03）+ PDF 提取 ✅
- 完整 LLM 分析：EDBCM030/2026 high/721chars，EDBCM026/2026 mid/462chars ✅
- Dashboard 真實數據整合：EDBCM030（HK$800,000 今天截止）正確顯示 ✅
- GitHub：tag v0.3.0-backend 推送成功（52 objects，11.35 MiB）✅

#### Technical
- gpt-5-nano 已確認為推理模型（temperature=1, developer role, max_completion_tokens=16000）
- EDB HTML 結構：3 cells per row，無 detail_url，PDF C/E/S 三語

---

## [v0.2.1-frontend] — 2026-03-10

### 里程碑：Dashboard UI 修訂（13 項跟進）

#### Fixed / Improved
- 統計列 4 個 Tag 改為可點擊連結（本月通告→篩選、需關注→filter、即將截止→截止列、已收藏→收藏頁）
- Dashboard 視圖工具列加上「卡片」「列表」文字標籤，新增「🖨️ 列印」按鈕
- 收藏頁加說明橫幅及清晰指引，Tab 顯示釘選數量徽章
- 月曆顏色邏輯修正：🔴 紅=高影響+必須 / 📋 藍=一般通告 / ⏰ 綠=一般截止，圖例更新
- 收藏頁新增 3 條預設常備通告（EDBCM004/2013 財務管理、EDBCM019/2004 學校管治、EDBCM029/2012 防止性騷擾）
- 4 個色調配搭顯著增強：Spring=紫紅/青綠、Autumn=深橙/琥珀、Winter=靛藍/天藍；深/淺主題加色調表面染色
- 數據來源卡片移至 Dev 頁，Settings 只保留用戶設定
- 使用指南移至 Dev 頁（標示「開發者專用」）
- 主題快捷鍵由 T 改為 D（避免衝突）；Header 新增角色指示器徽章
- 通告行動欄位顯示中文角色名稱（原為 coding 名稱），目前角色高亮顯示
- 新增頁腳免責聲明：資料來源香港教育局，一切以官方公告為準
- 新增系統設計者署名：Leonard Wong
- 供應商頁移除「政策指引」統計，加入外部連結注釋（廉政公署、教育局官網）

#### Technical
- HTML 語法驗證通過（0 unclosed tags），2,453 行
- REFERENCE_CIRCULARS 預設常備通告內嵌於前端，首次開啟自動釘選

---

## [v0.2.0-frontend] — 2026-03-10

### 里程碑：正式版 Dashboard 前端完成

#### Added
- **正式版 Dashboard** (`edb-dashboard.html`, 2,292 行)
  - **6 主分頁**：📊 通告總覽 / 📅 月曆 / 📁 資源與申請 / ⭐ 收藏清單 / 🏢 供應商 / ⚙️ 設定
  - **詳情面板**（右側滑入，5 個內部分頁）：總結 / 行動方案 / 截止日期 / 角色分析 / 版本比較
  - **角色系統**（6 個角色，localStorage 保存）：校長 / 副校長 / 科主任 / 教師 / 行政主任 / 供應商
  - **供應商 Tab 條件顯示**：選供應商角色才出現，自動切換
  - **4 色調主題系統**（Spring / Summer / Autumn / Winter）× 2 主題（深色/淺色），CSS 自訂屬性
  - **3 種佈局**（compact / standard / spacious）+ 字體大小（12–18px）
  - **localStorage 持久化**（14 個 key）：角色 / 主題 / 色調 / 佈局 / 字體 / 語言 / 視圖模式 / 書籤 / 常備通告 / 狀態 / 申請狀態 / 提醒天數 / 顯示已完成 / 顯示已過期
  - **Grant Info 雙類型**：💰 可申請（直接撥款，計入統計）vs 📦 資源（政府提供，估算值）
  - **截止日期三類型**：`apply_deadline` / `submission_deadline` / `awareness_deadline`，顏色區分
  - **狀態三態循環**：未讀 → 已讀 → ✅ 已跟進（per circular，localStorage 保存）
  - **書籤雙軌**：⭐ 一般收藏 + 📌 常備參考通告（分開顯示）
  - **統計列（Stats Bar）**：school 角色顯示通告總數/需關注/申請截止；supplier 角色顯示可申請總金額
  - **篩選列（6 維度）**：類型 / 學校類別 / 主題 / 影響程度 / 行動要求 / 年份，可收摺
  - **月曆（Notion 風格）**：桌面版在格內顯示通告標題；支援排序/篩選
  - **需關注區塊**：impact=high 或 urgency=mandatory 的通告置頂顯示
  - **Dev 頁面**：URL `?dev=1` 或版本號連按 5 次觸發；顯示技術設定
  - **鍵盤快捷鍵**：1–6（切換角色）/ /（搜尋）/ T（切換主題）/ Esc（關閉面板）/ ?（說明）
  - **Print 支援**：`@media print` 隱藏所有 UI，僅印出詳情面板內容
  - **語言切換**：zh/en，data-zh/data-en 屬性
  - **文件包下載**：ZIP（摘要PDF + ics + JSON）按鈕（前端示意）
  - **Mock 數據**：4 條完整格式通告（含 grant_info、deadline type、diff）

#### Technical Notes
- 前端：純 HTML/CSS/JS 單頁應用，無外部框架，SheetJS CDN 僅供 Excel 匯出
- 數據：`fetch('./circulars.json')` → fallback to MOCK（離線可用）
- 主題：CSS 自訂屬性，`[data-theme]` + `[data-palette]` 雙層覆蓋
- QC：HTML 語法驗證通過（0 unclosed tags），26/26 功能驗證全通過
- 規格 SSOT：`dev/v0.2.0-FRONTEND-SPEC.md`

#### Source
- 規格文件：`dev/v0.2.0-FRONTEND-SPEC.md`（2026-03-10，用戶已確認）
- AI Agent：Claude (Claude_20260310_FE01)

---

## [v0.1.0-mockup] — 2026-03-09

### 里程碑：UI Mockup 完成，治理框架建立

#### Added
- **治理框架**
  - `AGENTS.md` — AI Agent 多 session 協作治理規則（完整版）
  - `CLAUDE.md` — Claude Code 自動讀取橋接（`@AGENTS.md`）
  - `GEMINI.md` — Gemini CLI 自動讀取橋接（`@./AGENTS.md`）
  - `dev/SESSION_HANDOFF.md` — 會話接力文件（初始化）
  - `dev/SESSION_LOG.md` — 會話記錄（初始化）

- **互動式 UI Mockup** (`edb-dashboard-mockup.html`, 1,452 行)
  - 4 個主分頁：📊 通告總覽 / 📅 月曆 / 🏢 供應商 / ⚙️ 設定
  - 詳情面板（從右側滑入，z-index: 100）：
    - 📝 總結（LLM 摘要 + 官方摘要 + 合規/緊迫/範圍標籤）
    - 📋 行動方案（structured_actions，含角色/截止日）
    - ⏰ 截止日期（structured_deadlines 表格）
    - 👥 角色分析（6 角色可展開卡片，key_points + actions）
    - 🔄 版本比較（changes 列表 + 遷移計劃）
  - 全局 Header：品牌 / 角色選擇器（6 角色）/ 搜尋框 + 即時建議下拉 / 同步 / Excel / PDF
  - 截止倒數列（顯示最近 4 個截止項目，紅/黃/綠天數標記）
  - 篩選列（時間 / 影響程度 / 合規類型）
  - 月曆視圖（藍點=發佈日，紅點=截止日，點擊查看事件）
  - 主題系統（深色 #0f172a / 淺色 #f8fafc / 自動）
  - 字體大小滑桿（12px–18px）
  - Mock 數據：4 條完整格式通告（含 llm 欄位、role_relevance、diff）

- **文件**
  - `README.md` — 完整項目說明、架構、CLI 參數、Roadmap
  - `CHANGELOG.md` — 本文件
  - `.gitignore` — Python/Node/macOS 標準排除規則

#### Technical Notes
- 前端：純 HTML/CSS/JS 單頁應用，無外部框架依賴
- 主題：CSS 自訂屬性（`[data-theme="dark/light"]`）
- Mock 數據：符合需求文件 v2.0 `circulars.json` schema
- QC：HTML 語法驗證通過（0 unclosed tags），20/20 UI 組件驗證通過

#### Source
- 需求文件：`EDB-項目需求及規則總覽.docx` v2.0（2026-03-09）
- AI Agent：Claude (Claude_20260309_1943)

---

## 版本命名規則

| 版本 | 里程碑 | 說明 |
|------|--------|------|
| `v0.1.x-mockup` | UI Mockup | 互動式視覺原型，不含真實數據 |
| `v0.2.x-frontend` | 正式前端 | 連接真實 circulars.json |
| `v0.3.x-backend` | 後端管線 | Python 爬蟲 + LLM 分析 |
| `v1.0.0-release` | 正式發布 | 前後端聯調完成，驗收通過 |
| `v1.x.x` | 維護版本 | Bug fix / 功能增強 |
