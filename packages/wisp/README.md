# Wisp

> AI job-search decision-support assistant. Helps you decide which jobs are worth pursuing — and quietly tracks the rest.

**Status:** v0.1.0.dev — pre-alpha. The M1 skeleton; nothing user-facing works yet.

Wisp is a calm, local-first web app that runs on your machine. It reads job descriptions you paste in, gives you an honest read on whether the role is worth your time, and tracks what you decide. It is **not** a job tracker, ATS, resume builder, or Kanban board.

## Core values (pinned)

1. Help the user decide which jobs are worth pursuing — and quietly keep track of the rest.
2. Optimize for *better* applications, not more.
3. Near-zero capture friction.
4. AI gives human-readable signals, not fake percentages.
5. Auto-tracking with no manual status updates.
6. Calm, supportive, assistant-like UX.
7. Low input, high output.
8. AI output is **advisory**, non-authoritative, exploratory.
9. Every AI verdict carries a confidence score.
10. The product must work without AI — heuristic + decision checklist always available.
11. No "AI says X, do X." Wisp surfaces perspective; the user decides.

## Install (development)

```bash
pip install -e packages/wisp[dev]
wisp --version
```

## Run

```bash
wisp
```

Opens a browser tab on a free localhost port. First run takes you through a setup wizard.

## Architecture

See [the implementation plan](../../.claude/plans/c-users-admin-downloads-specs-md-c-user-sequential-russell.md) (in this repo, not yet public) for the full design — milestones M1–M14, AI provider Protocol, evaluator chain, hot-brief vs cold-storage UX.
