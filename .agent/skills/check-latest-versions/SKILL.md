---
name: check-latest-versions
description: Before using or recommending any library, API, SDK, MCP server, or tool, actively verify the current stable version and recommended usage patterns via web search.
---

# Check Latest Versions — Skill Guide

> "Old tutorials and examples are the #1 source of deprecated code in AI-assisted projects."

AI models have a training cutoff. Without active verification, they default to the version they last saw in training data — which may be months or years behind. This skill enforces **version-first thinking**: check before recommending.

---

## 1. When to Apply

Trigger this skill whenever any of the following are being **added, updated, or referenced**:

- Python packages (`pyproject.toml`, `uv add`, `pip install`)
- Node/npm packages (`package.json`, `npm install`)
- AI model identifiers (Gemini, Claude, OpenAI, etc.)
- SDK clients (`google-genai`, `anthropic`, `openai`, `langchain`, etc.)
- MCP servers (any `mcp__*` tool or server being installed/configured)
- REST or GraphQL API versions (endpoints with `/v1/`, `/v2/`, etc.)
- Docker base images (`python:3.x-slim`, `node:x-alpine`, etc.)
- CLI tools (`uv`, `ruff`, `mypy`, `pytest`, etc.)
- Cloud services (Cloud Run, Vertex AI, GCP APIs, etc.)

---

## 2. How to Verify

Always use `WebSearch` to confirm the current version **before** writing any code or making a recommendation.

### Packages (PyPI / npm)
```
Search: "site:pypi.org <package-name>" or "<package-name> latest version pypi 2025"
Check:  pypi.org/project/<package-name>/ → "Latest version" field
```

### AI Models and APIs
```
Search: "<provider> latest model <year>" or "<provider> API changelog"
Check:  Official docs — model IDs change frequently (e.g., gemini-2.0-flash, claude-sonnet-4-6)
```

### MCP Servers
```
Search: "<mcp-server-name> mcp server latest version"
Check:  GitHub releases or npm/PyPI page of the server package
```

### Docker Base Images
```
Search: "python docker official image latest stable"
Check:  hub.docker.com/_/python → Tags tab
```

### Cloud APIs / REST Versions
```
Search: "<service> API current version <year>"
Check:  Official API reference for the latest stable endpoint version
```

---

## 3. Rules

1. **Never assume** a version from training memory is current — always verify.
2. **State the version** when recommending: write `google-genai>=1.15.0` not `google-genai`.
3. **Check the migration guide** when upgrading a major version — breaking changes are common in AI SDKs.
4. **Prefer official sources**: pypi.org, npmjs.com, GitHub releases, official docs. Avoid random tutorials.
5. **Check release dates**: if the latest version was released recently, mention it in case the user needs stability.
6. **Note deprecations**: flag deprecated methods or model IDs even if they still work.

---

## 4. This Project's Key Dependencies to Watch

| Dependency | Where Used | Check At |
|---|---|---|
| `google-genai` | `agents/llm_client.py` | Any LLM call change |
| `langchain-core` / `langgraph` | `agents/workflow.py` | Any workflow change |
| `chromadb` | `rag/retrieval.py`, `rag/ingest.py` | Any RAG change |
| `fastapi` | `api/` | Any API change |
| `gradio` | `frontend/app.py` | Any UI change |
| `pydantic` / `pydantic-settings` | `config.py`, all agents | Any model change |
| `uv` (CLI) | `pyproject.toml`, `Dockerfile` | Any dep/build change |
| Gemini model IDs | `config.py` | Any LLM config change |
| Claude model IDs | Any Anthropic SDK usage | Any model reference |

---

## 5. Output Format

When reporting a version check, use this format:

```
✅ <package> — current stable: X.Y.Z (released YYYY-MM-DD)
   Used in: <file>
   Currently pinned: X.Y.Z [up to date / ⚠️ outdated — latest is X.Y.Z]
   Breaking changes since current: <none / describe>
```

---

## 6. Periodic Audit

When running `uv lock --upgrade` or at the start of a new sprint, audit all dependencies in `pyproject.toml` against their current PyPI versions. Report any that are more than one minor version behind.

---

*Apply this skill proactively — version drift is invisible until something breaks in production.*
