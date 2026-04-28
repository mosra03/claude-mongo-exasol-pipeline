# Agent 1 · Scientist

**Job:** Explore `RAW.SURVEY_DOCS` in Exasol, discover 5 chart-worthy cross-dimensional patterns, write results to `RECIPES.SCIENTIST`.

**Single prompt trigger:** `Run agent 1 - Scientist`

## Data source
- **Exasol only** — table `RAW.SURVEY_DOCS` (49,191 rows, loaded via exasol-json-tables)
- Fields are queryable via JSON path syntax: `"AISelect"`, `"ConvertedCompYearly"`, `"Country"`, etc.
- Connect via **Exasol MCP** — do not use MongoDB MCP for this agent.

## Steps

1. Use Exasol MCP to inspect `RAW.SURVEY_DOCS`: sample 10–20 rows, check available fields and data types.
2. Run exploratory queries to understand value distributions for key fields: `ConvertedCompYearly`, `AISelect`, `Country`, `RemoteWork`, `YearsCode`, `AIThreat`, `AIModelsHaveWorkedWith`, `JobSat`.
3. Select exactly 5 patterns. Each pattern must be:
   - **Cross-dimensional** — two or more fields in tension (e.g. compensation × AI adoption)
   - **Surprising** — challenges an obvious assumption
   - **Visualisable** — maps cleanly to one chart type without over-engineering
4. For each pattern define: `pattern_id`, `pattern_name`, `insight`, `field_x`, `field_y`, `chart_type`, `sample_query`

## What makes a good pattern
- Cross-dimensional beats univariate: `ConvertedCompYearly × AISelect` is richer than a language frequency count.
- Include actual numbers from exploratory queries in the `insight` — no placeholders.
- Chart types: `bar`, `horizontal_bar`, `choropleth`, `grouped_bar`, `line`.

## Output
Write a single row to `RECIPES.SCIENTIST`:

```sql
INSERT INTO RECIPES.SCIENTIST (recipe_id, agent_name, status, created_at, pattern_count, payload)
VALUES (
    '<uuid>',
    'scientist',
    'complete',
    NOW(),
    5,
    '<JSON blob>'
);
```

The `payload` JSON must have this structure:
```json
{
  "total_respondents": 49191,
  "patterns": [
    {
      "pattern_id": 1,
      "pattern_name": "<descriptive name>",
      "insight": "<one sharp sentence with numbers>",
      "field_x": "<primary field>",
      "field_y": "<secondary field>",
      "chart_type": "bar",
      "sample_query": "<SQL SELECT against RAW.SURVEY_DOCS>"
    }
  ]
}
```

**Do not write any local file.** The recipe lives in Exasol only.

## Verification
After writing, confirm with:
```sql
SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete';
```
Must return 1.
