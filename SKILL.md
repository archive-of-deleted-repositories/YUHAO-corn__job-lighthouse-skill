---
name: job-lighthouse-skill
description: Search and compare current public job openings through the Job Lighthouse remote API using natural-language requirements. Use when a user asks to find jobs, discover adjacent roles whose titles may not match exactly, compare opportunities, inspect evidence or risks, or access the public Job Lighthouse index from Codex, OpenClaw, Claude Code, and other tool-using agents.
---

# Job Lighthouse

Use Job Lighthouse as a public job-search backend. Send the user's natural-language requirement to the remote API, retrieve a broad candidate set, and explain the strongest matches using original job evidence.

## Search workflow

1. Preserve the user's complete request, including cities, experience, preferred work, exclusions, and willingness to consider adjacent titles.
2. Run:

```bash
python3 scripts/job_lighthouse.py search "<用户的完整需求>" --json
```

3. Read `results` broadly. Do not keep only titles that literally repeat the query. Treat `direct` as strong matches, `adjacent` as plausible non-standard titles, and `exploratory` as lower-confidence leads.
4. For the best candidates, report:
   - title, company, city, and source link;
   - why it matches;
   - the original evidence returned by the API;
   - risks, missing information, or hard-condition conflicts.
5. Keep deterministic scores and AI analysis distinct. If `ai.used` is false, state that the result uses the platform's base ranking and continue; do not present unavailable AI reasoning as fact.
6. Never claim that a job is still open without checking its returned `status`, and never claim that an application was submitted.

Use `--limit 20` for a compact search or up to `--limit 100` for broader exploration. Use `--no-ai` when the user prefers speed or when AI quota is unavailable.

## Other operations

Check platform health and coverage:

```bash
python3 scripts/job_lighthouse.py health --json
python3 scripts/job_lighthouse.py stats --json
```

Use `references/api.md` for the public endpoint contract and response fields.

## Privacy and telemetry

The search request necessarily sends the user's job-search sentence to the Job Lighthouse API. Do not include names, phone numbers, résumé text, employer-confidential material, or unrelated personal data unless the user explicitly asks.

The bundled client records one anonymous installation count and aggregate invocations. It sends no prompt, search query, job ID, device fingerprint, or account identity to the telemetry endpoint. Explain this when asked. Disable it with either:

```bash
python3 scripts/job_lighthouse.py telemetry off
export JOB_LIGHTHOUSE_TELEMETRY=0
```

Telemetry is transparent and best-effort; its failure must never block search. Users may inspect or modify the open-source client.

## Self-hosting

The default client uses the public Job Lighthouse platform. Point the same workflow at a compatible self-hosted API with:

```bash
export JOB_LIGHTHOUSE_API_URL=https://example.com/api
```

Do not infer access to the platform's private crawlers, database, ranking implementation, or deployment code from this Skill. This repository is the open client layer only.
