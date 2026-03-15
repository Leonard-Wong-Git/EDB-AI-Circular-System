# Next Session Handoff Prompt — v14（最新版本 ✅，請用此版本）

> 將以下全文貼入新 session 的第一條訊息

---

## 項目：EDB Circular AI Analysis System
## GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
## GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/

---

### 你是此項目的 AI 開發助手，請先讀取以下文件（按順序）：
1. `dev/SESSION_HANDOFF.md` — 當前狀態 + 所有已知風險
2. `dev/SESSION_LOG.md` — 完整歷史記錄
3. `dev/v0.2.0-FRONTEND-SPEC.md` — 前端規格 SSOT

---

### 項目概況
- **單頁 HTML Dashboard**（`edb-dashboard.html`，2796 行）— 顯示 EDB 教育局通告 + AI 分析
- **Python 爬蟲**（`edb_scraper.py`）— 爬取 EDB 網站 + 用 gpt-5-nano LLM 分析
- **GitHub Actions** 自動排程（每日 3 次）抓取新通告 → 更新 `circulars.json` → 部署 GitHub Pages
- **當前版本**：v1.1.0-features（含 8 項新功能），但 GitHub Pages **未更新**（仍顯示舊版）

---

### ⭐ 最緊急任務：修復 PDF timeout → 部署 GitHub Pages

**問題**：pdfminer/pdfplumber C 擴展在解析某些 EDB PDF 時進入無限迴圈，卡死 GitHub Actions workflow。

**已失敗方案（RE05 實測，全部無效）：**
| # | 方案 | 結果 | 原因 |
|---|------|------|------|
| 1 | `signal.SIGALRM(60)` | ❌ 卡死 29+ min | C 擴展不回應 Python 信號 |
| 2 | `signal.SIGALRM(10)` | ❌ NameError | handler 被刪但調用殘留 |
| 3 | `multiprocessing.Process` + `proc.terminate()` | ❌ 卡死 32+ min | SIGTERM 被 C 擴展忽略 |

**待測試方案（優先順序）：**
1. **`proc.kill()` (SIGKILL)** — 改 `terminate()` → `kill()`，SIGKILL 無法被攔截
2. **`subprocess.run(timeout=N)`** — 用獨立 Python 子程序做 PDF 提取
3. **PyMuPDF (fitz)** — 替代 pdfplumber/pdfminer，不同 C 底層
4. **暫時禁用 PDF** — `HAS_PDF = False`，先部署 dashboard（最後手段）

**同時必須**：關閉 pdfminer DEBUG logging（防止 107K+ 行 log 爆炸）

---

### 當前 edb_scraper.py 狀態（GitHub 上的版本）
```python
# 已存在的函數（multiprocessing 版本，但用 terminate() — 無效）
def _pdf_extract_worker(pdf_path_str, max_pages, queue):
    """Runs in a child process."""
    import pdfplumber
    with pdfplumber.open(pdf_path_str) as pdf:
        ...
    queue.put(text)

def extract_pdf_text(pdf_path, max_pages=PDF_MAX_PAGES, timeout_secs=10):
    import multiprocessing
    proc = multiprocessing.Process(target=_pdf_extract_worker, ...)
    proc.start()
    proc.join(timeout_secs)
    if proc.is_alive():
        proc.terminate()  # ← 這裡要改成 proc.kill()
        proc.join()
        return ""
    return q.get_nowait()[:PDF_MAX_CHARS]
```

---

### 項目已成功的部分 ✅
1. **前端 Dashboard** — 2796 行 HTML，8 項功能全部實作完成，HTML 語法驗證通過
2. **後端爬蟲** — 14 條真實 EDB 通告 dry-run 通過，LLM 分析成功
3. **GitHub Actions CI/CD** — workflow 配置正確，排程 + 手動觸發 + Pages 部署
4. **circulars.json** — 14 條通告 + gpt-5-nano 分析數據已生成
5. **知識庫** — `dev/knowledge/` 目錄含角色知識文件
6. **治理框架** — AGENTS.md / SESSION_HANDOFF / SESSION_LOG 完整

### gpt-5-nano 必遵守規則
- `temperature=1`（固定，否則 400 Bad Request）
- `max_completion_tokens=16000`（非 `max_tokens`）
- `role="developer"`（非 `"system"`）

---

### Git 操作注意
- 本機項目路徑深（~/Library/Application Support/Claude/...），需用 `find ~/Library -maxdepth 12 -type d -name "EDB-Circular-AI-analysis-system"` 找到
- Push 需用 PAT：`git push https://USERNAME@github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git main`
- GitHub Actions 會自動 commit circulars.json，push 前先 `git pull --rebase`

---

### Workflow 安全模式
- `days-3`（排程預設）：增量模式，通常 43 秒完成，**安全**
- `school-year`（手動觸發）：完整重建，會處理所有 PDF，**目前會卡死**
- **修好 PDF timeout 前，只用 `days-3` 模式**

---

### 次要待辦（PDF 修好後）
- D8/D9 月曆篩選邏輯
- F4 書籤 badge 計數
- H5 天數選擇器
- H6 已跟進切換
- K1 知識庫參考文件框架
- R1 全角色職責精確度
- LLM 引擎切換機制
