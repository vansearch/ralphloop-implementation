# Skill: ralphloop-implementation

Activate with `/ralphloop-implementation` to bootstrap a complete Ralph Loop
scaffolding for any new project.

---

## What this skill does

1. Audits the project to understand its tech stack and existing structure
2. Creates `TASKS.md` — flat checkbox task list the loop will consume
3. Creates `docs/DOC-INDEX.md` — semantic routing table (task → doc sections)
4. Creates `ralph.py` — autonomous development loop with **self-directed planning**
5. Creates `.ralph/` state directory (guardrails.md, progress.md)
6. Creates `.gitignore` entries for generated state files
7. **Runs a security audit gate** after each task batch completes — routes to
   existing security skills/scripts, scans for vulnerabilities, and generates
   fix tasks before planning the next batch

The loop is **continuous by design**: when the **first plan's** task list runs
out, it runs a **security audit** of the completed plan (routed through existing
vulnerability-scanner / security-auditor skills), then enters planning mode —
reads the PRD + git history + source tree, generates the next batch of tasks,
and keeps going. The security audit only runs once (after the initial plan),
not after every planning round.

---

## Prompt

You are setting up the **Ralph Loop** autonomous development workflow for this project.

The Ralph Loop is an agentic coding pattern where an AI agent:
1. Picks the next pending task from a checklist (`TASKS.md`)
2. Reads **only the relevant documentation sections** for that task (not all docs)
3. Implements the task
4. Verifies via build/test commands
5. Marks the task done and loops
6. **When tasks run out → runs a security audit** (routes to security skills)
7. **Then enters planning mode** (reads PRD, generates new tasks)
8. Continues indefinitely until planning finds nothing more to do

The key innovation is **doc routing** — a `DOC-INDEX.md` mapping each task ID
to specific documentation file+section pairs, reducing context by ~95% per iteration.

The **security gate** ensures every batch of work is audited for vulnerabilities
before the loop moves on. It references existing security skills and scripts as
routing targets.

---

## Step 1 — Audit the project

Before creating any files, read:
- The project root (`ls`, `README.md`, `CLAUDE.md` if present)
- Existing documentation (any `docs/` directory)
- The tech stack (package.json, Package.swift, pyproject.toml, Cargo.toml, etc.)

Answer these questions to yourself:
- What language/runtime is this project? (Swift, Python, TypeScript, Rust, etc.)
- What are the verification commands? (`swift build && swift test`, `bun test`, `cargo test`, etc.)
- Does a task list already exist? (TASKS.md, TODO.md, GitHub Issues, Linear, etc.)
- Does a docs directory already exist with structured documentation?

---

## Step 2 — Create or validate `TASKS.md`

The task file must follow this exact format:

```markdown
# <Project Name> — Task List (Ralph Loop)

> Format: `- [ ] **EPIC-TASK** Description`
> The ralph.py script reads this file to drive the loop.
> Mark tasks done with `[x]` — or let the agent do it automatically.
> Add `[parallel]` to an epic header to run its tasks concurrently.

---

## Epic 1 — Foundation

- [ ] **E1-T1** <Task description — specific and actionable>
- [ ] **E1-T2** <Task description>

## Epic 2 — <Feature Name> [parallel]

<!-- Tasks in a [parallel] epic run concurrently via git worktrees.
     Use for independent tasks that don't touch the same files. -->
- [ ] **E2-T1** <Independent task A>
- [ ] **E2-T2** <Independent task B>
- [ ] **E2-T3** <Independent task C>
```

Rules for tasks:
- Each task should be implementable in **one coding session** (< 2 hours)
- Task descriptions must be **specific and verifiable** (not "improve the code")
- Tasks within an epic should be **independent** (minimal interdependence)
- Epics map to logical feature areas (Foundation, Core Engine, CLI, UI, etc.)
- Use IDs like `E1-T1`, `E2-T3` — never use dots or spaces in IDs
- Add `[parallel]` to an epic header to run its tasks concurrently (good for scanners, handlers, plugins — things that are independent and don't share files)

If a task list already exists in another format, convert it to this format.

---

## Step 3 — Create `docs/DOC-INDEX.md`

This is the core token-saving mechanism. It maps each task ID to the **exact
documentation sections** the agent needs for that task — nothing more.

Format:

```markdown
# Doc Index — Context Router for Ralph Loop

> This file is read by `ralph.py` to determine which documentation
> sections each task needs. The agent reads ONLY the listed sections.
>
> Format per task:
>   TASK_ID | file:section | file:section | ...
>
> Sections use the heading text after `##` in each doc file.

---

## Routing Table

\`\`\`
# Epic 1 — Foundation
E1-T1 | ARCHITECTURE.md:Package Structure | TECH-STACK.md:Build System
E1-T2 | TECH-STACK.md:Dependencies
E1-T3 | CONTRIBUTING.md:Running Tests

# Epic 2 — Core Feature
E2-T1 | ARCHITECTURE.md:Core Components | DATA-MODELS.md:MainEntity
\`\`\`
```

Rules for the routing table:
- Every task in `TASKS.md` must have an entry here
- Use at most **2-3 sections per task** — more is waste
- Section names must match exactly the `## Section Name` headings in the docs
- If no docs exist yet, use `ARCHITECTURE.md:Overview` as a placeholder

---

## Step 3.5 — Security Skill Routing Paths

The Ralph Loop acts as a **router** to existing security skills when the
security audit gate triggers. Update the `SECURITY_SKILL_PATHS` dict in
`ralph.py` to match the project's agent/skill layout.

Default paths (adapt if your project uses a different structure):

```python
SECURITY_SKILL_PATHS = {
    # Core security analysis
    "vulnerability-scanner": ".agent/skills/vulnerability-scanner/SKILL.md",
    "security-scan-script":  ".agent/skills/vulnerability-scanner/scripts/security_scan.py",
    "security-checklist":    ".agent/skills/vulnerability-scanner/checklists.md",
    # Agent-level security
    "security-auditor":      ".agent/security-auditor.md",
    # Additional skills (optional — uncomment if available)
    # "red-team-tactics":    ".agent/skills/red-team-tactics/SKILL.md",
    # "senior-security":     ".agents/skills/senior-security/SKILL.md",
    # "senior-secops":       ".agents/skills/senior-secops/SKILL.md",
}
```

The security audit prompt includes the content of reachable skills so the
auditing agent has expert-level security context without needing to read
the entire skill tree.

---

## Step 4 — Add `ralph.py` and `setup.py` to your project

### Option A — Use setup.py (recommended for new projects)

The scaffolding script creates `TASKS.md`, `docs/`, `.ralph/`, and `.gitignore`
entries automatically:

```bash
curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/ralph.py
curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/setup.py
python setup.py --name "<Your Project Name>" --lang <swift|ts|python|rust>
```

### Option B — Copy ralph.py manually

```bash
curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/ralph.py
```

Then adapt `VERIFY_STEPS` in `ralph.py` to your tech stack (see the commented
examples at the top of the file for Swift, TypeScript, Python, and Rust).

> Full source: https://github.com/vansearch/ralphloop-implementation/blob/main/ralph.py

### What ralph.py contains

The production loop includes 6 security hardening measures:
- `sanitize_for_prompt()` — strips shell metacharacters from task descriptions
- Path traversal guard — blocks `../` escape from `docs/` in doc routing
- Guardrails sanitization — strips headings from `.ralph/guardrails.md` reads
- Data block wrapping — wraps `git log` / file tree in fenced blocks
- Output cap — limits planning output to 500 KB
- `sanitize_guardrail()` — sanitizes failure summaries before writing to guardrails

**CLI flags:**
```
python ralph.py               # run the loop
python ralph.py --dry-run     # preview next task and prompt
python ralph.py --status      # show progress summary
python ralph.py --task E2-T3  # run a specific task
python ralph.py --reset       # clear .ralph/ state
python ralph.py --no-plan     # disable planning mode
python ralph.py --no-security # disable security audit gate
python ralph.py --security-only  # run audit without executing tasks
```

---

## Step 5 — Create `.ralph/` state directory

Create these two files manually (they are also auto-created by `ralph.py`):

**`.ralph/guardrails.md`:**
```markdown
# Guardrails — Learned Patterns

> Append-only. The Ralph Loop reads this file each iteration to avoid
> repeating past mistakes. Format: [date] TASK-ID: description of failure.

<!-- entries added automatically by ralph.py on task failure -->
```

**`.ralph/progress.md`:**
```markdown
# Progress Log

> Append-only. Records pass/fail for every task attempt.
> ralph.py appends to this file — do not edit manually.

<!-- entries added automatically by ralph.py -->
```

---

## Step 6 — Add `.gitignore` entries

Add to `.gitignore` (do NOT commit generated state):

```
# Ralph Loop state
.ralph/activity.log
.ralph/current_prompt.md
.ralph/progress.md
.ralph/security-report.md
```

Commit `guardrails.md` to share learned failure patterns with the team.

---

## Step 7 — Verify the setup

Run these checks and confirm all pass:

```bash
# 1. Show status (should show task list with 0% done)
python ralph.py --status

# 2. Preview next task without running agent
python ralph.py --dry-run

# 3. Preview a specific task
python ralph.py --task E1-T1 --dry-run
```

The `--dry-run` output should show:
- Task ID and description
- Relevant doc sections extracted (not the full docs)
- Token estimate (should be under ~2,000 for most tasks)
- Context reduction % vs full docs

---

## Architecture Notes

### Why doc routing saves tokens

Every Ralph Loop iteration starts fresh (clean context). Without routing:
- Agent reads all docs → ~15,000–90,000 chars per iteration
- For 80 tasks: up to 7.2M chars total context loaded

With routing:
- Agent reads 1–2 doc sections → ~500–2,000 chars per iteration
- For 80 tasks: ~120,000 chars total — **~97% reduction**

### The loop structure

```
while tasks_remain:
    task = next_pending_task()
    context = extract_doc_sections(task.id)  ← only relevant sections
    prompt = build_prompt(task, context)
    output = run_agent(prompt)
    if verify():
        mark_done(task.id)
    else:
        save_guardrail(failure_summary)
        pause_for_human_review()
```

### Security Audit Gate — plan review after first batch

After the **first plan's** tasks all complete, the loop runs a **security
audit gate** once. It reviews the completed plan (task descriptions) for
security risks — it does NOT scan individual source files.

```
loop:
    task = get_next_task()
    if task is None and not security_audit_done:
        security_audit_done = True
        run_security_audit()   ← review plan for security risks
        if fix_tasks_generated:
            continue           ← execute security fixes first
    … planning mode / normal execution …
```

**How it works:**
1. Loads content from `SECURITY_SKILL_PATHS` — existing security skills and checklists
2. Builds a prompt with the completed task plan from `TASKS.md`
3. Sends to Claude acting as a security auditor agent
4. Agent reviews which tasks could introduce vulnerabilities based on descriptions
5. Saves report to `.ralph/security-report.md`
6. Generates `SEC-TX` fix tasks for CRITICAL/HIGH risks → appends to `TASKS.md`
7. Loop executes fix tasks before entering planning mode

**Key:** The audit analyzes the **plan**, not the project files. This keeps it
fast and focused on architectural/design-level security concerns.

**Skill routing:** The audit prompt includes content from existing security
skills (vulnerability-scanner, security-auditor, etc.) for expert context.

**Flags:**
- `--no-security` — disable the audit gate entirely
- `--security-only` — run just the audit without executing any tasks

### Planning Mode — continuous self-direction

When all tasks are done and the security audit passes, the loop enters
**planning mode**. Planning reads context and writes new tasks directly
into `TASKS.md`, then continues immediately — making the loop perpetually
self-directed.

```
loop:
    task = get_next_task()
    if task is None:
        security_audit()        ← security gate first
        if planning_rounds >= MAX_PLANNING_ROUNDS:
            break               ← safety stop
        new_count = run_planning_mode()
        if new_count == 0:
            break               ← planning exhausted, nothing more to do
        reload routing          ← DOC-INDEX may have been updated
        continue                ← go back to top with new tasks
    … normal task execution …
```

**What the planning prompt includes:**
- Full PRD content (first 5,000 chars of `docs/PRD.md`)
- `git log --oneline -40` — what has been built so far
- `find Sources Tests -name "*.swift"` — current source tree
- `swift test --list-tests` — what's tested
- Summary of all done tasks

**What the planning prompt asks agent to do:**
1. Append new `[ ] E{n}-T{n}: …` tasks to `TASKS.md`
2. Update `docs/DOC-INDEX.md` with routing entries for new tasks
3. `git commit -m "Plan: add next tasks"`
4. Print `PLANNING_DONE: N new tasks added` on the last line

**Safety guards:**
- `MAX_PLANNING_ROUNDS = 5` — stops if planning stalls (no real progress)
- Zero new tasks from planning → loop exits cleanly
- `--no-plan` flag disables planning entirely (finite mode, original behavior)

### When to run autonomously vs manually

Run fully autonomously (`python ralph.py`):
- Deterministic tasks with clear acceptance criteria
- Tasks with working verification (build + test)
- Tasks where failure is caught by tests

Run with `--task ID` for manual control:
- First few tasks to validate the setup
- After failures requiring human investigation
- Tasks touching external APIs or auth

Run security only (`python ralph.py --security-only`):
- Quick security check without executing tasks
- After manual code changes outside the loop
- Before merging or deploying

---

## Common Mistakes

1. **doc routing sections don't match actual headings** — run `--dry-run` and
   check for `[Section '...' not found]` in the output. Fix by matching the
   exact `## Heading` text in the doc file.

2. **VERIFY_STEPS is empty** — the loop will mark tasks done without verifying.
   Always configure at least one verify command.

3. **Tasks are too broad** — "Implement the entire scanner engine" will fail.
   Break into specific tasks: "Implement UserCacheScanner scanning ~/Library/Caches".

4. **Missing `@main` or entry point** — for Swift/TypeScript, ensure the CLI
   target has a proper entry point before running loop tasks that depend on it.

5. **Numbered doc headings** — if docs use `## 2. Section Name` but the routing
   table lists `Section Name`, the extractor handles this automatically via the
   `(?:\d+[\.\d]*\s+)?` prefix pattern.

6. **SECURITY_SKILL_PATHS not updated** — if your project uses a non-standard
   layout, update the paths dict in ralph.py. Missing skill files are skipped
   gracefully but reduce audit quality.
