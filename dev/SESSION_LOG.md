# Session Log
<!-- Archives: dev/archive/ — entries moved when >800 lines or oldest entry >30 days -->

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

## 2026-04-09 Sparse summary follow-up fallback (workspace v3.0.27)

1. Agent & Session ID: Codex_20260409_0009
2. Task summary: 針對 sparse circular 摘要過度保守的問題，加入精簡 follow-up 第二段。當摘要只剩框架句，但 `roles/actions` 已有明確工作點時，補回最多 1-2 個最高訊號的校內跟進重點。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output quality issue。`v3.0.26` 已成功壓掉空話，但像 `EDBCM053/2026` 這種 sparse 通告會被收得過空；問題不在 K1 或 workflow，而在 summary 對 sparse cases 太保守。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `edb_scraper.py`, live `circulars.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ prompt 補充 sparse case guidance：若官方內容少但已有明確工作點，可在第 2 段簡述 1-2 個最重要的校內跟進點
   - ✅ 新增 `_build_sparse_summary_followup()`，只從最高訊號 roles 中抽最多 2 個 follow-up
   - ✅ 封掉 `第二段內容摘要需以官方全文公布為準...` 這類 prompt leakage
   - ✅ 版本升至 `v3.0.27`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - sparse helper regression → PASS
9. Pending:
   - 發布 `v3.0.27`
   - 重跑 school-year workflow
   - 驗證 live `EDBCM053/2026` 等 sparse 通告摘要已補回精簡而實用的第二段
10. Next priorities:
   - 發布 `v3.0.27`
   - 重跑 workflow 並驗 live sparse summaries
   - 視結果再決定是否需要 topic-specific sparse summary rules
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - sparse fallback 若過度放寬，可能再次滑向角色百科；目前已限制最多 2 個 follow-up points
   - `v3.0.27` 尚未發布，live 仍是 `v3.0.26`
12. Notes:
   - 這輪不是讓 summary 重新展開所有角色，而是只在必要時補一段短短的工作重點。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - `EDBCM053/2026` 這類 sparse circular 在 live `v3.0.26` 中摘要過度保守，只剩框架句，沒有已存在於 roles/actions 的實用工作點。
2. Root Cause:
   - circular-first summary rule 成功消除了空話，但對資訊較少的通告沒有保留一個合理的 follow-up 第二段出口。
3. Fix:
   - 新增 sparse-summary fallback：當 summary 僅剩單段而 roles/actions 已有明確內容時，自動補一段精簡 follow-up，最多摘 2 個最高訊號的校內跟進點。
4. Verification:
   - local helper 顯示 `EDBCM053/2026` 類摘要可補成兩段，第二段為「校內跟進重點包括…」
   - 句尾標點已收斂，不再出現 `。；` 之類重疊
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #29 added: sparse summaries may append one concise follow-up paragraph from role/action signals.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | sparse circular with meaningful role/action signals | apply sparse fallback | add one concise second paragraph with at most 2 follow-up points | `053` helper now adds concise follow-up paragraph | PASS |
| Boundary | sparse circular with repeated role action text | apply sparse fallback | dedupe repeated follow-up text and avoid role encyclopedia | helper kept max 2 concise points | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local helper/syntax checks only | local QC valid; cloud regression explicitly skipped | local QC passed; cloud run skipped | PASS with notes |
| Regression | rich circulars already have detailed summary | sparse fallback should not trigger | existing 2-3 paragraph summaries remain primary | logic only triggers when summary has <=1 paragraph | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |

## 2026-04-09 Circular-first summary rewrite (workspace v3.0.26)

1. Agent & Session ID: Codex_20260409_0008
2. Task summary: 將摘要生成策略從「再補丁式清模板句」提升為整體重整：summary 只寫通告已知內容，不再敘述缺失資訊或把 K1/角色常識寫成主體。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output quality issue。live `v3.0.25` 已證明模板句清理仍不足，根因是摘要生成方式本身過於依賴補位和概括式空話，因此需要重寫 summary 規則，而不是再逐條 regex 補洞。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `edb_scraper.py`, `README.md`, live `edb-dashboard.html`, live `circulars.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 將 summary 規則改為 `120-260` 字，優先兩段、只有資訊明確且較多時才三段
   - ✅ prompt 明確要求：只寫已知內容；資訊不足時直接略去，不要描述「未提供什麼」
   - ✅ prompt 明確限制：除非通告本身逐一分派角色，否則不要在 summary 展開角色百科
   - ✅ 後處理只保留 very light cleanup，並將 `本公告` 正規化為 `本通告`
   - ✅ 版本升至 `v3.0.26`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - summary helper regression → PASS
9. Pending:
   - 發布 `v3.0.26`
   - 重跑 school-year workflow
   - 驗證 live `049/050/053` 及其他抽樣通告摘要已改為通告本位風格
10. Next priorities:
   - 發布 `v3.0.26`
   - 重跑 workflow 並驗 live summary
   - 視結果再決定是否需要更細的 topic-specific summary guidance
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - 真正的摘要品質仍主要取決於 prompt 對模型的約束，後處理只作輕量保護
   - `v3.0.26` 尚未發布，live 仍是 `v3.0.25`
12. Notes:
   - 這輪的重點是把 summary 從「不知道也要寫一段」改成「不知道就不寫」。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者反映不只單一通告，整體 AI 摘要都不理想，常流於空話、模板句、或知識庫延伸式說明。
2. Root Cause:
   - 先前版本仍允許模型把資訊不足寫成一段話，並在摘要內補一般管理背景；summary 任務定義沒有真正回到「通告本身講什麼」。
3. Fix:
   - 把 summary 改成 circular-first 規則：只寫明示/可直接讀出的內容，缺資料直接略去；限制角色百科化敘述；保留 very light cleanup。
4. Verification:
   - `049` / `050` helper 輸出仍保持差異
   - `053` helper 輸出只保留明確已知句子
   - 泛用樣本 `本通告旨在向學校說明有關安排...` 不再自動補「後續通知」模板句
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #28 added: summary must be circular-first and omit missing areas instead of narrating them.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | course circular with explicit requirements | run `_normalize_summary_text()` | retain circular-specific 2-paragraph summary | `049` keeps distinct course content | PASS |
| Boundary | survey circular with long second paragraph | run `_normalize_summary_text()` | keep specific details without dangling filler ending | `050` keeps distinct details and no filler clause | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local syntax/helper checks only | local QC valid; cloud regression explicitly skipped | local QC passed; cloud run skipped | PASS with notes |
| Regression | sparse circular with previously filler-heavy summary | run `_normalize_summary_text()` | output should omit absent-info narration and keep only explicit known sentence(s) | `053` reduced to one explicit sentence | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |

## 2026-04-09 Summary paragraph flexibility + filler cleanup (workspace v3.0.25)

1. Agent & Session ID: Codex_20260409_0007
2. Task summary: 進一步修正 A 風格摘要，從固定兩段改為「優先兩段、必要時三段」，並清除 `若有…將另行通知`、`目前尚未披露`、`等待後續公告` 這類低信息模板句，避免 live 摘要雖已分段但仍顯得空泛。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output quality issue。`v3.0.24` 已解決「049=050」與重複 supplier 術語，但 live 摘要仍常以後續通知式模板句收尾；這屬 prompt / summary post-process 邊界問題，不是 K1 integration bug。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `edb_scraper.py`, `README.md`, live `edb-dashboard.html`, live `circulars.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 將 summary 規則改為 `160-320` 字，優先兩段、必要時三段
   - ✅ 在 prompt 中加入禁止低信息模板句的要求
   - ✅ 新增 sentence-level filler cleanup，移除 `若有…將另行通知`、`目前尚未披露`、`等待後續公告` 等句子
   - ✅ 保留 `049/050` 差異，並讓 `053` 不再以「後續通知」式空話主導摘要
   - ✅ 版本升至 `v3.0.25`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile (`node` + `new Function`) → PASS
   - summary helper regression → PASS
9. Pending:
   - 發布 `v3.0.25`
   - 重跑 school-year workflow
   - 驗證 live `049/050/053` 等摘要已去掉低信息模板句，且沒有新殘句
10. Next priorities:
   - 發布 `v3.0.25`
   - 重跑 workflow 並驗 live summary
   - 視結果再決定是否還要微調 prompt
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - 摘要品質仍主要受 LLM 原始輸出影響，後處理只應做輕量收口
   - `v3.0.25` 尚未發布，live 仍是 `v3.0.24`
12. Notes:
   - 這輪不再嘗試句內大幅刪字，而是改成整句過濾，避免把有效內容切成殘句。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - `v3.0.24` live 摘要雖已兩段，但仍常帶有 `若有…將另行通知`、`目前尚未披露` 等低信息模板句，令內容顯得空泛。
2. Root Cause:
   - prompt 仍過度鼓勵固定兩段式收尾，而 summary 後處理沒有清理這些佔位句；部分句內刪字還會留下殘句。
3. Fix:
   - 改成優先兩段、必要時三段；在 prompt 明確禁止低信息模板句；在 summary post-process 改為整句級過濾這些 filler。
4. Verification:
   - `049` 與 `050` helper 輸出仍保持差異
   - `050` 不再留下句尾分號
   - `053` helper 輸出不再帶「後續通知」模板句
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #27 added: summary 可兩段或三段，但必須避免低信息 filler prose。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | curriculum circular with concrete requirements | run `_normalize_summary_text()` | retain meaningful 2-paragraph summary without filler | `049` keeps distinct content and no placeholder ending | PASS |
| Boundary | survey circular with long second paragraph | run `_normalize_summary_text()` | keep distinct details, remove trailing filler, no broken punctuation | `050` keeps distinct details and no dangling `；` | PASS |
| Error / failure path | no `OPENAI_API_KEY` in env | local helper/syntax checks only | local QC still valid; cloud regression explicitly skipped | local QC passed, cloud run skipped | PASS with notes |
| Regression | sparse circular previously ending in “後續通知” boilerplate | run `_normalize_summary_text()` | summary should stay concise without placeholder prose | `053` now reduces to the explicit known sentence only | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |

## 2026-04-09 Tighten deterministic review raw-signal gating (workspace v3.0.21)

1. Agent & Session ID: Codex_20260409_0002
2. Task summary: 針對 live `v3.0.20` 抽樣後仍可見的 deterministic `knowledge_review.recommended_links` cross-topic contamination，收緊 procurement / finance gating，避免 AI summary 或 supplier role 自我放大後把 supplier / finance links 漏進 curriculum / student 通告。
3. Layer classification: Product / System Layer（deterministic review behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 問題不在 K1 public fetch，而在 second-pass deterministic review。live `k1_*` fields 已正常，但 `knowledge_review.recommended_links` 仍可能過寬。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 確認 live `v3.0.20` + school-year workflow 已完成
   - ✅ 將 procurement / finance gating 改為依 `title + official + pdf_text` 的 raw signals 判斷
   - ✅ 阻止僅因 AI summary 或 supplier role 文字而追加 supplier links
   - ✅ 保留真正有 finance / procurement raw signals 的通告之相關 links
   - ✅ 版本升至 `v3.0.21`
8. Validation / QC:
   - `python3 -c "ast.parse(...)"` → PASS (`PY_AST_OK`)
   - dashboard JS compile (`new Function(script)`) → PASS (`JS_COMPILE_OK`)
   - curriculum/student contamination guard sample → PASS (`has_supplier_links=False`)
   - procurement/finance positive sample → PASS (`has_supplier_links=True`, `has_finance_links=True`)
   - full OpenAI LLM regression → BLOCKED (`OPENAI_API_KEY` absent)
9. Pending:
   - 發布 `v3.0.21`
   - 重跑 school-year workflow，驗證 raw-signal gating 已反映到 live records
   - 如仍有 supplier / finance links 漏入 curriculum / student，繼續微調 deterministic review gating
   - 等待新版 `role_facts.json`
10. Next priorities:
   - 發布 `v3.0.21`
   - 重跑 workflow 並驗證 raw-signal gating
   - 視結果再微調 deterministic review gating
11. Risks / blockers:
   - 本輪 gating 驗證仍以 local deterministic samples 為主，尚未做 live workflow 後對照
   - `OPENAI_API_KEY` 不在此環境，無法真跑完整雲端 LLM regression
   - `role_facts.json` 仍未到位
12. Notes:
   - 這輪修正不改 K1 fetch 路徑；只修 second-pass enrichment 的 self-amplification 問題。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - live `k1_*` fields 已正常，但 curriculum / student 通告的 `knowledge_review.recommended_links` 仍可能帶入 supplier / finance links。
2. Root Cause:
   - deterministic review 之前用 `summary` 及 supplier role 文字判斷 procurement / finance，會被 AI 生成內容自我放大。
3. Fix:
   - 改用 raw circular text (`title` + `official` + `pdf_text`) 判斷 procurement / finance；supplier enrichment 只在真有 procurement raw signal 時觸發。
4. Verification:
   - curriculum/student sample 雖然 summary 故意放入「供應商採購安排」，仍不再拿到 supplier links
   - finance/procurement positive sample 仍保留 supplier / finance links
5. Regression / rule update:
   - 更新 `CODEBASE_CONTEXT.md` Key Decision #23；無新增治理規則。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | curriculum/student sample with no raw procurement cues | run `_apply_post_analysis_review()` | should keep curriculum/student links only | no supplier links added | PASS |
| Boundary | AI summary intentionally mentions supplier/procurement | run `_apply_post_analysis_review()` | summary wording alone must not trigger procurement enrichment | `has_supplier_links=False` | PASS |
| Error / failure path | env lacks OpenAI key | scope QC | record block clearly without faking full LLM run | `OPENAI_API_KEY` absent; full LLM regression skipped | PASS with notes |
| Regression | sample with real finance/procurement raw cues | run `_apply_post_analysis_review()` | supplier and finance links remain present | `has_supplier_links=True`, `has_finance_links=True` | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |

## 2026-04-09 Summary bugfix: preserve differences + dedupe repeated supplier term

1. Agent & Session ID: Codex_20260409_0006
2. Task summary: 修正 `v3.0.23` 摘要後處理副作用，避免不同通告被壓成過於相似的模板，同時清除 `供應商／供應商／供應商／承辦商` 這類重複術語。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: user-visible output regression。根因不是模型本身，而是 summary normalizer 過度刪句與改寫，令 049 / 050 這類課程通告被收斂得過於相似；另外 terminology 替換在 summary 內未完全收斂重複 supplier 字樣。
5. Files read: `edb_scraper.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ summary 字數要求放寬到 `150-280`
   - ✅ `_normalize_summary_text()` 降級為 light-touch，保留原句差異，只做分段與輕量裁切
   - ✅ 新增 `_dedupe_summary_phrases()`，收斂重複 `供應商／承辦商`
   - ✅ 版本升至 `v3.0.24`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile → PASS
   - helper regression checks → PASS
9. Pending:
   - 發布 `v3.0.24`
   - 重跑 school-year workflow
   - 驗證 live `049/050/053` 摘要已保留差異且不再重複 supplier 術語
10. Next priorities:
   - 發布 `v3.0.24`
   - 重跑 workflow 並驗 live summary
   - 視結果再決定是否只靠 prompt、進一步弱化後處理
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端端到端回歸
   - 摘要最終品質仍以 LLM 原始輸出為主，後處理只應做輕量整理
12. Notes:
   - 這輪不再嘗試刪除太多 meta 片語，因為那會傷到通告本身差異性。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - `049` 和 `050` 類摘要被壓成過於相似，且 `053` 出現重複 `供應商` 字樣。
2. Root Cause:
   - `v3.0.23` 的 summary normalizer 過度刪句與重寫，破壞原有差異；supplier terminology 在 summary 中未完全去重。
3. Fix:
   - 把 summary normalizer 改為 light-touch，只做分段與輕量裁切；新增 summary 專用術語去重 helper。
4. Verification:
   - `053` 樣本輸出已恢復為 `供應商／承辦商`
   - `049` 與 `050` 樣本輸出不再被壓成同一句型
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #26 added: summary post-processing must preserve circular-specific differences and stay light-touch.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | 兩段式摘要已由 LLM 產出 | 套用新的 `_normalize_summary_text()` | 保留原句差異，只整理分段與長度 | 049/050 helper 輸出保留不同內容 | PASS |
| Boundary | summary 含重複 `供應商／...` | 套用 `_dedupe_summary_phrases()` | 收斂為單一 `供應商／承辦商` | 053 helper 輸出正常 | PASS |
| Error / failure path | 無 `OPENAI_API_KEY` | 做本地 helper / syntax 檢查 | 可完成本地回歸，雲端回歸留待 workflow | local checks passed | PASS with notes |
| Regression | dashboard 前端未改 summary rendering 邏輯 | JS compile | 前端仍可正常顯示兩段式 summary | dashboard JS compile PASS | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |

## 2026-04-09 Summary A-style refinement for circular-first summaries

1. Agent & Session ID: Codex_20260409_0005
2. Task summary: 收斂 AI `summary` 風格，採用較短、兩段式、以通告本身為主的 A 版本，減少 K1 / role-facts 常識侵入摘要主體。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 非 bug fix；屬 prompt / output-quality refinement。根因是既有 summary 規則要求 300-600 字，且 prompt 注入 K1 / role-facts 後，模型容易把知識庫一般規則寫成通告摘要。
5. Files read: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ `SYSTEM_PROMPT` 的 summary 規則改為 120-220 字、兩段式
   - ✅ `_build_prompt()` 新增 `【摘要寫作要求】` 區塊，明確禁止把知識庫一般規則與角色百科寫進 summary
   - ✅ `_normalize_summary_text()` 新增後處理，清理「可推斷 / 初步判讀 / 根據標題可判斷」等 meta 語氣並嘗試收斂成兩段
   - ✅ 版本升至 `v3.0.23`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile → PASS
   - summary helper sample check → PASS（`EDBCM053/2026` 長摘要樣本已收斂為兩段，總長約 128 字）
9. Pending:
   - 發布 `v3.0.23`
   - 重跑 school-year workflow，驗證 live 摘要已轉成 A 風格
   - 抽樣檢查 K1 / role-facts 仍然幫助 roles / actions，但不再主導 summary
10. Next priorities:
   - 發布 `v3.0.23`
   - 重跑 workflow 並驗證 live summary 風格
   - 視結果再決定是否微調 summary normalizer
11. Risks / blockers:
   - 本機仍缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - summary normalizer 目前是保守的字句清理與分段，不應替代 prompt 本身的主約束
   - 真正效果仍需看 live 重生後的通告樣本
12. Notes:
   - 前端本身已支援 `\n\n` 分段顯示，這輪重點是把後端輸出改得更像正式摘要，而不是改 UI。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - live 摘要過長，且混入 K1 / role-facts 一般知識，像管理百科而不是通告簡介。
2. Root Cause:
   - summary 被要求寫成 300-600 字，且 prompt 允許知識增強材料與「合理推斷」影響摘要主體。
3. Fix:
   - 把 summary 收斂成兩段式 A 風格，縮短字數，新增摘要寫作約束，並在後處理清理 meta / disclaimer 語氣。
4. Verification:
   - py_compile PASS
   - dashboard JS compile PASS
   - `EDBCM053/2026` 長摘要樣本經 helper 收斂為兩段、128 字
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #25 added: summary must stay circular-first and shorter, with K1/role knowledge kept out of the main summary body.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | summary 由 LLM 生成 | 套用新 prompt 規則 | 摘要應為兩段、較短、以通告本身為主 | prompt 明確要求兩段式、120-220 字 | PASS |
| Boundary | 現有 summary 為單大段且過長 | 執行 `_normalize_summary_text()` | 收斂為較短的 1-2 段，不保留 meta/disclaimer 語氣 | `EDBCM053/2026` 樣本收斂為兩段、128 字 | PASS |
| Error / failure path | 無 `OPENAI_API_KEY` | 做本地語法與 helper 檢查 | 不阻塞本地 QC；雲端回歸標記未做 | local QC passed; end-to-end cloud call skipped | PASS with notes |
| Regression | 前端已支援摘要分段 | 保留 dashboard summary rendering | UI 無需改邏輯，只需版本同步 | dashboard JS compile PASS | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |

## 2026-04-09 Workflow fix for circulars.json commit conflict

1. Agent & Session ID: Codex_20260409_0004
2. Task summary: 針對 school-year workflow error 做根因調查與修正。確認失敗發生在 GitHub Actions 的 `Commit updated circulars.json` step，然後把 workflow 從 `git pull --rebase` 策略改成保存新 JSON → 同步最新遠端 → 還原 JSON → commit/push。
3. Layer classification: Product / System Layer（CI / deployment workflow behavior）+ Development Governance Layer（session persistence）
4. Source triage: 屬 CI / external platform behavior issue，不是 scraper / OpenAI / K1 邏輯錯誤。失敗根因在 workflow 的 git conflict handling，而不是分析程式本身。
5. Files read: `.github/workflows/update-circulars.yml`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`
6. Files changed: `.github/workflows/update-circulars.yml`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 查明失敗 run `#134` 的 error 發生在 `Commit updated circulars.json`
   - ✅ 對回 workflow，失敗點是 `git pull --rebase origin main`
   - ✅ 將 workflow 改成：保存新 `circulars.json` → `git fetch origin main` → `git reset --hard origin/main` → 還原 JSON → `git add/commit/push`
   - ✅ 確認較新的 run `#135` 已成功；Node.js 20 warning 為次要警告，非主因
8. Validation / QC:
   - GitHub Actions public run-page inspection → PASS
   - failed run root-cause identification → PASS
   - workflow step mapping to `.github/workflows/update-circulars.yml` → PASS
9. Pending:
   - 發布 workflow conflict fix
   - 重跑 school-year workflow，驗證 `role_fact_topics` / `role_facts` 已回填 live
   - 其後再開始摘要風格收斂（A 風格、兩段式）
10. Next priorities:
   - 發布 workflow fix
   - 重跑 workflow 並驗證 live role-facts 回填
   - 之後調整 summary prompt 為兩段式 A 版本
11. Risks / blockers:
   - 修正尚未發布；在此之前手動跑 school-year 仍可能再撞同類 CI conflict
   - public log inspection 可定位 step 與 annotation，但未直接取得完整 private step log
   - Node.js 20 deprecation warning 仍存在，但不是本次失敗主因
12. Notes:
   - 這次 workflow 修正其實讓 CI 策略重新對齊 `CODEBASE_CONTEXT.md` 已記錄的 Key Decision #7（fetch+reset conflict strategy）。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - school-year workflow 出現 error，無法穩定提交新生成的 `circulars.json`。
2. Root Cause:
   - workflow 在 commit `circulars.json` 後直接執行 `git pull --rebase origin main`，若執行期間遠端同時出現新 commit，便可能在 `circulars.json` 衝突並失敗。
3. Fix:
   - 將 workflow 改為先保存新 JSON，再同步到最新 `origin/main`，然後把 JSON 複回來後才 commit / push，避免直接 rebase 衝突。
4. Verification:
   - public failed run `#134` annotation 顯示失敗在 `Commit updated circulars.json`
   - workflow file line mapping confirmed the risky command
   - newer run `#135` 已成功，說明不是整條 workflow 或外部服務全面故障
5. Regression / rule update:
   - 無新增長期治理規則；是把現有 CI conflict strategy 正式落實到 workflow。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | workflow 生成新的 `circulars.json` | Commit step syncs latest origin before commit | 不因 rebase 衝突而失敗 | new strategy saved in workflow file | PASS |
| Boundary | 遠端在 workflow 執行期間新增 commit | Commit step handles latest origin state | 保留新生成 JSON，避免 `git pull --rebase` 衝突 | strategy now uses save + fetch/reset + restore | PASS |
| Error / failure path | public logs only, no `gh` CLI available | inspect public GitHub Actions HTML | 仍可定位 failing run / step / annotation | failed run `#134`, step `Commit updated circulars.json` identified | PASS |
| Regression | Scraper / deploy steps unchanged | only replace commit conflict handling | 其他 workflow step names and ordering stay intact | only commit strategy block changed | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-09 Adopt K1 public schema v1.3.1 in Circular System (workspace v3.0.20)

1. Agent & Session ID: Codex_20260409_0001
2. Task summary: 依 K1 平台最新 handoff，將 Circular System 重新對齊到 K1 public `v1.3.1` schema，改用 `subject_head + panel_chair + all_roles` 組裝主任層 facts，並檢查是否仍殘留 public-schema `department_head` 假設。
3. Layer classification: Product / System Layer（external API integration alignment + K1 prompt assembly change）+ Development Governance Layer（session persistence / doc sync）
4. Source triage: 屬外部平台整合更新；不是 K1 repo 內部邏輯問題。先以 public `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md` 為 SSOT 核對，再做本地 fetch 邏輯最小修正。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`, `dev/DOC_SYNC_CHECKLIST.md`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 直接抓取 K1 public `knowledge.json`, `guidelines.json`, `K1_API_SPEC.md`
   - ✅ 核實 live version = `1.3.1`
   - ✅ 核實 public `department_head` bucket 已移除，主任層 bucket 為 `subject_head` + `panel_chair` + `all_roles`
   - ✅ 更新 Circular System K1 fetch logic 至新 public schema
   - ✅ 清理前端 mock data 裡殘留的 `department_head`
   - ✅ 版本升至 `v3.0.20`
8. Validation / QC:
   - `python3 -c "ast.parse(...)"` → PASS (`PY_AST_OK`)
   - dashboard JS compile (`new Function(script)`) → PASS (`JS_COMPILE_OK`)
   - K1 extract block check → PASS (`department_head_in_k1_extract_block=False`)
   - live K1 public SSOT fetch → PASS (`knowledge.json`, `guidelines.json`, `K1_API_SPEC.md`, all `v1.3.1`)
   - live K1 assembly regression via public endpoints → PASS (`facts_count=25`, `docs_count=8`, subject/panel facts present)
   - full OpenAI `LLMAnalyzer.analyze()` regression → BLOCKED (`OPENAI_API_KEY_PRESENT=False`)
9. Pending:
   - 發布 `v3.0.20`
   - 重跑 school-year workflow，驗證 live records 已按 K1 `v1.3.1` schema consume
   - 視結果再修 deterministic review cross-topic contamination
   - 等待新版 `role_facts.json`
10. Next priorities:
   - 發布 `v3.0.20`
   - 重跑 workflow 並驗證 K1 `v1.3.1` consume + slimmed payload
   - 視結果再修 deterministic review gating
11. Risks / blockers:
   - 本輪若未發布，live site 仍不會反映 `v3.0.20`
   - K1 public schema現已穩定，但 Circular System 仍需 live workflow 後回歸驗證
   - `role_facts.json` 仍未到位
12. Notes:
   - K1 public `K1_API_SPEC.md` 已恢復可用，不再是 404；本輪以公開端點而非 repo artifact 作為唯一 API truth

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - Circular System 仍以舊的 public-schema 假設處理 K1 主任層 facts，包含 `department_head`。
2. Root Cause:
   - K1 public schema 已在 `v1.3.1` 拆分為 `subject_head` / `panel_chair`，但 Circular System 尚未完全改用公開 SSOT。
3. Fix:
   - 重新核對 public `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md`，再把 K1 facts assembly 改為 `all_roles` + `subject_head` + `panel_chair`，並清理前端 mock data 裡殘留的 `department_head`。
4. Verification:
   - K1 public SSOT fetched successfully and matched `v1.3.1`
   - K1 extract block no longer contains `department_head`
   - public-endpoint regression over `finance + activity + student` topics produced `25` facts and `8` docs, including `subject_head` / `panel_chair` content
5. Regression / rule update:
   - 更新 `CODEBASE_CONTEXT.md` External Services block 與 Key Decision #22；無新增治理規則。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | live K1 public endpoints reachable | fetch public `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md` | all public SSOT artifacts available and aligned | all 3 fetched, all report `v1.3.1` | PASS |
| Boundary | Circular System must consume new主任層 schema | inspect K1 extract block in `edb_scraper.py` | no public-schema `department_head` assumption remains in K1 fetch logic | `department_head_in_k1_extract_block=False` | PASS |
| Error / failure path | current env lacks OpenAI key | check env and attempt to scope regression | report blocking condition clearly without faking full LLM run | `OPENAI_API_KEY_PRESENT=False`; full LLM regression skipped | PASS with notes |
| Regression | sample finance/activity/student circular against live K1 endpoints | assemble facts/docs from public endpoints using `subject_head + panel_chair + all_roles` | non-empty facts/docs and subject/panel facts present | `facts_count=25`, `docs_count=8`, `has_subject_or_panel_fact=True` | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| External API / service change | CODEBASE_CONTEXT.md External Services block | ✓ Done |
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-08 Tighten K1 topic slimming + payload caps (workspace v3.0.19)

1. Agent & Session ID: Codex_20260408_0004
2. Task summary: 續做 K1 integration 後的下一步，先在 workspace 收緊 K1 topic detection 與 prompt payload，減少 cross-topic contamination，並把 stale handoff/state files 對齊到目前真實進度。
3. Layer classification: Product / System Layer（K1 topic detection / prompt payload behavior change）+ Development Governance Layer（session persistence / stale state remediation）
4. Source triage: 屬現有行為調整，不是新外部 API 整合。問題核心是 topic 補充過寬、guideline/facts payload 過大，導致 curriculum / student 通告容易混入不必要 topic。
5. Files read: `AGENTS.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`, `dev/DOC_SYNC_CHECKLIST.md`, `README.md`, `edb_scraper.py`, `edb-dashboard.html`
6. Files changed: `edb_scraper.py`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 確認 workspace 已有 `v3.0.19` 版本標記與 K1 slimming constants
   - ✅ 驗證並修正 `general` fallback 漂移：現在只有在完全沒有其他 topic 時才回退到 `general`
   - ✅ 保留 payload caps：最多 3 個 K1 topics、4 facts/topic（12 total）、2 guidelines/topic（6 total）
   - ✅ 將 handoff / log / context / README 對齊到「live K1 backfill 已完成、下一步是發布 `v3.0.19`」
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS syntax check (`node --check` extracted script) → PASS
   - sample topic detect → PASS
   - payload cap test → PASS
9. Pending:
   - 發布 `v3.0.19`
   - 重跑 school-year workflow，驗證 slimmed K1 payload 已反映到 live records
   - 視結果再修 deterministic review cross-topic contamination
   - 等待新版 `role_facts.json`
10. Next priorities:
   - 發布 `v3.0.19`
   - 重跑 workflow 並驗證 slimmed K1 payload
   - 視結果再修 deterministic review gating
11. Risks / blockers:
   - 這輪對 contamination 的驗證仍以 local sample 為主，尚未做 live record 對照
   - public K1 facts schema 與舊 brief 不完全一致；目前依兼容 parser 處理
   - `role_facts.json` 仍未到位
12. Notes:
   - workspace 不是 git repo，`git status` 在此目錄失敗是預期現象；真正 deploy/push 仍需走外部 repo / `deploy.sh`

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - K1 integration 雖已 live，但 sample 結果顯示 topics / facts / guidelines 容易過寬，並出現 `student + general` 之類不夠乾淨的補充。
2. Root Cause:
   - K1 topic supplementation 邏輯太寬，而且 `general` 會與已選 topic 疊加；同時 facts / guidelines 缺少較嚴格上限。
3. Fix:
   - 將 K1 topic 補充限制在最多 3 個 topic，保留 payload caps，並把 `general` 改成只在完全沒有其他 topic 時 fallback。
4. Verification:
   - `student_case` 由 `['student', 'general']` 收斂為 `['student']`
   - `hr_false_positive_guard` 仍維持 `['curriculum', 'activity']`
   - payload cap test 通過：`facts_count=12`、`docs_count=6`
5. Regression / rule update:
   - 已更新 `CODEBASE_CONTEXT.md` Key Decision #21 與 maintenance log；無新增治理規則。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | finance/activity/student sample with existing analysis topics | run `K1KnowledgeClient.detect_topics()` | keep clear mapped topics, no overflow beyond cap | `['finance', 'activity', 'student']` | PASS |
| Boundary | student-only sample with generic admin words present | run `detect_topics()` | keep `student` only; do not append `general` when a clearer topic already exists | `['student']` | PASS |
| Error / failure path | workspace lacks PyMuPDF | run logic-only topic/payload tests | tests still run because K1 logic is independent of PDF parsing | test scripts completed with warning only | PASS with notes |
| Regression | teacher/curriculum activity sample | run `detect_topics()` | should not reintroduce `hr` from loose teacher wording | `['curriculum', 'activity']` | PASS |
| Regression | oversized facts/guidelines source lists | run capped fetch tests | respect topic/per-topic/total caps | `facts_count=12`, `docs_count=6` | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

## 2026-04-08 Verify live v3.0.17 + closeout

1. Agent & Session ID: Codex_20260408_0003
2. Task summary: 依使用者要求做 session closeout，核實 `v3.0.17` 是否已 live，並判斷下一步工作重點。
3. Layer classification: Product / System Layer（release/live verification）+ Development Governance Layer（session closeout / persistence）
4. Source triage: 非新功能開發；屬已發布版本的 live state verification 與 closeout。重點是分辨前端版本是否已 live，以及資料是否已反映 K1 integration。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ cache-busted 驗證 public GitHub Pages HTML 已是 `v3.0.17`
   - ✅ cache-busted 驗證 public `circulars.json`：`generated_at=2026-04-08T08:45:24Z`, `count=117`
   - ✅ 抽樣檢查 `EDBCM048/2026`、`EDBCM043/2026`
   - ✅ 確認 sampled live records 仍未帶出 `k1_topics` / `k1_facts` / `k1_guidelines`
   - ✅ 更新 handoff / log，將下一步工作聚焦到重跑 workflow 而不是再次 push
8. Validation / QC:
   - `curl -L 'https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html?...' | rg ...` → PASS (`v3.0.17` visible markers all present)
   - `curl -L 'https://leonard-wong-git.github.io/EDB-AI-Circular-System/circulars.json?...'` → PASS (`generated_at=2026-04-08T08:45:24Z`, `count=117`)
   - sample live records → PASS with notes (`k1_topics=[]`, `k1_facts_count=0`, `k1_guidelines_count=0`)
9. Pending:
   - 重跑 workflow / 重新生成 `circulars.json`
   - 驗證 live K1 facts / guidelines prompt integration
   - 修正 topic-aware review 疊加污染
   - 等待新版 `role_facts.json`
10. Next priorities:
   - 重跑 workflow / 更新 live `circulars.json`
   - 驗證 live K1 integration
   - 修正 topic-aware review 疊加污染
11. Risks / blockers:
   - 前端 `v3.0.17` 已 live，但 live data 抽樣仍未帶出 `k1_*` fields
   - public K1 facts schema 與舊 brief 不完全一致；目前依兼容 parser 處理
   - public `K1_API_SPEC.md` URL 於 2026-04-08 返回 404
12. Notes:
   - 這輪最重要的結論是：下一步不是再 push，而是重跑資料生成流程。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者確認 `v3.0.17` 已 live，並希望 closeout 時知道下一步工作。
2. Root Cause:
   - 需要區分「前端版本已 live」和「資料內容已反映 K1 integration」這兩件事。
3. Fix:
   - 重新抓取 live HTML 和 live `circulars.json`，並抽樣檢查實際 records 的 `k1_*` 欄位。
4. Verification:
   - HTML 已是 `v3.0.17`
   - `circulars.json` 已更新到 `2026-04-08T08:45:24Z`
   - sampled records 的 `k1_topics` / `k1_facts` / `k1_guidelines` 仍為空
5. Regression / rule update:
   - 無新增治理規則；屬當前狀態對帳。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | repo 已發佈 `v3.0.17` | fetch public HTML | visible version markers show `v3.0.17` | all checked markers show `v3.0.17` | PASS |
| Boundary | live data 可能已更新但未必含 K1 fields | fetch public `circulars.json` and inspect sample records | determine whether K1 fields are present | sampled records had empty `k1_*` fields | PASS with notes |
| Regression | closeout should not assume data integration from front-end version alone | compare HTML vs JSON state | next priority should be workflow rerun, not another push | handoff priorities updated accordingly | PASS |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from verified live `v3.0.17` as of 2026-04-08. Public GitHub Pages HTML is now on `v3.0.17`, and public `circulars.json` was fetched at `generated_at=2026-04-08T08:45:24Z` with `count=117`; however, sampled live records still showed empty `k1_topics`, `k1_facts`, and `k1_guidelines`, so the K1 prompt integration is not yet reflected in live data output.

Pending tasks (priority order):
1. Rerun the workflow / regenerate `circulars.json` so live data is rebuilt under the `v3.0.17` K1 integration code.
2. After regeneration, verify on live records that `k1_topics`, `k1_facts`, and `k1_guidelines` are populated where relevant.
3. Fix topic-aware review cross-topic contamination so supplier / finance links do not leak into curriculum / student circulars.
4. When the refreshed `role_facts.json` arrives, validate it against `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` v2.0.0 before integrating that separate K1 role-facts path.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- Front-end `v3.0.17` is live, but sampled live data still does not expose the new `k1_*` fields.
- The live K1 facts schema still differs from the older task brief; current code supports both shapes, but this should remain under watch.
- `role_facts.json` is still not available, so that separate K1 integration path remains pending.

Validation status: public HTML PASS at `v3.0.17`; public JSON PASS with `generated_at=2026-04-08T08:45:24Z`, `count=117`; sampled live records still had empty `k1_topics`, `k1_facts`, and `k1_guidelines`.

Post-startup first action: trigger or verify a workflow run that regenerates `circulars.json`, then fetch two or three live circulars again to confirm whether the K1 fields are now populated.
```

## 2026-04-08 Publish v3.0.17 K1 public JSON integration to repo

1. Agent & Session ID: Codex_20260408_0002
2. Task summary: 依使用者要求先 `push`，將本地 `v3.0.17`（K1 public JSON prompt integration）發布到 deploy repo / GitHub repo，並立即檢查 public GitHub Pages 是否已追上。
3. Layer classification: Product / System Layer（release publish / verification）+ Development Governance Layer（session persistence）
4. Source triage: 非新功能開發；屬發佈與 propagation 驗證。目標是讓前一輪已完成的 K1 integration code 上 repo，並如實確認 public site 狀態。
5. Files read: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/CODEBASE_CONTEXT.md`
6. Files changed: `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 執行 `bash /Users/leonard/Downloads/Claude-edb-Project-V3/deploy.sh --no-bump`
   - ✅ 發布成功，deploy repo `main` 更新到 commit `05084d0`
   - ✅ deploy repo status 驗證 clean 且對齊 `origin/main`
   - ✅ cache-busted 抓取 public GitHub Pages HTML 驗證 live 狀態
8. Validation / QC:
   - `bash /Users/leonard/Downloads/Claude-edb-Project-V3/deploy.sh --no-bump` → PASS
   - `git -C ~/Documents/EDB-AI-Circular-System rev-parse --short HEAD` → PASS (`05084d0`)
   - `git -C ~/Documents/EDB-AI-Circular-System status --short --branch` → PASS (`main...origin/main`)
   - `curl -L 'https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html?t=20260408-v3017-push'` → PASS with notes (public HTML still shows `v3.0.16`)
9. Pending:
   - 等待 GitHub Pages propagation 或手動觸發 workflow
   - 驗證 live K1 facts / guidelines prompt integration
   - 修正 topic-aware review 疊加污染
10. Next priorities:
   - 追蹤 public GitHub Pages 是否追上 `v3.0.17`
   - 驗證 live K1 integration
   - 修正 topic-aware review 疊加污染
11. Risks / blockers:
   - repo 已是 `v3.0.17`，但 public Pages 最新 cache-busted 檢查仍回 `v3.0.16`
   - live K1 facts schema 仍需持續留意與 task brief 的差異
12. Notes:
   - 這次 push 已成功，若 public site 未即時更新，需待 Pages propagation 或手動 workflow。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 使用者要求立即推送 `v3.0.17`，並希望後續可以交給 K1 agent 跟進。
2. Root Cause:
   - `v3.0.17` 只在 workspace；尚未進入 deploy repo / public site。
3. Fix:
   - 執行既有 `deploy.sh --no-bump` 發布流程，之後立刻以 cache-busting 方式檢查 public HTML。
4. Verification:
   - deploy repo `HEAD=05084d0`
   - deploy repo clean and tracking `origin/main`
   - public HTML 暫仍為 `v3.0.16`
5. Regression / rule update:
   - 無新增治理規則；本次屬 release publish / current-state persistence。

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Publish flow | workspace 已在 `v3.0.17` | 執行 `deploy.sh --no-bump` | repo `main` 成功更新到 `v3.0.17` | commit `05084d0` pushed | PASS |
| Repo parity | push 完成後 | 檢查 deploy repo status | working tree clean and tracking origin | `main...origin/main` | PASS |
| Public frontend propagation | push 後再次檢查 public HTML | 應看到 `v3.0.17` 或明確辨識 propagation 未完成 | public HTML 仍顯示 `v3.0.16` | PASS with notes |

Overall: PASS with notes

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | ✓ Done |

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: continue from repo-pushed `v3.0.17` as of 2026-04-08. The K1 public JSON prompt integration has been published to the deploy repo at commit `05084d0`, but the latest cache-busted public GitHub Pages HTML still showed `v3.0.16`, so propagation is not complete yet.

Pending tasks (priority order):
1. Recheck public GitHub Pages until the site actually shows `v3.0.17`.
2. Once public Pages catches up, verify that regenerated live data reflects the K1 facts / guidelines prompt integration.
3. Fix topic-aware review cross-topic contamination so supplier / finance links do not leak into curriculum / student circulars.
4. When the refreshed `role_facts.json` arrives, validate it against `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md` v2.0.0 before integrating that separate K1 role-facts path.

Key files changed in this session:
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- Repo is already on `v3.0.17`, but public Pages still showed `v3.0.16` during the latest cache-busted verification.
- The live K1 facts schema still differs from the older task brief; the code supports both shapes, but this should remain under watch.
- `role_facts.json` is still not available, so that separate K1 integration path remains pending.

Validation status: deploy script PASS; deploy repo HEAD/status PASS; public HTML check still showed `v3.0.16`.

Post-startup first action: fetch the public `edb-dashboard.html` again with a cache-busting query param and confirm whether GitHub Pages has caught up to `v3.0.17`.
```

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

## 2026-04-09 Local role_facts.json prompt integration

1. Agent & Session ID: Codex_20260409_0003
2. Task summary: 接入 K1 交付的本地 `dev/knowledge/role_facts.json`，將角色知識注入現有 LLM prompt 流程，並把命中結果寫回輸出 JSON，作為 K1 public facts/guidelines 之外的本地角色知識層。
3. Layer classification: Product / System Layer（analysis pipeline behavior change）+ Development Governance Layer（session persistence）
4. Source triage: 非 bug fix；屬外部知識整合與 prompt enrichment 擴展。現有 K1 public JSON consume 已穩定，因此本輪採最小可運行版，把 local role facts 掛到現有 topic selection / backfill flow，而非另起新分析管線。
5. Files read: `edb_scraper.py`, `README.md`, `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/knowledge/role_facts.json`
6. Files changed: `edb_scraper.py`, `edb-dashboard.html`, `README.md`, `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
7. Completed:
   - ✅ 確認新版 `dev/knowledge/role_facts.json` 已到位，`_meta.version=2.0.0`
   - ✅ 新增 `RoleFactsClient`，載入本地 role-facts 並重用現有 topic selection 邏輯
   - ✅ LLM prompt 新增 `【EDB學校管理知識中心角色事實】` 區塊
   - ✅ 新增輸出欄位 `role_fact_topics` / `role_facts`
   - ✅ Phase 3 skip-carry-forward 與 Phase 4.5 backfill 現均會處理 role-facts
   - ✅ 版本升至 `v3.0.22`
8. Validation / QC:
   - `python3 -m py_compile edb_scraper.py` → PASS
   - dashboard JS compile check → PASS
   - role-facts logic check → PASS
9. Pending:
   - 發布 `v3.0.22`
   - 重跑 school-year workflow，驗證 live `role_fact_topics` / `role_facts`
   - 抽樣檢查 role-facts 對 `subject_head` / `panel_chair` 命中是否合理
10. Next priorities:
   - 發布 `v3.0.22`
   - 重跑 workflow 並驗證 live role-facts 回填
   - 抽樣檢查 role-facts 對角色判斷的實際幫助
11. Risks / blockers:
   - 本機缺 `OPENAI_API_KEY`，未做完整雲端 LLM 端到端回歸
   - role-facts 目前只做 local prompt / backfill 驗證，仍需 live workflow 驗證
   - 如注入量過大，後續可能仍需再收緊 per-role facts cap
12. Notes:
   - 本輪刻意重用 K1 topic selection，避免 role-facts 自行再建立另一套 topic detector，降低 cross-topic 漂移風險。

### Problem -> Root Cause -> Fix -> Verification
1. Problem:
   - 新版 `role_facts.json` 已交付，但 Circular System 仍只有 K1 public `knowledge.json` / `guidelines.json` consume 路徑，未能把本地角色事實注入 prompt。
2. Root Cause:
   - 先前只完成 public K1 JSON integration，未建立 local role-facts loader / prompt assembly / backfill path。
3. Fix:
   - 在 `edb_scraper.py` 新增 `RoleFactsClient`，讀取 `dev/knowledge/role_facts.json`，沿用現有 topic selection，將 role facts 分組注入 prompt，並持久化 `role_fact_topics` / `role_facts`。
4. Verification:
   - py_compile PASS
   - JS compile PASS
   - sample `student/activity/finance` 測試：`role_facts` 非空，prompt 含 `【EDB學校管理知識中心角色事實】`
5. Regression / rule update:
   - `CODEBASE_CONTEXT.md` Key Decision #24 added: local role-facts prompt injection is now a first-class enrichment layer with backfill support.

### Test Scenarios
| Scenario | Precondition | Action / input | Expected | Actual | Result |
|---|---|---|---|---|---|
| Normal flow | `dev/knowledge/role_facts.json` present and valid | Load client and fetch facts for `student/activity/finance` sample | Returns non-empty role facts and prompt block | topics=`['student','activity','finance']`, `role_facts` non-empty, prompt block present | PASS |
| Boundary | Some roles absent in a topic | Build grouped role facts | Only roles with facts should appear | output omits empty roles, keeps `all_roles` and populated role keys only | PASS |
| Error / failure path | No `OPENAI_API_KEY` in environment | Run local integration checks only | Syntax / prompt checks still possible; end-to-end cloud call skipped | local checks passed; cloud call not run | PASS with notes |
| Regression | Existing K1 public JSON enrich path must remain intact | Keep K1 client + prompt sections unchanged while adding role facts | `k1_facts` / `k1_guidelines` logic remains alongside role facts | code path preserved; prompt builder now appends role block after K1 sections | PASS |

Overall: PASS

### Doc Sync

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | ✓ Done |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | ✓ Done |
