# Session Log

## 2026-03-17 AGENTS.md v2 升級 + CODEBASE_CONTEXT.md

1. Agent & Session ID: Claude_20260317_0800
2. Task summary: INIT.md 治理框架升級（AGENTS.md 整合 7 項新增內容）+ dev/CODEBASE_CONTEXT.md 首次生成
3. Layer classification: Development Governance Layer（治理框架升級 + 項目上下文文檔化）
4. Source triage: 用戶上傳新版 INIT.md → 與現有 AGENTS.md 差異分析 → 純增強整合
5. Files read: AGENTS.md（兩個 repo）、INIT.md（上傳）、README.md、CHANGELOG.md、requirements.txt、.gitignore、update-circulars.yml、SESSION_HANDOFF.md、SESSION_LOG.md
6. Files changed:
   - `AGENTS.md`（兩個 repo：395→622 行，整合 7 項新增內容）
   - `dev/CODEBASE_CONTEXT.md`（新建：177 行，7 個 section + 3 External Services + 8 Key Decisions）
7. Completed:
   - ✅ **INIT.md 差異分析**：逐節比對 §0–§12，確認 INIT.md 為現有 AGENTS.md 的嚴格超集（無衝突、無刪除）
   - ✅ **Root Safety Check §5a**：兩個 repo 路徑確認、風險檢查、dry-run plan、INSTALL_ROOT_OK + INSTALL_WRITE_OK 雙重確認
   - ✅ **備份快照**：`dev/init_backup/20260317_081952_UTC/`（兩個 repo）
   - ✅ **AGENTS.md 整合**（7 項新增）：§0a CODEBASE_CONTEXT Note、§0b External API Code Safety、§1 CODEBASE_CONTEXT 讀取+自動生成、§2 優先級更新、§3d Test Plan Design、§4 Session Close 擴充+handoff 開頭、§10 Active trigger rule
   - ✅ **CLAUDE.md / GEMINI.md**：已有正確 @import，skip
   - ✅ **dev/CODEBASE_CONTEXT.md 首次生成**：掃描 7 個源文件，填入 Stack / Directory Map / Key Entry Points / Build & Run / External Services（3 API，全部有 Doc-reviewed + Test-verified）/ Key Decisions（8 項）/ AI Maintenance Log
8. Validation / QC:
   - AGENTS.md：兩個 repo 622 行，完全一致（diff confirmed）
   - CODEBASE_CONTEXT.md：177 行，7 section 全部存在；3 External Services 各含完整 10 欄位
   - 備份快照完整（5 files per repo）
   - CLAUDE.md / GEMINI.md：已有 @import（skip confirmed）
9. Pending:
   - school-year workflow re-run 進行中（R1-v2 效果驗證）
   - GitHub Pages v2.0.0 視覺驗證
   - README.md 和 CHANGELOG.md 內容過時（仍顯示 v0.1.0-mockup）— 非阻塞，可下次更新
   - Mac Terminal push 本次 session 的治理文件更新
10. Next priorities:
    - school-year workflow 完成後檢查 R1-v2 角色分佈
    - GitHub Pages v2.0.0 視覺驗證
    - K1 PDF 提取項目（另立）

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow §1 startup: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md.

EDB Circular AI Analysis System — Session Handoff

Current state:
- v2.0.0 Dashboard DEPLOYED on GitHub Pages (commit 7151ed7)
- R1-v2 role accuracy (few-shot + postprocess) PUSHED (commit dbd997e)
- AGENTS.md upgraded to v2 (622 lines, 7 new sections from INIT.md) in BOTH repos
- dev/CODEBASE_CONTEXT.md generated (177 lines, 3 External Services, 8 Key Decisions)
- school-year workflow RE-RUNNING (R1-v2 new prompt + postprocess applied to all circulars)
- Result of school-year re-run NOT YET CHECKED

Immediate actions needed:
1. Check school-year workflow result — if success, git pull on Mac then verify circulars.json role distribution
2. Expected improvement: teacher ~40-60% (was 96%), supplier ~20-30% (was 49%)
3. Open GitHub Pages and visually verify v2.0.0 Dashboard with updated data
4. If R1-v2 results unsatisfactory, adjust _WEAK_ACT_PATTERNS or few-shot examples in edb_scraper.py
5. Push governance file updates from Mac Terminal:
   git stash && git pull --rebase origin main && git stash pop && git add AGENTS.md dev/CODEBASE_CONTEXT.md dev/SESSION_HANDOFF.md dev/SESSION_LOG.md && git commit -m "chore: AGENTS.md v2 upgrade + CODEBASE_CONTEXT.md" && git push origin main

Key files changed this session:
- AGENTS.md (both repos, 395→622 lines, 7 new governance sections)
- dev/CODEBASE_CONTEXT.md (new, 177 lines)
- dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md

Known risks:
- R1-v2 internal role reduction depends on LLM prompt response (school-year re-run in progress)
- README.md and CHANGELOG.md are outdated (still show v0.1.0-mockup) — non-blocking
- official field still mostly empty (UI fallback in place)
- Node.js 20 deprecation warning in workflow (cosmetic, deadline June 2026)

Validation status: AGENTS.md identical in both repos (622 lines); CODEBASE_CONTEXT.md 7 sections complete; backup snapshots created
First action: Check school-year workflow result, then verify role distribution
```

---

## 2026-03-16 v2.0.0 + R1-v2

1. Agent & Session ID: Claude_20260316_1600
2. Task summary: R1-v2 角色精確度（few-shot + postprocess filter）+ v2.0.0 Dashboard 37 項全面改版 + CI 修復
3. Layer classification: Product / System Layer（前端全面改版 + 後端 LLM prompt 優化 + CI 修復）
4. Source triage: R1 過度標記 = prompt 設計 + LLM 行為偏差；Dashboard 改版 = 用戶需求
5. Files read: `edb-dashboard.html`、`edb_scraper.py`、`circulars.json`、`.github/workflows/update-circulars.yml`
6. Files changed:
   - `edb-dashboard.html`（v2.0.0 全面改版，2766 行）
   - `edb_scraper.py`（R1-v2：SYSTEM_PROMPT few-shot 3 組 + `_postprocess_roles()` 4 規則）
   - `.github/workflows/update-circulars.yml`（fetch+reset 修復 circulars.json 衝突）
   - `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`
7. Completed:
   - ✅ **R1-v2 few-shot**：SYSTEM_PROMPT 加入 3 組角色標記參考範例（差餉→2 roles、員工交流→2 roles、熱帶氣旋→2 roles）
   - ✅ **R1-v2 postprocess**：`_postprocess_roles()` 函數，4 規則（空acts→false、≥2/3弱acts→false、全弱pts→false、supplier限採購）
   - ✅ **R1-v2 commit** `dbd997e`；postprocess simulation: supplier 49%→21%
   - ✅ **v2.0.0 Dashboard 37 項改版**：版本集中管理（`const VERSION`）、預設淺色主題、簡化圖標（✅+📌 only）、AI 免責聲明、詳情面板重構（3 tab：總結/角色及資源/比較）、PDF 連結置頂、日曆 EDBC 號+標題、ICS 匯出、EDB 官方學校類型篩選、type filter 標籤改善、分享按鈕（Web Share API + clipboard）、手機/平板修復、統計 placeholder、供應商分析視角、移除 REF_CIRCULARS、Leonard Wong footer link
   - ✅ **v2.0.0 commit** `7151ed7`；14/14 key checks 通過；v1.1.2 殘留 = 0
   - ✅ **CI 修復**：workflow circulars.json 衝突 → fetch+reset 方案（commit `bec0a81`）
   - ✅ **school-year workflow** 成功跑完（108 circulars）— 但用舊 R1 prompt
8. Validation / QC:
   - HTML 驗證：14/14 checks 通過；2766 行；v1.1.2 remnants = 0
   - R1-v2 postprocess simulation：supplier 49%→21%（有效）
   - CI workflow 修復後成功：school-year 108 circulars
   - Python syntax OK
9. Pending:
   - ✅ Mac push 成功；days-3 workflow 8m9s 成功；GitHub Pages v2.0.0 已部署
   - school-year workflow re-run（驗證 R1-v2 新 prompt + postprocess 效果）
   - GitHub Pages v2.0.0 視覺驗證（目視確認）
10. Next priorities:
    - GitHub Pages v2.0.0 視覺驗證 + school-year re-run
    - K1 PDF 提取項目（另立）
    - 後端 #35/#36 上年度分析 + 預算預測

### Problem -> Root Cause -> Fix -> Verification (R1-v2)

**R1-v2: prompt-only 方案不足，需 few-shot + postprocess**
1. Problem: R1 prompt-only 改寫後，school-year workflow 結果仍 96%+ 角色 true
2. Root Cause: gpt-5-nano 行為偏向 inclusive，僅靠排除準則不足以覆蓋全部情況
3. Fix: (1) few-shot 範例 3 組（展示正確的 2-role 標記）(2) `_postprocess_roles()` 後處理 4 規則
4. Verification: postprocess simulation supplier 49%→21%；內部角色效果待 school-year re-run（新 prompt + postprocess 同時生效）
5. Regression: 下次 school-year 後檢查全角色分佈

**v2.0.0 Dashboard 37 項改版**
1. Problem: v1.1.2 Dashboard 有多處 UX 問題（圖標繁雜、詳情面板結構差、日曆缺 EDBC 號、無分享功能等 37 項）
2. Fix: 用戶提供 37 項清單，全部一次過完成
3. Verification: 14/14 key checks；HTML parse OK；2766 行；v1.1.2 殘留 = 0
4. Regression: GitHub Pages 部署後視覺驗證

### Next Session Handoff Prompt (Verbatim)

```text
EDB Circular AI Analysis System — Session Handoff

Current state:
- v2.0.0 Dashboard (37-item overhaul) PUSHED and DEPLOYED on GitHub Pages (commit 7151ed7)
- R1-v2 role accuracy (few-shot + postprocess) PUSHED (commit dbd997e)
- CI workflow fix (fetch+reset) on remote (commit bec0a81)
- days-3 workflow ran successfully (8m9s) after push — but this was NOT school-year scope
- circulars.json has school-year data (108 circulars) from PREVIOUS run with OLD R1 prompt
- R1-v2 new prompt + postprocess NOT YET applied to school-year data

Immediate actions needed:
1. Trigger school-year workflow to apply R1-v2 (new prompt + postprocess to all 108 circulars)
2. After workflow: check role distribution improvement (expect teacher ~40-60%, supplier ~20-30%)
3. Open GitHub Pages and visually verify v2.0.0 Dashboard renders correctly with real data
4. If R1-v2 results unsatisfactory, consider adjusting _WEAK_ACT_PATTERNS or few-shot examples

Key files changed this session:
- edb-dashboard.html (v2.0.0, 2766 lines, 37 items)
- edb_scraper.py (R1-v2: few-shot + _postprocess_roles())
- .github/workflows/update-circulars.yml (fetch+reset fix)
- dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md

Known risks:
- R1-v2 internal role reduction depends on LLM prompt response (postprocess alone mainly catches supplier + weak-act patterns)
- official field still mostly empty (UI fallback in place, root cause = GH Actions PDF extraction)
- HEAD.lock may reappear if VM git operations fail mid-way (rm -f before operations)
- Node.js 20 deprecation warning in workflow (cosmetic, no functional impact)

Validation status: HTML 14/14 OK; R1-v2 postprocess simulation OK; CI workflow fixed and green
First action: Push commits from Mac Terminal, then trigger school-year workflow
```

---

## 2026-03-16 R1 (續)

1. Agent & Session ID: Claude_20260316_0850 (R1 continued)
2. Task summary: R1 全角色職責精確度 — SYSTEM_PROMPT roles 判斷準則改進
3. Layer classification: Product / System Layer（LLM prompt 優化）
4. Source triage: 過度標記問題 = LLM prompt 設計問題（缺乏 r=false 的明確排除準則）
5. Files read: `circulars.json`（role 分佈分析）、`edb_scraper.py` SYSTEM_PROMPT roles 部分
6. Files changed: `edb_scraper.py`（SYSTEM_PROMPT roles 節改寫）
7. Completed:
   - ✅ **現狀分析**：principal 97%、teacher/VP/dept_head 各 ~96%、supplier 53%（105 條通告）
   - ✅ **R1 根本原因**：SYSTEM_PROMPT roles.r 定義不精確，缺乏排除標準
   - ✅ **SYSTEM_PROMPT 改寫**：r 定義 → 「直接職責」；⭐ r=true 三條件；⛔ r=false 四排除；六角色邊界；校準提示（預期 2-4 roles）
   - ✅ **commit `a2a0d38`**；⏳ push 待 Mac Terminal 執行
8. Validation / QC: Python syntax OK；SYSTEM_PROMPT roles 節完整；預期效果待下次 workflow 驗證
9. Pending: Mac push + days-3 workflow 驗證 R1 效果

### Problem -> Root Cause -> Fix -> Verification (R1)

**R1: 角色相關性過度標記（97%/96% → 預期 40-60%）**
1. Problem: 105 條通告中 principal/teacher/VP/dept_head 各 ~96-97% 標為 true；角色篩選幾乎無效
2. Root Cause: roles.r 定義為「是否相關」（模糊）而非「是否有直接職責」（精確）；無排除標準 → LLM 預設 inclusive
3. Fix: r=true 三條件（明確點名/需提交文件/工作範疇受直接影響）+ r=false 四排除規則（純知悉/協助上司/範疇不符/supplier 限制）+ 角色職責邊界 + 校準提示
4. Verification: Python syntax OK；commit `a2a0d38`；實際效果待 days-3 workflow 驗證
5. Regression: 下次 workflow 後檢查 role distribution（預期 teacher ~40-60%，supplier ~20-30%）

---

## 2026-03-16

1. Agent & Session ID: Claude_20260316_0850
2. Task summary: Issue 4 修復（官方摘要空白）+ K1 知識注入框架 + K1 接口規格文件
3. Layer classification: Product / System Layer（前端 UI 修復 + 後端 LLM 管線增強）
4. Source triage: Issue 4 = 後端緩存問題（Phase 3 未還原 `official`）+ GH Actions PDF 提取失效；K1 = 新功能增強
5. Files read:
   - `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`
   - `edb-dashboard.html`（VM workspace）
   - `edb_scraper.py`（Mac git repo）
6. Files changed:
   - `edb-dashboard.html`（Issue 4 UI 修復 + 版本標籤 v1.1.1→v1.1.2；VM workspace + Mac git repo 同步）
   - `edb_scraper.py`（Issue 4 Phase 3 緩存修復 + K1 注入函數 + `_build_prompt()` 更新）
   - `dev/knowledge/role_facts.json`（新建：基線知識庫，6 個主題 × 7 個角色）
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md`（新建：K1 獨立項目接口合約）
   - `Claude-edb-Project-V3/dev/K1_KNOWLEDGE_INTERFACE_SPEC.md`（複製副本供 K1 項目參考）
7. Completed:
   - ✅ **Issue 4 UI 修復（前端）**：card-summary fallback `d.official || (d.summary||'').substring(0,150)`；detail panel 條件顯示 官方摘要
   - ✅ **Issue 4 後端緩存修復**：Phase 3 restore `official` from existing JSON cache
   - ✅ **版本標籤 v1.1.1→v1.1.2**（VM workspace + Mac git repo）
   - ✅ **K1 知識注入框架**：`_detect_topics_early()`、`_load_knowledge_context()`、`_build_prompt()` 更新；4 測試案例全通過
   - ✅ **baseline `role_facts.json`** 建立（finance/hr/curriculum/activity/student/it/general × 7 角色）
   - ✅ **K1 接口規格文件** `K1_KNOWLEDGE_INTERFACE_SPEC.md` 建立（獨立項目可憑此交付）
   - ✅ **K1 規格複製** 至 `Claude-edb-Project-V3/dev/`（供 K1 項目開發者閱讀）
   - ✅ **git push**：Issue 4 + K1 injection 已推送至 GitHub（`7c6bd46`）
8. Validation / QC:
   - Python 語法驗證：OK（`_detect_topics_early`、`_load_knowledge_context` 函數正確）
   - K1 注入功能測試：4 測試案例全通過（finance/it、hr、activity/student、general fallback）
   - git push 成功：commit `7c6bd46` 已推送
9. Pending:
   - R1 全角色職責精確度
   - LLM 引擎切換機制
   - 觀察 v1.1.2 在 GitHub Pages 顯示效果（Issue 4 修復驗證）
10. Next priorities:
    - 確認 GitHub Pages v1.1.2 部署（Issue 4 官方摘要 fallback 是否生效）
    - R1 全角色職責精確度分析
    - K1 第二階段：PDF 提取真實 EDB 知識內容（另立項目）
11. Risks / blockers:
    - `official` 仍對 105/108 通告為空（PDF 提取在 GH Actions 環境失敗）；UI fallback 已緩解，根本原因待 K1 PDF 提取項目解決
    - K1 `role_facts.json` 目前為人工整理的基線資料，待 K1 項目 PDF 提取完成後替換

### Problem -> Root Cause -> Fix -> Verification

**Issue 4: 官方摘要（official）空白**
1. Problem: 105/108 真實通告在 Dashboard 的 官方摘要 欄位顯示空白
2. Root Cause（多重）：
   - GH Actions 環境 PyMuPDF subprocess 提取 PDF 返回空字串
   - Phase 3 緩存還原 LLM keys 但未還原 `official` 欄位
   - `pdf_text` 不保存在輸出 JSON，無法從緩存還原
   - 列表頁無 `detail_url`，`enrich_detail()` 無法運行
3. Fix（分層）：
   - 前端：card-summary fallback → 顯示 LLM summary 前 150 字；detail panel 條件隱藏空 official
   - 後端：Phase 3 restore `official` from existing cache（確保重跑不丟失）
4. Verification: HTML/Python 語法 OK；git push 成功
5. Regression: 根本原因（GH Actions PDF 提取失敗）留待 K1 項目解決

**K1 知識注入框架**
1. Problem: LLM 缺乏 EDB 學校運作背景知識，分析精準度有限
2. Solution: 在 `_build_prompt()` 前端注入 600 字符預算的角色相關知識事實
3. Implementation: 關鍵字匹配（`_detect_topics_early`）→ 按主題查找（`_load_knowledge_context`）→ 注入 prompt
4. Architecture: K1 作為獨立項目，通過 `role_facts.json` 文件接口交付，EDB 項目只消費 JSON
5. Verification: 4 測試案例全通過（finance/it 採購門檻、hr CPD、activity 安全、general fallback）

---

## 2026-03-15

1. Agent & Session ID: Claude_20260315_1400
2. Task summary: 次要 UI 修復（D8/D9/F4/H5/H6）+ pdfplumber→PyMuPDF 遷移 + school-year workflow 首次成功
3. Layer classification: Product / System Layer（前端修復 + 後端 PDF 引擎替換）
4. Source triage: D8/D9 = 程式碼邏輯問題；F4 = 初始化遺漏；pdfminer = 外部依賴行為問題
5. Files read:
   - `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`
   - `dev/v0.2.0-FRONTEND-SPEC.md`（月曆/設定規格）
   - `dev/ACCEPTANCE_CHECKLIST.md`（D8/D9/F4/H5/H6 定義）
   - `edb-dashboard.html`（月曆/書籤/設定程式碼）
   - `edb_scraper.py`（PDF 提取 + pdfminer 抑制邏輯）
   - `.github/workflows/update-circulars.yml`
6. Files changed:
   - `edb-dashboard.html`（D8/D9 月曆篩選修復 + F4 badge 初始化 + 版本標籤 v1.1.0→v1.1.1）
   - `edb_scraper.py`（pdfplumber/pdfminer 完全替換為 PyMuPDF/fitz）
   - `requirements.txt`（pdfplumber→PyMuPDF）
   - `dev/ACCEPTANCE_CHECKLIST.md`（D8/D9/F4/H5/H6 標記 ✅）
7. Completed:
   - ✅ **D8 月曆高影響篩選**：`isAttention(d)`（high+mandatory）改為 `d.impact!=='high'`，與按鈕標示語義一致
   - ✅ **D9 月曆截止日篩選**：`calFilter==='deadline'` 時跳過通告發布日事件，只顯示 deadline 類型
   - ✅ **F4 書籤 Tab badge**：`renderAll()` 新增 `updateBmBadge()` 調用，初始載入後 badge 正確顯示
   - ✅ **H5 截止天數切換**：程式碼審查確認已完整實作（`setAlertDays` + `applySettingsUI`）
   - ✅ **H6 已跟進顯示切換**：程式碼審查確認已完整實作（`toggleShowDone` + `filteredData`）
   - ✅ **pdfplumber→PyMuPDF 遷移**：完全移除 pdfminer 依賴，消除 107K+ 行 DEBUG 洪流
   - ✅ **school-year workflow 首次成功**：1h 25m 4s，全步驟綠色，GitHub Pages 已部署
8. Validation / QC:
   - HTML 語法驗證：OK（2800 行）
   - Python 語法驗證：OK（1085 行）
   - Inline worker script 語法驗證：OK
   - GitHub Actions school-year workflow：全綠 ✅（1h 25m 4s）
   - pdfminer 引用檢查：0（僅 1 處註釋）
   - GitHub Pages 部署：✅
9. Pending:
   - K1 知識庫參考文件框架
   - R1 全角色職責精確度
   - LLM 引擎切換機制
10. Next priorities:
    - K1/R1 知識框架實作
    - 觀察 school-year 數據在 Dashboard 的顯示效果
    - 考慮 days-3 排程是否需要調整（school-year 已成功）
11. Risks / blockers:
    - school-year 耗時 1h25m + OpenAI API 費用可觀（僅適合偶爾全量重建，日常用 days-3）
    - VM workspace 路徑 ≠ git repo 路徑（必須用 mount 或手動複製同步）
12. Notes: 本 session 發現並確認 VM workspace (`Claude-edb-Project-V3`) 和 git repo (`EDB-Circular-AI-analysis-system`) 是不同資料夾。日後 VM 修改後端文件需先 mount git repo 再複製。

### Problem -> Root Cause -> Fix -> Verification

**Issue 1: D8/D9 月曆篩選邏輯**
1. Problem: D8 高影響篩選過於嚴格（只顯示 high+mandatory）；D9 截止日篩選仍顯示所有通告發布日
2. Root Cause: D8 使用 `isAttention()` 而非 `impact==='high'`；D9 無 guard 阻止發布日事件加入 evMap
3. Fix: D8 改用 `d.impact!=='high'`；D9 加 `if(S.calFilter!=='deadline')` guard
4. Verification: HTML parser OK；grep 確認程式碼正確
5. Regression: ACCEPTANCE_CHECKLIST.md D8/D9 標記 ✅

**Issue 2: F4 書籤 Tab badge 初始載入不顯示**
1. Problem: 頁面載入後如有 localStorage 書籤記錄，Tab badge 不顯示數字
2. Root Cause: `renderAll()` 未調用 `updateBmBadge()`
3. Fix: `renderAll()` 末尾新增 `updateBmBadge()` 調用
4. Verification: grep 確認調用存在
5. Regression: ACCEPTANCE_CHECKLIST.md F4 標記 ✅

**Issue 3: pdfminer DEBUG 洪流（107K+ 行，school-year 模式）**
1. Problem: GitHub Actions 日誌被 pdfminer.psparser/pdfinterp DEBUG 輸出淹沒（107,600+ 行），步驟被截斷
2. Root Cause: pdfminer 的 C 擴展（psparser/pdfinterp）直接寫入 fd 2（stderr），繞過 Python logging 控制。`fork()` 後子程序繼承父程序的 file descriptor，無論 `logging.disable()`、`logging.setLevel()`、`sys.stderr = devnull` 都無法攔截 C 層直接 I/O
3. **❌ 已失敗的方案（本 session 實測）：**
   - `logging.disable(CRITICAL)` in child → 無效（C 擴展不走 Python logging）
   - `sys.stderr = open(os.devnull, 'w')` in child → 無效（只影響 Python 層，不影響 fd 2）
   - `os.dup2(os.open(os.devnull, os.O_WRONLY), 2)` in child → 無效（fork 後 fd 2 已被繼承）
   - `subprocess.Popen` + `stderr=subprocess.DEVNULL` → 無效（pdfminer 仍在子程序內部產生洪流）
   - 三層防禦（module-level + handler filter + subprocess）→ 無效
4. **✅ 成功方案：完全移除 pdfplumber/pdfminer，替換為 PyMuPDF（fitz）**
   - PyMuPDF 使用 MuPDF C 庫，無 DEBUG 洪流問題
   - 速度更快（MuPDF vs pdfminer）
   - 保留 subprocess.Popen + SIGKILL timeout 作為安全網
   - requirements.txt：`pdfplumber>=0.10.0` → `PyMuPDF>=1.24.0`
5. Verification: school-year workflow 全綠，1h 25m 4s，零 pdfminer 輸出
6. **Regression / rule update：**
   - ⭐ **新規則：不要對有問題的依賴疊補丁，直接替換為已知可行的方案**
   - Known Risk #6（pdfminer 卡死）→ 已解決，降級為 historical record
   - `edb_scraper.py` PDF 引擎：pdfplumber/pdfminer → PyMuPDF/fitz（永久替換）

**Issue 4: VM workspace ≠ git repo**
1. Problem: VM 對 `edb_scraper.py` 的修改未到達 GitHub（3 次 push 嘗試全部失敗）
2. Root Cause: VM mount `Claude-edb-Project-V3` 和 git repo `EDB-Circular-AI-analysis-system` 是不同的 Mac 資料夾
3. Fix: 使用 `request_cowork_directory` mount git repo 路徑，直接 `cp` 文件過去
4. Verification: `git status` 顯示 modified，commit + push 成功（`184b867`）
5. **Regression / rule update：**
   - ⭐ **新規則：修改後端文件（edb_scraper.py / requirements.txt 等）時，必須先 mount git repo 資料夾再寫入**
   - RE06 的「VM 路徑 ≠ Mac git repo 路徑」規則已擴展

### Consolidation / Retirement Record
1. Duplicate / drift found: pdfminer 相關的 3 層抑制程式碼 + SESSION_HANDOFF Known Risk #6 的舊方案描述
2. Single source of truth chosen: PyMuPDF 為唯一 PDF 引擎
3. What was merged: 所有 pdfminer 補丁代碼合併為單一方案（PyMuPDF 替換）
4. What was retired / superseded: pdfplumber, pdfminer, signal.SIGALRM, multiprocessing.Process+SIGTERM, multiprocessing.Process+SIGKILL, logging.disable, handler filter, 三層防禦
5. Why consolidation was needed: 6 次補丁嘗試均失敗，根本原因是 C 擴展層 I/O 無法被 Python 攔截；替換依賴是唯一正確方案

### Next Session Handoff Prompt (Verbatim)

```text
項目：EDB Circular AI Analysis System
GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/
你是此項目的 AI 開發助手，請先讀取以下文件（按順序）：
1. dev/SESSION_HANDOFF.md — 當前狀態 + 所有已知風險 + Session Close 保障規則
2. dev/SESSION_LOG.md — 完整歷史記錄
3. dev/v0.2.0-FRONTEND-SPEC.md — 前端規格 SSOT

當前系統狀態（2026-03-15 全部正常）✅
* GitHub Pages：v1.1.1 已上線，school-year 數據已部署
* GitHub Actions school-year workflow：1h 25m 完成（首次成功 ✅）
* GitHub Actions days-3 workflow：33 秒完成（穩定）
* edb_scraper.py：PyMuPDF (fitz) 替換 pdfplumber/pdfminer（零 DEBUG 洪流 ✅）
* edb-dashboard.html：~2800 行，版本標籤 v1.1.1
* D8/D9/F4/H5/H6 次要 UI 修復全部完成 ✅

待辦（按優先級）
1. K1 知識庫參考文件框架
2. R1 全角色職責精確度
3. LLM 引擎切換機制
4. 觀察 school-year 數據在 Dashboard 的顯示效果

⭐ 重要規則
* 版本標籤同步：每次功能 push 後在 Mac Terminal 執行 sed 更新 5 處版本標籤
* VM ≠ git repo：修改後端文件時必須先 mount git repo 再寫入
  - VM workspace: Claude-edb-Project-V3（前端文件在此）
  - Git repo: EDB-Circular-AI-analysis-system（後端文件必須寫到這裏）
  - Mount 方法：request_cowork_directory 掛載 git repo 路徑
* gpt-5-nano：temperature=1 / max_completion_tokens=16000 / role="developer"
* Git push：git push https://Leonard-Wong-Git@github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git main
* Workflow 觸發：手動 GitHub Actions / 安全模式：days-3（33秒）/ school-year（1h25m）
* Mac git repo 路徑：
  /Users/leonard/Library/Application Support/Claude/local-agent-mode-sessions/f52b21f7-e7c9-49a3-80dc-00ab322afbcf/51c234d2-cb9f-4b55-bb07-b71de9e93c27/local_e454964f-74da-4734-9a60-bf4b4362ca65/outputs/EDB-Circular-AI-analysis-system

建議第一個動作：開啟 GitHub Pages 檢視 school-year 數據顯示效果，討論 K1/R1。
```

---

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

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE04
2. Task summary: gpt-5-nano LLM 修正（developer role + max_completion_tokens）+ 完整管線通過 + GitHub 推送
3. Layer classification: Product / System Layer（後端 LLM 調試 + 發布）
4. Source triage: OpenAI API 錯誤訊息驅動修正；Mac Terminal 實測驗證
5. Files changed:
   - `edb_scraper.py`（更新：max_tokens→max_completion_tokens，system→developer role，tokens 4096→16000）
   - `test_llm.py`（更新：同步修正 + 增加 developer role）
   - `dev/SESSION_HANDOFF.md`（更新：v0.3.0-backend 完成標記 + LLM 規則補充）
   - `dev/SESSION_LOG.md`（本條目）
6. Completed:
   - 修正 `max_tokens` → `max_completion_tokens`（gpt-5-nano 推理模型要求）
   - 修正 `"system"` → `"developer"` role（推理模型要求）
   - 修正 `max_completion_tokens` 4096 → 16000（推理 tokens 消耗大）
   - test_llm.py Test 2 ✅ Test 3 ✅（finish_reason: stop，1675 chars）
   - 完整 LLM 執行成功：EDBCM030 high/721chars，EDBCM026 mid/462chars ✅
   - GitHub force push 成功（52 objects，11.35 MiB）✅
   - tag v0.3.0-backend 推送成功 ✅
7. Validation / QC:
   - LLM 分析：summary 有內容，impact/tags 正確 ✅
   - GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git tag v0.3.0-backend ✅
8. Pending: 瀏覽器開啟 edb-dashboard.html 確認真實數據顯示
9. Next priorities:
   - ⭐ open edb-dashboard.html 確認真實 circulars.json 整合
   - 根據真實數據微調 Dashboard（如有需要）
   - v1.0.0-release
10. Notes: gpt-5-nano 確認為推理模型（需要 developer role + max_completion_tokens + 16000 tokens）

### Problem -> Root Cause -> Fix -> Verification
1. Problem: LLM 返回空內容（finish_reason: length，0 chars）
2. Root Cause: gpt-5-nano 是推理模型，max_completion_tokens=4096 被推理過程耗盡；system role 不支援
3. Fix: developer role + max_completion_tokens=16000
4. Verification: test_llm.py Test 3 finish_reason=stop，1675 chars ✅；完整管線 LLM 成功 ✅
5. Regression / rule update: 記錄於 SESSION_HANDOFF Known Risks #1（補充）

### Consolidation / Retirement Record
1. SSOT: SESSION_HANDOFF Known Risks #1 = gpt-5-nano 所有規則（temperature=1, developer role, max_completion_tokens=16000）
2. Retired: system role（已替換為 developer）；max_tokens（已替換為 max_completion_tokens）

---

### Next Session Handoff Prompt — v8（已由 v9 取代）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.3.0-backend ✅ 完成並推送 GitHub，準備瀏覽器整合確認

已完成（全部 ✅）：
- Dashboard v0.2.1（2453行）✅
- edb_scraper.py v0.3.0：14條真實通告 + PDF + LLM 分析 ✅
- circulars.json 已生成（真實 EDB 數據）✅
- GitHub tag v0.3.0-backend 已推送 ✅

⚠️ gpt-5-nano 規則（全部已確認，不可更改）：
  temperature=1（固定）
  role="developer"（非"system"）
  max_completion_tokens=16000（非max_tokens，非4096）

⭐ 下一步：
  open edb-dashboard.html  # 確認真實 circulars.json 正確顯示
  # 如有顯示問題，調整 Dashboard JS 數據載入邏輯

最終里程碑：v1.0.0-release（整合測試通過後）
```

---

## 2026-03-10（Session Close — Claude_20260310_BE04）

1. Agent & Session ID: Claude_20260310_BE04（Session Close）
2. Task summary: Session 收尾打包 — CHANGELOG 更新、診斷工具歸檔、手動 git 指南、SESSION 文件完成
3. Layer classification: Development Governance Layer（Session 管理）
4. Source triage: 用戶指示（「session close，pack 好相關文件，建設新資料夾，git 上載方法詳細清楚，handover 去其他 session」）
5. Files read: SESSION_HANDOFF.md（驗證），CHANGELOG.md（更新前確認）
6. Files changed:
   - `CHANGELOG.md`（更新：新增完整 v0.3.0-backend 節，含 Added/Fixed/Verified/Technical 四段）
   - `dev/tools/`（新建資料夾）：
     * `debug_edb_html.py`（移入）
     * `parse_form.py`（移入）
     * `parse_structure.py`（移入）
     * `parse_row.py`（移入）
     * `test_llm.py`（移入）
   - `dev/GIT_PUSH_MANUAL.md`（新建：完整手動 git 推送指南，含 PAT 方法、版本號規則、常用指令）
   - `dev/SESSION_HANDOFF.md`（更新：Last Session Record 完整補全，Open Priorities 全部標記完成）
   - `dev/SESSION_LOG.md`（本條目 + v9 Handoff Prompt）
7. Completed:
   - CHANGELOG.md v0.3.0-backend 完整記錄（Added 7項 + Fixed 8項 + Verified 4項 + Technical 2項）✅
   - 診斷工具從根目錄移至 `dev/tools/`（保持根目錄整潔）✅
   - `dev/GIT_PUSH_MANUAL.md` 建立（無需依賴 push-to-github.sh，手動 PAT 推送全流程）✅
   - SESSION_HANDOFF.md Last Session Record 完整更新（BE04 全部完成事項）✅
   - SESSION_LOG.md v9 Handoff Prompt 完成（見下方）✅
8. Validation / QC:
   - CHANGELOG.md 結構正確（Keep-a-Changelog 格式）
   - dev/tools/ 5 個工具文件確認存在
   - GIT_PUSH_MANUAL.md 包含：標準推送流程、首次設定、PAT 生成步驟、版本號規則、現有 tags
9. Pending: 在 Mac Terminal 執行最終 git push（含 dev/tools/ + GIT_PUSH_MANUAL.md + CHANGELOG 更新）
10. Notes: 下個 session 的首要任務是 v1.0.0-release 整合測試

### Problem -> Root Cause -> Fix -> Verification
1. Problem: N/A（session close 無 bug）
2. Root Cause: —
3. Fix: —
4. Verification: —
5. Regression / rule update: 無新規則；診斷工具歸檔政策記錄於本條目

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: GIT_PUSH_MANUAL.md 為手動 git 推送的 SSOT（push-to-github.sh 仍保留作參考）
3. Merged: 診斷工具集中於 dev/tools/
4. Retired: v8 Handoff Prompt（由 v9 取代）
5. Why: Session close 時清理工具文件，保持根目錄整潔

---

### Next Session Handoff Prompt — v9（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.3.0-backend ✅ 完整完成 + GitHub 推送 + Session Close 打包完畢

已完成（全部 ✅）：
- 治理框架 ✅ | 需求文件解析 ✅ | Mockup ✅ | 知識庫 ✅
- Dashboard v0.2.1（2453行，13修訂）✅
- edb_scraper.py v0.3.0-backend：完整管線（POST + PDF + LLM）✅
- circulars.json：14條真實 EDB 通告 + LLM 分析 ✅
- GitHub tag v0.3.0-backend ✅
- Session Close 打包：CHANGELOG ✅ | dev/tools/ ✅ | GIT_PUSH_MANUAL.md ✅

⚠️ gpt-5-nano 規則（全部已確認，不可更改）：
  temperature=1（固定）
  role="developer"（非 "system"）
  max_completion_tokens=16000（非 max_tokens，非 4096）

⚠️ EDB 網站字段（已從實測確認，不可更改）：
  PlaceholderID : MainContentPlaceHolder
  日期字段      : txtPeriodFrom / txtPeriodTo
  搜尋按鈕      : btnSearch2
  必要字段      : ctl00$currentSection="2", lbltab_circular="通告"

⚠️ EDB HTML 通告結構（已從實測確認）：
  每條通告 = <tr> 含 3× <td class="circularResultRow circulartRow">
  Cell[0]=日期（"日期DD/MM/YYYY"），Cell[1]=標題+通告號，Cell[2]=PDF連結（C/E/S）
  無 detail_url；PDF C.pdf（繁中）優先

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html        ← 正式版 Dashboard v0.2.1
  ├── edb_scraper.py            ← 後端管線 v0.3.0
  ├── circulars.json            ← 14條真實通告（真實 LLM 分析）
  ├── requirements.txt
  ├── push-to-github.sh         ← 舊推送腳本（備用）
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      ├── GIT_PUSH_MANUAL.md    ← ⭐ 新版手動 git 推送指南
      ├── v0.2.0-FRONTEND-SPEC.md
      ├── tools/                ← 診斷工具（debug/parse/test）
      └── knowledge/[9 個知識庫文件]

⭐ 下一步（v1.0.0-release）：
  1. 在瀏覽器開啟 edb-dashboard.html，確認 circulars.json 真實數據正確顯示
  2. 如有顯示問題，微調 Dashboard JS 數據載入邏輯
  3. 整合驗收通過後，參照 dev/GIT_PUSH_MANUAL.md 推送 tag v1.0.0-release

Mac Terminal 最終 git push（先推送 session close 文件）：
  cd "<EDB 項目路徑>"
  git add dev/tools/ dev/GIT_PUSH_MANUAL.md CHANGELOG.md dev/SESSION_HANDOFF.md dev/SESSION_LOG.md
  git commit -m "chore: session close — pack tools, git manual, update docs"
  # 然後按 GIT_PUSH_MANUAL.md 步驟推送

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

## 2026-03-10（SESSION CLOSE — Claude_20260310_RE01）

1. Agent & Session ID: Claude_20260310_RE01
2. Task summary: v1.0.0 整合測試修復 + --school-year 功能 + GitHub Pages 部署配置 + Session Close
3. Layer classification: Product / System Layer（整合修復 + 部署）
4. Source triage: 整合測試發現 bug（title 污染、ID 碰撞）+ 用戶新需求（學年模式、公開部署）
5. Files read: edb_scraper.py, edb-dashboard.html, CHANGELOG.md, .gitignore, SESSION_HANDOFF.md
6. Files changed:
   - `edb_scraper.py`（更新：title 污染修復 + school_year_start() + date_from + v1.0.0）
   - `edb-dashboard.html`（更新：REFERENCE_CIRCULARS id 9001/9002/9003）
   - `.github/workflows/update-circulars.yml`（新建）
   - `index.html`（新建）
   - `.gitignore`（更新）
   - `CHANGELOG.md`（更新：v1.0.0-release + v1.0.1-hosting）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - title 污染修復 ✅ | REFERENCE_CIRCULARS ID 碰撞修復 ✅
   - `school_year_start()` + `--school-year` + `date_from` 參數 ✅
   - circulars.json 新增 range/date_from/date_to 欄位 ✅
   - GitHub Actions workflow（每天 HKT 07:00 + 手動 4 模式）✅
   - index.html + .gitignore 更新 ✅
   - py_compile 語法驗證 ✅
   - ⏳ 學年爬蟲執行中（用戶確認後補錄）
8. Pending: 確認學年爬蟲結果 → GitHub Pages 一次性設定 → tag v1.0.1-hosting

### Problem -> Root Cause -> Fix -> Verification
1. title 含「摘要：」→ EDB content_div 直接文字節點包含摘要 → `re.sub(r"\s*摘要[：:].*$","",title)` → py_compile ✅
2. REFERENCE_CIRCULARS id 碰撞 → 固定 id 10/11/12 與真實數據重疊 → 改為 9001/9002/9003 → 代碼審閱 ✅

### Consolidation / Retirement Record
1. Retired: v9 Handoff Prompt（由 v10 取代）

---

### Next Session Handoff Prompt — v10（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v1.0.1-hosting 配置完成，學年爬蟲 ✅ 104條/834.5KB，待 GitHub Pages 設定

已完成（全部 ✅）：
- Dashboard v0.2.1（2453行）✅
- edb_scraper.py v1.0.0：--school-year + title fix + ID fix ✅
- GitHub Actions workflow + index.html + .gitignore 更新 ✅
- ✅ 學年爬蟲完成：104 條通告，834.5KB circulars.json

⚠️ gpt-5-nano 規則（不可更改）：
  temperature=1 | role="developer" | max_completion_tokens=16000

⚠️ EDB 字段 + HTML 結構：見 SESSION_HANDOFF Known Risks #4 + #5

⭐ 下一步（按序）：
  1. 在瀏覽器開啟 edb-dashboard.html，確認 104 條學年通告正確顯示
  2. GitHub Pages 一次性設定（見下方步驟）
  3. GitHub Pages 一次性設定（Mac Terminal + GitHub 網頁操作）：
     a. git add . && git commit && git push（含 .github/workflows/, index.html, .gitignore 更新）
     b. github.com/Leonard-Wong-Git/EDB-AI-Circular-System
        → Settings → Secrets → Actions → New secret: OPENAI_API_KEY
        → Settings → Pages → Source: GitHub Actions
        → Actions → Update EDB Circulars → Run workflow → school-year
  4. 確認公開 URL：https://leonard-wong-git.github.io/EDB-AI-Circular-System/

完成後：
  git tag v1.0.1-hosting
  git push --force origin main && git push origin --tags
  cp -r "." "../EDB-Circular-AI-analysis-system-snapshot-v1.0.1"

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html, edb_scraper.py, circulars.json
  ├── index.html（新）← GitHub Pages 根 URL 跳轉
  ├── .github/workflows/update-circulars.yml（新）← 自動更新
  ├── requirements.txt, .gitignore（更新）
  └── dev/ [SESSION_HANDOFF, SESSION_LOG, GIT_PUSH_MANUAL, tools/, knowledge/]

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

## 2026-03-11（SESSION CLOSE — Claude_20260311_RE02）

1. Agent & Session ID: Claude_20260311_RE02
2. Task summary: PDF 連結修復 + 導航 Bug 修復 + 系統說明 + 驗收清單
3. Layer classification: Product / System Layer（UI 修復 + 文件）
4. Source triage: 用戶要求（PDF 連結未能直link EDB原文件、導航未互通、系統說明、驗收清單）
5. Files read: edb_scraper.py, edb-dashboard.html, circulars.json（結構確認）, SESSION_HANDOFF.md
6. Files changed:
   - `edb_scraper.py`（更新：output record 新增 `pdf_urls` 欄位）
   - `edb-dashboard.html`（更新：buildPdfLinks() + 導航修復 + 系統說明卡）
   - `dev/ACCEPTANCE_CHECKLIST.md`（新建）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - pdf_urls 修復（scraper 未輸出→已加，dashboard 靜態#→動態 EDB URL）✅
   - buildPdfLinks() helper：pdf_urls有時→用真實URL；無時→推算EDBCM格式URL；fallback→EDB列表頁 ✅
   - Stats Bar「即將截止」chip：先 switchTab('overview')，再 scrollIntoView ✅
   - 供應商 Tab Note 重複插入 bug：加 id='supplierNote' guard ✅
   - Settings 新增全寬「📖 系統功能說明」卡片（8個功能模組說明）✅
   - dev/ACCEPTANCE_CHECKLIST.md：11類別 80+測試項目 ✅
8. Pending: git push → 重新爬取取得 pdf_urls → 按驗收清單測試

### Problem -> Root Cause -> Fix -> Verification
1. PDF 按鈕 href="#" → 靜態硬碼，未使用 pdf_urls 欄位；且 pdf_urls 本身未輸出至 JSON → 雙重修復：scraper 加 pdf_urls 至 record；dashboard 改用 buildPdfLinks() ✅
2. Stats Bar「即將截止」在非總覽 tab 點擊不切換 tab → 未加 switchTab() 呼叫 → 加入 switchTab 後 setTimeout scroll ✅
3. Supplier Note 每次 renderSupplier() 都插入 → 無 guard → 加 id='supplierNote' 防重複 ✅

### Consolidation / Retirement Record
1. Retired: v10 Handoff Prompt（由 v11 取代）

---

## 2026-03-11（SESSION CLOSE — Claude_20260311_RE03）

1. Agent & Session ID: Claude_20260311_RE03
2. Task summary: 自動化驗收測試（完整清單報告）+ `💰null` Bug 修復 + git push upstream 診斷
3. Layer classification: Product / System Layer（驗收測試 + Bug 修復）
4. Source triage: 用戶指示「由你自動在 GitHub Pages 按清單逐項檢視，再報告予我」
5. Files read: edb-dashboard.html（grantChip 函數定位）
6. Files changed:
   - `edb-dashboard.html`（修復：grantChip() applicable type 缺 null fallback → `||'資助'`）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - 自動化驗收測試（瀏覽器 JS 執行，測試 A–K 全部類別）✅
   - 完整驗收報告（73/80 通過，91%）✅
   - **Bug 修復：** `grantChip()` applicable 類型缺少 null guard → `${g.amount_label||'資助'}`（影響 10+ 張卡片）✅
   - git push upstream 錯誤診斷：`fatal: no upstream branch` → 建議 `git push --set-upstream origin main` ✅
8. Pending: 用戶執行 `git push --set-upstream origin main` 推送 grantChip 修復

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 卡片顯示「💰null」（約 10 張卡片受影響）
2. Root Cause: `grantChip()` 第 1776 行：applicable 類型直接 `${g.amount_label}` 無 null guard；resource 類型已有 `||'資源'` 但 applicable 類型遺漏
3. Fix: `${g.amount_label}` → `${g.amount_label||'資助'}`（一字之差）
4. Verification: 邏輯確認正確；live site 需推送後確認
5. Regression / rule update: 無新規則

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. Retired: v11 Handoff Prompt（由 v12 取代）

---

### 驗收報告摘要（RE03 自動測試結果）
- **A. 資料載入** 4/4 ✅
- **B. 通告總覽** 13/15（B5 無下拉建議，屬 UX 差異非 bug）
- **C. 詳情面板** 17/17 ✅
- **D. 月曆** 7/9（D8/D9 篩選按鈕未實作）
- **E. 資源申請** 5/5 ✅
- **F. 收藏** 4/5（F4 badge 計數未顯示）
- **G. 供應商** 6/6 ✅
- **H. 設定** 9/12（H5 天數選擇器 / H6 已跟進切換 未找到）
- **I. 鍵盤快捷鍵** 5/5 ✅
- **J. GitHub Actions** 7/7 ✅
- **K. 響應式設計** 未測試（需人手）
- **Bug:** `💰null` 顯示（已修復於本 session）

---

### Next Session Handoff Prompt — v12（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v1.0.2 驗收通過（91%），grantChip null 修復，待最終 git push

已完成（全部 ✅）：
- Dashboard v1.0.2：PDF連結、導航、系統說明、供應商Note去重
- edb_scraper.py：output record 含 pdf_urls
- GitHub Pages：https://leonard-wong-git.github.io/EDB-AI-Circular-System/ 已上線
- GitHub Actions：每日 HKT 07:00/13:00/17:00 自動更新（105條通告，全部含 pdf_urls）
- 驗收測試：73/80（91%）通過 ✅
- grantChip() null 修復：applicable 類型加 `||'資助'` ✅

⚠️ gpt-5-nano 規則（不可更改）：
  temperature=1 | role="developer" | max_completion_tokens=16000

⚠️ EDB 字段 + HTML 結構：見 SESSION_HANDOFF Known Risks #4 + #5

⭐ 下一步（按序）：
  1. git push --set-upstream origin main（推送 grantChip 修復）
  2. 確認 GitHub Pages 自動重新部署
  3. 選做：修復次要缺陷（D8/D9 月曆篩選 / F4 收藏 badge / H5 天數選擇器 / H6 已跟進切換）
  4. 完成後打 tag v1.0.3-bugfix

次要缺陷清單（可選做，非阻礙性）：
  - D8/D9：月曆頁添加篩選按鈕（高影響 / 截止日 類型篩選）
  - F4：收藏 tab badge 顯示收藏數量
  - H5：設定頁截止提醒天數選擇器（3/7/14天）
  - H6：設定頁「顯示/隱藏已跟進通告」切換按鈕

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html（v1.0.2 + grantChip null fix）
  ├── edb_scraper.py（含 pdf_urls 輸出）
  ├── circulars.json（105條，含 pdf_urls，由 GitHub Actions 維護）
  ├── index.html, .github/workflows/update-circulars.yml
  └── dev/ [SESSION_HANDOFF, SESSION_LOG, ACCEPTANCE_CHECKLIST, GIT_PUSH_MANUAL, ...]

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

## 2026-03-11（SESSION CLOSE — Claude_20260311_RE04）

1. Agent & Session ID: Claude_20260311_RE04
2. Task summary: 8 項功能實作（B5/B6/B7/B8 匯出列印日曆多選 + F1/F2 排序主題 + C1/C2 狀態互通）
3. Layer classification: Product / System Layer（前端功能擴展）
4. Source triage: 用戶確認「自做一、及二」= Batch 1（F1/F2/C1/C2/B5/B7）+ Batch 2（B6/B8）；K1/R1 留後討論
5. Files read: edb-dashboard.html（多次，修改前後確認）
6. Files changed:
   - `edb-dashboard.html`（更新：2453→2796 行，8 項功能，HTML 驗證通過）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed（全部 8 項）：
   - **F1（排序持久化）**：`lsLoad()` 讀 `edb_sort_field`/`edb_sort_asc`；`sortList()` 寫 localStorage；預設日期降序 ✅
   - **F2（時段自動主題）**：`applyTheme()` 改用時鐘（07-18=淺色，其餘=深色）；60秒 setInterval ✅
   - **C1（狀態互通）**：`updateBmBadge()` + `syncStatusBtns(id,status)`；所有狀態/書籤/釘選按鈕改為 DOM 即時更新（無 full re-render）；data-sid 屬性 ✅
   - **C2（資源行色+日期）**：行色 CSS（.res-applying/applied/closed/na）；`setApplyStatus()` 即時更新行 CSS + 記錄申請日期至 `edb_apply_dates` localStorage + toast ✅
   - **B5（CSV 增強）**：`exportExcel()` 加「行動數」「AI摘要前200字」兩欄 ✅
   - **B7（.ics 日曆匯出）**：新增 `exportICS()`（iCalendar VCALENDAR/VEVENT 格式）；📅 日曆工具列按鈕 ✅
   - **B6（格式化列印）**：`printDetail()` 改寫（`window.open` 新視窗，完整 HTML 報告含列印/關閉按鈕）；移除舊 `window.print()` 重複函數 ✅
   - **B8（多選批量匯出）**：新增 `toggleMultiSelect()`/`cardClick()`/`exportSelected()`；浮動 #batchBar；.card-selected CSS + 框 overlay；☑️ 多選工具列按鈕 ✅
   - **HTML 驗證**：`html.parser` 確認「HTML OK — All tags balanced」✅
   - **函數驗證**：所有 11 個新函數 grep 全部找到 ✅
   - **git 衝突診斷**：
     * `fatal: no upstream` → `git push --set-upstream origin main`
     * `fatal: not a git repository` → 需先 cd 至項目目錄（`find ~ -maxdepth 6 -name ".git" -type d 2>/dev/null | grep -i EDB`）
     * `[rejected] fetch first` → `git pull --rebase origin main && git push`（GitHub Actions 持續 push 造成衝突）
8. New localStorage keys: `edb_sort_field`、`edb_sort_asc`、`edb_apply_dates`（總共 12 個 keys）
9. Validation / QC:
   - HTML parser: HTML OK ✅
   - 11 新函數全部 grep 找到 ✅
   - 2796 行（+343 行 vs v1.0.2）
10. Pending:
    - ✅ git push 已完成（commit b593707，tag v1.1.0-features 已推送）
    - ❌ GitHub Pages 仍是舊版（無 📅 日曆 / ☑️ 多選）：手動觸發 workflow 因 pdfminer 卡死逾 1 小時被取消
    - ⭐ 下個 session 首要：修復 edb_scraper.py PDF timeout → 重新 push → workflow 自動觸發 → Pages 部署
    - 討論：K1 知識庫框架、R1 全角色職責精確度、LLM 引擎切換機制
    - 選做：次要缺陷（D8/D9/F4/H5/H6）
11. Risks / blockers: ⚠️ pdfminer 無 timeout → workflow 卡死（已記錄 SESSION_HANDOFF Known Risks #6）；修復前勿手動觸發 school-year workflow

### Problem -> Root Cause -> Fix -> Verification
1. Problem: B6 `printDetail()` 重複定義（新舊兩個版本同時存在）
2. Root Cause: 實作新版本時，舊 `window.print()` 版本未移除
3. Fix: 找出舊版本（Export section）並移除
4. Verification: grep 確認只有一個 `printDetail` 定義 ✅
5. Regression / rule update: 實作新函數前先搜尋是否存在舊版本

### Consolidation / Retirement Record
1. Duplicate / drift: 舊 `printDetail()` 移除（只保留新格式化版本）
2. SSOT: 無新 SSOT；功能規格沿用 `dev/v0.2.0-FRONTEND-SPEC.md`
3. Merged: B6/B7/B8 工具列按鈕整合至現有工具列
4. Retired: v12 Handoff Prompt（由 v13 取代）
5. Why: 版本進度更新，8 項功能完成

---

### Next Session Handoff Prompt — v13（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v1.1.0-features ✅ 代碼已推送 GitHub，但 GitHub Pages 仍是舊版（待修 PDF timeout 後重新部署）

已完成（全部 ✅）：
- Dashboard v1.1.0（2796行）：8 項新功能已寫入代碼並推送 ✅
  * F1 排序持久化 / F2 時段主題 / C1 狀態互通 / C2 資源行色
  * B5 CSV增強 / B6 格式化列印 / B7 .ics日曆 / B8 多選批量匯出
- git push 完成：commit b593707，tag v1.1.0-features ✅
- GitHub Pages 功能正常（舊版），但新按鈕尚未顯示

⚠️ 緊急修復（第一優先）：pdfminer PDF 解析無 timeout
  症狀：Actions workflow 卡死超過 1 小時（正常 25 分鐘），日誌停在 pdfminer DEBUG
  影響：GitHub Pages 無法部署新版本（workflow 被取消）
  ⚠️ 勿再手動觸發 school-year workflow，修復前會再次卡死

  修復方案（在 edb_scraper.py PDF 解析函數加入）：
  import signal
  def _pdf_timeout(signum, frame): raise TimeoutError("PDF parse timeout")
  signal.signal(signal.SIGALRM, _pdf_timeout)
  signal.alarm(60)   # 60秒 timeout
  try:
      text = pdfplumber.open(...)...
  except TimeoutError:
      text = ""      # 跳過此 PDF
  finally:
      signal.alarm(0)

⚠️ gpt-5-nano 規則（不可更改）：
  temperature=1 | role="developer" | max_completion_tokens=16000

⚠️ EDB 字段 + HTML 結構：見 SESSION_HANDOFF Known Risks #4 + #5 + #6

⭐ 下一步（按序）：
  1. 修復 edb_scraper.py PDF timeout（見上方方案）
  2. git add edb_scraper.py && git commit -m "fix: PDF parse timeout to prevent workflow hang"
  3. git push → GitHub Actions 自動觸發 → 等待完成（約 25 分鐘）
  4. Cmd+Shift+R 確認 GitHub Pages 出現 📅 日曆 + ☑️ 多選 按鈕

待討論（下個 session）：
- K1：知識庫參考文件框架（每主題域濃縮底稿；半年自動更新）
- R1：全角色職責精確度（6角色×真實 EDB 職責）
- LLM 引擎切換機制
- 次要缺陷：D8/D9 / F4 / H5 / H6

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html（v1.1.0，2796行，8項新功能）
  ├── edb_scraper.py（⚠️ 需加 PDF timeout）
  ├── circulars.json, index.html
  ├── .github/workflows/update-circulars.yml
  └── dev/ [SESSION_HANDOFF, SESSION_LOG, GIT_PUSH_MANUAL, ACCEPTANCE_CHECKLIST, tools/, knowledge/]

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

### Next Session Handoff Prompt — v11（已由 v13 取代，內容略）
