# MCP Agentic Data Pipeline

Data app built on the 2025 Stack Overflow Developer Survey (49,191 respondents).

**Single source of truth: Exasol.** Recipes are Exasol tables. Analytics are Exasol views. The data app queries Exasol live on every user interaction. No static data.

## Single-prompt agent commands

These phrases trigger a specific agent. Use them exactly as written:

```
Run agent 1 - Scientist    → query RAW.SURVEY_DOCS, find 5 patterns, write to RECIPES.SCIENTIST
Run agent 2 - Chef         → read RECIPES.SCIENTIST, create ANALYTICS views, write to RECIPES.CHEF
Run agent 3 - Artist       → read RECIPES.CHEF, query ANALYTICS views, generate app/server.py + app/index.html
Run agent 4 - Postman      → install deps, start server, open tunnel, write recipes/04_postman_delivery.json
Run full pipeline          → ingest → Scientist → Chef → Artist → Postman (in sequence)
```

## Full pipeline — execution rules

When "Run full pipeline" is triggered:

0. **Ingest** (skip if `RAW.SURVEY_DOCS` already has rows): run `python3 scripts/ingest.py`
1. **Agent 1 (Scientist).** After it finishes, validate:
   ```sql
   SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete';
   ```
   Must return > 0. If not: **Agent 1 failed** — report the actual count and any error status rows.
2. **Agent 2 (Chef).** After it finishes, validate:
   ```sql
   SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete';
   SELECT COUNT(*) FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS';
   ```
   Both must return > 0 (second must return 5). If not: **Agent 2 failed**.
3. **Agent 3 (Artist).** After it finishes, validate:
   - `app/server.py` and `app/index.html` exist on filesystem
   If not: **Agent 3 failed**.
4. **Agent 4 (Postman).** After it finishes, read `recipes/04_postman_delivery.json` and confirm `status === "complete"`. If not: **Agent 4 failed**.

On success: report all four agents completed, the data app URL, and the tunnel address from `recipes/04_postman_delivery.json`.

## Recipe tables (in Exasol)

| Table | Written by | Validated by |
|-------|-----------|--------------|
| `RECIPES.SCIENTIST` | Scientist | `SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete'` |
| `RECIPES.CHEF` | Chef | `SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete'` |

Recipes 01–03 are no longer local files — they live in Exasol.
`recipes/04_postman_delivery.json` remains a local file (ephemeral tunnel URL).

## Analytics views (in Exasol)

Five views in the `ANALYTICS` schema — one per pattern discovered by Agent 1.

Verify: `SELECT VIEW_NAME FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS'`

Each view is filterable via `WHERE 1=1` clauses that the server appends dynamically.

## Data sources

- **MongoDB Atlas** — `stackoverflow.survey_2025` — source only; exported to NDJSON by `scripts/ingest.py`
- **Exasol SaaS** — `RAW.SURVEY_DOCS` — single source of truth for all agents and the live data app

## MCP servers required

| Server | Required by |
|--------|------------|
| `exasol-mcp` | **All agents** (Scientist, Chef, Artist) — primary data access |
| `mongodb-mcp` | **Ingest step only** — `scripts/ingest.py` uses `mongoexport`, not MCP directly |

## How to verify pipeline state

```sql
-- Raw data loaded
SELECT COUNT(*) FROM RAW.SURVEY_DOCS;

-- Agent 1 complete
SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete';

-- Agent 2 complete
SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete';

-- Analytics views built
SELECT VIEW_NAME FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS';
```

## How to reset

```sql
DROP SCHEMA RECIPES CASCADE;
DROP SCHEMA ANALYTICS CASCADE;
```
Then re-run `python3 scripts/ingest.py` and the full pipeline.

## Project structure

```
agents/          agent spec markdown files (orchestrator + 4 agents)
scripts/         ingest.py — MongoDB export + Exasol load + schema setup
skills/          Claude Code skill — auto-loads pipeline context
recipes/         04_postman_delivery.json only (ephemeral tunnel URL)
app/             data app written by Agent 3 (server.py + index.html)
assets/          screenshot PNGs
data/            raw survey data (gitignored — large NDJSON export)
```
