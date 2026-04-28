# Agent 3 · Artist

**Job:** Read view definitions from `RECIPES.CHEF`, query each `ANALYTICS` view for sample data, generate `app/server.py` and `app/index.html`.

**Single prompt trigger:** `Run agent 3 - Artist`

## Prerequisite
```sql
SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete';
SELECT COUNT(*) FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS';
```
Both must return > 0 (second must return 5). If not, stop and report: **Agent 2 has not completed — run Agent 2 first.**

## Data source
- **Exasol only** — reads from `RECIPES.CHEF` and queries `ANALYTICS.*` views
- Connect via **Exasol MCP** — do not use MongoDB MCP.

## Steps

1. Read the `payload` from `RECIPES.CHEF WHERE status = 'complete'`.
2. For each of the 5 views: run `SELECT * FROM ANALYTICS.<view_name> LIMIT 100` to understand the column shape and data types.
3. Generate `app/server.py` (see spec below).
4. Generate `app/index.html` (see spec below).

## app/server.py specification

- Use **pyexasol** to connect to Exasol SaaS.
- Connection details from env vars: `EXASOL_HOST`, `EXASOL_PORT` (default 8563), `EXASOL_USER`, `EXASOL_PASSWORD`.
- Start with `--port` argument (default 8080): `python3 app/server.py --port 8080`
- Expose one endpoint: `GET /api/query`
  - Accepts query params: `view_name` (required), plus any filter params specific to that view
  - Validates `view_name` is in the allowed list (the 5 ANALYTICS views) — reject anything else with 400
  - Enforces read-only: only `SELECT` queries — reject any other SQL with 400
  - Builds a parameterised `SELECT * FROM ANALYTICS.<view_name> WHERE 1=1` with safe filter appends
  - Returns JSON array of row objects
  - Handles CORS for localhost: `Access-Control-Allow-Origin: *`
- Also serve `GET /` and `GET /index.html` → `app/index.html`
- Use Python stdlib `http.server` — no Flask/FastAPI dependency.

## app/index.html specification

- Load **Apache ECharts** from CDN (no local copy).
- **5 chart tabs** — one per ANALYTICS view, matching the `pattern_name` from `RECIPES.CHEF`.
- Each chart tab has:
  - Filter controls (dropdowns and/or sliders) for the `filter_fields` listed in the view's RECIPES.CHEF entry
  - On filter change: call `/api/query?view_name=<view>&<filter>=<value>`, receive JSON, re-render the ECharts chart
  - "Last updated" timestamp displayed below the chart (update on every fetch)
- Charts use the dark theme:
  - Background: `#1A1A2E`
  - Accent / primary series: `#E94560`
  - Secondary colours: `#38bdf8`, `#34d399`, `#fbbf24`, `#818cf8`
  - Text: `#f1f5f9`
  - Muted text: `#94a3b8`
- **No static data baked in.** Every chart renders from a live `/api/query` call on page load and on filter change.
- Show a loading spinner while fetch is in-flight.
- On fetch error: display the error message inside the chart container.

## Dark theme constants
```json
{
  "backgroundColor": "#1A1A2E",
  "primary_accent":  "#E94560",
  "palette": ["#E94560", "#38bdf8", "#34d399", "#fbbf24", "#818cf8"],
  "text_primary":    "#f1f5f9",
  "text_muted":      "#94a3b8",
  "surface":         "#16213E",
  "border":          "#0F3460"
}
```

## Output
Write `app/server.py` and `app/index.html` to the filesystem. No Exasol write required for this agent — the filesystem is the output.

## Verification
- `app/server.py` exists on filesystem
- `app/index.html` exists on filesystem
- `grep -l "EXASOL_HOST" app/server.py` — confirms Exasol connection is wired up
- `grep -l "api/query" app/index.html` — confirms live queries, not static data
