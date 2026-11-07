---
name: update-docs
description: Update project documentation after code changes. Maintains the four docs/ai-context files (spec, project-structure, progress, deployment-infrastructure) and the project instruction file (AGENTS.md). Use after features, refactors, or anything that changes architecture, structure, or status; bootstraps the docs when they do not exist yet.
whenToUse: A change has landed that a future session could not reconstruct from the code alone — new architecture, contract, invariant, or structure. Also when docs/ai-context is missing and needs a first pass.
user-invocable: true
---

# Update Docs — documentation maintenance

Keep project documentation synchronized with the code. Updates the core `docs/ai-context/` files and the project instruction file as needed.

## Core principle

**Compress aggressively — the default for every line is DELETE.** A line earns its place only when it encodes something an agent cannot derive from the code, the git log, or the spec. Every run prunes as much as it adds.

**Document the current "is" state only — never legacy, never what changed.**

- Write as if the docs are being read for the first time.
- No "previously", "was changed from", "used to be", "improved".
- No migration notes or upgrade paths inside the docs.
- Something removed → remove its documentation, do not leave a "removed X" note.
- No build-state qualifiers ("recently added", "just landed", "new in this release") — dead the moment the work ships; git carries that.

**Audience: agents, not humans.** These docs exist so a future session can prime fast. No marketing, no narrative arc, no "we did X then Y" — dead the moment work ships; git log carries that. Prefer tables, bold inline labels, and pseudocode over prose. Put code identifiers in backticks. Pair every non-obvious rule with a one-phrase reason (security, past incident, vendor quirk).

## When to skip

**The bar is architecture, not activity.** A run only earns doc changes when a change lands **new architecture** — a data flow, contract, invariant, or design decision a future session could not reconstruct from code alone. Fold that into `spec.md` in present tense. That is the only thing that earns new lines — never a record that the work happened. If "document this change" reduces to "note that we did it", write nothing.

Do not run this skill for:

- Bug fixes that change no architecture or capability
- Small refactors (rename, extract method) with no behavior change
- UI tweaks or styling
- Single-file additions that follow an existing pattern
- Performance work with no architectural impact
- Comment or formatting changes

If the caller asked for a doc update and none of the above applies, say so in one line and stop. Silence plus a confident "nothing architectural changed" beats churn.

## What not to document

The agent can read files and grep code. Document only what **cannot be inferred from the code itself**:

| Don't document | Why | Instead |
|---|---|---|
| Standard language conventions | The agent already knows them | Only project-specific deviations |
| Response JSON examples | It reads the actual source | Request contract + error codes only |
| File-by-file descriptions | It can glob and read | Only non-obvious file purposes |
| Completed checklist items | Done lives in git history | Delete from `progress.md` |
| ASCII art diagrams | Many lines, low value | Compact tables |

**Density test:** before adding a line, ask "could the agent figure this out by reading the code?" If yes, do not write it.

## Process

### Step 0 — Get the change set

A git repository:

```bash
git diff --stat HEAD
git log --oneline -5
```

Not a git repository (no commits, or no repo at all): reconstruct the change set from the session context, and ask the user only if that is impossible. Never fabricate a diff.

Then classify the change:

- New feature or capability → `spec.md`, maybe `progress.md`
- New files or directories → `project-structure.md`
- Deployment or infrastructure change → `deployment-infrastructure.md`
- Milestone completed or status change → `progress.md`
- New rule or architecture decision → the project instruction file

### Step 1 — Update only the files the change touches

| File | Owns | Update when |
|---|---|---|
| `docs/ai-context/spec.md` | What the product does — features, API contracts, data flows | New feature, API change, behavior change |
| `docs/ai-context/project-structure.md` | File tree, tech stack, directory organization | New files/dirs, dependency or stack change |
| `docs/ai-context/progress.md` | What's done, what's next, blockers | Phase completed, work started, status change |
| `docs/ai-context/deployment-infrastructure.md` | Hosting, accounts, secrets, CI/CD | Infrastructure change, new service, new secret |
| Project instruction file | Rules, architecture decisions, coding standards | New rule, new decision, changed constraint |

### Step 2 — Apply the single-source-of-truth rule

State each fact exactly once across the ai-context bundle and the instruction file. If the same fact appears twice, keep the canonical owner and delete the rest — no breadcrumb pointer left behind. Resolve contradictions by trusting the canonical owner.

- **Internal section references are allowed** — within one file, `§3.7 → §3.2` is fine for navigation.
- **Cross-file breadcrumbs are forbidden.** `/prime` loads the bundle together, so `See spec.md §X` written from another file is pure overhead. Move the fact to its owner.

Ownership examples:

- API endpoint details → `spec.md` (not the instruction file)
- File naming conventions → the instruction file (not `project-structure.md`)
- Deployment URLs → `deployment-infrastructure.md` (not `spec.md`)

**Header-rename hazard:** in single-source docs, section-number pointers are load-bearing. A light prime loads only the TOC and opening invariants; deep facts are reached through pointers into `spec.md`. Renaming a `## ` header means updating every pointer that cites it, or the pointer dangles.

### Step 3 — Pick the project instruction file correctly

The harness auto-loads `AGENTS.md` **and** `CLAUDE.md` from the project root down to the working directory. Both are live instructions at once.

1. `AGENTS.md` exists → it is the owner. Edit it.
2. Only `CLAUDE.md` exists → edit that; do not create a near-duplicate `AGENTS.md` (two files saying almost the same thing both load, and they will drift).
3. Neither exists → create `AGENTS.md` from `references/doc-templates.md`.
4. Both exist and say different things → flag the contradiction to the user and consolidate into `AGENTS.md`, leaving `CLAUDE.md` as a thin pointer or removing it with approval.

**Porting hazard:** the upstream kit's `templates/AGENTS.md` is a read-only "second opinion consultant" persona written for a different CLI. If a project has that file at its root, the harness will load it as project instructions. Flag it and do not treat it as the rules file.

Wording rules for the instruction file: only rules that change agent behavior. If deleting a line would not change what the agent does, delete it. Not a reference doc — no test-structure tables, no naming-convention tables for standard patterns.

### Step 4 — Create missing files

If `docs/ai-context/` does not exist or is partial, create the missing files from the current codebase — populated with accurate present-state content, not placeholder headings. `references/doc-templates.md` holds the skeleton for each file; it is a scaffold, not content. Strip every `<!-- -->` hint you did not fill.

Order of work when bootstrapping: read the manifest and top-level tree → `project-structure.md` → `spec.md` (from actual behavior, entry points, and public interfaces) → `progress.md` (what exists, what is missing) → `deployment-infrastructure.md` only if evidence exists (CI config, Dockerfile, deploy scripts, env templates). No evidence → leave the file out rather than inventing it.

## File-specific rules

**progress.md**

- Absolute dates only ("March 2026", never "last week").
- Marking work complete → DELETE the item; the fix is in git history.
- Completed phases: one table row (~10 words), never paragraphs.
- Remove checklist items completed more than two weeks ago.
- Security items: remove when fixed; keep only open issues.

**spec.md**

- Do not duplicate instruction-file content (architecture principles, coding standards).
- Request format + error codes + key behaviors; skip response examples.
- Reference shared utility files by path; do not reproduce their contents.
- Cross-cutting invariants live in the **opening** section(s). A light prime reads only the opening plus the TOC, so an invariant buried mid-document is invisible at session start. When folding a shipped feature in, hoist any new cross-cutting invariant to one terse line plus a `→ §` pointer.

**project-structure.md**

- The `## Map` section is what `/prime` reads — keep it current and at the top.
- File tree entries get a one-line role; no deep descriptions.
- No full dependency listings; point at the manifest.

## Lifecycle

- **Fold on ship.** When a feature ships, fold its feature doc's architecture into `spec.md` (present tense) and retire the feature doc. Shipped architecture never stays in a future/feature doc.
- **Hoist cross-cutting invariants.** An invariant spanning the project belongs in the opening of `spec.md`, not buried in a feature doc.
- **Permanence.** `spec.md`, `project-structure.md`, and the instruction file must not cite non-permanent docs (open issues, feature docs) by specific-file link. Only `progress.md` may. Carve-out: `project-structure.md` may list a non-permanent doc as a file-tree entry (filename + one-line role), without section citations into it.

## Named-reference lifecycle (optional convention)

If recurring traps or open issues carry stable IDs, give each tag a stale-pass rule so dead references get pruned instead of accumulating.

- **Traps / gotchas:** grep the cited files and symbols. All gone → delete the item. Keyed to a resolution that shipped → verify, then delete.
- **Gates / checklists:** any checked (`[x]`) row → delete immediately.
- **Open follow-ups:** cited file or symbol gone, or a recent commit closes it → delete.
- **Library-version notes** ("X needs Y ≥ 0.31"): if the current pin is already past the threshold, surface it to the user instead of silently deleting — upstream may not have fixed the real issue.

Run the stale pass on every invocation, whatever tagging scheme is in use.

## Bloat check

After updating, check `progress.md` silently:

- Each completed phase row: ~10 words in the "What" column — trim on sight.
- No duplication with `spec.md` — restating architecture there means delete and cross-reference.
- Dead items: remove completed checklist entries older than two weeks.

**Net-line audit guard:** a run that adds ≥10 lines while deleting 0 is a smell — pause and find what is now prunable. A run that only grows is almost never right.

Finish by checking whether the project instruction file also needs the change. If not, leave it untouched.
