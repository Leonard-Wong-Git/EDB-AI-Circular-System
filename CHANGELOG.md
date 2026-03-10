# Changelog

本文件記錄 EDB 通告智能分析系統的所有版本變更。
格式參照 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，版本號遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

---

## [Unreleased]

### Planned — v1.0.0-release
- 整合測試：真實 circulars.json 與 Dashboard 聯調驗收
- 更多天數通告爬取（--days 90 / 365）
- 定期自動更新（cron / 排程）
- Mobile 優化（A6 批次）

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
