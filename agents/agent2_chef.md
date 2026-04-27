# Agent 2 · Chef

**Job:** Run MongoDB aggregations for each pattern, shape data into ECharts-ready series, write the second recipe.

## Inputs
Reads `recipes/01_scientist_patterns.json` — confirm `status: "complete"` before proceeding.

## Steps
For each pattern in the Scientist's recipe:
1. Write a MongoDB aggregation pipeline that produces a clean result set (≤ 200 rows).
2. Handle data quality: all numeric fields are stored as strings; use `$convert` with `onError: null`. Always exclude `"NA"` before numeric conversion.
3. Compute the metric (avg, count, percent) and sort the result meaningfully.
4. Shape into ECharts-ready arrays: `xAxis_labels` (or `yAxis_labels`), `series` data arrays, and an `insight` string — one sharp sentence that names the key finding with numbers.

## Field notes
- `ConvertedCompYearly`, `YearsCode`, `JobSat` — strings; always `$convert` to double.
- Multi-select fields (e.g. `AIModelsHaveWorkedWith`, `LanguageHaveWorkedWith`) — split on `";"`, `$unwind`, trim whitespace before grouping.
- Filter compensation to `$0–$2M` to remove outliers.
- Do not hard-code country or language lists — derive them from the data.

## What makes a good insight string
One sentence. Name the finding. Include at least two numbers. Example: *"Fully remote developers earn 58% more than in-person ($108K vs $68K)."*

## Output: `recipes/02_chef_kitchen.json`
```json
{
  "agent_name": "Chef",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "source_recipe": "recipes/01_scientist_patterns.json",
  "charts": [
    {
      "id": 1,
      "title": "<title from pattern>",
      "question": "<question from pattern>",
      "chart_type": "<type from pattern>",
      "echarts_data": {
        "xAxis_labels": ["..."],
        "series": [{ "name": "...", "data": [0] }],
        "insight": "<one sharp sentence with numbers>"
      }
    }
  ]
}
```
