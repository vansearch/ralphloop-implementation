#!/usr/bin/env python3
"""
setup.py — Ralph Loop Project Scaffolder
=========================================
Bootstraps a new project with the Ralph Loop workflow files.

Run this once in your project root to create:
  - TASKS.md          → task checklist the loop consumes
  - docs/             → documentation directory
  - docs/DOC-INDEX.md → token-saving routing table
  - docs/PRD.md       → product requirements (placeholder)
  - docs/ARCHITECTURE.md → architecture notes (placeholder)
  - .ralph/           → agent state directory
  - .ralph/guardrails.md → learned failure patterns
  - .ralph/progress.md   → run history

Usage:
    python setup.py                         # interactive prompts
    python setup.py --name "My Project"     # set project name directly
    python setup.py --lang swift            # preset verify commands for Swift
    python setup.py --lang ts               # preset verify commands for TypeScript
    python setup.py --lang python           # preset verify commands for Python
    python setup.py --lang rust             # preset verify commands for Rust
    python setup.py --force                 # overwrite existing files

After running this script, copy ralph.py to your project root:
    cp /path/to/ralph.py .
Or download it:
    curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/ralph.py

Then adapt VERIFY_STEPS in ralph.py to your tech stack, and start the loop:
    python ralph.py --dry-run
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── Colors ──────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

# ── Language presets ─────────────────────────────────────────────────────────
LANG_PRESETS = {
    "swift": {
        "verify_comment": (
            '    ("swift build", ["swift", "build", "-c", "debug"]),\n'
            '    ("swift test",  ["swift", "test"]),'
        ),
        "build_cmd": "swift build -c debug && swift test",
    },
    "ts": {
        "verify_comment": (
            '    ("bun build", ["bun", "run", "build"]),\n'
            '    ("bun test",  ["bun", "test"]),'
        ),
        "build_cmd": "bun run build && bun test",
    },
    "typescript": {
        "verify_comment": (
            '    ("bun build", ["bun", "run", "build"]),\n'
            '    ("bun test",  ["bun", "test"]),'
        ),
        "build_cmd": "bun run build && bun test",
    },
    "python": {
        "verify_comment": (
            '    ("pytest", ["uv", "run", "pytest"]),'
        ),
        "build_cmd": "uv run pytest",
    },
    "rust": {
        "verify_comment": (
            '    ("cargo build", ["cargo", "build"]),\n'
            '    ("cargo test",  ["cargo", "test"]),'
        ),
        "build_cmd": "cargo build && cargo test",
    },
    "node": {
        "verify_comment": (
            '    ("npm test", ["npm", "test"]),'
        ),
        "build_cmd": "npm test",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# FILE TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

def tasks_md(project_name: str) -> str:
    return f"""# {project_name} — Task List (Ralph Loop)

> Format: `- [ ] **EPIC-TASK** Description`
> The ralph.py script reads this file to drive the loop.
> Mark tasks done with `[x]` — or let the agent do it automatically.
>
> Rules:
> - Each task must be completable in one session (< 2 hours)
> - Task descriptions must be specific and verifiable
> - Use IDs like E1-T1, E2-T3 — never dots or spaces in IDs
> - Every task must have an entry in docs/DOC-INDEX.md

---

## Epic 1 — Foundation

- [ ] **E1-T1** <Replace with your first task description>
- [ ] **E1-T2** <Replace with your second task description>

## Epic 2 — Core Feature

- [ ] **E2-T1** <Replace with core feature task>
- [ ] **E2-T2** <Replace with core feature task>
"""


def doc_index_md(project_name: str) -> str:
    return f"""# Doc Index — Context Router for Ralph Loop

> This file is read by `ralph.py` to determine which documentation
> sections each task needs. The agent reads ONLY the listed sections.
>
> Format per task:
>   TASK_ID | file:section | file:section | ...
>
> Sections use the heading text after `##` in each doc file.
> Keep entries to 2-3 sections max — more is waste.
>
> Generated for: {project_name}

---

## Routing Table

```
# Epic 1 — Foundation
E1-T1 | ARCHITECTURE.md:Overview | PRD.md:Goals
E1-T2 | ARCHITECTURE.md:Package Structure

# Epic 2 — Core Feature
E2-T1 | ARCHITECTURE.md:Core Components | PRD.md:Core Features
E2-T2 | ARCHITECTURE.md:Core Components
```
"""


def prd_md(project_name: str) -> str:
    return f"""# {project_name} — Product Requirements Document

> Replace this file with your actual PRD.
> The Ralph Loop planning mode reads the first 5,000 chars of this file
> to generate new tasks when the current task list is exhausted.

---

## Goals

- <Primary goal of this project>
- <Secondary goal>
- <Success metric>

## Core Features

### Feature 1
<Description>

### Feature 2
<Description>

## Non-Goals

- <What this project explicitly does NOT do>

## Technical Constraints

- <Language/runtime/platform>
- <Key dependencies>
- <Performance requirements>
"""


def architecture_md(project_name: str) -> str:
    return f"""# {project_name} — Architecture

> Replace this file with your actual architecture documentation.
> The doc router uses sections of this file — keep headings consistent
> with the routing table in docs/DOC-INDEX.md.

---

## Overview

<High-level description of the system architecture>

## Package Structure

<Directory layout and module responsibilities>

## Core Components

<Key classes, modules, or services — one subsection per component>

## Data Flow

<How data moves through the system>

## Build System

<Build tool, commands, and configuration>

## Dependencies

<Key external dependencies and why they were chosen>
"""


def guardrails_md() -> str:
    return """# Guardrails — Learned Patterns

> Append-only. The Ralph Loop reads this file each iteration to avoid
> repeating past mistakes.
>
> Format: [YYYY-MM-DD] TASK-ID: description of what went wrong and how to fix it.
>
> Commit this file to share learned failure patterns with the team.
> Do NOT commit .ralph/progress.md, activity.log, current_prompt.md.

<!-- entries added automatically by ralph.py on task failure -->
"""


def progress_md() -> str:
    return """# Progress Log

> Append-only. Records pass/fail for every task attempt.
> ralph.py appends to this file — do not edit manually.
> This file is in .gitignore — do not commit it.

<!-- entries added automatically by ralph.py -->
"""


def gitignore_entries() -> str:
    return """
# Ralph Loop state (do not commit these)
.ralph/activity.log
.ralph/current_prompt.md
.ralph/progress.md
.ralph/security-report.md
"""


# ═══════════════════════════════════════════════════════════════════════════
# SCAFFOLDING LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def ask(prompt: str, default: str = "") -> str:
    """Prompt the user for input with an optional default."""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    return input(f"{prompt}: ").strip()


def create_file(path: Path, content: str, force: bool = False) -> bool:
    """Create a file. Returns True if created, False if skipped."""
    if path.exists() and not force:
        print(f"  {DIM}skip{RESET}  {path}  (already exists, use --force to overwrite)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  {GREEN}create{RESET} {path}")
    return True


def append_gitignore(root: Path, entries: str, force: bool = False) -> None:
    """Append Ralph Loop entries to .gitignore if not already present."""
    gi_path = root / ".gitignore"
    marker = "# Ralph Loop state"

    if gi_path.exists():
        existing = gi_path.read_text()
        if marker in existing and not force:
            print(f"  {DIM}skip{RESET}  .gitignore  (Ralph entries already present)")
            return
        # Append
        with gi_path.open("a") as f:
            f.write(entries)
        print(f"  {GREEN}update{RESET} .gitignore  (appended Ralph Loop entries)")
    else:
        gi_path.write_text(entries.strip() + "\n")
        print(f"  {GREEN}create{RESET} .gitignore")


def copy_ralph_py(root: Path, force: bool = False) -> None:
    """Copy ralph.py from the same directory as this script, if available."""
    script_dir = Path(__file__).parent
    source = script_dir / "ralph.py"
    dest = root / "ralph.py"

    if dest.exists() and not force:
        print(f"  {DIM}skip{RESET}  ralph.py  (already exists)")
        return

    if source.exists():
        shutil.copy2(source, dest)
        print(f"  {GREEN}copy{RESET}   ralph.py  (from {source})")
    else:
        print(f"  {YELLOW}note{RESET}   ralph.py not found next to setup.py")
        print(f"         Download: curl -O https://raw.githubusercontent.com/vansearch/ralphloop-implementation/main/ralph.py")


def scaffold(
    root: Path,
    project_name: str,
    lang: str | None,
    force: bool,
) -> None:
    print(f"\n{BOLD}Ralph Loop Scaffolder{RESET}")
    print(f"Project: {CYAN}{project_name}{RESET}")
    print(f"Root:    {root}\n")

    # Core files
    create_file(root / "TASKS.md",               tasks_md(project_name),      force)
    create_file(root / "docs" / "DOC-INDEX.md",  doc_index_md(project_name),  force)
    create_file(root / "docs" / "PRD.md",        prd_md(project_name),        force)
    create_file(root / "docs" / "ARCHITECTURE.md", architecture_md(project_name), force)

    # State directory
    create_file(root / ".ralph" / "guardrails.md", guardrails_md(), force)
    create_file(root / ".ralph" / "progress.md",   progress_md(),   force)

    # .gitignore
    append_gitignore(root, gitignore_entries(), force)

    # Copy ralph.py
    copy_ralph_py(root, force)

    # Summary
    print(f"\n{GREEN}{BOLD}✓ Scaffold complete!{RESET}\n")
    print(f"Next steps:")
    print(f"  1. Edit {CYAN}TASKS.md{RESET} — replace placeholder tasks with your real tasks")
    print(f"  2. Edit {CYAN}docs/DOC-INDEX.md{RESET} — map each task ID to relevant doc sections")
    print(f"  3. Edit {CYAN}docs/PRD.md{RESET} — describe what you're building")
    print(f"  4. Edit {CYAN}docs/ARCHITECTURE.md{RESET} — describe the system structure")

    if lang:
        preset = LANG_PRESETS.get(lang.lower())
        if preset:
            print(f"\n  5. In {CYAN}ralph.py{RESET}, set VERIFY_STEPS to:")
            print(f"     {DIM}{preset['verify_comment']}{RESET}")
        else:
            available = ", ".join(LANG_PRESETS.keys())
            print(f"\n  {YELLOW}Unknown lang '{lang}'. Available: {available}{RESET}")
    else:
        print(f"\n  5. In {CYAN}ralph.py{RESET}, set VERIFY_STEPS for your tech stack")

    print(f"\n  6. Run the loop:")
    print(f"     {DIM}python ralph.py --dry-run   # preview first task{RESET}")
    print(f"     {DIM}python ralph.py --status    # show progress{RESET}")
    print(f"     {DIM}python ralph.py             # start autonomous loop{RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap a project with the Ralph Loop workflow.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py                          # interactive mode
  python setup.py --name "MemorySaver"    # set name directly
  python setup.py --lang swift            # Swift preset for VERIFY_STEPS hint
  python setup.py --lang ts               # TypeScript/Bun preset
  python setup.py --force                 # overwrite existing files
""",
    )
    parser.add_argument(
        "--name", "-n",
        help="Project name (used in file headers). Prompted if omitted.",
    )
    parser.add_argument(
        "--lang", "-l",
        choices=list(LANG_PRESETS.keys()),
        help="Tech stack preset for VERIFY_STEPS hint (swift, ts, python, rust, node).",
        metavar="LANG",
    )
    parser.add_argument(
        "--root", "-r",
        help="Root directory to scaffold (default: current directory).",
        default=".",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing files (default: skip existing).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"{RED}Error: directory '{root}' does not exist.{RESET}")
        sys.exit(1)

    # Determine project name
    if args.name:
        project_name = args.name
    else:
        default_name = root.name.replace("-", " ").replace("_", " ").title()
        project_name = ask("Project name", default_name)
        if not project_name:
            print(f"{RED}Error: project name is required.{RESET}")
            sys.exit(1)

    scaffold(root, project_name, args.lang, args.force)


if __name__ == "__main__":
    main()
