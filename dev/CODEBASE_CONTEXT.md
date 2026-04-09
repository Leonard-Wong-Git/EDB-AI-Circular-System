# Codebase Context

> Auto-generated per AGENTS.md §1 — Claude_20260317_0800
> This file contains Product / System Layer facts. Update when tech stack, External Services, or Key Decisions change.

---

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Pure HTML / CSS / JS (single-page) | No framework; SheetJS CDN for Excel export only |
| Backend | Python 3.10+ (`edb_scraper.py`) | Single-file pipeline: scrape → PDF → LLM → deterministic post-analysis knowledge review → JSON |
| PDF extraction | PyMuPDF (fitz) >= 1.24.0 | Replaced pdfplumber/pdfminer (2026-03-15) |
| LLM | OpenAI gpt-5-nano | temperature=1 fixed; `developer` role; `max_completion_tokens`=16000; `json_schema` structured output |
| Embeddings | text-embedding-3-small | Used for semantic knowledge search (KnowledgeStore); 0.45 threshold |
| CI/CD | GitHub Actions | `update-circulars.yml` — cron 3×/day (days-3) + manual (school-year) |
| Hosting | GitHub Pages | Root deploy; `index.html` redirects to `edb-dashboard.html` |
| Data | `circulars.json` | Tracked in git (required for Pages); output of `edb_scraper.py` |
| Knowledge | `dev/knowledge/knowledge.json` | Vetted knowledge from edb-knowledge repo; 107 facts in v1.2.2 |

---

## Directory Map

```
EDB-Circular-AI-analysis-system/
├── AGENTS.md                       # Governance SSOT
├── CLAUDE.md                       # Claude bridge (@AGENTS.md)
├── GEMINI.md                       # Gemini bridge (@./AGENTS.md)
├── README.md                       # Project overview (v2.1.0; updated 2026-03-23)
├── CHANGELOG.md                    # Version history (up to v2.1.0)
├── .gitignore                      # Standard exclusions
│
├── edb-dashboard.html              # ★ v2.1.0 production Dashboard (3,047 lines)
├── edb-dashboard-mockup.html       # Legacy v0.1.0 mockup (archived)
├── index.html                      # GitHub Pages redirect → edb-dashboard.html
├── edb_scraper.py                  # ★ Backend pipeline (scrape + AI + R1-v2 postprocess; PHASE 4 merge fix)
├── fetch_knowledge.py              # EDB/ICAC knowledge fetcher
├── requirements.txt                # Python deps (requests, bs4, PyMuPDF, openai, lxml)
├── circulars.json                  # ★ AI analysis output (incremental merge; school-year full data)
│
├── .edb_cache/                     # PDF cache (not versioned)
├── .github/workflows/
│   └── update-circulars.yml        # CI: scrape + commit + Pages deploy
│
└── dev/
    ├── CODEBASE_CONTEXT.md         # This file
    ├── SESSION_HANDOFF.md          # Current session state
    ├── SESSION_LOG.md              # Session history
    ├── ACCEPTANCE_CHECKLIST.md     # A–K 11 categories, 80+ test items
    ├── GIT_PUSH_MANUAL.md          # Git push instructions
    ├── K1_KNOWLEDGE_INTERFACE_SPEC.md  # K1 project interface contract
    ├── v0.2.0-FRONTEND-SPEC.md     # Frontend spec SSOT
    ├── HANDOFF_PROMPT_v14.md       # Legacy handoff (archived)
    ├── knowledge/
    │   ├── role_facts.json         # K1 local role-facts knowledge (v2.0.0 contract; prompt injection source for role-specific facts)
    │   ├── ROLE_KNOWLEDGE_INDEX.md # Top 5 files per role
    │   ├── *.md                    # Topic knowledge files (fin, hr, curriculum, etc.)
    ├── tools/
    │   ├── debug_edb_html.py       # EDB POST diagnostics
    │   ├── parse_form.py           # ASP.NET form parser
    │   ├── parse_row.py            # Circular row parser
    │   ├── parse_structure.py      # DOM structure analyzer
    │   ├── simulate_post_analysis_review.py  # Prototype: post-analysis knowledge review simulation
    │   └── test_llm.py             # LLM API diagnostics
    └── init_backup/                # AGENTS.md install backups
```

---

## Key Entry Points

| Entry Point | Description |
|-------------|-------------|
| `edb-dashboard.html` | Open in browser; fetches `circulars.json` from same directory |
| `edb_scraper.py --school-year -o ./circulars.json -v` | Full school-year scrape + LLM analysis + post-analysis knowledge review |
| `edb_scraper.py --days 3 -o ./circulars.json -v` | Incremental 3-day scrape + deterministic knowledge review |
| `edb_scraper.py --llm-only -o ./circulars.json -v` | Re-run LLM only (no scrape) while retaining post-analysis review |
| `.github/workflows/update-circulars.yml` | CI trigger (manual: school-year; cron: days-3) |

---

## Build & Run

### Local development
```bash
# Install deps
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="sk-..."

# Run scraper (school-year)
python3 edb_scraper.py --school-year --output ./circulars.json -v

# Serve dashboard
python3 -m http.server 8080
# Open: http://localhost:8080/edb-dashboard.html

# Publish latest workspace to GitHub
bash ~/Downloads/Claude-edb-Project-V3/deploy.sh
```

### CI (GitHub Actions)
- **Trigger:** push to `main` auto-deploys Pages for code/docs changes; cron 3×/day (HKT 07:00/13:00/17:00) auto uses `--days 3`; manual dispatch supports school-year/days-3/14/30/365
- **Secret:** `OPENAI_API_KEY` (Settings → Secrets → Actions)
- **Deploy:** Commits `circulars.json` → deploys entire repo root to GitHub Pages
- **Conflict strategy:** Save fresh JSON to `/tmp`, `git fetch + reset --hard origin/main`, copy back, commit

### CLI parameters
| Param | Default | Description |
|-------|---------|-------------|
| `--days N` | 90 | Scrape last N days |
| `--school-year` | — | Scrape from Sep 1 of current school year |
| `--from / --to` | — | Custom date range (YYYY-MM-DD) |
| `--output / -o` | `./edb_data/circulars.json` | Output path |
| `--llm-only` | false | Re-run LLM only (must use with `--output`) |
| `--skip-llm` | false | Skip LLM analysis |
| `--verbose / -v` | false | Verbose logging |

---

## External Services

### EDB Circular Website
- Base URL: https://applications.edb.gov.hk/circular/circular.aspx?langno=2
- Version: ASP.NET WebForms (POST + ViewState)
- Auth: None (public)
- Required params: ViewState, `ctl00$MainContentPlaceHolder$txtPeriodFrom`, `txtPeriodTo`, `btnSearch2`, `currentSection="2"`, `lbltab_circular="通告"`
- Forbidden params: `ddlYear`, `ddlMonth` (do not exist); `ContentPlaceHolder1` (wrong prefix)
- Response path: `<tr>` rows → 3× `<td class="circularResultRow circulartRow">` → Cell[0]=date, Cell[1]=title+number, Cell[2]=PDF links
- Official docs: N/A (reverse-engineered)
- Doc-reviewed: 2026-03-10 (Claude_20260310_FE01)
- Test-verified: 2026-03-10 (Claude_20260310_FE01 — 14 circulars scraped)
- Notes: No detail_url in list page; PDF priority: C.pdf > E.pdf > S.pdf

### OpenAI gpt-5-nano API
- Base URL: https://api.openai.com/v1/chat/completions
- Version: gpt-5-nano (reasoning model)
- Auth: Bearer token (`OPENAI_API_KEY`)
- Required params: `model`, `messages` (with `developer` role, NOT `system`), `temperature=1`, `max_completion_tokens=16000`, `response_format: { type: "json_schema", json_schema: {...} }`
- Forbidden params: `max_tokens` (use `max_completion_tokens`); `system` role (use `developer`); `temperature≠1` (causes 400)
- Response path: `choices[0].message.content` → JSON parse
- Official docs: https://platform.openai.com/docs/api-reference/chat/create
- Doc-reviewed: 2026-03-10 (Claude_20260310_FE01)
- Test-verified: 2026-03-10 (Claude_20260310_FE01 — EDBCM030/2026 analysis successful)
- Notes: Reasoning model — high token consumption for internal reasoning; 400K context window

### GitHub Pages
- Base URL: https://leonard-wong-git.github.io/EDB-AI-Circular-System/
- Version: GitHub Pages v4 (actions/deploy-pages@v4)
- Auth: `id-token: write` OIDC
- Required params: contents write + pages write permissions
- Response path: N/A (static hosting)
- Official docs: https://docs.github.com/en/pages
- Doc-reviewed: 2026-03-10 (Claude_20260310_FE01)
- Test-verified: 2026-03-10 (Claude_20260310_FE01 — Pages deployment successful)
- Notes: Node.js 20 deprecation warning (cosmetic, deadline June 2026); deploy entire repo root

### K1 Knowledge Public JSON API
- Base URL: https://leonard-wong-git.github.io/edb-knowledge/
- Version: live payload `_meta.version` = `1.3.1`
- Auth: None (public GitHub Pages JSON)
- Required params:
  - `knowledge.json`: no query params; returns topic-keyed knowledge payload
  - `guidelines.json`: no query params; returns topic-keyed guideline document lists
- Forbidden params:
  - none documented
  - do not use local exports / backup artifacts from the K1 repo as API truth; public SSOT is `knowledge.json`, `guidelines.json`, and `K1_API_SPEC.md`
- Response path:
  - `knowledge.json`: current live shape is `topic_id -> object` with `_keywords_zh` plus role arrays (`all_roles`, `principal`, `vice_principal`, `subject_head`, `panel_chair`, `teacher`, `eo_admin`, optional `supplier` for finance); public `department_head` bucket has been removed as of `v1.3.1`
  - `guidelines.json`: `topic_id -> [ { id, title, titleShort, url, year, format, ... } ]`
- Official docs: https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md
- Doc-reviewed: 2026-04-09 (Codex_20260409_0001)
- Test-verified: 2026-04-09 (Codex_20260409_0001 — fetched live `knowledge.json`, `guidelines.json`, and `K1_API_SPEC.md`, verified `_meta.version=1.3.1`)
- Notes:
  - prompt injection now assembles主任層 facts from `all_roles` + `subject_head` + `panel_chair`
  - guideline links are attached for every detected topic
  - fetch failure must degrade gracefully and continue LLM analysis without K1 context

---

## Key Decisions

| # | Decision | Date | Rationale |
|---|----------|------|-----------|
| 1 | PyMuPDF replaces pdfplumber/pdfminer | 2026-03-15 | pdfminer C extension caused 107K+ DEBUG log lines; 6 patch attempts failed; PyMuPDF has zero debug output |
| 2 | circulars.json tracked in git | 2026-03-10 | Required for GitHub Pages static hosting; `.edb_cache/` for PDFs remains untracked |
| 3 | gpt-5-nano fixed constraints | 2026-03-10 | temperature=1 mandatory; developer role; max_completion_tokens≥16000; json_schema (not json_object) |
| 4 | K1 knowledge injection via role_facts.json | 2026-03-16 | Decoupled from PDF extraction project; interface contract in K1_KNOWLEDGE_INTERFACE_SPEC.md |
| 5 | R1-v2 three-layer role accuracy | 2026-03-16 | Prompt criteria + few-shot examples + _postprocess_roles() — LLM over-assigns roles without all three |
| 6 | Dashboard as single HTML file | 2026-03-16 | No framework; all CSS/JS inline; v2.1.0 = 3,047 lines; centralized VERSION constant |
| 7 | CI conflict strategy: fetch+reset | 2026-03-16 | Workflow saves fresh JSON to /tmp, resets to remote, copies back — avoids rebase conflicts with local pushes |
| 8 | Frontend spec SSOT in v0.2.0-FRONTEND-SPEC.md | 2026-03-10 | All frontend feature decisions documented here; user confirmed |
| 9 | Scraper PHASE 4 merge (not overwrite) | 2026-03-23 | days-3 mode was overwriting entire circulars.json; PHASE 4 now loads existing JSON, merges raw results in, sorts by date desc — prevents school-year data loss |
| 11 | Semantic Fact-Checking (0.45 Threshold) | 2026-04-03 | Replaced keyword matching with vector similarity against knowledge.json. Threshold set to 0.45 to prevent irrelevant fact injection. |
| 12 | Enhanced Supplier Schema | 2026-04-04 | Added is_tender, procurement_cat, budget_estimate, and compliance_ref to CIRCULAR_SCHEMA for improved supplier statistics. |
| 13 | Deterministic Post-analysis Knowledge Review | 2026-04-04 | After primary AI analysis, apply an ordered normalization/enrichment pass to standardize supplier terminology, backfill missing supplier guidance, attach recommended links, and reduce role drift without overwriting hard facts from the circular. |
| 14 | Topic-aware Curriculum Review Extension | 2026-04-04 | Extended the deterministic second-pass review to curriculum-style circulars so terminology normalization, curriculum implementation reminders, and official curriculum/KPM links can be added without rewriting hard facts. |
| 15 | Idempotent Terminology Normalization Guard | 2026-04-06 | Term-standardization rules that expand a source string into a target containing that same source must collapse duplicate expansions and avoid reapplying on already-normalized text. |
| 16 | Topic-aware Finance Review Extension | 2026-04-06 | Extended the deterministic second-pass review to finance-style circulars so grant-use, document-retention, and finance-process reminders plus official finance references can be added without overwriting grant facts or deadlines. |
| 17 | Topic-aware Student Review Extension | 2026-04-06 | Extended the deterministic second-pass review to student-style circulars so participation support, parent-notice, and student-record reminders plus student-operations references can be added without overwriting hard facts. |
| 18 | K1 Role Contract Alignment Target | 2026-04-06 | The agreed next-step contract for knowledge exchange is `subject_head` = 科主任, `panel_chair` = 主任, `eo_admin` = EO; product code still requires a compatibility refactor before fully adopting these keys end-to-end. |
| 19 | Role Compatibility Layer Before Full Schema Cutover | 2026-04-06 | Product code now normalizes legacy `department_head` data into `panel_chair` while accepting the new `subject_head` / `panel_chair` contract, so old `circulars.json` remains readable during the migration window. |
| 20 | K1 Public JSON Prompt Injection | 2026-04-08 | `edb_scraper.py` now fetches K1 `knowledge.json` and `guidelines.json` at analysis time, injects prompt-ready facts and guideline links with graceful fallback, and tolerates both the older entry-list facts schema and the current live role-bucket facts schema. |
| 21 | K1 Topic Slimming Guard | 2026-04-08 | K1 topic supplementation is now capped and prioritized to reduce cross-topic contamination: at most 3 topics, 4 facts per topic / 12 total, 2 guidelines per topic / 6 total, and `general` only falls back when no clearer topic is selected. |
| 22 | K1 Public Schema v1.3.1 Adoption | 2026-04-09 | Circular System now consumes the public K1 role-bucket schema as documented in `K1_API_SPEC.md`:主任層 facts are assembled from `subject_head` + `panel_chair` + `all_roles`; public `department_head` is no longer assumed in K1 fetch logic. |
| 23 | Deterministic Review Raw-signal Gating | 2026-04-09 | Second-pass procurement / finance enrichment now keys off raw circular text (`title` + `official` + `pdf_text`) instead of AI-generated summary or supplier-role text, preventing supplier / finance links from leaking into curriculum / student circulars through self-amplified signals. |
| 24 | Local Role-Facts Prompt Injection | 2026-04-09 | `dev/knowledge/role_facts.json` is now loaded as a local role knowledge layer. It reuses the K1 topic selection path, injects grouped role facts into the LLM prompt, persists `role_fact_topics` / `role_facts` in output JSON, and backfills older records when the fields are missing. |

---

## Path Map (VM Session)

| Role | VM Path |
|------|---------|
| Workspace (frontend SSOT) | `/sessions/.../mnt/Claude-edb-Project-V3` |
| Git Repo (deploy target) | `/sessions/.../mnt/EDB-Circular-AI-analysis-system` |

**Deployment flow:** Claude copies workspace → git repo → commits automatically. User runs ONE push command:
```bash
bash ~/Downloads/Claude-edb-Project-V3/deploy.sh
```

---

## AI Maintenance Log

| Date | Session ID | Action |
|------|-----------|--------|
| 2026-03-17 | Claude_20260317_0800 | Initial CODEBASE_CONTEXT.md generation. Scanned: README.md, CHANGELOG.md, requirements.txt, .gitignore, .github/workflows/update-circulars.yml, dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md. Consolidated External Services from SESSION_LOG + Known Risks. |
| 2026-03-23 | Claude_20260323_0000 | v2.1.0 update: dashboard 2766→3,047 lines, README rewritten, CHANGELOG updated, Key Decision #9 (PHASE 4 merge fix). |
| 2026-03-26 | Claude_20260326_1100 | v3.0.0 update: list view bug fix (setView block), version bump v2.1.0→v3.0.0, Key Decision #10 (auto version bump rule), AGENTS.md INIT.md merge (5 sections updated). |
| 2026-04-04 | ba64ba27-0c19-41b8-95fc-7dc27a068588 | v3.0.4 integration: KnowledgeStore integrated with semantic search (0.45 threshold), enhanced supplier schema in CIRCULAR_SCHEMA, dashboard UI update for procurement stats. |
| 2026-04-04 | Codex_20260404_0004 | Added automated publish flow: `deploy.sh` now calls `dev/tools/publish_release.py` to patch-bump versions, sync workspace to deploy repo, commit, push, and rely on push-triggered Pages deployment. |
| 2026-04-04 | Codex_20260404_0005 | Added `dev/tools/simulate_post_analysis_review.py` prototype to validate a second-pass knowledge review layer: ordered terminology normalization, missing-point enrichment, recommended links, and role-drift stabilization. |
| 2026-04-04 | Codex_20260404_0006 | Integrated the first runnable post-analysis knowledge review into `edb_scraper.py`; bumped dashboard/scraper version to v3.0.8 and added `knowledge_review` output metadata. |
| 2026-04-04 | Codex_20260404_0008 | Extended deterministic post-analysis knowledge review to curriculum signals, added curriculum-specific reminders/links, and bumped local workspace version to v3.0.9 pending deploy. |
| 2026-04-06 | Codex_20260406_0002 | Fixed duplicated curriculum term replacement by making `_replace_terms()` idempotent, then prepared v3.0.11 for regenerated data and release. |
| 2026-04-06 | Codex_20260406_0005 | Extended deterministic post-analysis knowledge review to finance signals, adding grant-use/document reminders and finance reference links; bumped local workspace version to v3.0.13 pending deploy. |
| 2026-04-06 | Codex_20260406_0009 | Extended deterministic post-analysis knowledge review to student signals, adding participation-support/parent-notice reminders and student-operation reference links; bumped local workspace version to v3.0.15 pending deploy. |
| 2026-04-06 | Codex_20260406_0010 | Updated the K1 interface contract to v2.0.0 so knowledge exchange aligns on `subject_head` / `panel_chair` / `eo_admin=EO`, while documenting that product code still needs a compatibility-layer refactor before full schema adoption. |
| 2026-04-06 | Codex_20260406_0011 | Implemented the first product-side compatibility layer for the new role contract: scraper output now uses `subject_head` / `panel_chair`, legacy `department_head` is normalized to `panel_chair`, dashboard UI exposes 7 roles, and workspace version is now v3.0.16 pending deploy. |
| 2026-04-08 | Codex_20260408_0001 | Integrated K1 public JSON prompt enrichment into `edb_scraper.py`: fetches live `knowledge.json` / `guidelines.json`, detects topics before LLM analysis, injects facts and guideline links into the prompt with graceful fallback, and bumped workspace version to v3.0.17. |
| 2026-04-08 | Codex_20260408_0004 | Tightened K1 topic supplementation and prompt payload size in `edb_scraper.py`, bumped workspace version to v3.0.19, and added guards to reduce `general` / cross-topic contamination before the next publish. |
| 2026-04-09 | Codex_20260409_0001 | Re-aligned K1 integration against the public `v1.3.1` schema and public `K1_API_SPEC.md`, switched主任層 fact assembly to `subject_head` + `panel_chair` + `all_roles`, removed public-schema `department_head` assumptions from K1 fetch logic, and bumped workspace version to v3.0.20. |
| 2026-04-09 | Codex_20260409_0002 | Tightened deterministic knowledge-review gating to use raw circular signals for procurement / finance enrichment, preventing AI-summary / supplier-role self-amplification from leaking supplier or finance links into curriculum / student cases; bumped workspace version to v3.0.21. |
| 2026-04-09 | Codex_20260409_0003 | Integrated local `dev/knowledge/role_facts.json` into the analysis prompt flow, added persisted `role_fact_topics` / `role_facts` output fields plus backfill support, and bumped workspace version to v3.0.22 pending publish. |
