# MCP Agentic Data Pipeline

Analytics app built on the 2025 Stack Overflow Developer Survey (49,191 respondents).

## Single-prompt agent commands

These phrases trigger a specific agent. Use them exactly as written:

```
Run agent 1 - Scientist    → explore MongoDB, find 5 patterns, write recipes/01_scientist_patterns.json
Run agent 2 - Chef         → run aggregations, prep ECharts data, write recipes/02_chef_kitchen.json
Run agent 3 - Artist       → generate ECharts configs, write recipes/03_artist_manifest.json
Run agent 4 - Postman      → build web app, start server, open tunnel, write recipes/04_postman_delivery.json
Run full pipeline          → run all four agents in sequence (1 → 2 → 3 → 4)
```

## Recipe files

Each agent reads the previous agent's recipe and writes its own. All recipes live in `recipes/`.

| File | Written by | Status values |
|---|---|---|
| `recipes/01_scientist_patterns.json` | Scientist | pending → complete |
| `recipes/02_chef_kitchen.json` | Chef | pending → complete |
| `recipes/03_artist_manifest.json` | Artist | pending → complete |
| `recipes/04_postman_delivery.json` | Postman | pending → complete |

An agent must see `status: "complete"` in its input recipe before proceeding (Agent 1 has no input recipe).

## Data sources

- **MongoDB Atlas** — `stackoverflow.survey_2025` (49,191 docs, 173 fields)
- **Exasol SaaS** — available for SQL analytics if needed

## Project structure

```
agents/          agent spec markdown files
recipes/         structured JSON handoff files between agents
app/             web app output (written by Postman)
assets/          static assets
data/            raw survey data
```
