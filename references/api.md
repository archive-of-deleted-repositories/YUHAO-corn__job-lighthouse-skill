# Public API contract

Default base URL: `https://job-lighthouse.godcorn001.workers.dev/api`

Override it with `JOB_LIGHTHOUSE_API_URL` for compatible self-hosted deployments.

## `GET /health`

Returns service availability and current server time.

## `GET /stats`

Returns approximate public counters:

- `active_jobs`: current active job records;
- `companies`: distinct companies with active jobs;
- `sources`: enabled source connectors;
- `searches`: completed searches;
- `visits`: aggregate web visits;
- `updated_at`: latest successful job observation.

## `POST /search`

Request:

```json
{
  "query": "上海或杭州，AI 与游戏相关，偏创作者工具，不要纯销售",
  "ai": true,
  "limit": 40
}
```

`query` is required and may contain 2–500 characters. `limit` accepts 1–100.

Important response fields:

- `intent`: parsed cities, domains, job families, positive terms, and exclusions;
- `results[].job`: normalized original job data and source URL;
- `results[].score`: deterministic score from 0–100;
- `results[].confidence`: `direct`, `adjacent`, or `exploratory`;
- `results[].parts`: explainable score components;
- `results[].evidence`: deterministic matching signals;
- `results[].risks`: deterministic conflicts or missing conditions;
- `ai.used`: whether the optional AI pass ran;
- `ai.summary`: cross-candidate summary;
- `ai.jobs[]`: AI match explanation, source evidence, and risks for leading candidates.

AI quota exhaustion does not disable deterministic search. Clients should keep presenting results and disclose `ai.reason`.

## `POST /telemetry`

Accepted aggregate events:

```json
{ "channel": "skill", "event": "install" }
```

Channels: `web`, `skill`, `api`. Events: `visit`, `search`, `install`, `invoke`.

The endpoint accepts counts only. Do not send prompts, job IDs, user identifiers, or device metadata in the event body.

## Headers

Clients should set:

- `x-job-lighthouse-client: skill` for Skill calls;
- `x-job-lighthouse-visitor` to a locally generated random installation ID for fair anonymous rate limits.

The public API does not expose source connectors, database credentials, ranking implementation, or administrative endpoints.
