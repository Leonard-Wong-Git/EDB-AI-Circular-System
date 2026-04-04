# Session Log
<!-- Archives: dev/archive/ — entries moved when >800 lines or oldest entry >30 days -->

## 2026-04-04 Curriculum-aware Knowledge Review Extension + v3.0.9

1. Agent & Session ID: Codex_20260404_0008
2. Task summary: 依使用者同意，將 deterministic 第二輪 knowledge review 由 supplier 擴展到 curriculum 類通告，加入課程用語標準化、課程落實提醒與官方參考連結；workspace 版本升級到 `v3.0.9`，但本 session 未宣稱已 live。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 非 bug fix；屬既有 post-analysis enrichment 的 topic-aware 擴展。目標是提升 curriculum 類通告使用度，同時保持 deterministic / non-destructive。
5. Files read: `AGENTS.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`
6. Files changed: `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 確認 `edb_scraper.py` 已加入 `POST_REVIEW_CURRICULUM_KEYWORDS`
   - ✅ 確認第二輪 review 會在 curriculum 類訊號下補充課程落實 / 校本安排提醒
   - ✅ 確認 curriculum 類會加上課程發展指引與 KPM 連結
   - ✅ 確認本地版本標記已升至 `v3.0.9`
   - ✅ 同步更新 README / handoff / context，避免治理文件仍停留在 `v3.0.8`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - inline helper check using a curriculum-style sample → PASS
   - `rg -n "POST_REVIEW_CURRICULUM_KEYWORDS|CURRICULUM_RECOMMENDED_LINKS|_apply_post_analysis_review|v3\\.0\\.9" edb_scraper.py edb-dashboard.html` → PASS
9. Pending:
   - 如需上線，deploy / push `v3.0.9`
   - 等待用戶提供新版 `role_facts.json`
   - 決定下一個擴展 topic（finance / student / hr）
10. Next priorities:
   - 視需要發佈 `v3.0.9`
   - 等待 / 整合新版 role_facts.json
   - 決定下一個擴展 topic
11. Risks / blockers:
   - 第二輪 review 雖已擴展到 curriculum，但仍不可覆蓋 deadline、金額、編號、scope 等硬事實
   - README 描述已更新為 `v3.0.9` 功能說明，但這不代表 live site 已部署到 `v3.0.9`
12. Notes:
   - 本次 PERSIST 主要是把已完成的 workspace 變更正式記錄下來，避免之後 session 仍誤以為第二輪 review 只支援 supplier

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - supplier-only 的第二輪 review 使用面太窄，使用者希望 curriculum 類通告也可受益。
2. Root Cause:
   - handoff / log / context 仍停留在 `v3.0.8 supplier-only` 的描述，而 workspace 已存在未持久化的 curriculum 擴展。
3. Fix:
   - 確認並保留現有 curriculum 擴展實作，然後同步更新 README、CODEBASE_CONTEXT、SESSION_HANDOFF、SESSION_LOG。
4. Verification:
   - py_compile PASS；curriculum helper check PASS；local version markers PASS。
5. Regression / rule update:
   - 無新增長期治理規則；沿用既有 `Analysis pipeline behavior change` doc-sync row。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | curriculum 類通告，summary 含 `學與教資源` | 套用 `_apply_post_analysis_review` | 用詞標準化，補課程落實提醒與 curriculum links | helper check 顯示 summary 正常替換並加入 curriculum links | PASS |
| Boundary | 原 analysis 未標記全部 curriculum 角色 | 套用 `_apply_post_analysis_review` | principal / vice_principal / department_head / teacher 可按規則標為相關 | helper check 顯示 `vice_principal` 被自動標為相關 | PASS |
| Failure path guard | 通告含課程訊號但硬事實已存在 | 套用 review | 不改 deadline / 金額 / 編號 / scope | helper check 只改 summary / roles / knowledge_review | PASS |
| Regression | 既有 supplier review 路徑仍在 | 搜尋關鍵實作與版本標記 | supplier / curriculum 規則並存，版本標記一致 | `rg` 顯示 procurement + curriculum review constants / functions 均存在 | PASS |

Overall: PASS

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from the local v3.0.9 workspace, where deterministic post-analysis knowledge review now covers both supplier and curriculum signals. This state has been documented locally but has not yet been pushed/deployed in this session.

Pending tasks (priority order):
1. If the user wants v3.0.9 live, deploy/push the current workspace and verify GitHub Pages / output artifacts after publish.
2. If the user provides a new `role_facts.json`, integrate it to replace `dev/knowledge/role_facts.json` and validate the K1 interface.
3. Decide the next topic-aware review extension after curriculum (likely finance / student / hr), while keeping the second-pass review deterministic and non-destructive.

Key files changed in this session:
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- The second-pass review now covers supplier + curriculum, but it still must not overwrite hard facts such as dates, amounts, scope, or circular number.
- README now documents v3.0.9 behavior, but that does not mean GitHub Pages is already live at v3.0.9.
- During future deploys, if the only rebase conflict is on `circulars.json`, preserve the newer remote data.

Validation status: py_compile PASS; curriculum helper check PASS; local version markers PASS at v3.0.9; no deploy performed in this session.

Post-startup first action: confirm whether the user wants to publish v3.0.9 now, or continue directly into the next knowledge-review extension / role_facts integration.
```

## 2026-04-04 Publish v3.0.8 (Value-add Only)

1. Agent & Session ID: Codex_20260404_0007
2. Task summary: 依使用者要求，將 `v3.0.8` 發布上線，並保持這次只是加值功能，不再升版、不擴大改動範圍。
3. Layer classification: Product / System Layer（release publish）+ Development Governance Layer（session persistence）
4. Source triage: 非新功能開發；屬已完成 workspace 狀態的發布。關鍵要求是固定版本為 `v3.0.8`，不要再 bump。
5. Files read: `dev/tools/publish_release.py`, `deploy.sh`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 以 `deploy.sh --no-bump` 發布，版本保持 `v3.0.8`
   - ✅ deploy repo push 成功：commit `3e0a581`
   - ✅ live GitHub Pages fetched and confirmed at `v3.0.8`
   - ✅ 保持本次定位為加值功能發布，未再擴大改動範圍
8. Validation / QC:
   - `python3 dev/tools/publish_release.py --no-bump --dry-run` → PASS
   - `git -C ~/Documents/EDB-AI-Circular-System status --short --branch` → clean after push
   - `curl -L https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html | rg -n "v3\\.0\\.[0-9]+"` → all visible markers `v3.0.8`
9. Pending:
   - 等待用戶提供新版 `role_facts.json`
   - 視需要把 `knowledge_review` 顯示到 dashboard
10. Next priorities:
   - 等待 / 整合新版 role_facts.json
   - 顯示 `knowledge_review` 到 dashboard
   - 擴展第二輪 review 到更多角色
11. Risks / blockers:
   - 第二輪 review 目前仍只聚焦 supplier enrichment
   - 未來 deploy 仍需留意 remote `circulars.json` 可能較新
12. Notes:
   - 使用者特別要求「只是加值功能，其他不能更改」，因此本次用 `--no-bump` 發布既有 `v3.0.8`

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 需要把 `v3.0.8` 上線，但不能因自動發佈流程再升版或混入額外範圍。
2. Root Cause:
   - `deploy.sh` 預設會做 patch bump；若直接執行會變成 `v3.0.9`。
3. Fix:
   - 使用 `deploy.sh --no-bump` 發布目前 workspace。
4. Verification:
   - dry run 顯示 current/target 都是 `v3.0.8`；push 成功；live HTML all markers = `v3.0.8`
5. Regression / rule update:
   - 無新增治理規則；沿用既有發布腳本參數能力。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from v3.0.8, which is already live on GitHub Pages. This release added the first runnable post-analysis knowledge review as a value-add feature without changing the core hard-fact handling logic.

Pending tasks (priority order):
1. If the user provides a new `role_facts.json`, integrate it to replace `dev/knowledge/role_facts.json` and validate the K1 interface.
2. If the user wants the new enrichment visible in UI, surface `knowledge_review` in the dashboard detail view.
3. If expanding beyond supplier, keep the second-pass review deterministic and non-destructive.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- The post-analysis review must not overwrite hard facts such as dates, amounts, scope, or circular number.
- `knowledge_review` is in the JSON output but is not yet specially rendered by the dashboard.
- During future deploys, remote `circulars.json` may be newer than the workspace copy; preserve the newer remote data if that is the only rebase conflict.

Validation status: deploy dry run PASS; deploy repo push PASS; live GitHub Pages fetch PASS and confirmed v3.0.8.

Post-startup first action: confirm whether the user wants to work on `role_facts.json` integration next, or to expose `knowledge_review` in the dashboard UI.
```

## 2026-04-04 Runnable Knowledge Review Integration + v3.0.8

1. Agent & Session ID: Codex_20260404_0006
2. Task summary: 將模擬版第二輪 knowledge review 正式接入 `edb_scraper.py`，做 supplier-focused deterministic normalization / enrichment；版本升級到 `v3.0.8`。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 非 bug fix；屬既有 AI 分析流程的後置 enrichment 行為新增。目標是先上第一個 runnable 版，而非全面重做 prompt。
5. Files read: `edb_scraper.py`, `edb-dashboard.html`, `dev/SESSION_HANDOFF.md`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/CODEBASE_CONTEXT.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `_apply_post_analysis_review(circ)` 到 `edb_scraper.py`
   - ✅ primary analysis 成功後，會自動執行第二輪 deterministic review
   - ✅ reused existing analysed records 時，也會套用 deterministic review
   - ✅ 輸出新增 `knowledge_review` 欄位
   - ✅ supplier 場景自動補 `eligibility`、`contact_unit`、`compliance_ref`
   - ✅ supplier 場景自動附加 `recommended_links`
   - ✅ 版本升級：`v3.0.7` → `v3.0.8`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py dev/tools/simulate_post_analysis_review.py` → PASS
   - helper check via inline Python → PASS
   - `python3 dev/tools/simulate_post_analysis_review.py` → PASS
   - `rg -n "v3\\.0\\.8|knowledge_review|_apply_post_analysis_review|recommended_links|eligibility|contact_unit" edb_scraper.py edb-dashboard.html` → PASS
9. Pending:
   - 若用戶要正式上線，deploy/push `v3.0.8`
   - 等待用戶提供新版 `role_facts.json`
   - 視需要把第二輪 review 擴展到其他角色
10. Next priorities:
   - deploy/push `v3.0.8`
   - 等待 / 整合新版 role_facts.json
   - 擴展 deterministic review 到更多角色
11. Risks / blockers:
   - 第二輪 review 必須維持 non-destructive；不可覆蓋 deadline、金額、編號等硬事實
   - 目前 enrichment 主要集中 supplier，其他角色仍未擴展
12. Notes:
   - 這個版本先把最清晰、最容易觀察效果的 supplier path 做通
   - `knowledge_review` 暫時寫入 JSON；前端尚未專門顯示該 block

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者已確認方向，希望把第二輪知識校正從模擬變成第一個可運行版。
2. Root Cause:
   - 現有 pipeline 只有 primary AI analysis，沒有正式的 post-analysis review stage。
3. Fix:
   - 在 `edb_scraper.py` 新增 deterministic review helper，於 primary analysis 之後執行。
   - review 目前負責 ordered terminology normalization、missing-point enrichment、recommended links、supplier role stabilization。
4. Verification:
   - py_compile PASS；inline helper verification PASS；simulation PASS。
5. Regression / rule update:
   - 無新增長期治理規則；doc sync registry 新增 `Analysis pipeline behavior change` row。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | 採購/供應商相關通告，supplier 已標記相關 | 套用 `_apply_post_analysis_review` | 用詞標準化 + 補 `eligibility/contact_unit/compliance_ref` + links | helper check 顯示補齊與標準化均成功 | PASS |
| Boundary | 已分析舊記錄被 reuse | 進入 existing-summary skip path | 不重跑 LLM 也能套用 deterministic review | skip path 現已呼叫 `_apply_post_analysis_review` | PASS |
| Failure path guard | review 不應覆蓋硬事實 | 套用 review | 不改 deadline/金額/編號等欄位 | helper 只改 summary/roles/actions/knowledge_review | PASS |
| Regression | 模擬工具仍可運行 | 執行 `simulate_post_analysis_review.py` | 模擬輸出仍可觀察 before/after | script 執行成功 | PASS |

Overall: PASS

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from the first runnable post-analysis knowledge review integration. Workspace is now at v3.0.8, and `edb_scraper.py` includes a deterministic second-pass review after primary AI analysis.

Pending tasks (priority order):
1. If the user wants this live, deploy/push v3.0.8 and verify the updated output on GitHub Pages / generated JSON.
2. If the user provides a new `role_facts.json`, integrate it to replace `dev/knowledge/role_facts.json` and validate the K1 interface.
3. If expanding the review layer, keep it deterministic and non-destructive; extend beyond supplier only after verifying the current supplier path.

Key files changed in this session:
- `edb_scraper.py`
- `edb-dashboard.html`
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/DOC_SYNC_CHECKLIST.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- The post-analysis review must not overwrite hard facts such as dates, amounts, scope, or circular number.
- `knowledge_review` is written to JSON but is not yet specially rendered by the dashboard.
- During future deploys, remote `circulars.json` may still be newer than the workspace copy; preserve the newer remote data if that is the only rebase conflict.

Validation status: py_compile PASS; helper-based review check PASS; simulation PASS; version markers updated to v3.0.8.

Post-startup first action: decide with the user whether to deploy/push v3.0.8 now, or continue with `role_facts.json` / broader knowledge-review expansion first.
```

## 2026-04-04 Post-analysis Knowledge Review Simulation

1. Agent & Session ID: Codex_20260404_0005
2. Task summary: 依使用者確認的方向，先做一個 deterministic 模擬，驗證在 primary AI analysis 之後加一層 knowledge review 是否可行。
3. Layer classification: Product / System Layer（analysis pipeline prototype）+ Development Governance Layer（session persistence）
4. Source triage: 非 bug fix；屬新行為模擬。目標是先驗證第二輪 review 的 shape，而不是直接改 production scraper。
5. Files read: `edb_scraper.py`, `dev/knowledge/fin_management_supplier.md`, `dev/knowledge/icac_reference.md`, `dev/knowledge/press_releases_supplier.md`, `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `dev/tools/simulate_post_analysis_review.py`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `dev/tools/simulate_post_analysis_review.py`
   - ✅ 模擬 ordered terminology normalization
   - ✅ 模擬 missing-point enrichment：supplier `eligibility` / `contact_unit` / `compliance_ref`
   - ✅ 模擬 recommended links：EDB 財務管理（供應商）+ ICAC 採購參考
   - ✅ 模擬 role-drift 守門條件（採購/供應商 keyword）
8. Validation / QC:
   - `python3 dev/tools/simulate_post_analysis_review.py` → PASS
   - `python3 -m py_compile dev/tools/simulate_post_analysis_review.py` → PASS
   - 模擬輸出顯示 before/after、`terminology_review`、`knowledge_review`、`feasibility_assessment`
9. Pending:
   - 若用戶同意，把第二輪 review 接入 `edb_scraper.py`
   - 等待用戶提供新版 `role_facts.json`
10. Next priorities:
   - 接入 knowledge review 第二輪
   - 等待 / 整合新版 role_facts.json
   - 驗證下一次自動發布流程穩定性
11. Risks / blockers:
   - 正式接入前，必須限制第二輪只做補充/標準化，不可覆蓋 deadline、金額、編號等硬事實
   - 目前 simulation 是 deterministic prototype，尚未覆蓋所有角色與所有 topic
12. Notes:
   - 這個 prototype 特別對準 supplier 場景，因為現有知識檔最完整，也最容易觀察補漏/補連結效果

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者想先看到「AI 首輪分析後，再接入知識庫意見」的可行性，而不是直接改正式流程。
2. Root Cause:
   - 現有 `edb_scraper.py` 只有 primary analysis，knowledge 主要用於第一輪 prompt 注入，沒有獨立的 post-analysis review stage。
3. Fix:
   - 新增 `dev/tools/simulate_post_analysis_review.py`，用 sample circular + sample analysis 模擬第二輪 review。
4. Verification:
   - script 成功輸出 before/after JSON，顯示 ordered terminology normalization、missing-point enrichment、recommended links、role-drift note。
5. Regression / rule update:
   - 無新增長期規則；僅記錄 prototype 已建立，可作下一步接入基礎。

## 2026-04-04 Auto Publish Flow + v3.0.7 Live

1. Agent & Session ID: Codex_20260404_0004
2. Task summary: 實作自動發布流程，讓 `deploy.sh` 可自動 patch version bump、同步 workspace 至 deploy repo、commit、push，並透過 push-triggered GitHub Actions 令 GitHub Pages 生效；本次成功發布至 live `v3.0.7`。
3. Layer classification: Product / System Layer（deploy workflow / release automation）+ Development Governance Layer（session persistence）
4. Source triage: 問題屬部署流程缺口，而非產品邏輯 bug。原 `deploy.sh` 只在 deploy repo 內 `pull/push`，沒有同步 workspace、沒有版本 bump、也沒有自動觸發 Pages 生效。
5. Files read: `deploy.sh`, `dev/GIT_PUSH_MANUAL.md`, `.github/workflows/update-circulars.yml`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `edb-dashboard.html`, `edb_scraper.py`
6. Files changed: `dev/tools/publish_release.py`, `deploy.sh`, `.github/workflows/update-circulars.yml`, `edb-dashboard.html`, `edb_scraper.py`, `README.md`, `dev/GIT_PUSH_MANUAL.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `dev/tools/publish_release.py`
   - ✅ `deploy.sh` 改為調用自動發布腳本
   - ✅ push 到 `main` 時，workflow 現可直接部署 Pages；push event 會跳過 scraper / circulars commit steps
   - ✅ 自動版本升級成功：`v3.0.5` → `v3.0.7`
   - ✅ deploy repo push 成功：commit `3047c10`
   - ✅ GitHub Pages live fetch 確認已上線 `v3.0.7`
8. Validation / QC:
   - `python3 dev/tools/publish_release.py --dry-run` → PASS（預覽 `v3.0.5` → `v3.0.6`，後續實際發布到 `v3.0.7`）
   - `python3 -m py_compile dev/tools/publish_release.py` → PASS
   - `git -C ~/Documents/EDB-AI-Circular-System status --short --branch` → `main...origin/main`
   - `curl -L https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html | rg -n "v3\\.0\\.[0-9]+"` → live markers all `v3.0.7`
9. Pending:
   - 等待用戶提供新版 `role_facts.json`
   - 下一次發布時觀察 `circulars.json` conflict 是否再現
10. Next priorities:
   - 等待 / 整合新版 role_facts.json
   - 驗證下一次自動發布流程穩定性
   - 視需要補充 v3.0.7 發布說明
11. Risks / blockers:
   - remote `circulars.json` 可能比 workspace 新；若發布的是 code/docs，rebase conflict 時需保留較新的 remote data
   - `publish_release.py` 目前預設 patch bump；若之後要 minor/major bump，需擴充參數
12. Notes:
   - 第一次 sandbox 執行被 Documents 寫入權限阻擋，之後以批准方式完成
   - rebase 衝突僅出現在 `circulars.json`；本次以 remote 較新資料為準繼續發布

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者希望「自動更新 version number 及 upload GitHub 使生效」，但現有 `deploy.sh` 只做 deploy repo 內的 `pull/push`。
2. Root Cause:
   - 缺少 workspace → deploy repo 的同步步驟、缺少版本 bump、自動部署亦未由 push 觸發。
3. Fix:
   - 新增 `publish_release.py` 處理 patch bump、同步、commit、rebase、push。
   - `deploy.sh` 改為一鍵調用該腳本。
   - workflow 新增 `push` trigger，並在 push event 下跳過 scraper-only steps。
4. Verification:
   - dry run、語法檢查、deploy repo 狀態、live GitHub Pages HTML 均已驗證成功。
5. Regression / rule update:
   - 無新增 AGENTS 長期規則；僅在 doc-sync registry 補充 `Deploy / release workflow change` row。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal publish | workspace at `v3.0.5`, deploy repo exists | `bash deploy.sh` | patch version bump + sync + commit + push + Pages live update | `v3.0.7` pushed as commit `3047c10`; live HTML shows `v3.0.7` | PASS |
| Boundary dry run | workspace ready, no write wanted | `python3 dev/tools/publish_release.py --dry-run` | show current and target versions without writing | reported `v3.0.5` → `v3.0.6`, no writes | PASS |
| Failure path: remote ahead | deploy repo behind remote by one auto-update commit | publish followed by `pull --rebase` | conflict isolated and recoverable without losing newer data | conflict occurred only on `circulars.json`; resolved by keeping remote data | PASS with notes |
| Regression: scraper workflow | push event for code/docs release | GitHub Actions run | deploy Pages without re-running scraper or committing `circulars.json` | workflow updated with `if: github.event_name != 'push'` on scraper-only steps | PASS |

Overall: PASS with notes

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from a working auto-publish baseline. `deploy.sh` now performs patch version bump + sync to deploy repo + commit/push, and GitHub Pages was verified live at v3.0.7 on 2026-04-04.

Pending tasks (priority order):
1. If the user provides a new `role_facts.json`, integrate it to replace `dev/knowledge/role_facts.json` and validate the K1 interface.
2. On the next release, watch for `circulars.json` rebase conflicts. If the conflict is only between workspace data and a newer remote auto-update, keep the newer remote `circulars.json`.
3. If needed, extend `publish_release.py` to support explicit minor/major bumps instead of patch-only.

Key files changed in this session:
- `dev/tools/publish_release.py`
- `deploy.sh`
- `.github/workflows/update-circulars.yml`
- `edb-dashboard.html`
- `edb_scraper.py`
- `README.md`
- `dev/GIT_PUSH_MANUAL.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/DOC_SYNC_CHECKLIST.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- `publish_release.py` currently defaults to patch bump only.
- Remote `circulars.json` may be fresher than the workspace copy during code/docs releases; prefer the newer remote data if that is the only rebase conflict.
- The workspace itself is still not a git repo; deployment continues to rely on the external repo at `~/Documents/EDB-AI-Circular-System`.

Validation status: publish dry run PASS; Python compile PASS; deploy repo pushed cleanly; GitHub Pages live HTML fetched and confirmed at v3.0.7.

Post-startup first action: verify whether the user wants to work on the pending `role_facts.json` / K1 integration next, and if so inspect the current `dev/knowledge/role_facts.json` before changing any API/data-flow code.
```

## 2026-04-04 README K1 API Link Update

1. Agent & Session ID: Codex_20260404_0003
2. Task summary: 依使用者要求，在 README 相關連結區加入 K1 API spec 外部連結，並同步更新治理記錄。
3. Layer classification: Product / System Layer（README 使用者可見文檔更新）+ Development Governance Layer（session persistence）
4. Source triage: 非程式 bug；屬文檔引用更新。無程式碼或部署狀態變更。
5. Files read: `AGENTS.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `README.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/DOC_SYNC_CHECKLIST.md`
7. Completed:
   - ✅ 在 `README.md` 的「相關連結」區新增 `K1 知識庫接口` 連結
   - ✅ 補充 `dev/DOC_SYNC_CHECKLIST.md` row：`README link / reference update`
   - ✅ 更新 handoff / session log，保留目前部署狀態與後續優先事項
8. Validation / QC:
   - `sed -n '1,220p' README.md` → 確認新連結已出現在 `## 🔗 相關連結`
   - 文檔變更僅涉及 README 與治理文件；未修改產品程式碼
9. Pending:
   - deploy workspace `v3.0.5`
   - deploy 後重新抓取 live HTML，確認 `v3.0.5`
   - 若要保持治理完整性，補寫 v3.0.5 的產品層 session record
   - 等待用戶提供新版 `role_facts.json`
10. Next priorities:
   - deploy 並驗證 GitHub Pages v3.0.5
   - 補齊 v3.0.5 產品 session 記錄
   - 等待 / 整合新版 role_facts.json
11. Risks / blockers:
   - live site 仍為 `v3.0.4`
   - 本 workspace 不是 git repo；實際 deploy 仍需沿用外部 repo 流程
12. Notes:
   - Doc Sync: registry updated with `README link / reference update`

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - README 尚未提供 K1 API spec 的直接連結。
2. Root Cause:
   - 現有相關連結區只列出 Live Demo、EDB source、OpenAI API。
3. Fix:
   - 在 `README.md` 的相關連結區加入 `**K1 知識庫接口：** [K1_API_SPEC.md](https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md)`。
4. Verification:
   - README context reread after patch; link present in target section.
5. Regression / rule update:
   - 無新增長期治理規則；僅補齊 doc-sync registry row 以涵蓋 README reference 類型更新。

## 2026-04-04 Startup Verification + Live Deployment Check

1. Agent & Session ID: Codex_20260404_0002
2. Task summary: 依 AGENTS.md §1 重新執行 startup；驗證 workspace `v3.0.5` 內容；連線檢查 GitHub Pages live state，確認目前仍是 `v3.0.4`；用戶要求 closeout。
3. Layer classification: Development Governance Layer（startup / closeout）+ Product / System Layer（deployment state verification）
4. Source triage: 非程式錯誤修復；屬部署狀態確認與 documentation sync。關鍵問題為 live deployment mismatch，而非本地程式碼缺失。
5. Files read: `AGENTS.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `edb_scraper.py`, `edb-dashboard.html`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 完成 mandatory startup reads
   - ✅ 確認 workspace `edb_scraper.py` / `edb-dashboard.html` 均為 `v3.0.5`
   - ✅ 確認 supplier schema fields 包含 `eligibility`、`contact_unit`、`procurement_cat`、`compliance_ref`、`budget_estimate`
   - ✅ 確認 Dashboard Supplier UI 包含 procurement category chart 與 supplier special fields
   - ✅ 實測 GitHub Pages live `edb-dashboard.html` 仍回傳 `v3.0.4`
8. Validation / QC:
   - `rg -n "v3\\.0\\.5|eligibility|contact_unit|procurement_cat|compliance_ref|budget_estimate" edb_scraper.py edb-dashboard.html` → PASS
   - `curl -L https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html | rg -n "v3\\.0\\.[0-9]+"` → live markers all `v3.0.4`
9. Pending:
   - deploy workspace `v3.0.5`
   - deploy 後重新抓取 live HTML，確認 `v3.0.5`
   - 若要保持治理完整性，補寫 v3.0.5 的產品層 session record
   - 等待用戶提供新版 `role_facts.json`
10. Next priorities:
   - deploy 並驗證 GitHub Pages v3.0.5
   - 補齊 v3.0.5 產品 session 記錄
   - 等待 / 整合新版 role_facts.json
11. Risks / blockers:
   - 現時 live site 仍是 `v3.0.4`，不能宣稱 `v3.0.5` 已上線
   - 本 workspace 不是 git repo；實際 deploy 需沿用外部 deploy repo 流程
12. Notes:
   - 使用者貼上的 handoff 說 live 可能已是 `v3.0.5`，但已被 live fetch 否證

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 需要確認 `v3.0.5` 是否已 live，但 handoff 內容與實際 governance state 不完全一致。
2. Root Cause:
   - workspace 已更新到 `v3.0.5`，但 GitHub Pages 尚未同步部署。
3. Fix:
   - 重新執行 startup，直接抓取 live GitHub Pages HTML 驗證版本，而非依賴手動描述。
4. Verification:
   - live HTML fetched successfully; all version markers show `v3.0.4`
5. Regression / rule update:
   - 無新增長期規則；沿用既有「先驗證再宣稱已上線」原則

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: publish and verify workspace v3.0.5. Local files are at v3.0.5, but GitHub Pages was fetched on 2026-04-04 and still served v3.0.4.

Pending tasks (priority order):
1. Deploy the current workspace v3.0.5 through the established external deploy repo / workflow path.
2. After deploy, fetch the live `edb-dashboard.html` again and confirm all visible version markers show v3.0.5.
3. If continuing governance cleanup, add or reconcile the missing product-layer SESSION_LOG documentation for v3.0.5.
4. If the user provides a new `role_facts.json`, integrate it to replace `dev/knowledge/role_facts.json` and validate the K1 interface.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- Do not claim v3.0.5 is live until the fetched GitHub Pages HTML shows it.
- This workspace is not itself a git repo (`git root = none`), so deployment still depends on the external repo workflow.
- The user-provided handoff text in-chat was not authoritative; the live fetch confirmed v3.0.4.

Validation status: startup reads PASS; local v3.0.5 markers confirmed; live GitHub Pages fetch PASS and showed v3.0.4.

Post-startup first action: deploy the workspace v3.0.5 update, then re-fetch the live dashboard HTML to verify the version changed from v3.0.4 to v3.0.5.
```

## 2026-04-04 INIT.md No-op Verification + Session Log Archive Maintenance

1. Agent & Session ID: Codex_20260404_082231
2. Task summary: 依 INIT.md 執行 root safety check、雙重確認、backup snapshot；驗證 governance files 已完整存在，因此安裝為 no-op；同時依 §4a 封存超長 SESSION_LOG。
3. Layer classification: Development Governance Layer（bootstrap verification / archive maintenance）
4. Source triage: 非產品 bug；屬 governance bootstrap / documentation maintenance。另發現 workspace 版本標記 v3.0.5 與最新產品 session 記錄 v3.0.4 不一致，判定為 documentation drift。
5. Files read: `INIT.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/DOC_SYNC_CHECKLIST.md`; created `dev/archive/SESSION_LOG_2026_Q1.md`, `dev/archive/SESSION_LOG_2026_Q2.md`, `dev/init_backup/20260404_082231_UTC/`
7. Completed:
   - ✅ Root Safety Check 完成：`pwd=/Users/leonard/Downloads/Claude-edb-Project-V3`；`git root=none`
   - ✅ 使用者明確確認：`INSTALL_ROOT_OK: /Users/leonard/Downloads/Claude-edb-Project-V3`
   - ✅ 使用者明確確認：`INSTALL_WRITE_OK`
   - ✅ 建立 backup snapshot，備份 7 個既有 governance targets
   - ✅ 驗證 install 結果為 no-op：`AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `dev/SESSION_HANDOFF.md` / `dev/SESSION_LOG.md` / `dev/CODEBASE_CONTEXT.md` / `dev/DOC_SYNC_CHECKLIST.md` 均已存在且核心模板已在位
   - ✅ 因 `dev/SESSION_LOG.md` = 1852 lines，觸發 §4a archive rotation；保留最新 2 個 session entries，舊 entries 依 quarter 移至 archive files
   - ✅ 記錄風險：`edb-dashboard.html` 與 `edb_scraper.py` 版本標記已到 v3.0.5，但現有產品 session docs 尚未對應
8. Validation / QC:
   - `wc -l dev/SESSION_LOG.md` → 1852（archive 前）
   - backup snapshot files verified under `dev/init_backup/20260404_082231_UTC/`
   - `wc -l dev/SESSION_LOG.md` → 47（archive 後，符合 ≤350）
   - `rg -n 'v3\\.0\\.5' -S .` → 確認 `edb-dashboard.html` 與 `edb_scraper.py` 存在未對帳版本標記
9. Pending:
   - 補做 v3.0.5 的產品層對帳：確認實際 diff、驗證結果、與對應 session documentation
   - 完成 smoke test 後再決定是否 deploy
10. Next priorities:
   - 對帳 v3.0.5 drift
   - 執行 scraper smoke test
   - 視驗證結果決定 deploy
11. Risks / blockers:
   - 若跳過 v3.0.5 對帳直接 deploy，版本與驗證證據會不一致
   - 此專案目前不是 git working tree；部署與 diff 歷史需要依現有外部 git repo 流程核對
12. Notes:
   - Backup snapshot path: `dev/init_backup/20260404_082231_UTC/`
   - Archived files: `dev/archive/SESSION_LOG_2026_Q1.md`, `dev/archive/SESSION_LOG_2026_Q2.md`
   - Doc Sync: registry updated with `Session governance maintenance / log archive`

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - INIT.md 需要在不誤寫專案的前提下執行 bootstrap；同時 live `SESSION_LOG.md` 已超過 archive threshold，且治理文件未反映 workspace 的 v3.0.5 version markers。
2. Root Cause:
   - Governance install 已在先前 session 完成，但本次仍需正式走 §5a root safety + backup 流程。
   - `SESSION_LOG.md` 長期累積到 1852 lines，觸發 §4a。
   - 產品檔案版本已更新，但缺少對應的產品層 session 記錄，形成 documentation drift。
3. Fix:
   - 完整執行 root safety check、雙確認、backup snapshot。
   - 將 INIT 安裝判定為 no-op，只更新 governance records，不改動既有 install files。
   - 封存舊 session entries 至 quarter archive files，並在 handoff 中明示 v3.0.5 drift。
4. Verification:
   - Root path confirmed exactly by user.
   - Backup snapshot created with 7 expected files.
   - Live `SESSION_LOG.md` trimmed to 47 lines and archive pointer inserted.
   - `rg -n 'v3\\.0\\.5' -S .` confirms drift exists and is now documented for next session.
5. Regression / rule update:
   - 無新增 AGENTS rule；僅補齊 `dev/DOC_SYNC_CHECKLIST.md` 的 registry row，避免未來 archive maintenance 出現無對應 row 的假安全感。

### Consolidation / Retirement Record
1. Duplicate / drift found:
   - Workspace version markers (`v3.0.5`) 與 current governance docs (`v3.0.4`) 不一致。
2. Single source of truth chosen:
   - Current-state governance remains `dev/SESSION_HANDOFF.md` + live `dev/SESSION_LOG.md`，但必須先記錄 on-disk evidence 再交由下一 session 對帳產品層細節。
3. What was merged:
   - 將 archive maintenance 與 INIT no-op verification 合併記錄於同一 session entry。
4. What was retired / superseded:
   - 1852-line live `dev/SESSION_LOG.md` 改為保留最新兩筆，舊 entries 轉移到 archive files。
5. Why consolidation was needed:
   - 若不封存，startup 成本過高；若不記錄 drift，下一 session 會以錯誤版本作為 baseline。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: reconcile the undocumented v3.0.5 workspace state before any deploy or release claim. Governance bootstrap is already installed and was re-verified as a no-op on 2026-04-04.

Pending tasks (priority order):
1. Compare the current workspace files against the latest documented product record: `edb-dashboard.html` and `edb_scraper.py` both show v3.0.5, while the latest documented product session is v3.0.4 in `dev/SESSION_LOG.md`.
2. After understanding the v3.0.5 diff, run validation appropriate to the actual changes. At minimum, re-run the intended smoke checks before any deployment decision.
3. Only after version/documentation/validation are aligned, decide whether to run `bash ~/Downloads/Claude-edb-Project-V3/deploy.sh` and verify GitHub Pages with a hard refresh.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`
- `dev/DOC_SYNC_CHECKLIST.md`
- `dev/archive/SESSION_LOG_2026_Q1.md`
- `dev/archive/SESSION_LOG_2026_Q2.md`

Known risks / blockers / cautions:
- Do not treat v3.0.4 as the final current product state without reconciling the on-disk v3.0.5 markers.
- This workspace is not itself a git repo (`git root = none`), so use the established external git repo workflow carefully.
- Governance install files already exist; future INIT runs here should remain no-op unless the template changes.

Validation status: Root Safety Check PASS; backup snapshot created; SESSION_LOG archive rotation PASS; no product-layer validation was run in this session.

Post-startup first action: inspect the actual v3.0.5 changes in `edb-dashboard.html` and `edb_scraper.py`, then decide what missing product session documentation and validation must be added before deployment.
```

## 2026-04-03 Knowledge Platform Integration (v3.0.4)

1. Agent & Session ID: ba64ba27-0c19-41b8-95fc-7dc27a068588
2. Task summary: 整合 EDB Knowledge Platform 語義事實庫；實施 KnowledgeStore 語義搜尋（0.45 閾值）；升級供應商數據 Schema 並更新 Dashboard UI。
3. Layer classification: Product / System Layer（功能整合）
4. Files changed: `edb_scraper.py` (v3.0.4), `edb-dashboard.html` (v3.0.4 UI), `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`
5. Completed:
   - ✅ **KnowledgeStore**：實現 `text-embedding-3-small` 語義搜尋，替代舊關鍵字匹配。
   - ✅ **語義閾值**：設置為 0.45，平衡知識注入的精確度與覆蓋面。
   - ✅ **供應商 Schema**：新增 `procurement_cat`, `is_tender`, `budget_estimate`, `compliance_ref` 字段。
   - ✅ **Dashboard UI**：詳情面板角色分頁顯示增強後的供應商統計；供應商 Tab 增加招標計數與類別圖表。
   - ✅ **版本同步**：全系統升級至 v3.0.4。
6. Push status: 待用戶在 Mac Terminal 執行 `deploy.sh`

### Problem -> Root Cause -> Fix -> Verification
- **Problem**: 舊系統僅依賴 `role_facts.json` 靜態事實，且缺乏供應商採購細節。
- **Root Cause**: 缺乏語義索引能力，LLM 無法根據通告內容智能篩選最相關的政策事實。
- **Fix**: 引入 `KnowledgeStore` 調用 `knowledge.json` 公開 API，進行向量化檢索；更新 `CIRCULAR_SCHEMA` 強制 LLM 提取採購關鍵數據。
- **Verification**: JS syntax PASS；Dashboard CSS 注入確認；Scraper 編譯通過。

---

## 2026-04-02 截止日期類型標籤斷行修正 + v3.0.3

1. Agent & Session ID: Claude_20260402_0100
2. Task summary: 修正截止日期表格「類型」欄位斷行；同批次處理 v3.0.2 部署問題（git repo 直接存取）；建立繁體中文 commit 規範
3. Layer classification: Product / System Layer（前端 CSS bug fix）
4. Files changed: `edb-dashboard.html`（`.type-chip` CSS + v3.0.3）
5. Completed:
   - ✅ `.type-chip` 加入 `white-space:nowrap; display:inline-block`
   - ✅ v3.0.2 → v3.0.3（6 處）
   - ✅ JS syntax PASS；直接 commit 至 git repo
   - ✅ Git repo 已掛載至 VM（未來無需手動 cp）
   - ✅ 繁體中文 commit message 規範啟用
6. Push status: 待用戶執行 `bash ~/Downloads/Claude-edb-Project-V3/deploy.sh`

### Problem -> Root Cause -> Fix -> Verification
- **Problem**: 截止日期表格「類型」欄（知悉日期／申請截止）在窄欄時換行顯示
- **Root Cause**: `.type-chip` CSS 無 `white-space:nowrap`，badge 在有限欄寬下自動換行
- **Fix**: 新增 `white-space:nowrap; display:inline-block` 至 `.type-chip`
- **Verification**: JS syntax PASS；grep 確認 CSS 已更新

---
