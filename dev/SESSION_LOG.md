# Session Log
<!-- Archives: dev/archive/ — entries moved when >800 lines or oldest entry >30 days -->

## 2026-04-11 Session closeout after v3.0.38 push + workflow verification

1. Agent & Session ID: Codex_20260411_0003
2. Task summary: 完成 `v3.0.38` push 後的 live verification 與 session closeout。結果顯示 `school-year` workflow 已成功重生 `circulars.json` 至 `117` 份，但 public HTML 仍顯示 `v3.0.37`，且 `053 / 048 / 043` 的 summary 基本未見 `v3.0.38` 預期改良，因此目前應把 `v3.0.38` 視為 repo-pushed、live deploy 未證實。
3. Layer classification: Product / System Layer（release/deploy verification + summary behavior validation）+ Development Governance Layer（session closeout / archive rotation）
4. Source triage: closeout / release-state consolidation。問題不再是 circulars 消失，而是 release verification 顯示 code deploy 狀態與 data regeneration 狀態不一致。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, live `edb-dashboard.html`, live `circulars.json`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 依 §4a 先將 `SESSION_LOG.md` 舊 entry 歸檔到 `dev/archive/SESSION_LOG_2026_Q2.md`
   - ✅ 驗證 live `circulars.json` 已更新：`generated_at=2026-04-11T13:26:11Z`, `count=117`
   - ✅ 驗證 `EDBCM053/2026`、`EDBCM043/2026`、`EDBCM048/2026`、`EDBCM049/2026`、`EDBCM050/2026`
   - ✅ 確認 `053/048/043` summary 仍偏舊風格，`v3.0.38` 的 source-less fallback 改良未在 live 看到
   - ✅ 更新 `SESSION_HANDOFF.md` 為真實基線：repo pushed `v3.0.38`, live HTML still `v3.0.37`, live data regenerated
8. Validation / QC:
   - `curl -L .../edb-dashboard.html` → still shows `v3.0.37`
   - `curl -L .../circulars.json` → PASS (`generated_at=2026-04-11T13:26:11Z`, `count=117`, `len=117`)
   - targeted live sample review → PASS with notes (`049/050` acceptable; `053/048/043` still unsatisfactory)
9. Pending:
   - 先確認 `v3.0.38` 是否真的 deploy 到 live HTML
   - 若已 deploy 但 summaries 仍未變，修 source-less non-empty generic summary refresh
10. Next priorities:
   - 驗 deploy mismatch：repo-pushed `v3.0.38` vs live HTML `v3.0.37`
   - 若 deploy 無問題，再收 `053 / 048 / 043` 的 source-less summary 根因
   - 視需要再決定是否發布下一個窄修版本
11. Risks / blockers:
   - live HTML / live data 版本狀態不一致，增加判讀成本
   - 本機仍缺 `OPENAI_API_KEY`
   - 很多 live circular 仍缺 `official/pdf_text`，因此摘要上限受 source scarcity 影響
12. Notes:
   - 這輪不再改 code；只把 deploy verification 的真實狀態寫清楚，避免下個 session 從錯誤基線出發。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from the 2026-04-11 state where repo/deploy changes for `v3.0.38` have already been pushed, but live verification is inconsistent. Public `circulars.json` is fresh (`generated_at=2026-04-11T13:26:11Z`, `count=117`) after the latest school-year workflow, yet public `edb-dashboard.html` still reports `v3.0.37`, and the summaries for `EDBCM053/2026`, `EDBCM048/2026`, and `EDBCM043/2026` still look like the older generic style. Treat `v3.0.38` as repo-pushed but live deploy unverified until proven otherwise.

Pending tasks (priority order):
1. Verify whether public GitHub Pages is truly serving the `v3.0.38` HTML; if not, determine why the repo-pushed version did not appear on live.
2. If `v3.0.38` is live but the summaries still look unchanged, fix the actual root cause: source-less but non-empty generic summaries are not being force-refreshed into the new fallback wording.
3. Re-check live `EDBCM053/2026`, `EDBCM048/2026`, `EDBCM043/2026`, plus `EDBCM049/2026` and `EDBCM050/2026`, after any deploy or code change.
4. Only after the above passes, decide whether any further summary refinement is needed.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`
- `dev/archive/SESSION_LOG_2026_Q2.md`

Known risks / blockers / cautions:
- Live HTML and live JSON are currently out of sync in observed version state: HTML still reports `v3.0.37`, while `circulars.json` has been regenerated on 2026-04-11.
- `EDBCM053/2026`, `EDBCM048/2026`, and `EDBCM043/2026` still read like generic summaries; do not assume the `v3.0.38` fallback fix is active on live.
- The environment still lacks `OPENAI_API_KEY`, so no full cloud end-to-end regression was run locally.

Validation status: live `circulars.json` fetch PASS (`generated_at=2026-04-11T13:26:11Z`, `count=117`, `len=117`); live `edb-dashboard.html` still shows `v3.0.37`; targeted live sample review PASS with notes (`049/050` acceptable, `053/048/043` still problematic); `SESSION_LOG.md` archive rotation completed.

Post-startup first action: fetch public `edb-dashboard.html` and `circulars.json` again, confirm whether HTML still reports `v3.0.37`, then compare that result against the repo-pushed `v3.0.38` expectation before making any new summary code changes.
```

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

## 2026-04-11 Source-less summary fallback cleanup

1. Agent & Session ID: Codex_20260411_0002
2. Task summary: `v3.0.37` live 後，使用者確認 `053 / 048 / 043` 仍偏官式。核實後發現這些 live records 的 `official` / `pdf_text` 都是空值，因此 source-rich extractor 根本無法觸發；本輪只修 source-less fallback wording。
3. Layer classification: Product / System Layer（summary fallback wording）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output quality issue。問題不在 K1、actions 或 data volume，而在於無正文 case 仍沿用過於官式的 generic summary wording。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, live `circulars.json`, `edb_scraper.py`, `README.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 核實 live `v3.0.37`：`generated_at=2026-04-11T09:51:47Z`, `count=117`
   - ✅ 核實 `EDBCM053/2026` / `048` / `043` 的 `official` / `pdf_text` 都是 `0`
   - ✅ source-less fallback 改為較實在的 date/title/tag/topic wording
   - ✅ 移除 `後續協調的依據` / `請學校留意後續更新` / `校方公告中公布` 等空話 marker
   - ✅ workspace version 升到 `v3.0.38`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - helper regression → PASS
9. Pending:
   - 決定是否發布 `v3.0.38`
   - 若發布，重跑 workflow 後再驗 `053 / 043 / 048`
10. Next priorities:
   - 決定是否發布 `v3.0.38`
   - 若發布，驗 live source-less summaries 是否收口
   - 視結果再決定是否仍要收 `043` 類摘要濃度
11. Risks / blockers:
   - 本機缺 `OPENAI_API_KEY`
   - live 仍有不少 records 沒有 `official/pdf_text`，因此摘要品質上限會受 source scarcity 影響
12. Notes:
   - 這輪沒有再碰 source-rich extractor；只處理 live 真實最常見的 source-less case。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - `v3.0.37` live 後，`053 / 048 / 043` 仍有官腔、空泛或「後續更新」式摘要。
2. Root Cause:
   - live 這些通告根本沒有 `official` / `pdf_text`，所以 source-based summary 不會觸發，只能落回過於 generic 的 title/tag fallback。
3. Fix:
   - 收緊 source-less fallback wording，加入 date/title/tag/topic 的較實在摘要句，並把 `後續更新 / 後續協調` 類句子列入 banned markers。
4. Verification:
   - live JSON inspection confirmed `official_len=0`, `pdf_len=0` for `053 / 048 / 043`
   - local helper showed these cases no longer produce `後續更新 / 後續協調` style filler
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #38 added: source-less circulars need concrete fallback wording.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | source-less activity circular with official-sounding summary | apply post-analysis review | remove `後續協調 / 後續更新` filler and keep concrete synopsis | `053`/`048` style helpers lose filler and keep date/title/topic summary | PASS |
| Boundary | source-less exhibition circular already short | apply post-analysis review | preserve concise summary without adding filler | `043` style helper remains concise and two-paragraph | PASS |
| Error / failure path | no `official` / no `pdf_text` | source-based refresh unavailable | fallback still returns a usable summary | date/title/tag fallback used successfully | PASS |
| Regression | summary-only task must not affect actions/K1 | inspect helper output | actions count unchanged by fallback wording cleanup | actions untouched in helper samples | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |
