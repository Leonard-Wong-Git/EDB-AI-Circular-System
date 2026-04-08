# Session Log
<!-- Archives: dev/archive/ — entries moved when >800 lines or oldest entry >30 days -->

## 2026-04-08 K1 public JSON integration + v3.0.17

1. Agent & Session ID: Codex_20260408_0001
2. Task summary: 在 EDB Circular System 實作 K1 public JSON integration。`edb_scraper.py` 現可 fetch live `knowledge.json` / `guidelines.json`，在 LLM 分析前以 detected topics 注入 facts / guideline links，並在 fetch 失敗時自動降級。
3. Layer classification: Product / System Layer（external JSON API integration + analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 屬外部平台整合。先核實 K1 live endpoints 與現有分析入口，再做最小整合到 `KnowledgeStore` / `LLMAnalyzer` 附近，避免重寫整個分析流程。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md`, `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 驗證 live K1 endpoints：`knowledge.json` / `guidelines.json` 可抓取，`_meta.version=1.2.2`
   - ✅ 發現並記錄 live K1 facts schema 與舊 task brief 不完全一致：live `knowledge.json` 為 topic → role-arrays 形態
   - ✅ 在 `edb_scraper.py` 新增 `K1KnowledgeClient`
   - ✅ 新增 pre-LLM topic detection、K1 facts fetch、K1 guidelines fetch
   - ✅ 將 `【相關政策事實】` / `【相關指引文件】` 注入 prompt
   - ✅ 加入 graceful fallback：K1 fetch 失敗時不崩潰，繼續分析
   - ✅ 將 `k1_topics` / `k1_facts` / `k1_guidelines` 附於輸出 record
   - ✅ 版本同步升至 `v3.0.17`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS syntax check → PASS
   - live K1 payload verification → PASS (`knowledge.json`, `guidelines.json`, `_meta.version=1.2.2`)
   - finance scenario → PASS (`FIN_TOPICS=['finance']`, facts count `10`, docs count `2`)
   - curriculum scenario → PASS (`CUR_TOPICS=['curriculum']`, docs count `24`)
   - failure fallback scenario → PASS (`FAIL_FACTS=[]`, `FAIL_DOCS=[]`)
9. Pending:
   - 發布 `v3.0.17`
   - 修正 topic-aware review 疊加污染，避免 supplier / finance links 跑入 curriculum / student 通告
   - 等待新版 `role_facts.json`
10. Next priorities:
   - 發布並驗證 `v3.0.17`
   - 修正 topic-aware review 疊加污染
   - 等待 / 整合新版 role_facts.json
11. Risks / blockers:
   - K1 public facts live schema 與舊 task brief 不完全一致；目前靠兼容 parser 同時支持兩種形態
   - public `K1_API_SPEC.md` URL 於 2026-04-08 實測返回 404
   - `role_facts.json` 仍未交付，另一條 K1 role-facts integration 尚待驗證
12. Notes:
   - 這輪沒有 deploy，public GitHub Pages 仍以 `v3.0.16` 為準。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 需要把 K1 知識庫 facts / guideline docs 接入現有分析流程，而且 fetch 失敗時不能讓系統崩潰。
2. Root Cause:
   - 目前 pipeline 只有本地 semantic knowledge search，沒有針對 K1 public JSON endpoints 的 prompt enrichment。
3. Fix:
   - 新增 `K1KnowledgeClient`，在 LLM 前用 topic detection 取回 K1 facts / guidelines，注入 prompt，並在輸出保留 `k1_topics` / `k1_facts` / `k1_guidelines`。
4. Verification:
   - finance / curriculum / failure fallback 三類場景都通過；語法檢查亦通過。
5. Regression / rule update:
   - 未新增治理規則；已更新 `CODEBASE_CONTEXT.md` External Services 與 Key Decision。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | live K1 JSON 已可抓取 | 用 finance sample 呼叫 topic detect + facts/docs fetch | 取到 finance facts 與 guideline docs | `FIN_TOPICS=['finance']`, facts `10`, docs `2` | PASS |
| Boundary | live K1 knowledge schema 與舊 brief 不同 | 用目前 live `knowledge.json` 做 parser 測試 | role-array schema 仍可取出 facts | facts 成功由 `all_roles` / `department_head` buckets 取出 | PASS |
| Error / failure path | K1 fetch 發生 network error | monkeypatch `requests.get` to raise | 回傳空 facts/docs，不拋出 exception | `FAIL_FACTS=[]`, `FAIL_DOCS=[]` | PASS |
| Regression | dashboard 僅版本同步 | 做 JS syntax check | 前端 script 不壞 | `JS syntax OK` | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| External API / service change | CODEBASE_CONTEXT.md External Services block | ✓ Done |
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from workspace `v3.0.17` as of 2026-04-08. K1 public JSON integration is now implemented locally in `edb_scraper.py`: the pipeline fetches live `knowledge.json` and `guidelines.json`, detects topics before LLM analysis, injects K1 facts and guideline links into the prompt, and degrades gracefully if K1 fetch fails. Public GitHub Pages remains on `v3.0.16` until this workspace is deployed.

Pending tasks (priority order):
1. Publish `v3.0.17` and verify that the live site / regenerated data reflect the K1 prompt integration.
2. Fix topic-aware review cross-topic contamination so supplier / finance links do not leak into curriculum / student circulars.
3. When the refreshed `role_facts.json` arrives, validate it against `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` v2.0.0 before integrating that separate K1 role-facts path.

Key files changed in this session:
- `edb_scraper.py`
- `edb-dashboard.html`
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- live K1 `knowledge.json` currently uses a topic → role-array schema, not the older entry-list schema in the task brief; the code now supports both, but this should remain under watch.
- the public `K1_API_SPEC.md` URL returned 404 on 2026-04-08, so the integration was aligned against the user-provided spec plus live payload verification.
- `role_facts.json` still has not been delivered, so that separate K1 integration path remains pending.

Validation status: `python3 -m py_compile edb_scraper.py` PASS; dashboard JS syntax PASS; live K1 endpoint verification PASS (`_meta.version=1.2.2`); finance facts scenario PASS; curriculum guideline scenario PASS; network-failure fallback PASS.

Post-startup first action: either publish `v3.0.17` immediately, or if holding deploy, inspect `_apply_post_analysis_review()` and tighten topic gating so supplier / finance links stop leaking into curriculum / student circulars.
```

## 2026-04-06 Final live verification + session closeout for v3.0.16

1. Agent & Session ID: Codex_20260406_0013
2. Task summary: 依使用者要求執行 session closeout 並產出有日期的 handoff 文字；同時把 handoff / log 從「等待 propagation」修正為真實狀態：`v3.0.16` 已 live，workflow 已重生新角色資料。
3. Layer classification: Product / System Layer（release/live verification state）+ Development Governance Layer（session closeout / archive rotation）
4. Source triage: 非新功能開發；屬 closeout、live-state reconciliation、governance persistence。因 `SESSION_LOG.md` 超過 800 行，觸發 AGENTS §4a archive rotation。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/archive/SESSION_LOG_2026_Q2.md`
7. Completed:
   - ✅ 完成 mandatory startup reads after context compaction
   - ✅ 更新 `SESSION_HANDOFF.md`：baseline 改為 `v3.0.16` live 已確認、workflow data 已重生
   - ✅ `SESSION_LOG.md` 觸發 archive rotation：舊 entries moved to `dev/archive/SESSION_LOG_2026_Q2.md`
   - ✅ 重新生成 Open Priorities：移除 Pages propagation / workflow 重跑已完成項目
   - ✅ 寫入本 closeout entry 與 verbatim next-session handoff prompt
8. Validation / QC:
   - startup file reads → PASS
   - `wc -l dev/SESSION_LOG.md` before archive → PASS with notes (`1863`, archive triggered)
   - archive rotation → PASS（保留最近兩個 entries，舊 entries append 到 `dev/archive/SESSION_LOG_2026_Q2.md`）
   - final known live state → PASS：public HTML verified at `v3.0.16`; public JSON verified with `generated_at=2026-04-06T21:48:38Z`, `count=114`; live examples contain `subject_head` / `panel_chair`
9. Pending:
   - 等待新版 `role_facts.json`
   - 抽樣檢查 live `subject_head` / `panel_chair` 輸出質素
   - 視需要開始下一個 topic-aware review 擴展（例如 `hr` / `it`）
10. Next priorities:
   - 等待 / 整合新版 role_facts.json
   - 抽樣檢查 `subject_head` / `panel_chair` live 輸出質素
   - 視需要開始下一個 topic-aware review 擴展
11. Risks / blockers:
   - 新版 `role_facts.json` 尚未交付；K1 接入仍待驗證
   - `subject_head` / `panel_chair` 分流已上線，但仍建議用真實通告樣本觀察是否需要微調
   - 舊 AI 文字摘要中可能仍殘留「行政主任」等中文 prose；這不是 schema bug，但可日後做 wording cleanup
12. Notes:
   - 本 closeout 不改產品代碼；產品端 v3.0.16 已在前一輪完成與發布，本輪是最終狀態對帳與治理持久化。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - Handoff / latest log entry still described the earlier state where public Pages had not yet caught up to `v3.0.16`, but user later confirmed workflow was done and live verification showed the new schema.
2. Root Cause:
   - GitHub Pages propagation and workflow regeneration completed after the previous persistence entry.
3. Fix:
   - Updated `SESSION_HANDOFF.md` and prepended this final closeout entry; archived old `SESSION_LOG.md` entries per §4a.
4. Verification:
   - Live state recorded as `v3.0.16`, public JSON `generated_at=2026-04-06T21:48:38Z`, `count=114`, with `subject_head` / `panel_chair` present in live data examples.
5. Regression / rule update:
   - No new long-term rule added; existing closeout and archive rules were applied.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | Closeout requested after `v3.0.16` workflow completed | Update handoff/log to final live state | Handoff reflects live `v3.0.16` and regenerated data | Baseline and last session record updated | PASS |
| Boundary | `SESSION_LOG.md` >800 lines | Apply §4a archive rotation | Keep recent entries and move older entries to archive | old entries appended to `dev/archive/SESSION_LOG_2026_Q2.md` | PASS |
| Error / safety path | No new `role_facts.json` is present | Record as pending instead of assuming K1 integration complete | Handoff warns K1 payload still pending | pending/risk recorded | PASS |
| Regression | Existing next-session startup requirements remain intact | Persist verbatim handoff prompt | Prompt starts with required two-line startup instruction | block below matches closeout output | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from the verified live `v3.0.16` baseline as of 2026-04-06. GitHub Pages is live at `v3.0.16`, and the public `circulars.json` was regenerated by workflow at `2026-04-06T21:48:38Z` with `count=114`; live data now uses the new `subject_head` / `panel_chair` role schema.

Pending tasks (priority order):
1. Wait for / validate the new `role_facts.json` against `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` v2.0.0 before integrating K1 role knowledge.
2. Sample-check live circulars for `subject_head` vs `panel_chair` quality, then tune topic-aware routing only if real outputs show drift.
3. If role outputs remain stable, consider the next topic-aware review expansion, likely `hr` or `it`.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`
- `dev/archive/SESSION_LOG_2026_Q2.md`

Known risks / blockers / cautions:
- The refreshed `role_facts.json` has not yet been delivered, so K1 integration remains pending.
- `subject_head` / `panel_chair` is live, but role split quality should be judged with real circular samples before adding more rules.
- Older generated prose may still mention legacy Chinese wording such as `行政主任`; this is wording cleanup, not a schema blocker.

Validation status: local startup reads PASS; prior code checks PASS (`python3 -m py_compile edb_scraper.py`, dashboard JS syntax, legacy-role normalization helper); public HTML PASS at `v3.0.16`; public JSON PASS with `generated_at=2026-04-06T21:48:38Z`, `count=114`, and live examples containing `subject_head` / `panel_chair`.

Post-startup first action: check whether a refreshed `role_facts.json` has arrived; if not, sample two or three live circulars to review `subject_head` / `panel_chair` assignment quality before making further schema or topic-review changes.
```

## 2026-04-06 Publish v3.0.16 role-compatibility layer to repo

1. Agent & Session ID: Codex_20260406_0012
2. Task summary: 依使用者要求執行 `push`，將本地 `v3.0.16`（七角色 UI + 第一階段角色相容層）發布到 deploy repo / GitHub repo，並重新驗證 public GitHub Pages 狀態。
3. Layer classification: Product / System Layer（release publish / verification）+ Development Governance Layer（session persistence）
4. Source triage: 非新功能開發；屬 release publish 與 propagation 驗證。目標是把已完成的 role compatibility layer 推上 repo，並如實確認 public site 是否已更新。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 執行 `bash /Users/leonard/Downloads/Claude-edb-Project-V3/deploy.sh --no-bump`
   - ✅ 成功推送 deploy repo `main` 至 commit `839a743`
   - ✅ 驗證 deploy repo 狀態乾淨、已與 `origin/main` 對齊
   - ✅ 重新抓取 public GitHub Pages HTML / JSON 進行 cache-busted 驗證
   - ✅ 更新 handoff / log，記錄「repo 已上 `v3.0.16`、public site 暫仍 `v3.0.14`」的當前狀態
8. Validation / QC:
   - `bash /Users/leonard/Downloads/Claude-edb-Project-V3/deploy.sh --no-bump` → PASS
   - `git -C ~/Documents/EDB-AI-Circular-System rev-parse --short HEAD` → PASS (`839a743`)
   - `git -C ~/Documents/EDB-AI-Circular-System status --short --branch` → PASS (`main...origin/main`)
   - `curl -L 'https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html?t=20260406-v3016-push'` → PASS with notes (public HTML still shows `v3.0.14`)
   - `curl -L 'https://leonard-wong-git.github.io/EDB-AI-Circular-System/circulars.json?t=20260406-v3016-push'` → PASS with notes (`generated_at=2026-04-06T20:44:25Z`, `count=114`; roles still use old live data structure)
9. Pending:
   - 等待 GitHub Pages propagation 或手動觸發相關 workflow
   - 等待用戶提供新版 `role_facts.json`
   - 重跑 workflow，驗證 live `circulars.json` 在新角色結構下的輸出與顯示
10. Next priorities:
   - 追蹤 public GitHub Pages 是否追上 `v3.0.16`
   - 等待 / 整合新版 role_facts.json
   - 視需要重跑 workflow 更新 live `circulars.json`
11. Risks / blockers:
   - repo 已是 `v3.0.16`，但 public Pages 最新 cache-busted 檢查仍回 `v3.0.14`
   - live `circulars.json` 仍是舊角色結構，尚未用新 schema workflow 重生
12. Notes:
   - 這次 repo 推送成功，但 GitHub Pages propagation 顯然仍未完成；不能宣稱 live 已經是 `v3.0.16`

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者要求 `push` 本地 `v3.0.16`，並需要知道是否已真正上線。
2. Root Cause:
   - `v3.0.16` 僅存在 workspace，尚未推送到 deploy repo / public site；而 public Pages 是否更新需另行驗證。
3. Fix:
   - 執行既有 `deploy.sh --no-bump` 發布流程，之後立即用 cache-busting 方式檢查 public HTML / JSON。
4. Verification:
   - deploy repo `HEAD=839a743`
   - deploy repo clean and tracking `origin/main`
   - public HTML 仍為 `v3.0.14`
   - public JSON 仍為 `generated_at=2026-04-06T20:44:25Z`, `count=114`
5. Regression / rule update:
   - 無新增治理規則；本次屬 release publish 與 live-state documentation update。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Publish flow | local workspace 已在 `v3.0.16` | 執行 `deploy.sh --no-bump` | repo `main` 成功更新到 `v3.0.16` | commit `839a743` pushed | PASS |
| Repo parity | push 完成後 | 檢查 deploy repo status | working tree clean and tracking origin | `main...origin/main` | PASS |
| Public frontend propagation | push 後再次檢查 public HTML | 應看到 `v3.0.16` 或明確辨識 propagation 未完成 | public HTML 仍顯示 `v3.0.14` | PASS with notes |
| Public data refresh | 未再跑 workflow | 檢查 public `circulars.json` | 仍保留既有 live dataset | `generated_at=2026-04-06T20:44:25Z`, `count=114` | PASS |

Overall: PASS with notes

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from repo-pushed v3.0.16. The first product-side role compatibility layer has been published to GitHub repo commit `839a743`, but public GitHub Pages was cache-busted on 2026-04-06 and still served `v3.0.14`, so propagation is not complete yet.

Pending tasks (priority order):
1. Recheck public GitHub Pages until the site actually shows v3.0.16.
2. When the user provides a new `role_facts.json`, validate it against the K1 v2.0.0 contract before integrating it.
3. Rerun the workflow so live `circulars.json` is regenerated under the new role structure and then verify the public site output.
4. If needed, refine the topic-aware split between `subject_head` and `panel_chair`.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- Repo is already on v3.0.16, but public Pages still showed v3.0.14 during the latest cache-busted verification.
- live `circulars.json` still reflects the previous workflow output and old role structure.
- Do not claim v3.0.16 is live until the fetched public HTML actually shows it.

Validation status: deploy script PASS; deploy repo HEAD/status PASS; public HTML check still showed v3.0.14; public JSON check showed `generated_at=2026-04-06T20:44:25Z`, `count=114`.

Post-startup first action: fetch the public `edb-dashboard.html` again with a cache-busting query param and confirm whether GitHub Pages has caught up to v3.0.16.
```

## 2026-04-06 Product-side role compatibility layer + v3.0.16

1. Agent & Session ID: Codex_20260406_0011
2. Task summary: 把產品端做成第一階段角色相容層，讓 `edb_scraper.py` 和 `edb-dashboard.html` 可接受新的 `subject_head` / `panel_chair` 契約，同時保持舊 `department_head` 資料可讀，並把 workspace 版本升到 `v3.0.16`。
3. Layer classification: Product / System Layer（analysis pipeline behavior change + frontend display behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 非 bug fix；屬角色 schema 過渡重構。目標是避免 K1 規格已換新角色後，產品端仍只認舊 key，導致知識庫接入或 live 舊資料其中一邊失效。
5. Files read: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ `CIRCULAR_SCHEMA` / `SYSTEM_PROMPT` 改為 `subject_head` + `panel_chair`
   - ✅ 新增 `_normalize_roles_payload()`，將 legacy `department_head` 自動映射到 `panel_chair`
   - ✅ `actions` / `deadlines` 中的 legacy role key 也會一併正規化
   - ✅ dashboard 改為七角色 UI：校長 / 副校長 / 科主任 / 主任 / 教師 / EO / 供應商
   - ✅ localStorage 舊 `department_head` 角色選擇可自動轉為 `panel_chair`
   - ✅ 版本同步升至 `v3.0.16`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS syntax check → PASS
   - legacy-role normalization helper check → PASS
   - `rg -n "subject_head|panel_chair|department_head|v3\\.0\\.16" edb_scraper.py edb-dashboard.html README.md` → PASS
9. Pending:
   - 決定是否發布 `v3.0.16`
   - 等待用戶提供新版 `role_facts.json`
   - 重跑 workflow，驗證 live `circulars.json` 在新角色結構下的輸出與顯示
   - 視需要微調 `subject_head` / `panel_chair` 的 topic-aware 分流
10. Next priorities:
   - 視需要發布 `v3.0.16`
   - 等待 / 整合新版 role_facts.json
   - 視需要重跑 workflow 更新 live `circulars.json`
11. Risks / blockers:
   - `v3.0.16` 目前只在 workspace；live 站仍是 `v3.0.14`
   - 第一階段相容層目前採保守映射：legacy `department_head` 一律先落到 `panel_chair`
   - `subject_head` / `panel_chair` 的 topic-aware 分流仍可再細化
12. Notes:
   - 這輪刻意不做激進推斷；舊資料不會自動猜成 `subject_head`，避免錯分類

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - K1 契約已切到 `subject_head` / `panel_chair`，但產品端仍只認 `department_head`。
2. Root Cause:
   - 舊 schema、前端角色 UI、post-analysis review 與資料讀取流程都還沒建立過渡層。
3. Fix:
   - 在 scraper 與 dashboard 同步加入 compatibility layer，讓新舊角色鍵都能被吸收，並將前端顯示正式改為七角色。
4. Verification:
   - py_compile PASS
   - JS syntax PASS
   - helper 測試確認 legacy `department_head` → `panel_chair`，且 review 邏輯在新角色結構下仍可運作
5. Regression / rule update:
   - Key Decision #19 added in `CODEBASE_CONTEXT.md`: role compatibility layer before full schema cutover

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | 新分析輸出要採用新角色契約 | 以 `subject_head` / `panel_chair` schema 編譯與前端載入 | scraper / dashboard 接受新角色鍵 | schema / UI 均已更新 | PASS |
| Boundary | 舊資料只含 `department_head` | 套用 `_normalize_roles_payload(sample)` | 自動落到 `panel_chair`，`subject_head` 保持空白 | `panel_chair` 吃到 legacy 內容，`subject_head=[]` | PASS |
| Error / safety path | 舊 actions / deadlines 仍含 `department_head` | 正規化 sample actions / deadlines | role key 同步轉為 `panel_chair` | helper check shows `panel_chair` in actions / deadlines | PASS |
| Regression | student review 在新角色結構下仍可跑 | 以 student sample 執行 `_apply_post_analysis_review()` | `panel_chair` 與 `subject_head` 角色結構均有效 | helper check shows `REVIEW_PANEL_RELATED=True`, `REVIEW_SUBJECT_RELATED=True` | PASS |

Overall: PASS

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from local v3.0.16. The first product-side compatibility layer for the new role contract is now in place: scraper and dashboard accept `subject_head` / `panel_chair`, while legacy `department_head` data is normalized to `panel_chair`. This is still workspace-only and has not been deployed yet.

Pending tasks (priority order):
1. Decide whether to publish v3.0.16 so the 7-role UI and compatibility layer go live on GitHub Pages.
2. When the user provides a new `role_facts.json`, validate it against the K1 v2.0.0 contract before integrating it.
3. Rerun the workflow so live `circulars.json` is regenerated under the new role structure and then verify the public site output.
4. If needed, refine the topic-aware split between `subject_head` and `panel_chair` so curriculum / student / finance reminders land on the most appropriate role.

Key files changed in this session:
- `edb_scraper.py`
- `edb-dashboard.html`
- `README.md`
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- v3.0.16 is local only; the public site is still on v3.0.14 until a deploy happens.
- The compatibility layer currently maps legacy `department_head` conservatively to `panel_chair`; it does not auto-infer `subject_head` from old records.
- The workspace still does not contain a real new `dev/knowledge/role_facts.json`, so K1 payload validation remains pending.

Validation status: py_compile PASS; dashboard JS syntax PASS; legacy-role normalization helper PASS; version markers PASS at v3.0.16; no deploy performed in this session.

Post-startup first action: inspect whether the next step is deploying v3.0.16 or validating an incoming new `role_facts.json`, then use the compatibility layer as the baseline for that decision.
```

---

## 2026-04-08 K1 backfill fix + calendar fix + apply-ext form — v3.0.18

1. Agent & Session ID: Claude_20260408_1400
2. Task summary: 修復三個問題：(1) 月曆 April entries 只顯示通告編號無類型標籤；(2) 資源申請狀態無延伸互動功能；(3) live circulars.json 所有記錄 k1_topics/k1_facts/k1_guidelines 為空 — 根因：v3.0.17 K1 代碼於 workflow run #121 之後才 commit，舊 records 已被 incremental 跳過且 _empty_analysis() 無 k1_* fields。
3. Layer classification: Product / System Layer（scraper pipeline fix + dashboard UI fix）
4. Source triage: K1 空字段 = 代碼邏輯問題（timing mismatch + 缺 carry-forward 邏輯）；月曆標籤 = 代碼邏輯問題；apply-ext = 功能缺失
5. Files read: dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md, edb_scraper.py, edb-dashboard.html
6. Files changed: edb_scraper.py (git repo + workspace), edb-dashboard.html (git repo + workspace)
7. Completed:
   - ✅ 月曆 dlLabel fix：calendar cells 現顯示 `⏰ EDBC042 申請` 格式
   - ✅ apply-ext interactive form：已申請 → date-picker + notes input；申請中 → notes input；localStorage 持久化
   - ✅ K1 Phase 3 skip-block carry-forward：incremental skip 時從 existing record 帶 k1_* fields
   - ✅ K1 Phase 4.5 backfill pass：merge-sort 後對所有 k1_topics=[] records 批量補填
   - ✅ analyze() post-LLM K1 re-detect：LLM 返回後用 LLM-derived topics 重新偵測 K1 topics（更準確）
   - ✅ 版本升至 v3.0.18（scraper print + dashboard 6 locations，both git repo and workspace）
   - ✅ git commit d52ae17 — feat: v3.0.18 (Documents/EDB-AI-Circular-System)
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS (both repos)
   - dashboard JS syntax → PASS (6 version locations confirmed)
   - 4/4 logic unit tests → PASS (from prior session)
   - calendar dlLabel grep verified in both workspace + git repo
   - apply-ext CSS + JS grepped confirmed
9. Pending:
   - 用戶須在 Mac 執行 `git pull --rebase && git push`（Documents/EDB-AI-Circular-System）
   - 然後在 GitHub Actions 手動觸發 school-year workflow 以 backfill 所有 117 records
   - 驗證 live circulars.json 有非空 k1_topics / k1_facts / k1_guidelines
   - 修正 topic-aware review cross-topic 污染（supplier/finance links 跑入 curriculum/student）
10. Risks / blockers:
    - git push 前需 pull --rebase（GitHub Actions 可能已更新 circulars.json）
    - school-year workflow 需手動觸發；不會自動 backfill
    - 跨 repo 同步：Documents repo (v3.0.18 committed) vs EDB-Circular-AI-analysis-system (old, unrelated branch)
11. Git commits: d52ae17 (Documents/EDB-AI-Circular-System)

### Test Scenarios

| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Calendar dlLabel | April entries exist | Render calendar | Shows `⏰ EDBC042 申請` | grep confirms dlLabel code present | PASS |
| apply-ext form | Resource with 已申請 | Set status | Date-picker + notes appear | CSS + JS code confirmed | PASS |
| K1 carry-forward | Existing record has k1_topics | Incremental skip | k1_* preserved | Code path confirmed | PASS |
| K1 Phase 4.5 backfill | 117 records, all k1_topics=[] | Run script | All get k1_topics populated | Logic verified via unit test | PASS |
| Post-LLM re-detect | circ["topics"] from LLM | After LLM returns | k1_topics from LLM topics | Code path confirmed | PASS |

Overall: PASS

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: v3.0.18 has been committed to Documents/EDB-AI-Circular-System (commit d52ae17). User needs to push and trigger school-year workflow to backfill k1_* fields across all 117 records. After verification, next task is fixing topic-aware review cross-topic contamination.

Pending tasks (priority order):
1. [USER ACTION REQUIRED] git pull --rebase && git push in Documents/EDB-AI-Circular-System, then manually trigger school-year workflow on GitHub Actions.
2. Verify live circulars.json: sample 3-5 records for non-empty k1_topics / k1_facts / k1_guidelines.
3. Fix topic-aware review cross-topic contamination: supplier/finance links leaking into curriculum/student circulars (see Open Priorities in SESSION_HANDOFF.md).
4. Await and integrate new role_facts.json from K1 project — validate against K1_KNOWLEDGE_INTERFACE_SPEC.md v2.0.0 before use.

Key files changed in this session:
- edb_scraper.py (Documents/EDB-AI-Circular-System + Claude-edb-Project-V3 workspace)
- edb-dashboard.html (Documents/EDB-AI-Circular-System + Claude-edb-Project-V3 workspace)

Known risks / blockers / cautions:
- git push must be preceded by git pull --rebase (GitHub Actions commits circulars.json regularly)
- If rebase conflict on circulars.json: keep remote version, then push
- EDB-Circular-AI-analysis-system folder is a stale clone at v3.0.3 — do NOT use for backend work; always use Documents/EDB-AI-Circular-System
- K1 public API drift: knowledge.json live schema uses topic→role-arrays form; dual-schema compat parser in place

Validation status: py_compile PASS; dashboard JS syntax PASS; 4/4 logic tests PASS; git commit d52ae17 confirmed; version v3.0.18 in all 6 dashboard locations + scraper print.

Post-startup first action: ask user whether the workflow has been triggered and circulars.json has been updated; if yes, fetch live JSON and sample records for k1_topics. If not, provide the git push + workflow trigger instructions again.
```
