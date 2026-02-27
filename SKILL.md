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

---

## Epic 1 — <Epic Name>

- [ ] **E1-T1** <Task description — specific and actionable>
- [ ] **E1-T2** <Task description>
```

Rules for tasks:
- Each task should be implementable in **one coding session** (< 2 hours)
- Task descriptions must be **specific and verifiable** (not "improve the code")
- Tasks within an epic should be **independent** (minimal interdependence)
- Epics map to logical feature areas (Foundation, Core Engine, CLI, UI, etc.)
- Use IDs like `E1-T1`, `E2-T3` — never use dots or spaces in IDs

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

## Step 4 — Create `ralph.py`

Create the following Python script. **Adapt the `VERIFY_STEPS` list to match
the project's tech stack** (Swift, Python, TypeScript, etc.).

```python
#!/usr/bin/env python3
"""
ralph.py — Ralph Loop for <Project Name>
=========================================
Autonomous development loop.

Key feature: context-aware doc routing.
Reads ONLY the documentation sections relevant to the current task.

Usage:
    python ralph.py               # run the loop
    python ralph.py --dry-run     # preview next task and prompt
    python ralph.py --status      # show progress summary
    python ralph.py --task E2-T3  # run a specific task
    python ralph.py --reset       # clear .ralph/ state

Requirements:
    - claude CLI installed and authenticated
    - Project build tools available (swift, bun, cargo, uv, etc.)
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent
TASKS_FILE   = ROOT / "TASKS.md"
DOC_INDEX    = ROOT / "docs" / "DOC-INDEX.md"
DOCS_DIR     = ROOT / "docs"
RALPH_DIR    = ROOT / ".ralph"
PROGRESS_FILE  = RALPH_DIR / "progress.md"
GUARDRAILS_FILE = RALPH_DIR / "guardrails.md"
ACTIVITY_LOG   = RALPH_DIR / "activity.log"
PROMPT_FILE    = RALPH_DIR / "current_prompt.md"
SECURITY_REPORT = RALPH_DIR / "security-report.md"

# ── !! ADAPT THIS TO YOUR PROJECT !! ───────────────────────────────────────
# Each tuple: (label, command_list)
# All must pass (exit 0) before a task is marked done.
VERIFY_STEPS = [
    # Swift:
    # ("swift build", ["swift", "build", "-c", "debug"]),
    # ("swift test",  ["swift", "test"]),
    #
    # TypeScript/Bun:
    # ("bun build",  ["bun", "run", "build"]),
    # ("bun test",   ["bun", "test"]),
    #
    # Python/uv:
    # ("uv run pytest", ["uv", "run", "pytest"]),
    #
    # Rust:
    # ("cargo build", ["cargo", "build"]),
    # ("cargo test",  ["cargo", "test"]),
]
# ───────────────────────────────────────────────────────────────────────────

# ── SECURITY SKILL ROUTING ─────────────────────────────────────────────────
# Paths to existing security skills/scripts that the audit phase routes to.
# The audit prompt loads content from reachable files to give the security
# agent expert-level context. Adapt paths to your project layout.
SECURITY_SKILL_PATHS = {
    "vulnerability-scanner": ".agent/skills/vulnerability-scanner/SKILL.md",
    "security-scan-script":  ".agent/skills/vulnerability-scanner/scripts/security_scan.py",
    "security-checklist":    ".agent/skills/vulnerability-scanner/checklists.md",
    "security-auditor":      ".agent/security-auditor.md",
    # "red-team-tactics":    ".agent/skills/red-team-tactics/SKILL.md",
    # "senior-security":     ".agents/skills/senior-security/SKILL.md",
}
SECURITY_AUDIT_ENABLED = True
# ───────────────────────────────────────────────────────────────────────────

MAX_ITERATIONS       = 60
MAX_RETRIES_PER_TASK = 3

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ══════════════════════════════════════════════════════════════════════════════
# TASK PARSING
# ══════════════════════════════════════════════════════════════════════════════

def parse_tasks(path: Path = TASKS_FILE) -> list[dict]:
    tasks = []
    pattern = re.compile(r"^- \[([ x])\] \*\*(\w+-\w+)\*\* (.+)$")
    for line in path.read_text().splitlines():
        m = pattern.match(line.strip())
        if m:
            tasks.append({
                "done": m.group(1) == "x",
                "id":   m.group(2),
                "desc": m.group(3).strip(),
            })
    return tasks


def get_next_task(tasks: list[dict], specific_id: str | None = None) -> dict | None:
    if specific_id:
        return next((t for t in tasks if t["id"] == specific_id), None)
    return next((t for t in tasks if not t["done"]), None)


def mark_task_done(task_id: str):
    content = TASKS_FILE.read_text()
    TASKS_FILE.write_text(
        content.replace(f"- [ ] **{task_id}**", f"- [x] **{task_id}**")
    )


# ══════════════════════════════════════════════════════════════════════════════
# DOC ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def parse_doc_index(path: Path = DOC_INDEX) -> dict[str, list[tuple[str, str]]]:
    routing: dict[str, list[tuple[str, str]]] = {}
    in_code_block = False
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block or stripped.startswith("#") or not stripped:
            continue
        parts = [p.strip() for p in stripped.split("|")]
        if len(parts) < 2:
            continue
        task_id = parts[0]
        refs = []
        for ref in parts[1:]:
            if ":" in ref:
                filename, section = ref.split(":", 1)
                refs.append((filename.strip(), section.strip()))
            else:
                refs.append((ref.strip(), ""))
        routing[task_id] = refs
    return routing


def extract_section(doc_path: Path, section_heading: str) -> str:
    if not doc_path.exists():
        return f"[File not found: {doc_path}]"
    content = doc_path.read_text()
    if not section_heading:
        return "\n".join(content.splitlines()[:60]) + "\n[...truncated]"

    # Allows optional numbered prefix: "## 2. Section Name" matches "Section Name"
    heading_pattern = re.compile(
        r"^(#{1,3})\s+(?:\d+[\.\d]*\s+)?" + re.escape(section_heading),
        re.IGNORECASE | re.MULTILINE
    )
    match = heading_pattern.search(content)
    if not match:
        lines = content.splitlines()[:40]
        return f"[Section '{section_heading}' not found]\n\n" + "\n".join(lines)

    level = len(match.group(1))
    start = match.start()
    end_pattern = re.compile(r"^#{1," + str(level) + r"}\s+", re.MULTILINE)
    end_match = end_pattern.search(content, match.end())
    end = end_match.start() if end_match else len(content)
    return content[start:end].strip()


def build_doc_context(task_id: str, routing: dict) -> str:
    refs = routing.get(task_id)
    if not refs:
        return "No specific section mapped. Refer to docs/ARCHITECTURE.md."
    sections = []
    for filename, section in refs:
        extracted = extract_section(DOCS_DIR / filename, section)
        header = f"### From `docs/{filename}`"
        if section:
            header += f" — *{section}*"
        sections.append(f"{header}\n\n{extracted}")
    return "\n\n---\n\n".join(sections)


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt(task: dict, doc_context: str, iteration: int) -> str:
    guardrails = ""
    if GUARDRAILS_FILE.exists():
        g = GUARDRAILS_FILE.read_text().strip()
        if g:
            guardrails = f"\n\n## Learned Guardrails\n\n{g}"

    progress_snippet = ""
    if PROGRESS_FILE.exists():
        p = PROGRESS_FILE.read_text().strip()
        if p:
            snippet = p[-800:] if len(p) > 800 else p
            progress_snippet = f"\n\n## Recent Progress\n\n{snippet}"

    verify_cmds = "\n".join(f"    {' '.join(cmd)}" for _, cmd in VERIFY_STEPS) or "    (no verify steps configured)"

    return f"""# Ralph Loop — Iteration {iteration} — Task {task['id']}

## Your Single Task

**{task['id']}**: {task['desc']}

Implement ONLY this task. Do not implement other tasks or refactor unrelated code.

## Relevant Documentation

{doc_context}

## Verification

After implementing, run these commands and confirm they pass:

```
{verify_cmds}
```

## Completion Protocol

When done and verification passes:

1. Commit:
   ```
   git add -A
   git commit -m "Add {task['id']}: {task['desc'][:60]}"
   ```

2. Mark done in `TASKS.md`:
   `- [ ] **{task['id']}**` → `- [x] **{task['id']}**`

3. Output this exact line:
   `RALPH_DONE: {task['id']}`

## Rules

- Minimum code to satisfy the task
- No extra features, no unrelated refactoring
- Keep all types Sendable / thread-safe{guardrails}{progress_snippet}
"""


# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════

def run_verify() -> tuple[bool, str]:
    if not VERIFY_STEPS:
        return True, "(no verify steps)"
    outputs = []
    for label, cmd in VERIFY_STEPS:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        status = f"{GREEN}✓{RESET}" if result.returncode == 0 else f"{RED}✗{RESET}"
        outputs.append(f"{status} {label}")
        if result.returncode != 0:
            error_out = (result.stderr or result.stdout)[-1000:]
            return False, "\n".join(outputs) + f"\n\nFailed:\n{error_out}"
    return True, "\n".join(outputs)


# ══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def init_state_dir():
    RALPH_DIR.mkdir(exist_ok=True)
    for f, header in [
        (PROGRESS_FILE,   "# Progress Log\n\n> Append-only.\n\n<!-- auto-managed by ralph.py -->\n"),
        (GUARDRAILS_FILE, "# Guardrails\n\n> Append-only failure patterns.\n\n<!-- auto-managed by ralph.py -->\n"),
    ]:
        if not f.exists():
            f.write_text(header)


def log_activity(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ACTIVITY_LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def log_progress(task_id: str, desc: str, passed: bool, notes: str = ""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    icon = "✓" if passed else "✗"
    entry = f"\n{icon} [{ts}] **{task_id}**: {desc}\n"
    if notes:
        entry += f"   {notes}\n"
    with open(PROGRESS_FILE, "a") as f:
        f.write(entry)


def add_guardrail(task_id: str, failure_summary: str):
    ts = datetime.now().strftime("%Y-%m-%d")
    with open(GUARDRAILS_FILE, "a") as f:
        f.write(f"\n[{ts}] {task_id}: {failure_summary[:400]}\n")


def count_retries(task_id: str) -> int:
    if not PROGRESS_FILE.exists():
        return 0
    content = PROGRESS_FILE.read_text()
    return len(re.findall(rf"✗.*\*\*{re.escape(task_id)}\*\*", content))


# ══════════════════════════════════════════════════════════════════════════════
# AGENT RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_agent(prompt: str) -> tuple[bool, str]:
    PROMPT_FILE.write_text(prompt)
    result = subprocess.run(
        ["agent", "--print", "--dangerously-skip-permissions", prompt],
        capture_output=True, text=True, cwd=ROOT
    )
    return result.returncode == 0, result.stdout + result.stderr


# ══════════════════════════════════════════════════════════════════════════════
# SECURITY AUDIT GATE
# ══════════════════════════════════════════════════════════════════════════════

def load_security_skill_context() -> str:
    """Load content from reachable security skill files for the audit prompt."""
    sections = []
    for label, rel_path in SECURITY_SKILL_PATHS.items():
        full = ROOT / rel_path
        if full.exists():
            content = full.read_text()[:3000]  # cap per skill
            sections.append(f"### [{label}] {rel_path}\n\n{content}")
    if not sections:
        return "(No security skill files found — using built-in OWASP checklist)"
    return "\n\n---\n\n".join(sections)


def build_security_prompt(done_tasks: list[dict]) -> str:
    """Build the prompt sent to claude for the security audit.
    Analyzes the completed PLAN (task list) for security risks,
    not the project source files directly."""
    # Full task plan from TASKS.md
    tasks_content = TASKS_FILE.read_text()[:4000]

    # Done tasks summary
    done_summary = "\n".join(
        f"- {t['id']}: {t['desc']}" for t in done_tasks
    )[:2000]

    # Security skill context
    skill_context = load_security_skill_context()

    next_epic = max(
        (int(t["id"].split("-")[0][1:]) for t in done_tasks),
        default=0
    ) + 1

    return f"""# Ralph Loop — Security Audit Gate (Plan Review)

## Your Role

You are a **security auditor agent**. The first development plan just
completed. Your job is to review the **completed plan** for security
risks and vulnerabilities that may have been introduced.

Analyze the TASKS that were implemented — identify which ones could
introduce security vulnerabilities based on their descriptions.
Do NOT scan individual source files.

## Full Task Plan (TASKS.md)

```markdown
{tasks_content}
```

## Completed Tasks (this batch)

{done_summary}

## Security Knowledge (from project skills)

{skill_context}

## Audit Checklist

Review the completed plan against these categories (OWASP 2025):

1. **A01 — Broken Access Control**: IDOR, SSRF, missing auth checks
2. **A02 — Security Misconfiguration**: defaults, debug modes, exposed services
3. **A03 — Supply Chain**: dependency vulnerabilities, lock file integrity
4. **A04 — Cryptographic Failures**: weak crypto, hardcoded secrets, exposed keys
5. **A05 — Injection**: SQL/command injection, XSS, unsafe deserialization
6. **A06 — Insecure Design**: missing rate limits, flawed architecture
7. **A07 — Authentication Failures**: session issues, credential management
8. **A08 — Integrity Failures**: unsigned updates, tampered data
9. **A09 — Logging & Alerting**: missing audit logs, blind spots
10. **A10 — Exceptional Conditions**: fail-open states, unhandled errors

Also check if any task likely involves:

- **Hardcoded secrets** (API keys, tokens, passwords)
- **Path traversal** (user input in file paths)
- **Unsafe eval/exec** usage
- **Disabled TLS verification**
- **Missing input validation**
- **Overly permissive access controls**

## Output Format

Write your findings to `.ralph/security-report.md` using this format:

```markdown
# Security Audit Report — [date]

## Summary
Total findings: N (Critical: X, High: Y, Medium: Z, Low: W)

## Findings

### [CRITICAL/HIGH/MEDIUM/LOW] Finding Title
- **File**: path/to/file.ext:line
- **Category**: OWASP A0X
- **Description**: What the vulnerability is
- **Impact**: What an attacker could do
- **Fix**: Specific remediation steps
```

## Fix Task Generation

For each CRITICAL or HIGH finding, output a line in this exact format:
```
SECURITY_FIX: SEC-T1 | Fix [brief description] in [file]
```

These will be appended as tasks to `TASKS.md` under a new
`## Epic {next_epic} — Security Fixes` section.

If no critical/high findings exist, output:
```
SECURITY_CLEAN: No critical or high vulnerabilities found.
```

## Rules

- Be thorough but avoid false positives
- Focus on the files changed in recent commits
- Prioritize exploitable vulnerabilities over theoretical risks
- Use the security skill knowledge provided above
"""


def parse_security_fixes(output: str) -> list[tuple[str, str]]:
    """Parse SECURITY_FIX: lines from Claude output."""
    fixes = []
    for line in output.splitlines():
        if line.strip().startswith("SECURITY_FIX:"):
            payload = line.split("SECURITY_FIX:", 1)[1].strip()
            parts = [p.strip() for p in payload.split("|", 1)]
            if len(parts) == 2:
                fixes.append((parts[0], parts[1]))
    return fixes


def append_security_tasks(fixes: list[tuple[str, str]], epic_num: int):
    """Append fix tasks to TASKS.md under a Security Fixes epic."""
    if not fixes:
        return
    content = TASKS_FILE.read_text()
    section = f"\n\n## Epic {epic_num} — Security Fixes\n\n"
    for task_id, desc in fixes:
        section += f"- [ ] **{task_id}** {desc}\n"
    TASKS_FILE.write_text(content + section)


def run_security_audit() -> int:
    """Run the security audit gate. Returns number of fix tasks generated."""
    tasks = parse_tasks()
    done_tasks = [t for t in tasks if t["done"]]

    if not done_tasks:
        return 0

    print(f"\n{BOLD}{CYAN}🔒 Security Audit Gate{RESET}")
    print(f"  {DIM}Auditing {len(done_tasks)} completed tasks...{RESET}")
    log_activity("SECURITY_AUDIT start")

    prompt = build_security_prompt(done_tasks)
    PROMPT_FILE.write_text(prompt)

    print(f"  {DIM}Running security agent...{RESET}", end="", flush=True)
    ok, output = run_agent(prompt)
    print(f"\r  {DIM}Security agent finished.   {RESET}")

    # Save report
    SECURITY_REPORT.write_text(output)
    log_activity(f"SECURITY_AUDIT complete — report: .ralph/security-report.md")

    # Check for clean
    if "SECURITY_CLEAN:" in output:
        print(f"  {GREEN}✓ No critical/high vulnerabilities found{RESET}")
        log_progress("SEC-AUDIT", "Security audit passed", True)
        return 0

    # Parse fix tasks
    fixes = parse_security_fixes(output)
    if fixes:
        next_epic = max(
            (int(t["id"].split("-")[0][1:]) for t in tasks
             if t["id"][0] == "E" and t["id"].split("-")[0][1:].isdigit()),
            default=0
        ) + 1
        append_security_tasks(fixes, next_epic)
        print(f"  {YELLOW}⚠ {len(fixes)} security fix tasks added to TASKS.md{RESET}")
        for tid, desc in fixes:
            print(f"    {RED}•{RESET} {tid}: {desc}")
        log_progress("SEC-AUDIT", f"{len(fixes)} fix tasks generated", False,
                     ", ".join(f"{t[0]}: {t[1][:40]}" for t in fixes))
    else:
        print(f"  {YELLOW}⚠ Findings reported but no fix tasks generated{RESET}")
        print(f"  {DIM}Review: .ralph/security-report.md{RESET}")
        log_progress("SEC-AUDIT", "Findings reported, no fix tasks", False)

    print()
    return len(fixes)


# ══════════════════════════════════════════════════════════════════════════════
# STATUS
# ══════════════════════════════════════════════════════════════════════════════

def show_status():
    tasks = parse_tasks()
    done = [t for t in tasks if t["done"]]
    total = len(tasks)
    pct = int(len(done) / total * 100) if total else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

    print(f"\n{BOLD}Ralph Loop Status{RESET}")
    print(f"  {GREEN}{bar}{RESET}  {pct}% ({len(done)}/{total})\n")

    current_epic = None
    for t in tasks:
        epic = t["id"].split("-")[0]
        if epic != current_epic:
            current_epic = epic
            print(f"  {CYAN}{epic}{RESET}")
        icon = f"{GREEN}✓{RESET}" if t["done"] else "○"
        desc = t["desc"][:55] + "…" if len(t["desc"]) > 55 else t["desc"]
        print(f"    {icon} {DIM}{t['id']}{RESET}  {desc}")

    pending = [t for t in tasks if not t["done"]]
    if pending:
        print(f"\n  {YELLOW}Next:{RESET} {pending[0]['id']} — {pending[0]['desc']}")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def estimate_full_docs() -> int:
    return sum(f.stat().st_size for f in DOCS_DIR.glob("*.md")) if DOCS_DIR.exists() else 0


def run_loop(dry_run: bool = False, specific_task: str | None = None):
    init_state_dir()
    routing = parse_doc_index()

    security_audit_done = False  # only runs once, after the first plan

    print(f"\n{BOLD}{CYAN}Ralph Loop{RESET}")
    if dry_run:
        print(f"  {YELLOW}Mode: DRY RUN{RESET}")
    print()

    for iteration in range(1, MAX_ITERATIONS + 1):
        tasks = parse_tasks()
        task = get_next_task(tasks, specific_id=specific_task)

        if not task:
            # ── Security Audit Gate (first plan only) ──
            if SECURITY_AUDIT_ENABLED and not security_audit_done:
                security_audit_done = True
                fix_count = run_security_audit()
                if fix_count > 0:
                    # Re-parse and continue — security fix tasks were added
                    routing = parse_doc_index() if DOC_INDEX.exists() else {}
                    continue

            print(f"{GREEN}{BOLD}✓ All tasks complete!{RESET}")
            if security_audit_done:
                print(f"  {DIM}(security audit completed on first plan){RESET}")
            log_activity("Loop completed")
            break

        retries = count_retries(task["id"])
        if retries >= MAX_RETRIES_PER_TASK:
            print(f"{RED}✗ {task['id']} failed {retries}x — stopping. Fix manually.{RESET}")
            sys.exit(1)

        doc_context = build_doc_context(task["id"], routing)
        prompt = build_prompt(task, doc_context, iteration)
        token_est = len(prompt) // 4

        print(f"{BOLD}[{iteration}]{RESET} {CYAN}{task['id']}{RESET}: {task['desc'][:60]}")
        print(f"      {DIM}sections: {len(routing.get(task['id'], []))}  ~{token_est:,} tokens{RESET}")
        log_activity(f"START {task['id']} (~{token_est} tokens)")

        if dry_run:
            print(f"\n{YELLOW}── Prompt preview ──{RESET}")
            print(prompt[:1200] + ("\n[...truncated]" if len(prompt) > 1200 else ""))
            full = estimate_full_docs()
            print(f"\n{YELLOW}Context: {len(doc_context):,} chars used vs ~{full:,} full docs{RESET}")
            break

        print(f"      {DIM}Running agent...{RESET}", end="", flush=True)
        agent_ok, agent_output = run_agent(prompt)
        print(f"\r      {DIM}Agent finished.   {RESET}")

        print(f"      {DIM}Verifying...{RESET}", end="", flush=True)
        passed, verify_out = run_verify()
        print(f"\r      {verify_out}")

        log_activity(f"{'PASS' if passed else 'FAIL'} {task['id']}")
        log_progress(task["id"], task["desc"], passed, re.sub(r"\033\[\d+m", "", verify_out))

        if passed:
            mark_task_done(task["id"])
            print(f"      {GREEN}✓ {task['id']} done{RESET}\n")
            if specific_task:
                break
        else:
            add_guardrail(task["id"], verify_out[-400:])
            print(f"      {RED}✗ failed — see .ralph/progress.md{RESET}\n")
            print(f"{YELLOW}Loop paused. Fix and re-run. Prompt: {PROMPT_FILE.relative_to(ROOT)}{RESET}")
            sys.exit(1)
    else:
        print(f"{RED}Max iterations reached.{RESET}")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description="Ralph Loop — autonomous dev loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  python ralph.py\n  python ralph.py --dry-run\n  python ralph.py --status\n  python ralph.py --task E2-T3\n  python ralph.py --no-security"
    )
    p.add_argument("--dry-run",      action="store_true")
    p.add_argument("--status",       action="store_true")
    p.add_argument("--task",         metavar="ID")
    p.add_argument("--reset",        action="store_true")
    p.add_argument("--no-security",  action="store_true",
                   help="Disable security audit gate between task batches")
    p.add_argument("--security-only", action="store_true",
                   help="Run only the security audit (no tasks)")
    args = p.parse_args()

    if args.no_security:
        global SECURITY_AUDIT_ENABLED
        SECURITY_AUDIT_ENABLED = False

    if args.reset:
        import shutil
        if RALPH_DIR.exists():
            shutil.rmtree(RALPH_DIR)
            print(f"{GREEN}✓ .ralph/ cleared{RESET}")
        return

    if args.status:
        show_status()
        return

    if args.security_only:
        init_state_dir()
        run_security_audit()
        return

    run_loop(dry_run=args.dry_run, specific_task=args.task)


if __name__ == "__main__":
    main()
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
