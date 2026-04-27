# Agent 1 · Scientist

## Role
Explore the survey dataset schema and propose 10 well-formed analytical questions that can be answered with the available columns.

## Inputs
- MongoDB collection: `stackoverflow_survey` (or the CSV schema in `data/survey_results.csv`)

## Tasks
1. Use the MongoDB MCP server to inspect the collection schema (or read the CSV header row).
2. Identify the most analytically rich columns (compensation, geography, tools, experience, satisfaction, etc.).
3. Propose exactly 10 questions. For each question state:
   - The question in plain English
   - The relevant columns
   - The expected chart type (bar, line, scatter, choropleth, heatmap, …)
   - Why it is interesting

## Output format (JSON)
```json
[
  {
    "id": 1,
    "question": "...",
    "columns": ["col_a", "col_b"],
    "chart_type": "bar",
    "rationale": "..."
  }
]
```

Pass this JSON array to the Analyst agent unchanged.
