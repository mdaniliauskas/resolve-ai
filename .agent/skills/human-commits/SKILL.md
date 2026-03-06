---
name: human-commits
description: Guidelines for making meaningful, well-scoped git commits — like a senior developer, not a file-dump bot. Semantic commits in English.
---

# Human-Friendly Commits — Skill Guide

> A commit should tell the story of a purposeful step forward, not the history of a save button being pressed.

AI-assisted development tends to produce either massive single commits dumping everything at once, or meaningless micro-commits on every file save. This skill enforces **purposeful, human-scale commits** that make `git log` readable and code review pleasant.

---

## 1. When to Commit

Commit when a **meaningful unit of work is complete**. Think of commits as chapters in a story — each one should stand on its own.

### Commit triggers
- ✅ A feature or sub-feature is working (even if the full feature isn't done yet)
- ✅ A bug is fixed and verified
- ✅ A refactor is done and tests still pass
- ✅ A task or to-do item is checked off
- ✅ Setup/infra is complete and functional (e.g., "project scaffold ready", "CI pipeline configured")
- ✅ The user explicitly asks to commit

### Do NOT commit
- ❌ After every file save or small tweak
- ❌ With broken/failing tests (unless the commit message explicitly says `wip:`)
- ❌ With unreviewed AI-generated code that you don't understand yet
- ❌ A giant dump of 20 files that span 5 unrelated concerns

---

## 2. Commit Message Format (Conventional Commits)

All commits follow the **Conventional Commits** specification. Messages are always in **English**.

```
<type>(<scope>): <imperative short description>

[optional body — what and why, not how]

[optional footer — issue refs, breaking changes]
```

### Rules for the subject line
- Use the **imperative mood**: "add", "fix", "remove" — not "added", "fixing".
- **Max 72 characters** on the subject line.
- No period at the end.
- Lowercase after the colon.

---

## 3. Commit Types

| Type | When to use | Example |
|---|---|---|
| `feat` | New feature or capability | `feat(rag): add CDC chunking pipeline` |
| `fix` | Bug fix | `fix(api): handle empty message body` |
| `refactor` | Code change with no behavior change | `refactor(agents): extract intent classifier` |
| `test` | Adding or updating tests | `test(rag): add retrieval golden test set` |
| `docs` | Documentation only | `docs(readme): add architecture diagram` |
| `chore` | Tooling, config, deps, CI | `chore: add ruff and mypy to dev deps` |
| `perf` | Performance improvement | `perf(rag): cache embeddings across requests` |
| `ci` | CI/CD pipeline changes | `ci: add GitHub Actions workflow` |
| `wip` | Intentional work-in-progress | `wip(agents): legal analysis draft — not tested` |

---

## 4. Scope

The scope is the **component or module** being changed. Keep it short and consistent:

| Scope | Maps to |
|---|---|
| `rag` | `rag/` folder |
| `agents` | `agents/` folder |
| `api` | `api/` folder |
| `frontend` | `frontend/` folder |
| `config` | `config.py`, `.env.example` |
| `ci` | GitHub Actions, Docker |
| `deps` | `pyproject.toml`, `uv.lock` |

---

## 5. Commit Body — When to Add One

Add a body when the **why** isn't obvious from the subject. Skip it for routine changes.

```
feat(rag): split CDC ingestion into load, chunk, and index steps

Each step is now a separate function so they can be tested independently
and re-run in isolation (e.g., re-index after changing chunk size without
re-downloading the source document).
```

---

## 6. Good vs. Bad Examples

```
# ❌ Too vague
update files
fix stuff
wip

# ❌ Too granular (each of these should be one commit)
add import to legal_analysis.py
add import to orchestrator.py
fix typo in config

# ❌ Too big (spans 5 unrelated concerns)
feat: add agents, api, rag, frontend, and docker setup

# ✅ Right size and clarity
feat(api): add /api/chat and /api/health endpoints
feat(rag): implement CDC ingestion and ChromaDB indexing
fix(agents): prevent orchestrator from routing ambiguous inputs to legal analysis
chore: configure uv, ruff, and mypy for the project
ci: add GitHub Actions workflow for lint and test on push
```

---

## 7. Branch Strategy

Use short-lived **feature branches**, merged via pull request (or direct push on solo projects):

```
main          — always deployable
├── feat/rag-ingestion
├── feat/legal-analysis-agent
├── fix/api-cors-config
└── chore/project-setup
```

- Branch names are **kebab-case**, prefixed with the commit type.
- Delete branches after merging.
- On solo MVP projects, committing directly to `main` is acceptable for small changes.

---

## 8. Commit Checklist

Before every commit:

- [ ] Does this commit represent **one complete unit of work**?
- [ ] Does `git diff --stat` show a **reasonable scope** (not 30 files)?
- [ ] Do **all tests pass** (or is the commit explicitly marked `wip:`)?
- [ ] Is the **commit message in English**, imperative, under 72 chars?
- [ ] Are **secrets, `.env`, and large data files** excluded from the diff?
- [ ] Is `uv.lock` committed if dependencies changed?

---

*Apply this skill whenever creating, reviewing, or proposing a commit. The goal is a `git log` that reads like a coherent project journal.*
