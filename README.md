# 📋 EDB 通告智能分析系統
### EDB Circular AI Analysis System

> **版本 / Version:** v2.1.0 — 2026-03-22
> **狀態 / Status:** 🟢 正式版，線上運行中
> **Demo:** https://leonard-wong-git.github.io/EDB-AI-Circular-System/

---

## 📖 項目簡介

本系統自動抓取香港教育局（EDB）通告，利用 OpenAI gpt-5-nano 模型進行 AI 分析，並以互動式 Dashboard 呈現。幫助學校行政人員、教師及供應商快速掌握通告要點、截止日期及行動方案。

This system automatically scrapes Hong Kong Education Bureau (EDB) circulars, performs AI analysis using OpenAI gpt-5-nano, and presents results in an interactive dashboard — helping school administrators, teachers, and vendors quickly grasp key points, deadlines, and action items.

---

## ✨ 核心功能

| 功能 | 狀態 | 說明 |
|------|------|------|
| 🏠 首頁 | ✅ v2.1.0 | 最新通告、需關注項、即將截止一覽 |
| 📊 通告總覽 | ✅ 正式版 | 統計卡片、篩選、搜尋、卡片/列表切換 |
| 🤖 AI 智能分析 | ✅ 正式版 | gpt-5-nano 多角色分析，含摘要/行動/截止；行動清單現以較簡潔的 inline 角色標籤顯示主動作，寬屏 3 列設定在 768–1023px 也會正確生效 |
| 📄 官方原文整理版 | ✅ v3.0.12 | 清洗斷行、空白與段落，提升官方摘錄可讀性 |
| 🧠 知識校正層 | ✅ v3.0.37 (workspace) | AI 首輪分析前後同時使用知識增強：prompt 會注入 K1 facts / guidelines，並按 K1 public `v1.3.1` schema 以 `subject_head + panel_chair + all_roles` 組裝主任層事實；本地 `role_facts.json` 亦會按 topic 取角色事實注入 `【EDB學校管理知識中心角色事實】` 區塊；summary 現正式只作通告簡介，可借知識庫詞彙統一用字，但不再寫角色工作、行動清單或知識庫延伸內容；若模型輸出仍偏官式或空泛，post-review 會優先改用 `official/pdf_text` 的硬資訊重組摘要，先抽主辦、日期、地點、名額及截止等內容，否則才回退為較具體的 title/tag 摘要 |
| 👥 七角色視圖 | ✅ v3.0.16 | 校長/副校長/科主任/主任/教師/EO/供應商（兼容舊 `department_head` 資料） |
| 📅 月曆視圖 | ✅ 正式版 | EDBC 格式通告、截止日期標記 |
| 💰 資源申請 | ✅ 正式版 | 可申請撥款追蹤 |
| ⭐ 收藏 / 📌 釘選 | ✅ 正式版 | 一般收藏 vs 常備參考通告 |
| 🏢 供應商分頁 | ✅ 正式版 | 供應商相關通告、法規參考 |
| 🔄 版本比較 | ✅ 正式版 | 通告更新差異分析 |
| 🐍 後端爬蟲 | ✅ 正式版 | ASP.NET WebForms POST 抓取 + PyMuPDF |
| ⚙️ GitHub Actions CI | ✅ 正式版 | 每天 3 次自動更新 + 手動 school-year |

---

## 🔎 本地摘要 / 行動審核工具

在再次跑耗時的 `school-year workflow` 前，可先用本地 audit 掃現有 [`/Users/leonard/Downloads/Claude-edb-Project-V3/circulars.json`](/Users/leonard/Downloads/Claude-edb-Project-V3/circulars.json)：

```bash
python3 dev/tools/summary_action_audit.py --input ./circulars.json --max-examples 5
```

用途：
- 找出帶 filler 的 AI 摘要
- 找出摘要過長 / 單段輸出
- 找出 `roles.*.acts` 有內容但頂層 `actions` 仍為空的通告
- 先做全量 heuristic gate，再決定值不值得發版和跑長 workflow

## 🏗️ 系統架構

```
EDB 網站 (ASP.NET WebForms)
    │  POST + ViewState
    ▼
edb_scraper.py              ← Python 後端管線
    ├── HTML 抓取（位置式解析）
    ├── PDF 下載 + 解析（PyMuPDF）
    ├── AI 分析（gpt-5-nano, json_schema）
    ├── K1 知識注入（knowledge.json / guidelines.json）
    ├── 知識校正（統一字眼 / 補漏 / 補連結；目前覆蓋 supplier + curriculum + finance + student）
    └── circulars.json 輸出（增量 merge）
         │
         ▼
edb-dashboard.html          ← 單頁前端應用 (v2.1.0)
    ├── 🏠 首頁
    ├── 📊 通告總覽
    ├── 📅 月曆視圖
    ├── 💰 資源申請
    ├── ⭐ 收藏
    ├── 🏢 供應商分頁
    └── ⚙️ 設定頁
         │
         ▼
GitHub Actions → GitHub Pages (自動部署)
```

---

## 📁 專案結構

```
EDB-AI-Circular-System/
├── README.md                       ← 本文件
├── CHANGELOG.md                    ← 版本變更記錄
├── AGENTS.md                       ← AI Agent 治理規則（核心）
├── CLAUDE.md                       ← Claude 自動讀取橋接
├── GEMINI.md                       ← Gemini 自動讀取橋接
│
├── edb-dashboard.html              ← ✅ v2.1.0 正式版前端（3,047 行）
├── edb-dashboard-mockup.html       ← 舊版 v0.1.0 Mockup（已歸檔）
├── index.html                      ← GitHub Pages 入口重定向
├── edb_scraper.py                  ← ✅ 後端爬蟲管線（增量 merge）
├── fetch_knowledge.py              ← EDB/ICAC 知識庫抓取工具
├── requirements.txt                ← Python 依賴
├── circulars.json                  ← AI 分析輸出（納入版控，Pages 所需）
│
├── .github/workflows/
│   └── update-circulars.yml        ← CI：每天 3 次 days-3 + 手動 school-year
│
└── dev/
    ├── SESSION_HANDOFF.md          ← AI Agent 會話接力
    ├── SESSION_LOG.md              ← AI Agent 會話記錄
    ├── CODEBASE_CONTEXT.md         ← 項目技術上下文
    ├── ACCEPTANCE_CHECKLIST.md     ← 驗收清單（80+ 項）
    ├── GIT_PUSH_MANUAL.md          ← Git push 操作手冊
    ├── K1_KNOWLEDGE_INTERFACE_SPEC.md ← K1 知識庫接口合約
    ├── v0.2.0-FRONTEND-SPEC.md     ← 前端規格 SSOT
    └── knowledge/
        └── role_facts.json         ← 本地角色知識庫（角色契約以 K1 spec 為準；分析時直接注入 prompt）
```

---

## 🚀 快速開始

### 線上 Demo

直接訪問：https://leonard-wong-git.github.io/EDB-AI-Circular-System/

### 本地運行

```bash
# 安裝依賴
pip install requests beautifulsoup4 PyMuPDF openai

# 設定 API Key
export OPENAI_API_KEY="sk-..."

# 抓取最近 3 天通告（增量，快速）
python3 edb_scraper.py --days 3 --output ./circulars.json -v

# 抓取整個學年通告（完整，約 1.5 小時）
python3 edb_scraper.py --school-year --output ./circulars.json -v

# 啟動本地 Dashboard
python3 -m http.server 8080
# 開啟：http://localhost:8080/edb-dashboard.html
```

> ⚠️ `circulars.json` 必須與 `edb-dashboard.html` 在同一目錄

### 發布到 GitHub Pages

```bash
bash ~/Downloads/Claude-edb-Project-V3/deploy.sh
```

此命令會自動執行 patch version bump、同步 workspace 到 deploy repo、commit、push；若 GitHub Pages 未即時更新，請到 Actions 手動確認最新 workflow。
此命令現時亦會觸發 push-based GitHub Pages deployment；本次實測已成功把 live site 更新到 `v3.0.7`。

### K1 知識庫整合

- `knowledge.json`：提供 topic / role 對應的政策事實，於 LLM prompt 內以 `【相關政策事實】` 注入
- `guidelines.json`：提供 topic 對應的官方指引文件，於 LLM prompt 內以 `【相關指引文件】` 注入
- K1 public `v1.3.1` schema 現以 `subject_head`（科主任）+ `panel_chair`（主任類）+ `all_roles` 為主任層事實來源
- `dev/knowledge/role_facts.json`：提供本地角色知識，按 topic 抽取 `all_roles` + 各角色 facts，於 LLM prompt 內以 `【EDB學校管理知識中心角色事實】` 注入
- `fetch_knowledge.py`：仍屬維護中的本地知識支援腳本；其輸出與 `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md` / `dev/knowledge/*.md` 現已對齊 split-role contract，使用 `subject_head + panel_chair`，不再把新的 K1 交付寫成 `department_head`
- K1 topic 補充現已收緊為最多 3 個 topic，並限制 facts / guidelines 注入上限，以減少 prompt 過胖及跨 topic 污染
- deterministic `knowledge_review` 連結補充現改為以通告原始文字訊號判斷 procurement / finance，而不再依賴 AI summary / supplier role 自我放大
- fetch 失敗時會自動降級，不會中斷通告分析
- 目前整合的 live endpoints：
  - [knowledge.json](https://leonard-wong-git.github.io/edb-knowledge/knowledge.json)
  - [guidelines.json](https://leonard-wong-git.github.io/edb-knowledge/guidelines.json)
  - [K1_API_SPEC.md](https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md)

---

## 🔧 CLI 參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--days N` | 90 | 抓取最近 N 天（增量 merge） |
| `--school-year` | — | 抓取本學年（9月1日至今） |
| `--from / --to` | — | 自訂日期範圍（YYYY-MM-DD） |
| `--output / -o` | `./edb_data/circulars.json` | 輸出路徑 |
| `--llm-only` | false | 僅重跑 AI 分析（需已有快取） |
| `--skip-llm` | false | 跳過 AI 分析 |
| `--verbose / -v` | false | 詳細日誌 |

---

## 🤖 AI 分析規格

| 項目 | 規格 |
|------|------|
| 模型 | `gpt-5-nano`（固定） |
| Temperature | `1`（固定，其他值會報 400 錯誤） |
| Role | `developer`（推理模型，非 `system`） |
| max_completion_tokens | `16000`（最少，推理 token 消耗大） |
| Structured Output | `json_schema`（非 `json_object`） |
| Context Window | 400K tokens |

---

## 👥 七大分析角色

| 角色 Key | 中文 | 關注範圍 |
|----------|------|----------|
| `principal` | 校長 | 全校決策、資源分配、政策回應 |
| `vice_principal` | 副校長 | 日常營運監督、政策落實 |
| `subject_head` | 科主任 | 學科 / 科組落實、課程調整 |
| `panel_chair` | 主任 | 課程統籌、訓輔、活動、總務、教務、學務、SEN、IT 統籌等校本主任職系 |
| `teacher` | 教師 | 課堂影響、學生指導 |
| `eo_admin` | EO | 表格填報、截止追蹤 |
| `supplier` | 供應商 | 招標機會、規格變更 |

> 過渡說明：舊資料若仍使用 `department_head`，前端會先兼容映射為 `panel_chair`。

---

## ⚠️ 已知限制

| 項目 | 說明 |
|------|------|
| EDB 網站須 POST | GET 無效；必須帶 ViewState |
| gpt-5-nano temperature | 固定為 1，不可更改 |
| AI 分析準確性 | AI 生成，可能存在錯誤，以 EDB 官方原文為準 |
| 供應商圖表 | 目前為佔位符，待 scraper 新增統計字段 |

---

## 🗺️ 版本歷史

詳見 [CHANGELOG.md](./CHANGELOG.md)

- **v2.1.0** (2026-03-22) — 首頁分離、搜尋獨立、AI 改名、EDBC 月曆、scraper merge 修復
- **v2.0.0** (2026-03-16) — 全面改版 Dashboard（37 項改進）
- **v1.1.0** (2026-03-14) — 後端管線正式版（PyMuPDF + K1 + R1-v2）
- **v0.1.0** (2026-03-09) — Mockup 階段

---

## 🤝 AI Agent 協作

本項目採用 **Sustainable Session Governance** 模式：

- **新 session 啟動：** 告知 Agent `Read AGENTS.md first, then follow §1 startup sequence`
- **讀取順序：** `dev/SESSION_HANDOFF.md` → `dev/SESSION_LOG.md` → `dev/CODEBASE_CONTEXT.md`
- **主要 workspace：** `Claude-edb-Project-V3`（開發）→ `EDB-Circular-AI-analysis-system`（git push）

詳見 [AGENTS.md](./AGENTS.md)

---

## 📝 License

Private project — Leonard Wong (leonard.ai.wong@gmail.com)

---

## 🔗 相關連結

- **Live Demo:** https://leonard-wong-git.github.io/EDB-AI-Circular-System/
- **EDB 通告來源:** https://applications.edb.gov.hk/circular/circular.aspx?langno=2
- **OpenAI API:** https://platform.openai.com/docs
- **K1 知識庫接口：** [K1_API_SPEC.md](https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md)
