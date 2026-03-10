# 📋 EDB 通告智能分析系統
### EDB Circular AI Analysis System

> **版本 / Version:** v0.1.0-mockup — 2026-03-09
> **狀態 / Status:** 🟡 Mockup 階段（正式開發中）

---

## 📖 項目簡介

本系統旨在自動抓取香港教育局（EDB）通告，利用 OpenAI gpt-5-nano 模型進行智能分析，並以互動式 Dashboard 呈現，幫助學校行政人員、教師及供應商快速掌握通告要點、截止日期及行動方案。

This system automatically scrapes Hong Kong Education Bureau (EDB) circulars, performs AI analysis using OpenAI's gpt-5-nano model, and presents results in an interactive dashboard — helping school administrators, teachers, and vendors quickly grasp key points, deadlines, and action items.

---

## ✨ 核心功能

| 功能 | 狀態 | 說明 |
|------|------|------|
| 🤖 LLM 智能分析 | ✅ 規劃完成 | gpt-5-nano 多角色分析，400-600字摘要 |
| 📊 Dashboard 總覽 | 🟡 Mockup | 統計卡片、截止倒數、篩選列表 |
| 👥 六角色分析 | 🟡 Mockup | 校長/副校長/科主任/教師/行政/供應商 |
| 📅 月曆視圖 | 🟡 Mockup | 藍/紅點標記發佈與截止日期 |
| 🏢 供應商分頁 | 🟡 Mockup | 供應商相關通告篩選 |
| 🔄 版本比較 | 🟡 Mockup | 通告更新差異分析 |
| 🐍 後端爬蟲 | ⏳ 待開發 | ASP.NET WebForms POST 抓取 |
| 📄 PDF 解析 | ⏳ 待開發 | pdfplumber 全文提取 |

---

## 🏗️ 系統架構

```
EDB 網站 (ASP.NET WebForms)
    │  POST + ViewState
    ▼
edb_scraper.py              ← Python 後端管線
    ├── HTML 抓取（位置式解析）
    ├── PDF 下載（pdfplumber）
    ├── LLM 分析（gpt-5-nano, json_schema）
    └── circulars.json 輸出
         │
         ▼
edb-dashboard.html          ← 單頁前端應用
    ├── 📊 通告總覽
    ├── 📅 月曆視圖
    ├── 🏢 供應商分頁
    ├── ⚙️ 設定頁
    └── 詳情面板（5個內部分頁）
```

---

## 📁 專案結構

```
EDB-AI-Circular-System/
├── README.md                       ← 本文件
├── CHANGELOG.md                    ← 版本變更記錄
├── AGENTS.md                       ← AI Agent 治理規則（核心）
├── CLAUDE.md                       ← Claude Code 自動讀取橋接
├── GEMINI.md                       ← Gemini CLI 自動讀取橋接
│
├── edb-dashboard-mockup.html       ← ✅ v0.1.0 互動式 UI Mockup
├── edb-dashboard.html              ← ⏳ 正式版前端（待開發）
├── edb_scraper.py                  ← ⏳ 後端爬蟲管線（待開發）
├── start.sh                        ← ⏳ 一鍵啟動腳本（待開發）
│
├── circulars.json                  ← 爬蟲輸出（運行後生成，不納入版控）
│
└── dev/
    ├── SESSION_HANDOFF.md          ← AI Agent 會話接力文件
    ├── SESSION_LOG.md              ← AI Agent 會話記錄
    └── PROJECT_MASTER_SPEC.md      ← ⏳ 完整技術規格（待建立）
```

---

## 🚀 快速開始

### 前置要求

```bash
# Python 3.9+
python3 --version

# 建立虛擬環境
cd ~/Downloads/EDB-AI-Circular-System
python3 -m venv venv
source venv/bin/activate

# 安裝依賴（待開發完成後更新）
pip install requests beautifulsoup4 pdfplumber openai
```

### 設定 API Key

```bash
export OPENAI_API_KEY="sk-..."
```

### 執行爬蟲（後端）

```bash
# 完整執行（抓取 + PDF + LLM 分析）
python3 edb_scraper.py --days 30 --output ./circulars.json -v

# 快速測試（跳過 LLM）
python3 edb_scraper.py --days 90 --skip-llm --output ./circulars.json

# 僅重跑 LLM 分析
python3 edb_scraper.py --llm-only --output ./circulars.json
```

### 啟動 Dashboard（前端）

```bash
python3 -m http.server 8080
# 開啟瀏覽器：http://localhost:8080/edb-dashboard.html
```

> ⚠️ `circulars.json` 必須與 `edb-dashboard.html` 在同一目錄

---

## 🔧 CLI 參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--days N` | 90 | 抓取最近 N 天 |
| `--from / --to` | 無 | 自訂日期範圍（YYYY-MM-DD） |
| `--output / -o` | `./edb_data/circulars.json` | 輸出路徑 |
| `--data-dir` | `./edb_data` | PDF 存放目錄 |
| `--llm-only` | false | 僅重跑 LLM（必須搭配 `--output`） |
| `--skip-llm` | false | 跳過 LLM 分析 |
| `--verbose / -v` | false | 詳細日誌 |

---

## 🤖 LLM 規格

| 項目 | 規格 |
|------|------|
| 模型 | `gpt-5-nano`（固定） |
| Temperature | `1`（固定，其他值會報 400 錯誤） |
| Context Window | 400K tokens |
| Structured Output | `json_schema`（非 `json_object`） |
| 費用估算（40條） | ~$0.60–1.10 USD |

---

## 👥 六大分析角色

| 角色 Key | 中文 | 關注範圍 |
|----------|------|----------|
| `principal` | 校長 | 全校決策、資源分配、政策回應 |
| `vice_principal` | 副校長 | 日常營運監督、政策落實 |
| `department_head` | 科主任 | 科組落實、課程調整 |
| `teacher` | 教師 | 課堂影響、學生指導 |
| `eo_admin` | 行政主任 | 表格填報、截止追蹤 |
| `supplier` | 供應商 | 招標機會、規格變更 |

---

## ⚠️ 已知禁止做法

| ❌ 錯誤做法 | ✅ 正確做法 |
|------------|------------|
| EDB 網站用 GET 帶參數 | 必須用 POST + ViewState |
| CSS Class 選擇器解析 HTML | 位置式解析（`td[0]`, `td[1]`...） |
| gpt-5-nano 設 temperature ≠ 1 | 固定使用 temperature = 1 |
| `--llm-only` 不帶 `--output` | 必須加 `--output ./circulars.json` |
| Structured Output 用 `json_object` | 必須用 `json_schema` |

---

## 📊 成本估算

| 操作 | 時間 | 費用 |
|------|------|------|
| 抓取 HTML | ~5 秒 | 免費 |
| 下載 PDF（40條） | ~2 分鐘 | 免費 |
| LLM 分析（40條） | ~15-20 分鐘 | ~$0.50–1.00 USD |
| 版本比較 | ~1-2 分鐘 | ~$0.05–0.10 USD |
| **總計** | **~20 分鐘** | **~$0.60–1.10 USD** |

---

## 🗺️ Roadmap

### v0.1.0-mockup ✅（當前版本）
- [x] 項目治理框架（AGENTS.md）
- [x] 需求文件解析
- [x] 互動式 UI Mockup（edb-dashboard-mockup.html）
  - [x] 4 主分頁（總覽/月曆/供應商/設定）
  - [x] 詳情面板（5 個內部分頁）
  - [x] 深色/淺色主題
  - [x] 搜尋建議

### v0.2.0-frontend（下一里程碑）
- [ ] 正式版 `edb-dashboard.html`（功能完整，接 circulars.json）
- [ ] 角色篩選實作
- [ ] Excel / PDF 匯出功能
- [ ] localStorage 偏好設定保存

### v0.3.0-backend
- [ ] `edb_scraper.py` 後端管線
- [ ] ASP.NET WebForms POST 抓取
- [ ] pdfplumber PDF 解析
- [ ] gpt-5-nano LLM 分析整合

### v1.0.0-release
- [ ] 前後端完整聯調
- [ ] 驗收標準全部通過（需求文件第八節）
- [ ] `start.sh` 一鍵啟動
- [ ] 文件完善

---

## 🤝 AI Agent 協作

本項目採用 **Sustainable Session Governance** 模式，支援多 AI Agent 跨 session 協作：

- **新 session 啟動：** 告知 Agent `Follow AGENTS.md`
- **讀取順序：** `dev/SESSION_HANDOFF.md` → `dev/SESSION_LOG.md` → `dev/PROJECT_MASTER_SPEC.md`
- **支援 Agent：** Claude (via CLAUDE.md), Gemini (via GEMINI.md), Codex (via AGENTS.md)

詳見 [AGENTS.md](./AGENTS.md)

---

## 📝 License

Private project — Leonard Wong (leonard.ai.wong@gmail.com)

---

## 🔗 相關連結

- EDB 通告來源：https://applications.edb.gov.hk/circular/circular.aspx?langno=2
- OpenAI API：https://platform.openai.com/docs
