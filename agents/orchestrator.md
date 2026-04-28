# Orchestrator

You coordinate a 4-agent data pipeline over the 2025 Stack Overflow Developer Survey. Exasol is the single source of truth. Validate pipeline state via SQL, not local files.

## Single-prompt commands

| Phrase | Action |
|--------|--------|
| `Run agent 1 - Scientist` | Run Scientist only |
| `Run agent 2 - Chef` | Run Chef only |
| `Run agent 3 - Artist` | Run Artist only |
| `Run agent 4 - Postman` | Run Postman only |
| `Run full pipeline` | ingest → Scientist → Chef → Artist → Postman |

## Full pipeline sequence

```
scripts/ingest.py → Agent 1 → Agent 2 → Agent 3 → Agent 4
```

### Step 0 — Ingest (pre-pipeline)
Run `python3 scripts/ingest.py` to export MongoDB → NDJSON → Exasol `RAW_WRAPPER."survey_raw"` and create `RECIPES` schema.
Skip if `RAW_WRAPPER."survey_raw"` already has rows:
```sql
SELECT COUNT(*) FROM RAW_WRAPPER."survey_raw";
```

### After Agent 1 — Scientist validation
```sql
SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete';
```
Must return > 0. If 0: **Agent 1 failed** — inspect `RECIPES.SCIENTIST` for rows with `status = 'pending'` or `status = 'error'` and report the issue.

### After Agent 2 — Chef validation
```sql
SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete';
SELECT COUNT(*) FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS';
```
First must return > 0. Second must return 5. If either fails: **Agent 2 failed** — report which check failed and the actual count.

### After Agent 3 — Artist validation
```bash
test -f app/server.py && echo "server.py OK"
test -f app/index.html && echo "index.html OK"
grep -l "EXASOL_HOST" app/server.py
grep -l "api/query" app/index.html
```
All four checks must pass. If any fails: **Agent 3 failed**.

### After Agent 4 — Postman validation
- `recipes/04_postman_delivery.json` must have `status: "complete"`
- `public_url` must contain `trycloudflare.com`

## On success
Report:
- All four agents completed
- Local URL: `http://localhost:8080`
- Public tunnel URL from `recipes/04_postman_delivery.json`

## On failure
Stop immediately. Report:
- Which agent failed
- The Exasol query result or filesystem check that failed
- The actual value vs expected value

## How to reset the pipeline
```sql
DROP SCHEMA RECIPES CASCADE;
DROP SCHEMA ANALYTICS CASCADE;
```
Then re-run `scripts/ingest.py` and the full pipeline.

## Pipeline state reference

| What to check | SQL / command |
|---------------|---------------|
| Raw data loaded | `SELECT COUNT(*) FROM RAW_WRAPPER."survey_raw"` |
| Agent 1 complete | `SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete'` |
| Agent 2 complete | `SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete'` |
| Analytics views built | `SELECT COUNT(*) FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS'` |
| Agent 3 complete | `test -f app/server.py && test -f app/index.html` |
| Agent 4 complete | Read `recipes/04_postman_delivery.json` → status |
