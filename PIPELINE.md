# Pipeline Usage Guide

Analytics pipeline over the 2025 Stack Overflow Developer Survey (49,191 respondents).

---

## Mode 1 — Step by step

Run each agent individually. Use this when learning the system, debugging a single stage, or re-running one agent without touching the others.

```
Run agent 1 - Scientist
Run agent 2 - Chef
Run agent 3 - Artist
Run agent 4 - Postman
```

Each command is self-contained. The agent reads its input recipe, does its work, and writes its output recipe. You can re-run any single agent as many times as needed.

---

## Mode 2 — Full pipeline

Run all four agents in sequence with automatic recipe validation between each step.

```
Run full pipeline
```

The pipeline stops immediately if any agent's output recipe does not reach `status: "complete"`, and reports which agent failed and why.

---

## Agent reference

### Agent 1 — Scientist

| | |
|---|---|
| **Job** | Explore the MongoDB collection, find 5 chart-worthy patterns in the survey data |
| **Reads** | Nothing (first agent) |
| **Writes** | `recipes/01_scientist_patterns.json` |
| **Output contains** | 5 pattern objects, each with: question, columns, chart_type, rationale |

**If it fails:**
- Check that the MongoDB MCP server is connected and `stackoverflow.survey_2025` is reachable
- Confirm the collection has documents (`count` > 0)
- Look for a `status: "pending"` or missing `results` array in the output recipe

---

### Agent 2 — Chef

| | |
|---|---|
| **Job** | Run MongoDB aggregations for each pattern, shape data into ECharts-ready format |
| **Reads** | `recipes/01_scientist_patterns.json` — must have `status: "complete"` |
| **Writes** | `recipes/02_chef_kitchen.json` |
| **Output contains** | Per-chart `echarts_data` objects with axis labels, series arrays, and an insight string |

**If it fails:**
- Confirm Agent 1's recipe is `status: "complete"` before re-running
- All survey fields are stored as strings (including numeric ones like `ConvertedCompYearly`). Use `$convert` with `onError`/`onNull` rather than `$type: "number"` filters
- "NA" is the null sentinel throughout the dataset — always exclude it before numeric conversion

---

### Agent 3 — Artist

| | |
|---|---|
| **Job** | Generate complete ECharts option configs for each chart |
| **Reads** | `recipes/02_chef_kitchen.json` — must have `status: "complete"` |
| **Writes** | `recipes/03_artist_manifest.json` |
| **Output contains** | 5 ECharts `option` objects, one per chart, ready to drop into a `<script>` block |

**If it fails:**
- Confirm Agent 2's recipe is `status: "complete"` before re-running
- Check that `echarts_data` fields (xAxis_labels, series, matrix) are present for every chart
- The choropleth (chart 2) requires the ECharts `geo` component and a world map dataset

---

### Agent 4 — Postman

| | |
|---|---|
| **Job** | Build the web app (HTML/CSS/JS), start a local server, open a public tunnel |
| **Reads** | `recipes/03_artist_manifest.json` — must have `status: "complete"` |
| **Writes** | `recipes/04_postman_delivery.json`, `app/index.html` |
| **Output contains** | Local server URL, public tunnel URL, port number |

**If it fails:**
- Confirm Agent 3's recipe is `status: "complete"` before re-running
- Check that `app/` directory is writable
- If the tunnel fails, the web app may still be running locally — check `recipes/04_postman_delivery.json` for the local URL

---

## Recipe status flow

```
recipes/01_scientist_patterns.json   pending → complete
         ↓ (Chef reads this)
recipes/02_chef_kitchen.json         pending → complete
         ↓ (Artist reads this)
recipes/03_artist_manifest.json      pending → complete
         ↓ (Postman reads this)
recipes/04_postman_delivery.json     pending → complete
```

An agent will not proceed if its input recipe has any status other than `"complete"`.
