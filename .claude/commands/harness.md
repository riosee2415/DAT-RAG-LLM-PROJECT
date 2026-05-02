# /harness — Full-Stack Development Orchestrator

Operate fully autonomously. Zero clarifying questions. Every decision is yours to make.

## Invocation
```
/harness <task description>
```

---

## Phase 0 — Parse & Contract Definition

### 0.1 Decompose the Task
Read `CLAUDE.md` (root). Break the task into:
- **Frontend deliverables**: pages, components, forms, client state, UX flows
- **Backend deliverables**: API endpoints, services, DB schema changes, background jobs
- **Shared contract**: the exact interface between the two layers

### 0.2 Write the API Contract
Before any agent spawns, produce a contract document and hold it in memory:

```
CONTRACT
========
Endpoints:
  POST /api/v1/<resource>
    Request:  { field: type, ... }
    Response: { field: type, ... }
    Status:   201 | 400 | 422

Supabase tables affected:
  <table_name>: { column: type (constraints) }

Shared TypeScript / Pydantic types:
  <TypeName> { ... }
```

This contract is injected verbatim into both agent prompts. Neither agent may deviate.

If the task is purely frontend OR purely backend, skip the contract step and go straight to Phase 1 with a single agent.

---

## Phase 1 — Parallel Implementation

Spawn both sub-agents **in a single Agent tool call** (two blocks in parallel):

### Frontend Sub-Agent Config
```
subagent_type: "general-purpose"
isolation: "worktree"
prompt: |
  Read frontend/CLAUDE.md before touching any file.
  Scope: ONLY modify files under frontend/.
  
  Task: [frontend deliverables from Phase 0]
  
  API Contract (implement against this exactly):
  [contract from Phase 0.2]
  
  On completion, output:
  - List of files created/modified
  - Test coverage summary
  - Any deviations from the contract (must be justified)
```

### Backend Sub-Agent Config
```
subagent_type: "general-purpose"
isolation: "worktree"
prompt: |
  Read backend/CLAUDE.md before touching any file.
  Scope: ONLY modify files under backend/.
  
  Task: [backend deliverables from Phase 0]
  
  API Contract (implement against this exactly):
  [contract from Phase 0.2]
  
  On completion, output:
  - List of files created/modified
  - Test results (pytest summary)
  - Any deviations from the contract (must be justified)
```

---

## Phase 2 — Parallel Code Review

When both Phase 1 agents complete, spawn two reviewers **in a single parallel call**:

### Review Prompt Template
```
You are a senior code reviewer. Review the following changed files strictly against 
the checklist below. Do not be lenient. Return either:

  APPROVED
  
or

  REJECTED
  Reason: <specific issue>
  File: <path>
  Line: <number>
  Fix: <concrete change required>

Checklist:
- [ ] TypeScript: no `any`, no type assertions without justification
- [ ] Python: full mypy --strict compliance, no untyped functions
- [ ] No bare except / swallowed errors
- [ ] Every new endpoint/component has tests
- [ ] API contract compliance (see contract below)
- [ ] No hardcoded secrets, tokens, URLs
- [ ] Security: auth guards present, no SQL injection, no XSS sinks
- [ ] No N+1 queries; async I/O used correctly
- [ ] Conventional commit message format

Contract: [inject contract from Phase 0]
Changed files: [list from agent output]
```

### Review Loop
- **APPROVED** → proceed to Phase 3
- **REJECTED** → re-invoke the specific working sub-agent with the exact reviewer output
  - Max 3 re-runs per agent
  - On 4th failure: stop, output the reviewer's final report, ask user for guidance

---

## Phase 3 — CI Gate (via Hook)

The Stop hook (`.claude/hooks/tdd-and-push.ps1`) fires automatically when this command ends.

It runs the following gates in strict order per changed layer:

| Gate | Frontend | Backend |
|------|----------|---------|
| 1 — Lint | `eslint --max-warnings 0` | `ruff check` |
| 2 — Type | `tsc --noEmit` | `mypy --strict` |
| 3 — Tests | `vitest run --coverage` | `pytest --cov --cov-fail-under=80` |
| 4 — Build | `next build` | — |

- All gates pass → commit (conventional format) + push to `web` / `ai`
- Any gate fails → output full gate report, re-enter Phase 1 with gate failure as context

---

## Phase 4 — Summary Report

After successful push, output exactly:

```
HARNESS COMPLETE
================
Built:
  • [feature 1 — 1 sentence]
  • [feature 2 — 1 sentence]

Gates:
  Frontend: lint ✓ | types ✓ | tests ✓ (coverage: X%) | build ✓
  Backend:  lint ✓ | types ✓ | tests ✓ (coverage: X%)

Commits:
  web  ← feat(frontend): <subject>
  ai   ← feat(backend): <subject>
```

---

## Phase 4 — Work Rule Self-Update

After every successful commit/push, spawn a single sub-agent to update the work rules:

```
subagent_type: "general-purpose"
prompt: |
  Run the /update-work-rules command.
  
  Context: The following task just completed and was committed:
  - Task: [task description from Phase 0]
  - Frontend files changed: [list from Phase 1 agent output]
  - Backend files changed: [list from Phase 1 agent output]  
  - Review iterations: [count from Phase 2]
  - Any repeated failures or patterns: [from Phase 2 feedback]
  
  Update work_rule.md files to reflect this task's learnings.
  Output only: "Updated: [file] [+N lines]" for each modified file.
```

This sub-agent does NOT use worktree isolation (it writes to the live tree).
Its changes are included in the next git operation or committed separately with message:
`chore(harness): refresh work_rule.md [date]`

---

## Invariants (Never Break These)
- `harness_commands/` is never referenced at any phase
- Worktree isolation is always `isolation: "worktree"` for implementation agents
- Code review is never skipped, even for "small" changes
- A failed gate is never bypassed — fix and re-run
