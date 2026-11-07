---
name: prime
description: Load project context from docs/ai-context (spec, project-structure, progress, deployment) before working. Light prime by default (~4-6k tokens); --full loads everything. Use at session start and before designing or changing any subsystem.
whenToUse: Starting a session on an existing project, resuming work after a gap, or before architecture/design work where you have not read the relevant spec section yet.
user-invocable: true
---

# Prime — load project context

Bring the right project context into the session without flooding it. The workspace docs are the map; read the map, then read only the territory the task touches.

Default is a **light prime**: spec table of contents + opening invariants + structure Map + the task-relevant spec sections. `--full` is for design, architecture, and spec-review sessions where broad context genuinely pays for itself.

## Arguments

The argument string is the text that follows the `/prime` token in the user's message. (If this skill was loaded through the `skill` tool, there is no argument string — use defaults.)

Parse it in this order:

1. **Flags** — anywhere in the string, any order; strip each match:
   - `--full` → `full_mode = true`
   - `-p` or `--progress` → `progress_mode = true`
   - `--deploy` → `deploy_mode = true`
2. **Module** *(optional)* — the first remaining token that names a region of this codebase: a `## ` heading in `docs/ai-context/spec.md` (normalized: lowercase, punctuation dropped, e.g. `API` → `api`), or a top-level directory that exists. Strip the matched token.
3. **Task** — whatever remains is the user's task.

No token matches a module → whole project, and every remaining token is task text. So `/prime`, `/prime fix the login bug`, `/prime --deploy`, and `/prime api --full add rate limiting` are all valid.

Do not guess a module that does not exist; a wrong scope silently hides the section that mattered.

## Step 0 — Check the docs exist

Look for `docs/ai-context/spec.md` before anything else.

**If it is missing**, do not invent context. Say so plainly, then fall back to a cheap survey:
- `README.md` / `README.*` (first ~80 lines)
- the project manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `*.xcodeproj`, …)
- top-level directories (glob `*/`, depth 1) and any `AGENTS.md` / `CLAUDE.md`

Report: docs absent → offer `/update-docs` to bootstrap them from the current code, and present the survey as provisional. Never assert design facts you have not read.

## Light prime (default)

1. **Spec TOC** — `grep -n '^## ' docs/ai-context/spec.md`. Keep the line numbers; they drive every later targeted read this session.
2. **Spec opening** — read from the top through the end of the first framing section(s) (Overview / Architecture / Invariants). Use the TOC line numbers to find the stop line; typically under 80 lines. This is where cross-cutting invariants live.
3. **Structure Map** — `grep -n '^## ' docs/ai-context/project-structure.md`, then read the `## Map` section only. No Map section → read the first 40 lines instead.
4. *(only if `progress_mode`)* read `docs/ai-context/progress.md` in full.
5. *(only if `deploy_mode`)* read `docs/ai-context/deployment-infrastructure.md` in full. Otherwise just note it exists and that `--deploy` loads it.
6. **Task-aware deepening** — if a task was given, pick the spec section(s) governing its domain (plus the matched module's section) from the TOC and read just those with the `read` tool's `offset`/`limit`. Torn between two sections → read both; sections are cheap, the full spec is not.

Read files with the `read` tool (offset/limit for sections), search with `grep`, discover with `glob`. Do not `cat` whole documents into the session.

## Standing rule for the rest of the session

Before designing or changing a subsystem whose spec section you have not read, read that section first — the TOC is the map. Never assert a design fact about an unread section from memory. If mid-session work turns architectural (cross-cutting, multi-surface), escalate yourself to the full spec.

## Full prime (`--full`)

Read in parallel, one message with several `read` calls:

1. *(only if `progress_mode`)* `docs/ai-context/progress.md`
2. `docs/ai-context/spec.md` (entire)
3. `docs/ai-context/project-structure.md` (entire)
4. *(only if `deploy_mode`)* `docs/ai-context/deployment-infrastructure.md`

## Response

After reading, confirm compactly:

- **Scope** — whole project or which module; light or full.
- **Loaded** — which spec sections were read, and that the TOC line numbers are in hand for on-demand reads.
- **Flags** — whether `--deploy` / `-p` were active; if skipped, say `progress.md` (roadmap / live build-state) was not loaded and `-p` loads it, and that infra context is available via `--deploy`.
- **Status** — current status, immediate priorities, blockers visible from what was read.

Then handle the task portion of the arguments. No task given → confirm you are primed and ready.
