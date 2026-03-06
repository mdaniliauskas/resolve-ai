---
name: dev-journal
description: Auto-feed the 3 study files in estudos/ after each development session
---

# Dev Journal — Automatic Study Notes

## Purpose

After each development session (or when the user requests), update the 3 study files
in `estudos/` to help the developer learn and prepare for technical interviews.

## When to Trigger

Update these files:
1. **At the end of each sprint or major milestone** (e.g., after committing a feature)
2. **When the user explicitly asks** to update study notes
3. **When a significant problem was solved** — log it immediately in learnings

## Files to Update

### 1. `estudos/sprintN_summary.md` — Quick Walkthrough (Senior → Junior)

**Tone:** Senior developer explaining to a learning junior developer.
**Format:** One section per step/feature, each with:
- **What:** What was built (1-2 sentences)
- **Why:** Why this approach (1-2 sentences)
- **Senior tip:** One practical insight the junior wouldn't know

Keep it **concise** — max 2 pages. This is a summary, not a textbook.
Create a new file for each sprint (sprint1_summary.md, sprint2_summary.md, etc.).

### 2. `estudos/sprintN_deep_dive.md` — Detailed Study Guide

**Tone:** Technical reference for studying and interview prep.
**Format:** Organized by concept/technology, each section includes:
- Clear definition with example
- Code snippets from the actual project (not generic)
- "Interview question" + "Answer" pairs
- Comparison tables (e.g., RAG vs fine-tuning, ChromaDB vs Pinecone)
- Vocabulary/glossary of key terms

**Goal:** If the developer reads this before a technical interview, they can explain
every architectural decision with confidence.
Create a new file for each sprint (sprint1_deep_dive.md, sprint2_deep_dive.md, etc.).

### 3. `estudos/learnings_log.md` — Troubleshooting War Stories (APPEND ONLY)

**Tone:** Honest engineering log — what went wrong and how it was fixed.
**Format:** Each entry uses the L-NNN pattern:

```markdown
### L-NNN: [Short title]

**Problem:** What happened (observable symptom).
**Root cause:** Why it happened (technical explanation).
**How I identified it:** Debugging steps taken.
**Fix:** Code diff or configuration change.
**Lesson:** General principle to remember.
```

**This file is cumulative** — never delete old entries. Number entries sequentially
across sprints (L-001, L-002, ..., L-015, etc.).

## Rules

1. **Use real code from the project** — not generic examples.
2. **estudos/ is in .gitignore** — these are private notes, not project docs.
3. **Write in English** (matching the codebase), but the developer understands pt-BR.
4. **Include interview angles** in the deep dive — "How would you explain this?"
5. **Every error/bug/surprise goes in learnings_log.md** — even small ones.
6. The summary and deep_dive are **per-sprint**; the learnings_log is **one file, append-only**.
