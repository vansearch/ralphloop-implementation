# Ralph Loop

An autonomous development loop that drives itself from a task checklist — with context-aware doc routing, security audits, and self-directed planning.

## What it does

The Ralph Loop is an agentic coding pattern where an AI agent:

1. Picks the next pending task from `TASKS.md`
2. Reads **only the relevant documentation sections** for that task (not all docs)
3. Implements the task
4. Verifies via build/test commands
5. Marks the task done and loops
6. When tasks run out → runs a **security audit** (reviews the plan for risks)
7. Then enters **planning mode** (reads PRD + git history, generates new tasks)
8. Continues until planning finds nothing more to do

The key innovation is **doc routing** — a `DOC-INDEX.md` maps each task ID to specific doc file+section pairs, reducing per-iteration context by ~95%.

## Files

| File | Purpose |
|------|---------|
| `ralph.py` | Main loop script — runs autonomously |
| `setup.py` | Scaffolding script — bootstraps a new project |
| `templates/` | Ready-to-use file templates |
| `SKILL.md` | Claude Code slash command (`/ralphloop-implementation`) |

## Quick start

### Option 1 — Use the Claude Code skill

In any project, run:

```
/ralphloop-implementation
```

This activates a Claude Code skill that audits your project and creates all the Ralph Loop files automatically.

### Option 2 — Use setup.py directly

```bash
# Download both scripts to your project root
curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/ralph.py
curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/setup.py

# Run the scaffolder (interactive)
python setup.py

# Or pass args directly
python setup.py --name "My Project" --lang swift

# Start the loop
python ralph.py --dry-run   # preview first task
python ralph.py --status    # show progress
python ralph.py             # run autonomously
```

### Option 3 — Manual install

1. Copy `ralph.py` to your project root
2. Create `TASKS.md` (see `templates/TASKS.md`)
3. Create `docs/DOC-INDEX.md` (see `templates/docs/DOC-INDEX.md`)
4. Create `.ralph/` directory with `guardrails.md` and `progress.md`
5. Add `.gitignore` entries (see `templates/.gitignore`)

## CLI reference

```
python ralph.py                     # run the loop (parallel + planning)
python ralph.py --dry-run           # preview next task/batch and prompt
python ralph.py --status            # show progress summary
python ralph.py --task E2-T3        # run a specific task only (sequential)
python ralph.py --reset             # clear .ralph/ state and start fresh
python ralph.py --no-plan           # disable planning mode (finite, tasks only)
python ralph.py --no-parallel       # force sequential mode (disable parallel)
python ralph.py --max-parallel 8    # allow up to 8 concurrent workers
```

## Parallel execution

Add `[parallel]` to an epic header to run its tasks concurrently:

```markdown
## Epic 2 — Scanners [parallel]

- [ ] **E2-T1** Implement AppCacheScanner
- [ ] **E2-T2** Implement SystemCacheScanner
- [ ] **E2-T3** Implement LogsScanner
```

The orchestrator:
1. Creates a git worktree per task (`.ralph/worktrees/E2-T1/`, etc.)
2. Runs all workers simultaneously with prefixed output (`[E2-T1] ...`, `[E2-T2] ...`)
3. Merges successful branches sequentially into the main tree
4. Runs `VERIFY_STEPS` once on the merged state
5. Marks all passing tasks done; reverts and re-queues failed ones

Tasks in different epics are always sequential. Only tasks within the same `[parallel]` epic run concurrently. Use `[parallel]` for independent tasks that don't modify the same files.

## Generated file structure

After running `setup.py` or the skill:

```
your-project/
├── ralph.py             ← the loop
├── setup.py             ← scaffolder (optional, remove after setup)
├── TASKS.md             ← task checklist
├── docs/
│   ├── DOC-INDEX.md     ← routing table (task → doc sections)
│   ├── PRD.md           ← product requirements
│   └── ARCHITECTURE.md  ← architecture notes
└── .ralph/
    ├── guardrails.md    ← learned failure patterns (commit this)
    ├── progress.md      ← run history (.gitignore)
    ├── activity.log     ← debug log (.gitignore)
    └── security-report.md  ← audit output (.gitignore)
```

## TASKS.md format

```markdown
# Project Name — Task List (Ralph Loop)

## Epic 1 — Foundation

- [ ] **E1-T1** Create the package structure
- [ ] **E1-T2** Add core dependencies
- [x] **E1-T3** Write initial unit test scaffold   ← done

## Epic 2 — Scanners [parallel]

<!-- Tasks run concurrently — each gets its own git worktree -->
- [ ] **E2-T1** Implement AppCacheScanner
- [ ] **E2-T2** Implement SystemCacheScanner
- [ ] **E2-T3** Implement LogsScanner
```

## DOC-INDEX.md format

```
## Routing Table

```
# Epic 1 — Foundation
E1-T1 | ARCHITECTURE.md:Package Structure | PRD.md:Goals
E1-T2 | ARCHITECTURE.md:Dependencies

# Epic 2 — Core
E2-T1 | ARCHITECTURE.md:Core Components | DATA-MODELS.md:UserEntity
```
```

## Adapt VERIFY_STEPS

In `ralph.py`, set `VERIFY_STEPS` for your tech stack:

```python
# Swift
VERIFY_STEPS = [
    ("swift build", ["swift", "build", "-c", "debug"]),
    ("swift test",  ["swift", "test"]),
]

# TypeScript / Bun
VERIFY_STEPS = [
    ("bun build", ["bun", "run", "build"]),
    ("bun test",  ["bun", "test"]),
]

# Python / uv
VERIFY_STEPS = [
    ("pytest", ["uv", "run", "pytest"]),
]

# Rust
VERIFY_STEPS = [
    ("cargo build", ["cargo", "build"]),
    ("cargo test",  ["cargo", "test"]),
]
```

## Security audit gate

After the first plan's tasks complete, the loop automatically reviews the completed task descriptions for security risks. It:

1. Loads content from `SECURITY_SKILL_PATHS` (existing security skills/scripts)
2. Sends the completed task plan to Claude acting as a security auditor
3. Saves the report to `.ralph/security-report.md`
4. Generates `SEC-Tx` fix tasks for CRITICAL/HIGH risks
5. Executes fixes before entering planning mode

Disable with `--no-security`. Run standalone with `--security-only`.

## Security mitigations in ralph.py

The loop includes 6 security hardening measures to prevent prompt injection and other attacks:

1. `sanitize_for_prompt()` — strips shell metacharacters from task descriptions
2. Path traversal guard — blocks `../` escape from `docs/` in doc routing
3. Guardrails sanitization — strips markdown headings from `.ralph/guardrails.md` reads
4. Data block wrapping — wraps `git log` and file tree output in fenced blocks
5. Output cap — limits planning output to 500KB to prevent disk exhaustion
6. `sanitize_guardrail()` — sanitizes failure summaries before writing to guardrails

## Releases

| Tag | Description |
|-----|-------------|
| [v1.2.0](https://github.com/vansearch/ralphloop-implementation/releases/tag/v1.2.0) | Parallel orchestrator: git worktrees, ThreadPoolExecutor, `[parallel]` tag |
| [v1.1.0](https://github.com/vansearch/ralphloop-implementation/releases/tag/v1.1.0) | Full restore: ralph.py, setup.py, templates, README |
| [v1.0.0](https://github.com/vansearch/ralphloop-implementation/releases/tag/v1.0.0) | Initial stable release (SKILL.md only) |

## Install the Claude Code skill

```bash
# Clone the skill into your Claude skills directory
git clone https://github.com/vansearch/ralphloop-implementation \
    ~/.claude/skills/ralphloop-implementation

# Then in any project:
/ralphloop-implementation
```
