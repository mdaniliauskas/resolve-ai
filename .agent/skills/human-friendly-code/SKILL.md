---
name: human-friendly-code
description: Guidelines for generating code that is easy for humans to read, review, navigate, and evolve — especially in AI-assisted development.
---

# Human-Friendly Code — Skill Guide

> "Code is read far more often than it is written." — Guido van Rossum

AI-generated code tends to be verbose, over-abstracted, and hard for humans to navigate.
This skill enforces **simplicity, clarity, and discoverability** so that mid-level and senior developers can quickly understand, review, and evolve the codebase.

---

## 1. Core Principles

### 1.1 Flat over Nested
- **Max 3 levels** of folder depth from the project root.
- Avoid deeply nested structures like `src/modules/core/services/impl/`.
- Prefer **co-location**: keep related files close together.

```
# ❌ Bad — Deep nesting
src/
  modules/
    agents/
      legal/
        services/
          analysis/
            __init__.py
            service.py
            helpers.py

# ✅ Good — Flat and scannable
agents/
  orchestrator.py
  legal_analysis.py
  strategy.py
  response.py
```

### 1.2 Small Files, Single Responsibility
- Target **100–250 lines per file** (hard max: 400 lines).
- Each file should answer: **"What does this file do?"** in one sentence.
- If you can't summarize a file's purpose in one sentence, split it.

### 1.3 Explicit over Clever
- Prefer explicit code even if it's a few lines longer.
- Avoid "magic" patterns (metaclasses, decorator chains, runtime codegen).
- A junior/mid dev should understand the code without reading external docs.

```python
# ❌ Clever but opaque
handler = registry.get(intent, lambda s: s)(**state)

# ✅ Explicit and readable
if intent == "cdc_case":
    result = analyze_legal_case(state)
elif intent == "out_of_scope":
    result = format_out_of_scope_response(state)
else:
    result = format_generic_response(state)
```

### 1.4 Boring Technology
- Use well-known patterns. Avoid novel architectures unless justified.
- Standard library > third-party > custom implementation.
- When using a framework, follow its conventions — don't fight the framework.

### 1.5 Latest Stable Versions
- Always prefer the **latest stable release** of libraries, frameworks, APIs, and tools.
- When adding a dependency, check PyPI / npm for the current version — don't copy old examples.
- When calling external APIs or SDKs, verify the **current recommended patterns** in official docs.
  Old tutorials and Stack Overflow answers often use deprecated methods.
- Pin versions with `>=` in `pyproject.toml` to get latest compatible; rely on `uv.lock` for reproducibility.
- Periodically run `uv lock --upgrade` to pick up patches and minor releases.

---

## 2. File & Folder Structure Rules

### 2.1 Naming
- Use **snake_case** for Python files and folders.
- Use **descriptive nouns** for folders: `agents/`, `api/`, `rag/`.
- Use **descriptive verbs or nouns** for files: `legal_analysis.py`, `ingest_cdc.py`.
- **Avoid generic names**: `utils.py`, `helpers.py`, `misc.py`, `common.py`.
  - If you need shared code, name it by what it does: `text_cleaning.py`, `llm_client.py`.

### 2.2 Structure Template
Every project should have a structure scannable in **under 10 seconds**:

```
project-root/
├── agents/          # One file per agent (max 4-5 files)
├── rag/             # Ingestion + retrieval (max 3-4 files)
├── api/             # FastAPI app + routes (max 3 files)
├── frontend/        # Frontend app
├── data/            # Data files (gitignored binaries)
├── tests/           # Mirrors src structure
├── config.py        # All configuration in one place
├── main.py          # Entry point
├── .env.example
├── pyproject.toml   # Project metadata + dependencies (UV)
└── README.md
```

### 2.3 No Premature Abstractions
- Don't create `interfaces/`, `abstractions/`, or `base_classes/` folders until you have 3+ implementations.
- Don't create separate `models/` folders with one file — keep models co-located.
- Don't create `services/` + `repositories/` + `controllers/` for a simple API.

---

## 3. Code Style Rules

### 3.1 Module Structure
Every Python file follows this order:

```python
"""
Module name — Project Name

What this module does (one sentence).
"""

# 1. Imports (stdlib → third-party → local)
import os
from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter

from config import settings

# 2. Constants
MAX_RETRIES = 3

# 3. Types / Models (Pydantic)
class MyInput(BaseModel):
    """Input for my_function."""
    field: str

class MyOutput(BaseModel):
    """Output of my_function."""
    result: str

# 4. Public functions
async def my_function(input: MyInput) -> MyOutput:
    """One-line description.

    Longer description if needed.
    """
    ...

# 5. Private/helper functions (prefixed with _)
def _helper(text: str) -> str:
    """Explains what the helper does."""
    ...
```

### 3.2 Function Rules
- **Max 30 lines** per function (hard max: 50).
- **Max 4 parameters**. If you need more, use a Pydantic model or dataclass.
- Every public function has a **docstring** (one-liner minimum).
- Return types are **always annotated**.

### 3.3 Naming Rules
- Functions say **what they do**: `analyze_case()`, `format_response()`, `retrieve_chunks()`.
- Variables say **what they contain**: `user_message`, `relevant_chunks`, `analysis_result`.
- Booleans start with `is_`, `has_`, `should_`: `is_cdc_case`, `has_articles`.
- Avoid abbreviations: `msg` → `message`, `ctx` → `context`, `cfg` → `config`.

### 3.4 Comments: When and How
- **Don't** comment what the code does (the code should say that).
- **Do** comment **why** something is done a certain way.
- **Do** add `# TODO:` for known improvements (with context).

```python
# ❌ Redundant comment
# Increment counter by one
counter += 1

# ✅ Useful comment — explains WHY
# CDC articles use "Art." prefix which breaks standard sentence splitting,
# so we use a custom separator list here
separators = ["\n\n", "\n", "Art.", ". "]
```

---

## 4. Error Handling

- **Fail fast, fail clearly.** Don't silently swallow errors.
- Custom exceptions should explain what went wrong in human terms.
- Use `logging` (never `print()`).

```python
# ❌ Silent failure
try:
    result = call_llm(prompt)
except Exception:
    result = ""  # What happened? Nobody knows.

# ✅ Clear failure
try:
    result = call_llm(prompt)
except TimeoutError:
    logger.warning("LLM call timed out after 10s, returning fallback")
    raise LLMTimeoutError("The AI model took too long to respond. Please try again.")
```

---

## 5. Configuration

- **One config source**: a single `config.py` that reads from `.env`.
- Don't scatter `os.getenv()` calls across the codebase.

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """All app configuration. Loaded from .env file."""

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    chroma_persist_dir: str = "./data/chroma_db"
    api_port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6. Testing Rules

- Test files **mirror source structure**: `agents/legal_analysis.py` → `tests/test_legal_analysis.py`.
- Tests have **descriptive names**: `test_identifies_defective_product_as_cdc_case`.
- Each test has a **one-line docstring** explaining the scenario.
- **Mock external calls** (LLM, APIs), but **don't mock the business logic**.

---

## 7. Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Do Instead |
|---|---|---|
| `utils.py` catch-all | Grows into unmaintainable junk drawer | Name files by purpose |
| Abstract base classes for 1 implementation | Adds complexity with zero benefit | Just write the class; abstract later |
| `**kwargs` everywhere | Hides the actual interface | Explicit parameters or Pydantic model |
| 10-level folder nesting | Takes forever to navigate | Keep it flat (max 3 levels) |
| 500+ line files | Impossible to review quickly | Split by responsibility |
| Decorator chains | Invisible behavior, hard to debug | Explicit function calls |
| Runtime type checking + coercion | Surprising behavior | Pydantic validation at boundaries |
| Wrapper classes that just delegate | Extra indirection for nothing | Call the dependency directly |

---

## 8. Checklist Before Every File Change

- [ ] Can I explain this file's purpose in **one sentence**?
- [ ] Is the file **under 250 lines**?
- [ ] Can a mid-level dev understand this **without external documentation**?
- [ ] Are function names **self-explanatory**?
- [ ] Are there **no `utils.py` or `helpers.py`** catch-all files?
- [ ] Does the folder structure stay at **max 3 levels deep**?
- [ ] Did I avoid creating unnecessary abstractions?

---

## 9. Language-Specific Notes

### Python
- Use **[UV](https://docs.astral.sh/uv/)** as the package and environment manager (`uv sync`, `uv add`, `uv run`).
  - `pyproject.toml` is the single source of truth for dependencies — no `requirements.txt`.
  - Commit `uv.lock` to ensure reproducible installs across machines.
- Use **type hints** on all function signatures.
- Use **Pydantic** for data validation at I/O boundaries.
- Use **`async/await`** for I/O-bound operations (LLM calls, DB queries).
- Use **`ruff`** for linting, **`mypy`** for type checking.

### TypeScript/JavaScript (Frontend)
- Use **TypeScript** with strict mode enabled.
- Prefer **named exports** over default exports.
- Keep components under **150 lines**. Extract sub-components early.
- Use **CSS Modules** or **Vanilla CSS** — avoid utility-class frameworks unless explicit.

---

*This skill is applied automatically to every code generation and review task. The goal is to produce code that a human developer can understand in one reading pass.*
