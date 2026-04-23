---
name: company-brief
description: >-
  Researches a company and writes a structured SWE-focused brief with source
  discipline, personal fit vs master.yaml, and Proceed/Pass-style conclusion.
  Use when the user asks for company research, employer due diligence, or a
  brief saved under reports/briefs with sanitization.
---

# Company brief

**Role:** Assistant — career / company research (see `docs/AGENT_ROLES.md`).

**Context to load (if available):**
- `data/private/master.yaml` — use for **personal fit** (`profile.headline`, `career.direction_summary`, `career.target_titles`, `work_mode`, `preferred_location`, `deal_breakers`, `domains`, `skills`). **Do not** copy PII (email, phone, detailed address) into outputs intended for public; briefs saved under `reports/briefs/` must **strip PII** per `docs/SANITIZATION_CHECKLIST.md`.

**Target (collect, confirm, or ask):**
- If **company name** (and any disambiguation: legal entity, region, product line, or role/team) is **not** clear from memory or chat: **ask** before deep research.
- If you **infer** the target from context (e.g. prior thread about one employer): state the name and scope and **ask the user to confirm or correct** before producing the full brief.

Act as a **Senior / Staff-level engineer** with a **distributed systems** background, **end-to-end ownership**, and interest in **AI in production / AI-augmented engineering** when relevant — evaluating an opportunity at **<company-name>** (use the confirmed name).

**Goal:** Produce a structured report to decide **whether to pursue this offer/team**, from technical, operational, and career angles (not candidate evaluation).

### General requirements

- **Source priority:** (1) official financials / IR, (2) engineering blog, technical docs, talks, open source, (3) news with named outlets, (4) Glassdoor / Blind / LinkedIn reviews — label these as **opinion/anonymous**, prone to bias.
- For each important claim, provide:
  - **(a) Fact** (with source or short quote)
  - **(b) Inference** (reasonable)
  - **(c) Unknown / needs verification**
- No unfounded speculation. Missing data → **Unknown**.
- Objective tone, not PR.

### Personal fit (required short section)

After gathering company data, compare to `master.yaml` (do not paste PII):

- **Role fit:** distributed systems / backend / platform / ML-infra — which aligns with `career.target_titles` and `career.direction_summary`?
- **Reference weights** (adjust as needed): `CURSOR.md` §8 — distributed & execution, system design, ownership & cross-team delivery, AI in production (if JD/team), domain, seniority, practical constraints.
- **Constraints:** `work_mode`, location, `deal_breakers` (e.g. outsourcing-only / body-shop if signals appear).

---

## 1. Company overview (SWE context)

- Business model
- Core products / services
- Revenue streams (if known)
- Engineering’s role in the business (cost center vs growth lever)

---

## 2. Product & technical landscape

- Core tech stack (backend, frontend, infra, data)
- Architecture (monolith, microservices, event-driven, etc.) — public evidence vs inference
- Challenges: scale, latency, reliability, consistency, compliance
- **Technical complexity** (low / medium / high) + why

---

## 3. AI / ML & data (when relevant)

- Organization: research-only vs **production ML**; team owns models end-to-end vs siloed?
- Serving, evaluation, cost/latency, data governance — any public signals?
- If no AI in the business: **N/A** and do not force inference.

---

## 4. Engineering culture

- Process (Agile, Scrum, etc.) — evidence
- Code quality: testing, CI/CD, review, SLO/error budget (if signaled)
- **Ownership:** platform vs feature; on-call / incident culture
- Tech decisions: centralized vs per team
- Evidence: engineering blog, talks, reviews (classify reliability)

---

## 5. Developer experience (DX)

- Tooling (CI/CD, observability, internal platform)
- Deploy frequency / lead time (if metrics or DORA-like hints exist)
- Onboarding
- Tech debt — degree and signals

---

## 6. Remote work, timezone, outsourcing

- Remote / hybrid / onsite; does it match `work_mode` in `master.yaml`?
- Timezone & meeting load (if inferable from location/policy)
- **Body-shop / outsourcing-only** signals vs product/in-house (if any) — ties to `deal_breakers`

---

## 7. Career growth (IC)

- Mentorship, technical depth vs breadth
- IC vs management path
- Employer brand in the market (qualitative; cite if possible)

---

## 8. Compensation & stability

- Salary band (if known: levels.fyi, surveys, JD — cite source)
- Benefits (high level, no sensitive detail)
- Company financial health (if public)
- Layoff / hiring trend (with source)

---

## 9. Risks & red flags

- Technical: legacy, tech debt, scale
- Organizational: churn, culture (weak sources → state confidence)
- Market: declining sector, weak moat
- **Quick check** vs `deal_breakers` in `master.yaml`

---

## 10. Conclusion & recommendation

Pick one label:

- **Proceed** — worth interview/negotiation time
- **Proceed with conditions** — only if (state conditions)
- **Defer** — need more data or wrong timing
- **Pass** — misaligned goals / risk above tolerance

Include:

- **Seniority fit:** Junior / Mid / Senior / Staff — for the discussed team/role
- **Builder vs maintainer** (estimate)
- **Top 3–5 reasons** (short bullets)

---

## 11. Confidence & gaps

- **Confidence:** High / Medium / Low
- What still needs verification (specific questions for recruiter / hiring manager)

---

## 12. Assumptions & Risk (required)

- **Assumptions:** what you assumed when data was missing
- **Risk:** what breaks if assumptions are wrong; decision risk from this brief

---

**Output:** Markdown ready to save; if under `reports/briefs/`, **sanitize** per project policy (no PII, no sensitive contract detail).
