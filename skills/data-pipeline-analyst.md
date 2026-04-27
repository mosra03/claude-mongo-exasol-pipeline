# Data Pipeline Analyst

Activate when the user says "analyse my data", "run pipeline", "explore my collection", or triggers any single-prompt agent command from CLAUDE.md.

## How this pipeline works

A 4-agent sequence where each agent reads the previous recipe (JSON handoff file), does its work, and writes its own recipe. The Orchestrator validates `status: "complete"` before advancing. Any failure stops the pipeline.

### Agent sequence

| Command | Agent | Reads | Writes |
|---------|-------|-------|--------|
| `Run agent 1 - Scientist` | Scientist | _(none)_ | `recipes/01_scientist_patterns.json` |
| `Run agent 2 - Chef` | Chef | `recipes/01_scientist_patterns.json` | `recipes/02_chef_kitchen.json` |
| `Run agent 3 - Artist` | Artist | `recipes/02_chef_kitchen.json` | `recipes/03_artist_manifest.json` |
| `Run agent 4 - Postman` | Postman | `recipes/03_artist_manifest.json` | `recipes/04_postman_delivery.json` |
| `Run full pipeline` | All 1→2→3→4 | chain | all four |

### Recipe contract

Every recipe must have this shape:
```json
{
  "agent_name": "<name>",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "results": { }
}
```

An agent must see `status: "complete"` in its input recipe before proceeding. Agent 1 has no input recipe.

## Data source

- **MongoDB Atlas** — database `stackoverflow`, collection `survey_2025`
- 49,191 documents, 173 fields
- All numeric fields (e.g. `ConvertedCompYearly`, `YearsCode`, `JobSat`) are stored as strings — always `$convert` with `onError: null`
- `"NA"` is the null sentinel — always exclude before any numeric operation
- Multi-select fields (e.g. `AIModelsHaveWorkedWith`) use `";"` as delimiter — `$split`, `$unwind`, trim whitespace

## What each agent needs to know

### Scientist — finding good patterns
- Cross-dimensional beats univariate: `ConvertedCompYearly × AISelect` is richer than a simple count of languages.
- Prefer questions where the answer is surprising or challenges a common assumption.
- Target chart types: `bar`, `horizontal_bar`, `choropleth`, `grouped_bar`, `line`.
- Write `key_stats` with actual numbers from sample aggregations — not placeholders.

### Chef — running aggregations
- Always filter out `"NA"` before converting strings to numbers.
- Compensation filter: `{ $gte: 0, $lte: 2000000 }` after conversion.
- Insight string rule: one sentence, two or more specific numbers. Example: *"Remote developers earn 58% more ($108K vs $68K in-person)."*
- For choropleth: use full country names matching ECharts world map — not ISO codes.

### Artist — generating ECharts configs
- Use pure JSON — no JavaScript function strings in `formatter`.
- Dark theme: `backgroundColor: "#0f172a"`, primary accent `#38bdf8`, surface `#1e293b`, muted text `#94a3b8`.
- Choropleth requires `visualMap` component and world geo registered from CDN.
- Truncate x-axis labels to 20 chars; rotate if more than 5 categories.

### Postman — publishing the app
- Kill any existing server on port 8765 before starting: `lsof -ti:8765 | xargs kill -9 2>/dev/null || true`
- Verify server is alive with `curl -s http://localhost:8765/api/data` before opening tunnel.
- Parse `trycloudflare.com` URL from cloudflared stdout — it appears after `+------------------+`.
- `app/server.py` and `app/index.html` are already written — only rewrite if chart structure changes.

## MCP servers needed

| Server | Purpose |
|--------|---------|
| `mongodb-mcp` | Read/write access to MongoDB Atlas — used by Scientist (schema inspection) and Chef (aggregations) |
| `exasol-mcp` | Optional — available for SQL analytics if Chef needs columnar queries |

## Failure diagnosis

| Symptom | Likely cause |
|---------|-------------|
| Scientist writes `status: "pending"` | MongoDB MCP not connected or collection empty |
| Chef aggregation returns 0 results | `"NA"` not excluded before numeric filter |
| Artist produces invalid JSON | JavaScript function used in formatter — replace with template string |
| Postman tunnel URL not printed | cloudflared not installed or port 8765 already blocked |
