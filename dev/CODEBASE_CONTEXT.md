# Codebase Context

> Auto-generated per AGENTS.md §1 — Claude_20260317_0800
> This file contains Product / System Layer facts. Update when tech stack, External Services, or Key Decisions change.

---

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Pure HTML / CSS / JS (single-page) | No framework; SheetJS CDN for Excel export only |
| Backend | Python 3.10+ (`edb_scraper.py`) | Single-file pipeline: scrape → PDF → LLM → JSON |
| PDF extraction | PyMuPDF (fitz) >= 1.24.0 | Replaced pdfplumber/pdfminer (2026-03-15) |
| LLM | OpenAI gpt-5-nano | temperature=1 fixed; `developer` role; `max_completion_tokens`=16000; `json_schema` structured output |
| CI/CD | GitHub Actions | `update-circulars.yml` — cron 3×/day (days-3) + manual (school-year) |
| Hosting | GitHub Pages | Root deploy; `index.html` redirects to `edb-dashboard.html` |
| Data | `circulars.json` | Tracked in git (required for Pages); output of `edb_scraper.py` |
| Knowledge | `dev/knowledge/role_facts.json` | K1 baseline: 6 topics × 7 roles; injected into LLM prompt |

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
    │   ├── role_facts.json         # K1 baseline knowledge (6 topics × 7 roles)
    │   ├── ROLE_KNOWLEDGE_INDEX.md # Top 5 files per role
    │   ├── *.md                    # Topic knowledge files (fin, hr, curriculum, etc.)
    ├── tools/
    │   ├── debug_edb_html.py       # EDB POST diagnostics
    │   ├── parse_form.py           # ASP.NET form parser
    │   ├── parse_row.py            # Circular row parser
    │   ├── parse_structure.py      # DOM structure analyzer
    │   └── test_llm.py             # LLM API diagnostics
    └── init_backup/                # AGENTS.md install backups
```

---

## Key Entry Points

| Entry Point | Description |
|-------------|-------------|
| `edb-dashboard.html` | Open in browser; fetches `circulars.json` from same directory |
| `edb_scraper.py --school-year -o ./circulars.json -v` | Full school-year scrape + LLM analysis |
| `edb_scraper.py --days 3 -o ./circulars.json -v` | Incremental 3-day scrape |
| `edb_scraper.py --llm-only -o ./circulars.json -v` | Re-run LLM only (no scrape) |
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
```

### CI (GitHub Actions)
- **Trigger:** cron 3×/day (HKT 07:00/13:00/17:00) auto uses `--days 3`; manual dispatch supports school-year/days-3/14/30/365
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
| 10 | Auto version bump on every code change | 2026-03-26 | Every session that modifies edb-dashboard.html or edb_scraper.py must increment the version before closing. Scheme: **patch** (v3.0.x) for bug fixes / minor tweaks; **minor** (v3.x.0) for new features or significant UI changes; **major** (vx.0.0) for complete redesigns (user-initiated only). Version must be updated in all 6 locations: `<title>`, `brandVersion` span, `devVersion` span, `versionLabel` span, footer text, `const VERSION`. |

---

## AI Maintenance Log

| Date | Session ID | Action |
|------|-----------|--------|
| 2026-03-17 | Claude_20260317_0800 | Initial CODEBASE_CONTEXT.md generation. Scanned: README.md, CHANGELOG.md, requirements.txt, .gitignore, .github/workflows/update-circulars.yml, dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md. Consolidated External Services from SESSION_LOG + Known Risks. |
| 2026-03-23 | Claude_20260323_0000 | v2.1.0 update: dashboard 2766→3,047 lines, README rewritten, CHANGELOG updated, Key Decision #9 (PHASE 4 merge fix). |
| 2026-03-26 | Claude_20260326_1100 | v3.0.0 update: list view bug fix (setView block), version bump v2.1.0→v3.0.0, Key Decision #10 (auto version bump rule), AGENTS.md INIT.md merge (5 sections updated). |
