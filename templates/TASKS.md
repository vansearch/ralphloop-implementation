# <Project Name> — Task List (Ralph Loop)

> Format: `- [ ] **EPIC-TASK** Description`
> The ralph.py script reads this file to drive the loop.
> Mark tasks done with `[x]` — or let the agent do it automatically.
>
> Rules:
> - Each task must be completable in one session (< 2 hours)
> - Task descriptions must be specific and verifiable
> - Use IDs like E1-T1, E2-T3 — never dots or spaces in IDs
> - Every task ID must have an entry in docs/DOC-INDEX.md
> - Add `[parallel]` to an epic header to run its tasks concurrently

---

## Epic 1 — Foundation

- [ ] **E1-T1** Set up the project structure and package configuration
- [ ] **E1-T2** Add core dependencies and build configuration
- [ ] **E1-T3** Write initial unit test scaffold and CI verification

## Epic 2 — Core Feature [parallel]

<!-- Tasks in a [parallel] epic are run concurrently by the orchestrator.
     Each task gets its own git worktree. After all workers finish, branches
     are merged and VERIFY_STEPS runs once on the merged state.
     Use [parallel] for independent tasks that don't share files. -->

- [ ] **E2-T1** Implement <core feature name> with basic functionality
- [ ] **E2-T2** Add error handling and edge case coverage for <feature>
- [ ] **E2-T3** Write unit tests for <core feature>

## Epic 3 — CLI / Interface

- [ ] **E3-T1** Implement command-line interface with ArgumentParser
- [ ] **E3-T2** Add --help text and usage examples

## Epic 4 — Distribution

- [ ] **E4-T1** Configure build artifacts and release pipeline
- [ ] **E4-T2** Write installation documentation
