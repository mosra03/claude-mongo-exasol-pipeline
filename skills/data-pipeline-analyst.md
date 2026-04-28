# Data Pipeline Analyst

Activate when the user says "analyse my data", "run pipeline", "explore my collection", or triggers any single-prompt agent command from CLAUDE.md.

## Architecture

**Exasol is the single source of truth.** MongoDB is the source — data is exported once via `scripts/ingest.py`. All agents read from and write to Exasol only.

```
MongoDB Atlas
     ↓  scripts/ingest.py (mongoexport → exasol-json-tables)
RAW.SURVEY_DOCS  (Exasol)
     ↓  Agent 1 – Scientist
RECIPES.SCIENTIST  (Exasol table)
     ↓  Agent 2 – Chef
RECIPES.CHEF  (Exasol table)  +  ANALYTICS.*  (Exasol views ×5)
     ↓  Agent 3 – Artist
app/server.py + app/index.html  (filesystem)
     ↓  Agent 4 – Postman
recipes/04_postman_delivery.json  (local, ephemeral tunnel URL)
```

## How to check pipeline state

```sql
-- Raw data loaded?
SELECT COUNT(*) FROM RAW.SURVEY_DOCS;

-- Agent 1 done?
SELECT status, pattern_count, created_at FROM RECIPES.SCIENTIST ORDER BY created_at DESC LIMIT 1;

-- Agent 2 done?
SELECT status, view_count, created_at FROM RECIPES.CHEF ORDER BY created_at DESC LIMIT 1;

-- Analytics views built?
SELECT VIEW_NAME FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS' ORDER BY VIEW_NAME;
```

## Agent sequence and Exasol connections

| Command | Agent | Reads from | Writes to |
|---------|-------|-----------|-----------|
| `Run agent 1 - Scientist` | Scientist | `RAW.SURVEY_DOCS` | `RECIPES.SCIENTIST` |
| `Run agent 2 - Chef` | Chef | `RECIPES.SCIENTIST`, `RAW.SURVEY_DOCS` | `RECIPES.CHEF`, `ANALYTICS.*` views |
| `Run agent 3 - Artist` | Artist | `RECIPES.CHEF`, `ANALYTICS.*` | `app/server.py`, `app/index.html` |
| `Run agent 4 - Postman` | Postman | filesystem | `recipes/04_postman_delivery.json` |
| `Run full pipeline` | All 1→2→3→4 | chain | all above |

All agents connect via **Exasol MCP**. MongoDB MCP is used only by `scripts/ingest.py`.

## Recipe tables schema

### RECIPES.SCIENTIST
| Column | Type | Notes |
|--------|------|-------|
| recipe_id | VARCHAR(50) | UUID |
| agent_name | VARCHAR(50) | 'scientist' |
| status | VARCHAR(20) | 'pending' or 'complete' |
| created_at | TIMESTAMP | |
| pattern_count | INT | Should be 5 |
| payload | VARCHAR(2000000) | JSON: patterns array |

### RECIPES.CHEF
| Column | Type | Notes |
|--------|------|-------|
| recipe_id | VARCHAR(50) | UUID |
| agent_name | VARCHAR(50) | 'chef' |
| status | VARCHAR(20) | 'pending' or 'complete' |
| created_at | TIMESTAMP | |
| view_count | INT | Should be 5 |
| payload | VARCHAR(2000000) | JSON: views array with filter_fields |

## ANALYTICS views and filter fields

Agent 2 creates 5 views in the `ANALYTICS` schema — names derive from the patterns Agent 1 discovers. Each view includes a `WHERE 1=1` clause for dynamic filter appends.

To inspect available views and their columns:
```sql
SELECT VIEW_NAME, VIEW_TEXT FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS';
SELECT COLUMN_NAME, COLUMN_TYPE FROM EXA_ALL_COLUMNS WHERE COLUMN_SCHEMA = 'ANALYTICS';
```

Filter fields per view are stored in `RECIPES.CHEF.payload` under each view's `filter_fields` array.

## What each agent needs to know

### Scientist — finding good patterns
- Use Exasol MCP to sample `RAW.SURVEY_DOCS` and run exploratory queries.
- Cross-dimensional beats univariate: `ConvertedCompYearly × AISelect` is richer than a count of languages.
- Write actual numbers from exploratory queries in `insight` — no placeholders.
- Target chart types: `bar`, `horizontal_bar`, `choropleth`, `grouped_bar`, `line`.
- Payload goes into `RECIPES.SCIENTIST.payload` as a JSON string.

### Chef — building ANALYTICS views
- Always filter out `NULL` and `'NA'` before numeric casts.
- Compensation filter: `CAST(ConvertedCompYearly AS DOUBLE) BETWEEN 0 AND 2000000`.
- Multi-value fields (`;` delimited): unnest with lateral join or recursive split.
- Each view must have `WHERE 1=1` for dynamic filter injection by the server.
- Insight: one sentence, two or more specific numbers.

### Artist — generating the data app
- Reads `RECIPES.CHEF.payload` to get view names and filter fields.
- Queries each `ANALYTICS` view (`LIMIT 100`) to understand column shape.
- `server.py`: connects to Exasol via pyexasol, serves `/api/query`, validates view names, enforces SELECT-only.
- `index.html`: 5 chart tabs, filter controls per view, live fetch on filter change — no static data.
- Dark theme: background `#1A1A2E`, primary accent `#E94560`.

### Postman — publishing the app
- Port 8080 (not 8765).
- Verify server: `curl -s "http://localhost:8080/api/query?view_name=test"` — 400 response means server is alive.
- Parse `trycloudflare.com` URL from cloudflared stdout.
- Write `recipes/04_postman_delivery.json` — the only local recipe file.

## MCP servers needed

| Server | Purpose |
|--------|---------|
| `exasol-mcp` | **Required** — used by all three data agents (Scientist, Chef, Artist) |
| `mongodb-mcp` | **Not needed during pipeline** — only `scripts/ingest.py` uses mongoexport |

## Failure diagnosis

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete'` returns 0 | Scientist failed to insert or inserted with status 'pending' | Re-run Agent 1; check Exasol MCP connection |
| `SELECT COUNT(*) FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS'` < 5 | Chef created fewer than 5 views | Check `RECIPES.CHEF.payload` for view names; re-run Agent 2 |
| Chef aggregation returns 0 rows | `'NA'` not excluded before numeric filter, or `RAW.SURVEY_DOCS` empty | Verify ingest ran: `SELECT COUNT(*) FROM RAW.SURVEY_DOCS` |
| `app/server.py` missing | Artist did not run or failed mid-write | Re-run Agent 3 |
| `grep "api/query" app/index.html` fails | Artist baked in static data instead of live queries | Re-run Agent 3 with explicit instruction: no static data |
| Postman tunnel URL not printed | cloudflared not installed or port 8080 already blocked | `brew install cloudflare/cloudflare/cloudflared`; kill port 8080 |
| Server 500 on `/api/query` | pyexasol not installed or Exasol credentials wrong | `pip install pyexasol`; check env vars |
