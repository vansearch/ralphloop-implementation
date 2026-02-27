# Doc Index — Context Router for Ralph Loop

> This file is read by `ralph.py` to determine which documentation
> sections each task needs. The agent reads ONLY the listed sections.
>
> Format per task:
>   TASK_ID | file:section | file:section | ...
>
> Sections use the heading text after `##` in each doc file.
> Keep entries to 2-3 sections max — more is waste.
>
> Why this matters: without routing, every iteration loads all docs
> (15,000–90,000 chars). With routing: 500–2,000 chars per task.
> ~95% token reduction.

---

## Routing Table

```
# Epic 1 — Foundation
E1-T1 | ARCHITECTURE.md:Package Structure | PRD.md:Technical Constraints
E1-T2 | ARCHITECTURE.md:Dependencies | ARCHITECTURE.md:Build System
E1-T3 | ARCHITECTURE.md:Build System | PRD.md:Goals

# Epic 2 — Core Feature
E2-T1 | ARCHITECTURE.md:Core Components | PRD.md:Core Features
E2-T2 | ARCHITECTURE.md:Core Components
E2-T3 | ARCHITECTURE.md:Core Components | ARCHITECTURE.md:Build System

# Epic 3 — CLI / Interface
E3-T1 | ARCHITECTURE.md:CLI Interface | PRD.md:Core Features
E3-T2 | ARCHITECTURE.md:CLI Interface

# Epic 4 — Distribution
E4-T1 | ARCHITECTURE.md:Build System | PRD.md:Technical Constraints
E4-T2 | ARCHITECTURE.md:Overview
```

---

## Rules

- Every task in `TASKS.md` must have an entry in this file
- Section names must match `## Section Name` headings in the referenced doc
- Use the fewest sections needed (1–2 is ideal, 3 is the max)
- Missing sections are warned at runtime: `[Section 'X' not found in Y]`
- If a section is missing, check exact heading text with `grep "^## " docs/FILE.md`
