# Session Log
<!-- Archives: dev/archive/ — entries moved when >800 lines or oldest entry >30 days -->

## 2026-04-11 Summary tone cleanup for generic / official-sounding outputs

1. Agent & Session ID: Codex_20260411_0001
2. Task summary: 使用者回報 live AI summary 仍然「太官腔、太空泛」。本輪只修 summary 生成與後處理，不碰 K1、actions、roles；重點解 `053` 類過空、`042` 類推斷語氣、以及 rich circular 單段過長問題。
3. Layer classification: Product / System Layer（summary generation quality）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output quality issue。問題來源主要在 summary prompt 與 post-review 正規化／fallback 邏輯，而不是 live data 故障或 K1 接入故障。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `dev/DOC_SYNC_CHECKLIST.md`, `edb_scraper.py`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ summary prompt 新增「硬資訊優先」規則：若正文已有主辦、日期、地點、名額、對象、截止或提交方式，應優先寫出
   - ✅ 補強 summary filler 清理：新增 `就目前公開內容而言`、`官方渠道後續發布`、`推斷性說明`、`整體重點在於` 等官式/空泛 marker
   - ✅ 新增 source-priority summary refresh：若 normalized summary 仍過短、過長、單段或帶官式 marker，優先改用 `official/pdf_text` 重組摘要
   - ✅ `v3.0.37` sample 已對齊方向：`053` 類會抽出主辦、日期、名額與截止；`042` 類會自然化；`048` 類保留具體內容但不回到角色百科
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile → PASS
   - helper regression → PASS
9. Pending:
   - 決定是否發布 `v3.0.37`
   - 若發布，重跑 workflow 後重點驗 `053 / 042 / 043 / 048`
10. Next priorities:
   - 決定是否發布 `v3.0.37`
   - 若發布，驗 live summary 是否由官腔轉為硬資訊優先
   - 視結果再決定是否仍需個別 rich-summary 收口
11. Risks / blockers:
   - 本機缺 `OPENAI_API_KEY`，未做完整雲端回歸
   - 本地 `circulars.json` 仍是舊 114 份資料，helper 只能驗規則方向，不能代替 live workflow 後最終結果
12. Notes:
   - 這輪刻意不再動 K1 / action synthesis，避免把 summary 問題和其他層混在一起。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - live summary 仍常見官式句、推斷語氣、資訊空泛，像 `053` 類只有活動安排空句，`042` 類仍見「推斷性說明」。
2. Root Cause:
   - 現有 normalizer 只能移除部分 filler，但當模型輸出仍偏 generic 時，不一定會觸發 source-based fallback；同時 prompt 對「硬資訊優先」要求不夠明確。
3. Fix:
   - 補強 prompt 與 filler markers，並在 summary 過短/過長/單段或帶官式 marker 時，自動改用 `official/pdf_text` 的 source-priority summary。
4. Verification:
   - `053` helper 會輸出主辦、日期、名額、提名上限與截止
   - `042` helper 會去掉「推斷性說明」並自然化成兩段
   - `048` helper 仍保留具體內容，但不再洩漏角色工作
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #37 added: generic / official-sounding summaries should refresh from source rather than preserving weak model wording.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | source-rich activity circular summary still generic | apply post-analysis review | summary rebuilt from source with organizer/date/quota/deadline | `053` helper rebuilt into 2-paragraph hard-info summary | PASS |
| Boundary | generic one-paragraph summary with推斷語氣 but no source text | normalize summary | remove推斷語氣 and keep concrete content | `042` helper became 2 short paragraphs with `重點包括...` | PASS |
| Error / failure path | local env missing PyMuPDF / OPENAI key | run local helper only | local QC still works; cloud verification skipped | helper printed PyMuPDF warning only; QC unaffected | PASS with notes |
| Regression | rich circular with role-work leakage | apply post-analysis review | keep circular-first content, remove role-work sentence | `048` helper kept plan details and removed role-work sentence | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-10 Live circulars disappearance hotfix

1. Agent & Session ID: Codex_20260410_0006
2. Task summary: 使用者回報「更新後，通告不見了很多」。經核實，問題不是單純數量變少，而是 live `circulars.json` 同時出現了兩層故障：最新 auto-update commit `fd78c0a` 把資料縮成 `3` 份，其後 publish commit `2448f16` 又把 merge conflict marker 一併推上去，令 public JSON 直接失效。
3. Layer classification: Product / System Layer（live data hotfix）+ Development Governance Layer（session persistence）
4. Source triage: user-visible release incident。屬資料層 / deploy 層故障，不是前端 UI 或 summary 本身問題。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, live `circulars.json`, `/Users/leonard/Documents/EDB-AI-Circular-System/circulars.json`, deploy repo git log / status
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 確認 live `circulars.json` 含 conflict markers (`<<<<<<< HEAD`)
   - ✅ 確認 `8664c3c` 的 `circulars.json` 為最後正常版本（`117` 份）
   - ✅ 將 deploy repo `circulars.json` 還原到 `8664c3c` 版本
   - ✅ 推送 hotfix commit `442b9c3`：`hotfix: restore circulars.json to last known-good 117-record state`
8. Validation / QC:
   - local deploy repo `circulars.json` parse → PASS (`count=117`)
   - deploy repo status after push → PASS (`main...origin/main`)
   - live fetch immediately after push → still served old broken JSON with conflict markers
9. Pending:
   - 等 GitHub Pages propagation / cache 更新
   - propagation 後重新驗 live `circulars.json` 是否回復 `117`
10. Next priorities:
   - 驗 live hotfix 是否生效
   - 再查 `fd78c0a` 為何把資料縮成 `3` 份
   - 再決定是否發 `v3.0.36`
11. Risks / blockers:
   - hotfix 已推送，但 GitHub Pages 暫時仍回傳舊壞檔
   - `days-3` / auto-update path 可能重新引入 `3 circulars` regression，需後續追根因
12. Notes:
   - 這輪先救 live；未觸碰 summary/K1 邏輯

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-10 Wide 3-column layout override fix (workspace v3.0.36)

1. Agent & Session ID: Codex_20260410_0005
2. Task summary: 使用者指出「顯示設定 → 佈局 → 寬屏 3列」未能成功顯示。本輪只修 layout selector 的實際生效問題。
3. Layer classification: Product / System Layer（frontend display behavior change）+ Development Governance Layer（session persistence）
4. Source triage: frontend CSS override issue。根因是 `@media(min-width:768px) and (max-width:1023px)` 把 `.cards-grid` 一律強制成 `repeat(2,1fr)!important`，覆蓋了 `data-layout="wide"` 的三列設定。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb-dashboard.html`, `edb_scraper.py`
6. Files changed: `edb-dashboard.html`, `edb_scraper.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 把 768–1023px media query 改成依 `data-layout` 分流
   - ✅ `wide` 於該區間現可維持 3 列
   - ✅ 版本升至 `v3.0.36`
8. Validation / QC:
   - `node -e "..."` dashboard JS compile → PASS
   - `python3 -m py_compile edb_scraper.py` → PASS
   - version grep (`v3.0.36`) → PASS
9. Pending:
   - 決定是否發佈 `v3.0.36`
   - 發佈後驗 live layout setting
10. Next priorities:
   - 驗 live `v3.0.34` summaries
   - 如 OK，再發 `v3.0.36`
   - 發佈後驗 wide 3-column layout
11. Risks / blockers:
   - 這輪只修 layout CSS，不改資料或 summary
   - live verification 仍需發佈後確認
12. Notes:
   - `edb_scraper.py` 仍只同步 banner version，沒有邏輯改動

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | desktop/tablet width 768–1023px + `wide` layout | render cards grid | 3-column layout | media query now respects `[data-layout="wide"]` | PASS |
| Boundary | same width + `compact` layout | render cards grid | 1-column layout | media query now respects `[data-layout="compact"]` | PASS |
| Regression | same width + `standard` layout | render cards grid | 2-column layout unchanged | `[data-layout="standard"]` remains 2 columns | PASS |
| Error / failure path | live page not yet rechecked | local QC only | local compile checks pass; live deferred | local checks passed; live deferred | PASS with notes |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-10 Dashboard action-list badge visual cleanup (workspace v3.0.35)

1. Agent & Session ID: Codex_20260410_0004
2. Task summary: 使用者回報 top-level 行動清單中的角色 badge 「非常核突」。本輪只修 action-list badge 的視覺：移除 emoji、縮細字、淡化底色與邊框，保留 badge inline 顯示。
3. Layer classification: Product / System Layer（frontend display behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible UI issue。問題不在資料或 summary，而在 action-list badge 直接重用 `ROLE_NAMES`（含 emoji）且樣式過重，令畫面顯得突兀。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb-dashboard.html`, `edb_scraper.py`
6. Files changed: `edb-dashboard.html`, `edb_scraper.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `ROLE_ACTION_LABELS`，action-list 改用無 emoji 的角色短標籤
   - ✅ `.a-role` 改為更細、更淡、更圓角的 compact pill
   - ✅ 版本升至 `v3.0.35`
8. Validation / QC:
   - `node -e "..."` dashboard JS compile → PASS
   - `python3 -m py_compile edb_scraper.py` → PASS
   - version grep (`v3.0.35`) → PASS
9. Pending:
   - 決定是否發佈 `v3.0.35`
   - 發佈後驗 live action-list 視覺
10. Next priorities:
   - 驗 live `v3.0.34` summaries
   - 如 OK，再發 `v3.0.35`
   - 發佈後驗 badge 視覺是否改善
11. Risks / blockers:
   - 這輪只修 action-list 外觀，不改資料內容
   - live verification 仍需在 GitHub Pages 更新後檢視
12. Notes:
   - `edb_scraper.py` 仍只同步 banner version，沒有邏輯改動

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | action-list has role badge | render detail panel | compact text-only badge, no emoji | action-list now uses `ROLE_ACTION_LABELS` | PASS |
| Boundary | current-role highlight active | render detail panel | current role still highlighted, but lighter | inline style still applies accent override on compact pill | PASS |
| Regression | other role displays use `ROLE_NAMES` | render detail panel + role cards | other areas keep original emoji role labels | only action-list switched to `ROLE_ACTION_LABELS` | PASS |
| Error / failure path | live page not yet rechecked | local QC only | local compile checks pass; live deferred | local checks passed; live deferred | PASS with notes |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-10 Dashboard action-list inline role label (workspace v3.0.34)

1. Agent & Session ID: Codex_20260410_0003
2. Task summary: 使用者在 school-year workflow 完成後要求調整 dashboard top-level `行動清單` 顯示，讓每項 action 的角色標籤與主動作同一行呈現，而不是固定拆成兩行。
3. Layer classification: Product / System Layer（frontend display behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible display issue。問題不在資料內容，而在 `edb-dashboard.html` 的 action-item rendering 結構：`action-text` 固定在第一行，role badge 固定在第二行 meta 區，因此每項行動視覺上必然分成兩行。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb-dashboard.html`, `edb_scraper.py`
6. Files changed: `edb-dashboard.html`, `edb_scraper.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `.action-main` 容器，讓 role badge 與 action text 在 top-level action list 同一行排列
   - ✅ `action-meta` 只保留 deadline / note，不再重複渲染角色標籤
   - ✅ 版本升至 `v3.0.34`
8. Validation / QC:
   - `node -e "..."` dashboard JS compile → PASS
   - `python3 -m py_compile edb_scraper.py` → PASS
   - local structure review → PASS（top-level 行動清單 HTML 已改為 badge + text 同行）
9. Pending:
   - 核實 live `v3.0.33` workflow 結果
   - 決定是否發佈 `v3.0.34` 的 display-only tweak
10. Next priorities:
   - 驗 live `v3.0.33` summaries
   - 視驗證結果決定是否發 `v3.0.34`
   - 如發佈，再驗 action-list inline 顯示
11. Risks / blockers:
   - 此 VM 仍無法直接核實 GitHub Pages / workflow 最終結果
   - 這輪只修前端顯示，不會改變 `circulars.json` 內 actions 資料本身
12. Notes:
   - `edb_scraper.py` 只同步 banner version 到 `v3.0.34`，沒有產品邏輯改動

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | top-level `actions` has role + text + deadline | render detail panel | role badge and action text appear on the same first line | HTML now renders badge inside `.action-main` next to `.action-text` | PASS |
| Boundary | long action text wraps | render detail panel | wrapped text should continue under the same action block without breaking badge placement | flex layout with `.action-main` keeps badge anchored and text wraps inside same row group | PASS |
| Error / failure path | no live workflow verification available in VM | local QC only | local compile checks pass; live validation deferred | local checks passed; live deferred | PASS with notes |
| Regression | deadline and note meta still present | render detail panel | deadline/note remain in second line meta area | role badge removed from meta, deadline/note still rendered | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-10 Session closeout after preparing v3.0.33 push

1. Agent & Session ID: Codex_20260410_0002
2. Task summary: 完成 `v3.0.33` summary/source-fallback 調整與 deploy repo 發佈準備；closeout 時唯一未完成項是把已準備好的 deploy repo commit 推上 GitHub。
3. Layer classification: Product / System Layer（release-state tracking）+ Development Governance Layer（session closeout）
4. Source triage: closeout / release-state consolidation。需要把真實狀態寫清楚：workspace 與 deploy repo 本地都已是 `v3.0.33`，但 push 受 GitHub HTTPS 憑證阻塞。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, deploy repo git status / log, publish output
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 記錄 `v3.0.33` 已在 deploy repo 本地完成發佈準備，commit 為 `ae2b24a`
   - ✅ 更新 baseline 為 `live v3.0.30 / deploy-repo-local v3.0.33 / workspace v3.0.33`
   - ✅ 重排 open priorities，將「完成有憑證的 push」列為下一步
   - ✅ 寫入最新 next-session handoff prompt（verbatim）
8. Validation / QC:
   - `wc -l dev/SESSION_LOG.md` → `592` lines (no archive rotation needed)
   - `git -C ~/Documents/EDB-AI-Circular-System status --short --branch` → `## main...origin/main [ahead 1]`
   - `git -C ~/Documents/EDB-AI-Circular-System log --oneline -3` → top commit `ae2b24a chore: publish v3.0.33`
9. Pending:
   - 用有 GitHub 憑證的 terminal 完成 `git push origin main`
   - push 後重跑 `school-year` workflow
   - 驗 live `053 / 048 / 049 / 050`
10. Next priorities:
   - 完成 `v3.0.33` push
   - rerun workflow
   - 驗 live summaries
11. Risks / blockers:
   - sandbox / current shell 無法讀取 GitHub HTTPS credentials，`git push` 失敗訊息為 `could not read Username for 'https://github.com': Device not configured`
   - closeout 時 live 仍停留在 `v3.0.30`
12. Notes:
   - `deploy.sh --no-bump` 已完成 sync 與 rebase；失敗只在最後 push 步驟，因此 deploy repo 本地已是可推送狀態。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from local deploy-ready `v3.0.33` as of 2026-04-10. Live public GitHub Pages is still only verified up to `v3.0.30` (`generated_at=2026-04-09T16:49:14Z`), but the deploy repo at `~/Documents/EDB-AI-Circular-System` is already prepared at commit `ae2b24a` (`chore: publish v3.0.33`) and is `ahead 1` of `origin/main`. `v3.0.33` improves summary generation for source-rich circulars like `EDBCM053/2026` by extracting organizers, dates, quotas, nomination limits, and deadlines from `official/pdf_text`, while keeping the earlier rich-summary cleanup for `EDBCM048/2026`.

Pending tasks (priority order):
1. In a terminal with working GitHub credentials, run `git -C ~/Documents/EDB-AI-Circular-System push origin main` to publish the already-prepared `v3.0.33` commit.
2. After push succeeds, trigger or wait for the `school-year` workflow and verify live `edb-dashboard.html` / `circulars.json`.
3. Inspect live `EDBCM053/2026`, `EDBCM048/2026`, `EDBCM049/2026`, and `EDBCM050/2026`, plus at least 2 more circulars, to confirm summaries remain circular-first and information-dense without role-work leakage.
4. Only if live results still show summary issues, decide whether further refinement is needed.

Key files changed in this session:
- `edb_scraper.py`
- `edb-dashboard.html`
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- `v3.0.33` is not yet on GitHub because the current shell cannot read GitHub HTTPS credentials; the deploy repo is ready locally and only needs a successful push.
- Live public data is still `v3.0.30`, so no claims should be made yet about live `v3.0.33` behavior.
- The environment still lacks `OPENAI_API_KEY`, so no full cloud end-to-end regression was run locally.

Validation status: `python3 -m py_compile edb_scraper.py` PASS; dashboard JS compile PASS; source-rich `053` summary fallback sample PASS; `048` rich summary helper regression PASS; deploy repo local status PASS (`ahead 1`, commit `ae2b24a` ready to push).

Post-startup first action: confirm whether `git -C ~/Documents/EDB-AI-Circular-System push origin main` has already been run successfully; if not, provide that exact command first, then verify live only after the push and workflow complete.
```

## 2026-04-09 Live v3.0.30 verification + summary fallback/rich-guard fix (workspace v3.0.31)

1. Agent & Session ID: Codex_20260409_0017
2. Task summary: 先驗 live `v3.0.30` 真實效果，再做一個窄修版 `v3.0.31`，只處理 summary 的兩個 residual 問題：rich circular 仍殘留角色工作句，以及 sparse circular 可能被清理成空摘要。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: live-verified regression。問題不是 K1/action 邏輯本身，而是 live `v3.0.30` 的 summary 後處理仍不足：`EDBCM048/2026` 仍像角色百科文；`EDBCM053/2026` 因 summary 全被 marker 濾掉而變成空字串。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`, live `edb-dashboard.html`, live `circulars.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 驗證 live `v3.0.30` 已上線（dashboard `v3.0.30`, `generated_at=2026-04-09T16:49:14Z`, `count=117`）
   - ✅ 在 summary sentence filter 中加入 role-work sentence guard，濾走 rich circular 內的角色工作句
   - ✅ 新增 title/tag/topic-based summary fallback，避免 sparse circular 被清理成空摘要
   - ✅ 版本升至 `v3.0.31`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - targeted helper regression on live samples → PASS（`048` 會保留通告主體句、去掉角色工作句；`053` 空摘要會回退為標題摘要）
   - live verification → PASS with notes（`v3.0.30` live，但 summary 品質仍未達標，因此產生 `v3.0.31`）
9. Pending:
   - 決定是否發布 `v3.0.31`
   - 如發布，重跑 school-year workflow 並驗 live `048 / 049 / 050 / 053`
10. Next priorities:
   - 先本地看 `v3.0.31` helper 輸出是否值得發布
   - 再決定是否 push / rerun workflow
   - 發布後重點驗 `053` 空摘要是否修好，以及 `048` 是否不再像角色百科文
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，所以沒有完整雲端 LLM 端到端回歸
   - rich circular summary 仍依賴 LLM 原始句子品質；這輪只能後收口，不是重寫模型內容
12. Notes:
   - `v3.0.30` 已證實 filler 句大致清掉、sparse actions 已保住；所以這輪刻意不再碰 K1 或 action 規則，只修 summary。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | rich circular summary contains intro + role-work sentences (`EDBCM048/2026`-style) | normalize summary | keep circular intro, drop role-work expansion | helper kept通告主體句，濾走角色工作句 | PASS |
| Boundary | sparse circular summary collapses to empty after filler filtering (`EDBCM053/2026`-style) | apply post-analysis review | fallback to a short title-based synopsis | helper produced a short title-based two-paragraph summary | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local QC only | local checks valid; cloud regression explicitly skipped | local checks passed; cloud run skipped | PASS with notes |
| Regression | sparse action synthesis already fixed in `v3.0.29+` | apply post-analysis review | action synthesis remains unchanged while summary is repaired | top-level actions path untouched | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 Summary information-density refinement (workspace v3.0.32)

1. Agent & Session ID: Codex_20260409_0018
2. Task summary: 根據使用者對 sample 的判斷，進一步調整 summary 的信息密度：`053` 類 sparse 通告不能太空，`048` 類 rich 通告可保留更多具體內容，但仍不可滑回角色百科。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: targeted product-quality refinement。問題不是 summary 邊界本身，而是 `v3.0.31` sample 仍有兩個偏差：sparse fallback 太泛，rich summary 在刪掉方法語氣時連具體內容也一併刪掉。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`, live sample data from `circulars.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ `根據標題可推測` / `可推斷` 改成先剝前綴、保留句內具體內容
   - ✅ sparse summary fallback 改為使用 title + tags 組更具體的第二段
   - ✅ summary 保持不寫角色工作，但 rich circular 可保留更多通告具體資訊
   - ✅ 版本升至 `v3.0.32`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - targeted helper regression on live samples → PASS
     - `EDBCM053/2026` → `本通告介紹「京港澳學生交流夏令營（2026）」的安排。 / 內容聚焦跨境夏令營、學生交流、京港澳及學校相關安排。`
     - `EDBCM048/2026` → 保留資助方案與核心框架內容，不再出現角色百科段落
9. Pending:
   - 決定是否發布 `v3.0.32`
   - 如發布，重跑 school-year workflow 並驗 live `048 / 049 / 050 / 053`
10. Next priorities:
   - 先看 `v3.0.32` sample 是否足夠接近產品期待
   - 如接受，再 push / rerun workflow
   - 發布後重點驗 rich/sparse summary 都不再失衡
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，所以沒有完整雲端 LLM 端到端回歸
   - `049/050` 目前只做 local helper 驗證，最終仍要以 live workflow 結果為準
12. Notes:
   - 這輪仍然只動 summary；K1 / actions / role-facts 均未修改

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | `EDBCM048/2026` rich summary contains speculative prefix + usable content | `_apply_post_analysis_review()` | strip speculative prefix but keep useful content | summary now keeps 資助方案內容與核心要求 | PASS |
| Boundary | `EDBCM053/2026` empty summary | `_apply_post_analysis_review()` | fallback should be short but concrete, not generic | title/tag fallback now mentions 跨境夏令營、學生交流、京港澳 | PASS |
| Regression | `EDBCM049/2026` and `EDBCM050/2026` should keep circular-first summaries | `_apply_post_analysis_review()` | remain circular-first without action loss | summaries preserved; action counts unchanged | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local QC only | local checks valid; cloud regression explicitly skipped | local checks passed; cloud run skipped | PASS with notes |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-10 Source-rich summary fallback for activity circulars (workspace v3.0.33)

1. Agent & Session ID: Codex_20260410_0001
2. Task summary: 根據使用者對 `EDBCM053/2026` 的明確目標摘要，為正文充足的活動類通告加入 source-based fallback：直接從 `official/pdf_text` 抽主辦、日期、名額、提名上限與截止等硬資訊，而不再退回 generic title/tag 摘要。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: targeted product-quality refinement。問題不是 summary 邊界，而是 `053` 這類通告實際正文已很豐富，但 generic fallback 只寫成「有活動安排」，資訊密度不足。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`, user-provided `053` circular detail excerpt
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `_compact_summary_source_text()` 與 `_build_activity_source_summary()`
   - ✅ 對活動/夏令營/交流類通告，若 `official/pdf_text` 足夠，先從正文抽主辦、日期、名額、提名上限及截止
   - ✅ 版本升至 `v3.0.33`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - 以使用者提供的 `053` 詳情 sample 驗證 `_build_summary_fallback()` → PASS
   - `048` rich summary helper regression → PASS（保持 rich circular 改善，不回到角色百科）
9. Pending:
   - 決定是否發布 `v3.0.33`
   - 如發布，重跑 school-year workflow 並驗 live `053 / 048 / 049 / 050`
10. Next priorities:
   - 先看 `053` sample 是否已足夠接近產品期待
   - 如接受，再 push / rerun workflow
   - 發布後驗 source-rich 與 sparse/rich summaries 是否一併穩定
11. Risks / blockers:
   - 這輪 source-based fallback 目前主要針對活動/交流類摘要；其他通告類型仍以一般 summary 規則為主
   - 本機仍缺 `OPENAI_API_KEY`，沒有完整雲端 LLM 端到端回歸
12. Notes:
   - `053` sample 現會輸出接近「主辦 + 日期 + 名額 + 截止」的結構，但仍保留通告本位，不寫角色工作。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | user-provided `053` detail text available in `pdf_text` | `_build_summary_fallback()` | summary should extract organizers, schedule, quota, nomination limit, deadline | sample output now includes主辦、日期、名額、提名上限與截止 | PASS |
| Boundary | same `053` sample contains irregular spacing from PDF text | `_build_summary_fallback()` | spacing should be compacted before extraction | extraction still succeeds on spaced text | PASS |
| Regression | live-like `048` rich summary | `_apply_post_analysis_review()` | rich summary keeps useful content, not role百科 | helper output remains circular-first and concrete | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local QC only | local checks valid; cloud regression explicitly skipped | local checks passed; cloud run skipped | PASS with notes |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 Summary responsibility rewrite (workspace v3.0.30)

1. Agent & Session ID: Codex_20260409_0015
2. Task summary: 根據使用者明確拍板的新產品規格，重寫 summary 任務邊界：summary 只做通告簡介，可借知識庫詞彙統一用字，但不再寫角色工作、行動清單或知識庫延伸內容；這些內容一律交回 `actions` / `roles.*`。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: product-goal correction。問題核心不是單幾條 regex，而是 summary 任務被塞入了太多責任，導致每次修一份通告就影響其他通告。使用者已明確確認新的 summary/product 分工，因此這輪是任務重定義，不是局部 patch。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ summary 規格改成 `120-250` 字、1-2 段、只作通告簡介
   - ✅ prompt 明確禁止在 summary 寫角色工作、行動清單或跟進分工
   - ✅ prompt 明確允許只借用知識庫詞彙，不借用知識庫內容
   - ✅ 移除 sparse summary follow-up fallback
   - ✅ 補強 marker：`根據可得的知識庫` / `根據經審核知識庫` / `依照經審核知識庫` / `知識庫`
   - ✅ 版本升至 `v3.0.30`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - summary helper regression → PASS（含知識庫與角色工作的樣例摘要，經 `_normalize_summary_text()` 後只保留通告主句）
   - prompt grep / version grep → PASS
9. Pending:
   - 用 audit gate 再判斷 `v3.0.30` 是否值得發佈
   - 如決定發佈，再重跑 school-year workflow 驗 live summary 行為
10. Next priorities:
   - 先看本地 audit 是否支持發佈 `v3.0.30`
   - 再決定要不要 push / rerun workflow
   - 發佈後重點驗 `048 / 049 / 050 / 053`
11. Risks / blockers:
   - 本機沒有 `OPENAI_API_KEY`，無法做完整雲端 LLM 回歸
   - 目前 `circulars.json` 仍是舊資料，因此本地 audit 還不能直接證明 `v3.0.30` live 之後的全文表現
12. Notes:
   - 本輪刻意不再讓 summary 補 sparse follow-up；如果要呈現行動感，應由 `actions` 與 `roles.*` 負責。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - summary 同時承擔通告簡介、角色工作、知識庫延伸與 sparse recovery，導致一改就全局波動。
2. Root Cause:
   - summary 的產品責任邊界不清，prompt 和後處理都在嘗試替其他欄位補位。
3. Fix:
   - 把 summary 正式限縮為通告簡介欄位；角色工作與行動清單交回 `actions` / `roles.*`，知識庫只借詞彙不用內容。
4. Verification:
   - local helper 顯示含知識庫 / 角色工作句子的摘要，會被收斂為只保留通告主句
   - Python / JS compile 均通過
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #33 added: summary and action responsibilities must stay separate.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | summary contains known circular sentence + knowledge/role spillover | normalize summary | keep circular synopsis only | helper reduced sample to single circular-intro sentence | PASS |
| Boundary | prompt builder with official text but no PDF | build prompt | summary instructions must allow K1 vocabulary but forbid K1 content/role work in summary | prompt lines reflect new contract | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local QC only | local checks valid; cloud regression explicitly skipped | local checks passed; cloud run skipped | PASS with notes |
| Regression | actions / roles logic unchanged | inspect code path | summary rewrite must not touch sparse action synthesis path | action synthesis function remains separate; only summary path changed | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 Session closeout after v3.0.30 push

1. Agent & Session ID: Codex_20260409_0016
2. Task summary: 完成 `v3.0.30` push 後的 session closeout，將 handoff 狀態更新為 repo 已發佈、live workflow 待驗。
3. Layer classification: Product / System Layer（release-state tracking）+ Development Governance Layer（session closeout）
4. Source triage: closeout / release-state consolidation。需要把本輪 summary 規格重寫、audit gate、新版 push 收斂成可接手狀態。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, publish output
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 記錄 `v3.0.30` 已 push 到 repo commit `047d6ba`
   - ✅ 更新 baseline 成 `live v3.0.28 / repo-pushed v3.0.30 / workspace v3.0.30`
   - ✅ 重排 open priorities，聚焦於驗證 `v3.0.30` live 結果
   - ✅ 寫入最新 next-session handoff prompt（verbatim）
8. Validation / QC:
   - deploy script `bash /Users/leonard/Downloads/Claude-edb-Project-V3/deploy.sh --no-bump` → PASS
   - repo push PASS at `047d6ba`
   - `wc -l dev/SESSION_LOG.md` → 384 lines (no archive rotation needed)
9. Pending:
   - 跑 / 驗 `school-year` workflow
   - 驗證 live `v3.0.30` 是否真正改善 summary 並保留 action 可見性
10. Next priorities:
   - 驗 live `v3.0.30`
   - 核對 `048 / 049 / 050 / 053`
   - 視結果再決定是否需要下一輪調整
11. Risks / blockers:
   - closeout 時 live 仍是 `v3.0.28`
   - 本機仍缺 `OPENAI_API_KEY`，無完整雲端回歸
12. Notes:
   - 本輪已 push，但不宣稱 live 已更新；需以 workflow 結果為準。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from repo-pushed `v3.0.30` as of 2026-04-09. The deploy repo is now at commit `047d6ba`; this version re-scopes summary so it only describes the circular itself, may borrow K1 vocabulary but not K1 content, and no longer lets summary carry role work or action lists. At closeout, public GitHub Pages / live `circulars.json` were still only verified up to `v3.0.28`.

Pending tasks (priority order):
1. Verify whether the `school-year` workflow for `v3.0.30` has completed and whether live HTML / live `circulars.json` have caught up.
2. Check `EDBCM053/2026`, `EDBCM048/2026`, `EDBCM049/2026`, and `EDBCM050/2026` on live data and confirm summary is now circular-first while action visibility remains acceptable.
3. Compare at least 2 additional live circulars to ensure `v3.0.30` did not over-shorten rich circular summaries or hide useful role/action information.
4. Only if the above passes, decide whether any further summary/action refinement is needed.

Key files changed in this session:
- `edb_scraper.py`
- `edb-dashboard.html`
- `dev/tools/summary_action_audit.py`
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- `v3.0.30` has been pushed successfully, but closeout happened before live workflow verification.
- The local audit tool validates current `circulars.json`, but it cannot prove live `v3.0.30` behavior until the workflow regenerates data.
- The environment still lacks `OPENAI_API_KEY`, so no full cloud end-to-end regression was run locally.

Validation status: `python3 -m py_compile edb_scraper.py` PASS; dashboard JS compile PASS; summary helper PASS; `python3 dev/tools/summary_action_audit.py --input ./circulars.json --max-examples 2` PASS; deploy script PASS; repo push PASS at `047d6ba`.

Post-startup first action: fetch live `edb-dashboard.html` and `circulars.json`, confirm whether `v3.0.30` is live, then inspect `EDBCM053/2026`, `EDBCM048/2026`, `EDBCM049/2026`, and `EDBCM050/2026` before making any further summary/action changes.
```

## 2026-04-09 Local summary/action audit gate tool

1. Agent & Session ID: Codex_20260409_0014
2. Task summary: 為避免每次摘要/行動小改都直接進入 1 小時以上的 `school-year workflow`，新增本地 audit tool，直接掃現有 `circulars.json` 做全量 heuristic 檢查。
3. Layer classification: Product / System Layer（local tooling / quality gate）+ Development Governance Layer（session persistence）
4. Source triage: release-process / verification gap。使用者明確指出「若只看 5 份 sample，可能只是修好這幾份，然後又要再跑很久 workflow」，因此需要一個可快速覆蓋全量資料的本地檢查工具，而不是再依賴少量 sample 或每次重跑 LLM。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `dev/tools/simulate_post_analysis_review.py`, `circulars.json`
6. Files changed: `dev/tools/summary_action_audit.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `dev/tools/summary_action_audit.py`
   - ✅ 支援掃描現有 `circulars.json` 的 summary/action 風險
   - ✅ 可輸出文字報告或 JSON
   - ✅ 已把 tool 寫入 README、Directory Map、handoff
8. Validation / QC:
   - `python3 -m py_compile dev/tools/summary_action_audit.py` → PASS
   - `python3 dev/tools/summary_action_audit.py --input ./circulars.json --max-examples 3` → PASS
   - `python3 dev/tools/summary_action_audit.py --input ./circulars.json --json` → PASS
9. Pending:
   - 用 audit 結果判斷是否值得發布 `v3.0.29`
   - 若 audit 顯示 summary 問題屬全量性，先回到產品目標再調整，而不是繼續 patch
10. Next priorities:
   - 用 audit gate 先評估 `v3.0.29`
   - 只在本地 gate 過關後才考慮跑長 workflow
   - 若仍有全量 summary 問題，先調整策略，不急於發版
11. Risks / blockers:
   - 現有 local `circulars.json` 只有 114 筆，不一定完全等同最新 live；但已足夠作為發版前 heuristic gate
   - audit 是 heuristic，不取代人工最終抽樣閱讀
12. Notes:
   - 這個 tool 的目的不是判斷「摘要好不好」，而是先找出最值得人工看的高風險通告，避免盲目重跑 workflow。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者指出若只定 5 份人工驗收基線，仍有 overfit 風險；但若每次都直接跑 `school-year workflow`，成本又太高。
2. Root Cause:
   - 現有 release 驗證缺少一層快速、全量、可本地完成的 heuristic gate。
3. Fix:
   - 新增 `summary_action_audit.py`，直接讀取現有 `circulars.json`，統計 summary filler、過長/過短、單段、以及 `roles.*.acts` 有內容但頂層 `actions` 為空的案例。
4. Verification:
   - text report / JSON report / py_compile 均通過
   - 在目前 `circulars.json` 上已成功掃出全量問題分佈
5. Regression / rule update:
   - 之後摘要/行動相關改動，應先跑本地 audit gate，再決定是否值得進入 school-year workflow。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | current `circulars.json` present | run text audit | produce counts and examples for summary/action issues | report printed with counts and examples | PASS |
| Boundary | same input but machine-readable need | run with `--json` | emit valid JSON report | JSON output returned | PASS |
| Error / failure path | invalid / unsupported payload shape | load non-circular payload | script should fail loudly instead of silently misreporting | guarded by `ValueError` path in loader | PASS with notes |
| Regression | existing repo should remain unchanged unless docs/tool added | run py_compile | script syntax valid; no pipeline files touched | py_compile PASS | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Prototype / simulation tool added | CODEBASE_CONTEXT.md Directory Map if tool is meant for reuse; SESSION_LOG.md entry | ✓ Done |
| README link / reference update | README.md relevant section; SESSION_LOG.md entry if done in-session | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 Sparse action regression fix after live v3.0.28 verification (workspace v3.0.29)

1. Agent & Session ID: Codex_20260409_0013
2. Task summary: 使用者在 live `v3.0.28` workflow 完成後回報「通告分析＋知識庫後效果不好，也沒有了很多角色工作」。本輪針對該 regression 修正 sparse action synthesis 的執行時序，並補強 summary filler marker 清理。
3. Layer classification: Product / System Layer（analysis pipeline behavior fix）+ Development Governance Layer（session persistence）
4. Source triage: user-visible regression。問題不是 K1 fetch 本身，也不是 workflow 未跑，而是 live `v3.0.28` 的 deterministic post-review 在 sparse circular 上先做 top-level `actions` 合成、後做 role enrich，導致 `roles.*.acts` 雖然後續被補進來，但頂層 `actions` 保持空白；同時 summary filler marker 未擋住 `未披露 / 以正式發布的公告全文為準 / 此通告未逐一分派角色責任` 等句子。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`, live `edb-dashboard.html`, live `circulars.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 把 `_synthesize_sparse_actions()` 移到 `_apply_post_analysis_review()` 的最後，確保會在 curriculum / student / finance role enrich 之後才提升頂層 `actions`
   - ✅ 補強 `SUMMARY_BANNED_MARKERS`，加入 `未披露`、`以正式發布的公告全文為準`、`此通告未逐一分派角色責任`
   - ✅ 版本升至 `v3.0.29`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - targeted sparse helper regression → PASS（`053` 類 sample 會輸出 2 段 summary + 3 條頂層 `actions`）
   - version grep (`v3.0.29`) → PASS
9. Pending:
   - 發佈 `v3.0.29`
   - 重跑 school-year workflow
   - 驗證 live `EDBCM053/2026`、`EDBCM048/2026`、`EDBCM049/2026`、`EDBCM050/2026`
10. Next priorities:
   - 發佈 `v3.0.29`
   - 重跑 workflow 並驗 live sparse/rich summaries + actions
   - 視結果再決定是否需要進一步做 rich-summary guard
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - `v3.0.29` 尚未發布前，live 仍會維持使用者剛見到的 `v3.0.28` regression
12. Notes:
   - 本輪不是回退 K1 或 role-facts；而是修 deterministic 後處理的執行順序，讓既有角色工作能再次以頂層 action 形式顯示。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者在 live `v3.0.28` 回報通告分析＋知識庫後效果變差，且很多角色工作消失，尤其 `EDBCM053/2026` 頂層 `actions` 為空、summary 充滿 filler 句。
2. Root Cause:
   - sparse action synthesis 執行得太早，在 deterministic curriculum / student / finance enrich 把角色 `acts` 補齊之前便已決定 `actions`；此外 summary filler marker 未涵蓋 live 實際出現的幾條 meta 句。
3. Fix:
   - 把 `_synthesize_sparse_actions()` 改到 `_apply_post_analysis_review()` 末段執行；新增對 `未披露`、`以正式發布的公告全文為準`、`此通告未逐一分派角色責任` 的過濾。
4. Verification:
   - local targeted helper 以 `053` 類 sample 驗證：summary 只保留通告主句 + 精簡 follow-up，且重新產生 3 條頂層 `actions`
   - Python / JS compile 均 PASS
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #32 added: sparse action synthesis must run after deterministic role enrichment.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | sparse circular with empty top-level `actions` and role-level `acts` added by deterministic review | apply post-analysis review | summary keeps circular-first wording and top-level `actions` are synthesized after role enrich | `053`-style sample now emits 2 paragraphs + 3 top-level `actions` | PASS |
| Boundary | filler-heavy sparse summary | normalize + apply post-analysis review | ban known filler markers and preserve one useful follow-up paragraph only | `未披露 / 以正式發布的公告全文為準 / 此通告未逐一分派角色責任` removed | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local regression only | local QC valid; cloud regression explicitly skipped | local QC passed; cloud run skipped | PASS with notes |
| Regression | rich circular with existing `actions` | apply post-analysis review | existing top-level actions remain untouched | sparse synthesis still exits early when `actions` already present | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 Sparse action synthesis fallback (workspace v3.0.28)

1. Agent & Session ID: Codex_20260409_0011
2. Task summary: 針對 `EDBCM053/2026` 這類 sparse circular，補回頁面可見的頂層 action 清單。當 top-level `actions` 為空，但角色內 `acts` 已有明確內容時，自動提升 1-3 條既有角色行動到頂層 `actions`。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output quality issue。live `v3.0.27` 已讓 sparse summary 補回第二段，但 `actions` 仍為空，導致頁面上看起來像沒有行動清單；問題不是 K1 或 workflow，而是 sparse circular 沒把既有 role actions 提升到 dashboard 主要 action 區。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `edb_scraper.py`, `edb-dashboard.html`, live `circulars.json`, `README.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 新增 `_synthesize_sparse_actions()`，當 sparse circular 頂層 `actions` 為空時，從最高訊號角色的既有 `acts` 合成最多 3 條 action
   - ✅ 保持 rich circular 原本的頂層 `actions` 不變，不覆蓋既有 action 清單
   - ✅ 版本升至 `v3.0.28`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - sparse helper regression → PASS（`053` 類通告現在會產生 1-3 條頂層 action）
9. Pending:
   - 發布 `v3.0.28`
   - 重跑 school-year workflow
   - 驗證 live `EDBCM053/2026` 等 sparse 通告已重新顯示頂層 action 清單
10. Next priorities:
   - 發布 `v3.0.28`
   - 重跑 workflow 並驗 live sparse actions
   - 視結果再決定是否需要 rich/sparse action 分流進一步收口
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - sparse action synthesis 若過度放寬，可能把 rich circular 的角色行動重複升到頂層；目前已限制只在 `actions` 為空時啟用
12. Notes:
   - 這輪不是新增新 action，而是把既有角色內 action 以較可見的形式提升到頂層。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者指出 `EDBCM053/2026` 雖然摘要有改善，但頁面上看起來像失去了行動清單。
2. Root Cause:
   - sparse summary fallback 只改善了摘要；該類通告的明確行動仍留在 `roles.*.acts`，而頂層 `actions` 保持空陣列。
3. Fix:
   - 新增 sparse-action synthesis：若通告屬 sparse case 且 `actions` 為空，便從最高訊號角色的既有 `acts` 抽取最多 3 條，提升為頂層 `actions`。
4. Verification:
   - local helper 顯示 `EDBCM053/2026` 類資料在保留 summary 第二段的同時，也會得到頂層 action 清單
   - rich circular 原有 `actions` 不受影響
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #31 added: sparse circulars may synthesize top-level actions from existing role-level acts.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | sparse circular with empty top-level `actions` but non-empty role `acts` | apply sparse action synthesis | promote 1-3 existing role actions to top-level `actions` | `053` helper now emits synthesized top-level actions | PASS |
| Boundary | sparse circular with many duplicated role actions | apply sparse action synthesis | dedupe and cap at 3 actions | helper keeps unique actions and stops at 3 | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local helper/syntax checks only | local QC valid; cloud regression explicitly skipped | local QC passed; cloud run skipped | PASS with notes |
| Regression | rich circular already has top-level `actions` | sparse action synthesis should not rewrite list | existing top-level actions remain unchanged | synthesis exits early when `actions` already present | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 K1 split-role cleanup for local knowledge generator

1. Agent & Session ID: Codex_20260409_0010
2. Task summary: 清理 EDB 端仍殘留的 K1 split-role stale contract usage，聚焦 `fetch_knowledge.py` 與其維護中的本地知識輸出，避免新的 K1 交付再被寫回 `department_head`。
3. Layer classification: Product / System Layer（local knowledge support generation / contract cleanup）+ Development Governance Layer（session persistence）
4. Source triage: stale contract / documentation drift issue。主產品 runtime `edb_scraper.py` 已採 split-role contract，但 `fetch_knowledge.py` 與其生成的本地知識檔仍保留 `department_head` / `行政主任` 舊寫法，屬支援產生路徑與維護型文檔不同步，而非主分析流程故障。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `fetch_knowledge.py`, `edb_scraper.py`, `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`, `dev/knowledge/sch_admin_guide.md`, `dev/knowledge/fin_management.md`, `dev/knowledge/sch_activities.md`, `dev/knowledge/press_releases.md`, `dev/knowledge/curriculum_guides.md`, `dev/knowledge/kpm.md`
6. Files changed: `fetch_knowledge.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`, `dev/knowledge/sch_admin_guide.md`, `dev/knowledge/fin_management.md`, `dev/knowledge/sch_activities.md`, `dev/knowledge/press_releases.md`, `dev/knowledge/curriculum_guides.md`, `dev/knowledge/kpm.md`
7. Completed:
   - ✅ 確認 `fetch_knowledge.py` 不是主產品 runtime，但仍是 README 可見、會生成本地知識檔的 maintained support path
   - ✅ 將 `fetch_knowledge.py` 內 active role lists 由 `department_head` 改為 `subject_head + panel_chair`
   - ✅ 更新 `write_index()` role labels：新增 `科主任` / `主任`，並把 `eo_admin` 對外標示改為 `EO`
   - ✅ 同步修正 `ROLE_KNOWLEDGE_INDEX.md` 與維護中的 `dev/knowledge/*.md` header role wording，不再呈現 stale `department_head`
   - ✅ 保留主產品 flow 的 legacy compatibility，不移除 `edb_scraper.py` 對舊 `department_head` data 的 normalization
8. Validation / QC:
   - `python3 -m py_compile fetch_knowledge.py` → PASS
   - `rg -n "department_head" fetch_knowledge.py dev/knowledge/ROLE_KNOWLEDGE_INDEX.md dev/knowledge/sch_admin_guide.md dev/knowledge/fin_management.md dev/knowledge/sch_activities.md dev/knowledge/press_releases.md dev/knowledge/curriculum_guides.md dev/knowledge/kpm.md` → no matches (expected)
   - repo-wide grep still finds `department_head` only in justified legacy compatibility locations (`edb_scraper.py`, `README.md` legacy note, `circulars.json`, `edb-dashboard-mockup.html`) → PASS with notes
9. Pending:
   - 視需要重新執行 `fetch_knowledge.py` 完整生成流程，確認沒有其他未列出的 generated artifact 仍殘留舊角色字眼
   - 持續觀察未來是否可安全清理產品端 legacy `department_head` compatibility
10. Next priorities:
   - 發布 `v3.0.27`
   - 重跑 workflow 並驗證 live sparse summaries
   - 視需要補做 `fetch_knowledge.py` 全量再生成驗證
11. Risks / blockers:
   - K1 public URLs 的 live browser verification 仍屬外部依賴，這輪按使用者指示不阻塞本地 cleanup
   - `sch_admin_guide.md` 目前含 NUL byte；本次只做最小必要 header wording 修正，未重寫整個檔案
   - repo 中仍保留 legacy `department_head` occurrences 以兼容舊 data；不可在未確認安全前一併清除
12. Notes:
   - 本輪任務是「清 stale contract usage」，不是切掉所有歷史兼容層。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - `fetch_knowledge.py` 與其維護中的本地知識輸出仍使用 `department_head` / `行政主任`，與 K1 public `v1.3.1` schema 及本地 interface spec `v2.0.0` 不一致。
2. Root Cause:
   - 主產品 runtime 已先完成 split-role migration，但支援型知識生成腳本和既有 generated artifacts 沒有同步更新，形成 stale contract drift。
3. Fix:
   - 更新 `fetch_knowledge.py` active role lists 與 index labels，並最小修正其維護中的 `ROLE_KNOWLEDGE_INDEX.md` / `dev/knowledge/*.md` 角色字眼到 `subject_head + panel_chair + eo_admin=EO`。
4. Verification:
   - `fetch_knowledge.py` syntax check PASS
   - targeted grep 顯示維護中的 active path 不再含 `department_head`
   - repo-wide grep 僅剩 legacy compatibility usages，且已明確標記為保留理由
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #30 added: local knowledge generator / maintained artifacts must stay on split-role contract; remaining `department_head` is compatibility-only.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | `fetch_knowledge.py` maintained support path | inspect + py_compile | role lists and labels align to split-role contract; script still parses | active role lists now use `subject_head + panel_chair`; py_compile PASS | PASS |
| Boundary | maintained generated docs with stale role headers | patch maintained headers/index | docs no longer present active `department_head` wording | targeted docs/index now show `subject_head / panel_chair` | PASS |
| Error / failure path | binary-ish `sch_admin_guide.md` contains NUL | minimal patch only | avoid broad rewrite; update only necessary wording | header role wording updated without full file rewrite | PASS with notes |
| Regression | main product legacy data compatibility must remain | repo-wide grep review | legacy `department_head` may remain only in justified compatibility paths | remaining hits limited to `edb_scraper.py`, `README.md` note, `circulars.json`, archived mockup | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |


## 2026-04-09 Session closeout after v3.0.28 push

1. Agent & Session ID: Codex_20260409_0012
2. Task summary: 完成本輪 closeout，整理 K1 split-role cleanup + sparse-action synthesis 的真實狀態，並在 `v3.0.28` push 完成後重排下一輪 handoff。
3. Layer classification: Product / System Layer（release status / summary-action behavior follow-up）+ Development Governance Layer（session closeout / archive maintenance）
4. Source triage: closeout / release-state consolidation。需要把本輪多個連續改動收斂成單一可交接基線，並在 `SESSION_LOG.md` 觸發 archive rotation 後保留最新 2 entries + 本次 closeout entry。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, live workflow/publish status context
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 依 archive 規則將 `SESSION_LOG.md` 修剪至只保留最近 entries，舊 entries 已追加到 `dev/archive/SESSION_LOG_2026_Q2.md`
   - ✅ 更新 `SESSION_HANDOFF.md`，反映 `v3.0.28` 已 push 到 repo `590f398`
   - ✅ 重排 Open Priorities，將下一步聚焦於驗證 live `v3.0.28` 與 `EDBCM053/2026` 頂層 actions
   - ✅ 寫入本次 closeout handoff prompt（verbatim）
8. Validation / QC:
   - `wc -l dev/SESSION_LOG.md` after archive trim → 127 lines before appending closeout entry
   - `git -C ~/Documents/EDB-AI-Circular-System status --short --branch` → clean after push
   - `git -C ~/Documents/EDB-AI-Circular-System rev-parse --short HEAD` → `590f398`
9. Pending:
   - 驗證 `v3.0.28` 的 school-year workflow 是否已完成並帶上 live
   - 驗證 `EDBCM053/2026` 是否重新出現頂層 action 清單
   - 對照 `EDBCM048/2026` 與其他 rich circular，確認 sparse action synthesis 沒有副作用
10. Next priorities:
   - 驗證 live `v3.0.28`
   - 核對 `053` sparse actions 與 `048` rich summary/action 行為
   - 視結果再決定是否需要 rich/sparse action 分流再收口
11. Risks / blockers:
   - closeout 時無法確認 live workflow 最終結果
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
12. Notes:
   - 本輪 closeout 不再做新 code change；重點是把已完成工作收斂成可接手狀態。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from repo-pushed `v3.0.28` as of 2026-04-09. The deploy repo is at commit `590f398`; `v3.0.28` includes sparse-action synthesis so sparse circulars with empty top-level `actions` can promote up to three existing role-level actions into the dashboard-visible action list. At closeout, live GitHub Pages / live `circulars.json` for `v3.0.28` had not yet been re-verified.

Pending tasks (priority order):
1. Verify whether the `school-year` workflow for `v3.0.28` has completed and whether live HTML / live `circulars.json` have caught up.
2. Check `EDBCM053/2026` on live data and confirm top-level `actions` are now present again.
3. Compare `EDBCM048/2026` and at least 4 other live circulars to ensure sparse-action synthesis did not distort rich circular summaries/actions.
4. Only if the above passes, decide whether any further rich/sparse action split refinement is needed.

Key files changed in this session:
- `fetch_knowledge.py`
- `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`
- `dev/knowledge/sch_admin_guide.md`
- `dev/knowledge/fin_management.md`
- `dev/knowledge/sch_activities.md`
- `dev/knowledge/press_releases.md`
- `dev/knowledge/curriculum_guides.md`
- `dev/knowledge/kpm.md`
- `edb_scraper.py`
- `edb-dashboard.html`
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- `v3.0.28` was pushed successfully, but closeout happened before live workflow verification.
- Remaining `department_head` references in the repo are expected legacy compatibility only (`edb_scraper.py` normalization, old `circulars.json`, archived/mockup paths).
- The environment still lacks `OPENAI_API_KEY`, so no full cloud end-to-end regression was run locally.

Validation status: `fetch_knowledge.py` py_compile PASS; active-path grep PASS; `edb_scraper.py` py_compile PASS; dashboard JS compile PASS; sparse helper PASS (`053`-style sample now regains top-level actions); repo push PASS at `590f398`.

Post-startup first action: fetch live `edb-dashboard.html` and `circulars.json`, confirm whether `v3.0.28` is live, then inspect `EDBCM053/2026` and `EDBCM048/2026` before making any further summary/action changes.
```
