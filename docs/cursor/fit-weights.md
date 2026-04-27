# Fit weights & target metadata — Career Path 2026

Target role configuration and the weighted fit-scoring rubric. Loaded by JD/benchmark scoring, capability-gap analysis, and company briefs.

## Target metadata

```yaml
target_profile:
  primary_role: "Distributed Systems Engineer"
  fallback_role:
    allowed: true
    role: "Senior Software Engineer (Backend / Distributed Systems)"
    company_tier_condition: "FAANG+"
  preferred_company_tiers:
    - "Tier-1"
    - "FAANG+"
  editable_for_publish: true
```

## Fit score weights (experimental)

Emphasis on **systems ownership + AI in delivery**; when the JD has no AI/ML, redistribute the AI percentage into *Distributed systems* and *System design*.

- Distributed systems & backend execution: 32%
- System design & scalability / reliability: 22%
- Systems-level product ownership & cross-functional delivery: 18%
- AI/ML in production or AI-augmented engineering (when the JD includes this): 5% — if not, add to the first two buckets
- Domain & industry fit: 5%
- Seniority match: 8%
- Practical constraints (location/timezone/work mode): 10%
