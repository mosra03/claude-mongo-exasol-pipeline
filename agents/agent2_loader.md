# Agent 2 · Loader

## Role
Import the raw survey CSV into MongoDB Atlas so the Analyst can run aggregation pipelines against it.

## Inputs
- `data/survey_results.csv` — 2025 Stack Overflow Developer Survey
- Target collection: `stackoverflow_survey` in database `so_survey_2025`

## Tasks
1. Connect to MongoDB Atlas via the MongoDB MCP server.
2. Drop and recreate the collection to ensure a clean load.
3. Stream the CSV in batches of 1,000 rows; convert each row to a BSON document.
4. After loading, run a count query and confirm it matches the expected row count (49,191).
5. Create indexes on: `Country`, `LanguageHaveWorkedWith`, `ConvertedCompYearly`, `YearsCodePro`.

## Output (pass to Orchestrator)
```json
{
  "database": "so_survey_2025",
  "collection": "stackoverflow_survey",
  "documents_loaded": 49191,
  "indexes_created": ["Country", "LanguageHaveWorkedWith", "ConvertedCompYearly", "YearsCodePro"]
}
```
