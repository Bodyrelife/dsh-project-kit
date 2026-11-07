# Doc templates

Skeletons for bootstrapping `docs/ai-context/` and the project instruction file. Treat them as scaffolding: fill from the actual code, then delete every comment you did not act on. An empty section with a heading is worse than no section.

## `docs/ai-context/spec.md`

```markdown
# Technical Specification

<!-- What the product does: features, contracts, data flows. Present tense, is-state only. -->

## Overview

<problem, core value, one paragraph max>

## Invariants

<!-- Cross-cutting rules a future session must not violate. Light prime reads only this opening — put every project-wide invariant here. Detail lives in a section below. -->

- **<rule>** — <one-phrase reason> → §<section>

## Architecture

<!-- Components, boundaries, and how they talk to each other. Table beats prose. -->

| Component | Responsibility | Talks to |
|---|---|---|

## Data Model

<!-- Tables/collections and non-obvious relationships. Do not reproduce the schema. -->

## API Contracts

### <METHOD> <path>

Request: `<shape>` · Errors: `<code>` = `<meaning>` · Notes: <non-obvious behavior>

## Data Flows

<!-- End-to-end flow for the most important journeys. Numbered steps, 3-6 lines each. -->

## Constraints

<!-- Rate limits, quotas, platform limits, vendor quirks. -->
```

## `docs/ai-context/project-structure.md`

```markdown
# Project Structure

## Map

<!-- The section /prime reads. Keep it first and current: what lives where, and which subsystem owns what. -->

| Path | Holds | Entry point |
|---|---|---|

## Technology Stack

| Layer | Technology | Notes |
|---|---|---|

## File Tree

```
<project>/
├── <dir>/   # role, one line
└── <file>   # role, one line
```

## Build & Test

```bash
<install>  · <build>  · <test>  · <lint>
```
```

## `docs/ai-context/progress.md`

```markdown
# Progress

## Status

<one line: e.g. "Beta — core flows shipped, hardening auth">

## Current Work

| Item | State | Owner | Notes |
|---|---|---|---|
<!-- IN PROGRESS / TODO / BLOCKED -->

## Blockers

- <blocker> — <what unblocks it>

## Completed

| Phase | What | Date |
|---|---|---|
<!-- ~10 words per row; delete rows older than the current phase cycle -->
```

## `docs/ai-context/deployment-infrastructure.md`

Only create this when the repo shows evidence (CI config, Dockerfile, deploy scripts, IaC, env templates). Otherwise say the project is not deployed yet and skip the file.

```markdown
# Deployment & Infrastructure

## Environments

| Env | URL | Branch / trigger | Notes |
|---|---|---|---|

## CI/CD

<!-- Pipeline stages, required checks, where secrets come from. -->

## Services & Accounts

| Service | Purpose | Console |
|---|---|---|
<!-- Names only. Never secrets, tokens, or credentials. -->

## Rollback

<how to undo a bad deploy, in 1-3 steps>
```

## `AGENTS.md` (project instruction file)

```markdown
# <Project>

## Rules

<!-- Only rules that change agent behavior. If deleting a line changes nothing, delete it. -->

- **Ask before**: git commits, breaking changes, deleting files, architecture decisions worth ≥1 day of rework.
- **Stop and re-plan** when an approach fails twice or reveals unexpected complexity — do not push through.
- **Docs**: run `/update-docs` after architectural changes; `/prime` at session start.

## Architecture decisions (settled)

<!-- Decisions already made, so they are not relitigated. One line each, with the reason. -->

- **<decision>** — <reason>

## Conventions (non-obvious only)

- <project-specific deviation from the default, and why>

## Commands

```bash
<install>  · <test>  · <lint>  · <run>
```
```

Do not copy the upstream kit's `templates/AGENTS.md` here: that file is a read-only second-opinion persona for another CLI, and the harness would load it as project rules.
