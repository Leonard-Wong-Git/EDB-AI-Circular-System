# Doc Sync Checklist
<!-- LOCAL PROJECT RECORD -->
<!--
  USAGE: At PERSIST phase, if any file was created or modified during CHANGE:
  1. Identify the change category in the registry below
  2. Execute all "Required Doc Updates" for matched rows
  3. Record triggered rows in SESSION_LOG under "Doc Sync"
  4. If your change type has no matching row: add the row first, then proceed
     (prevents this registry from going stale)
-->

## Change Category Registry

| Change Category | Required Doc Updates | Verification Method |
|---|---|---|
| Governance rule change (AGENTS.md) | INIT.md FILE 1 mirror; README if behavior is user-facing | grep parity check |
| Tech stack / build / dependency change | CODEBASE_CONTEXT.md Stack or Build section | manual review |
| External API / service change | CODEBASE_CONTEXT.md External Services block | block format check |
| New governance file added to install | §5a backup list in AGENTS.md; INIT.md ROOT SAFETY CHECK backup list; INIT.md FILE 1 §5a | grep check |
| Session governance maintenance / log archive | SESSION_HANDOFF.md current state + SESSION_LOG.md current entry + archive pointer / files if rotation triggered | manual review |
| New project doc added | This file — add a row for the new doc's update triggers | row presence check |
| README link / reference update | README.md relevant section; SESSION_LOG.md entry if done in-session | manual review |
| Deploy / release workflow change | README.md publish instructions; GIT_PUSH_MANUAL.md; CODEBASE_CONTEXT.md Build & Run / Path Map | manual review |
| Prototype / simulation tool added | CODEBASE_CONTEXT.md Directory Map if tool is meant for reuse; SESSION_LOG.md entry | manual review |
| Analysis pipeline behavior change | CODEBASE_CONTEXT.md Key Decisions / maintenance log; README if user-visible; SESSION_LOG.md entry | manual review |
| Frontend display behavior change | README.md if user-visible; SESSION_LOG.md entry | manual review |
| _[Add project-specific rows below this line]_ | | |

## Anti-pattern: No Matching Row

If your change has no matching row above:
- Do NOT skip silently — add the missing row first, then proceed
- Record the registry addition in SESSION_LOG under `Doc Sync: registry updated`
- Reason: a stale registry is worse than no registry (false safety net)
