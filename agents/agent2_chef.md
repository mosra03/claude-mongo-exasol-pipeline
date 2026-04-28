# Agent 2 · Chef

**Job:** Read patterns from `RECIPES.SCIENTIST`, create `ANALYTICS` views in Exasol for each pattern, write results to `RECIPES.CHEF`.

**Single prompt trigger:** `Run agent 2 - Chef`

## Prerequisite
```sql
SELECT COUNT(*) FROM RECIPES.SCIENTIST WHERE status = 'complete';
```
Must return > 0. If not, stop and report: **Agent 1 has not completed — run Agent 1 first.**

## Data source
- **Exasol only** — reads from `RECIPES.SCIENTIST` and queries `RAW_WRAPPER."survey_raw"`
- Connect via **Exasol MCP** — do not use MongoDB MCP.

## Steps

For each pattern in the `payload` from `RECIPES.SCIENTIST`:

1. Write a SQL query against `RAW_WRAPPER."survey_raw"` that produces a clean result set (≤ 200 rows).
2. Apply data quality rules:
   - Exclude rows where the relevant fields are `NULL` or `'NA'`
   - Cast numeric strings to `DOUBLE`: `CAST(field AS DOUBLE)`
   - Filter `ConvertedCompYearly` to `>= 0 AND <= 2000000`
   - Multi-value fields (`;` delimited): use `REGEXP_REPLACE` + `CROSS JOIN` to unnest
3. Create the view in the `ANALYTICS` schema:
   ```sql
   CREATE SCHEMA IF NOT EXISTS ANALYTICS;

   CREATE OR REPLACE VIEW ANALYTICS.<pattern_name> AS
   SELECT <columns>
   FROM RAW_WRAPPER."survey_raw"
   WHERE 1=1
     AND <field> IS NOT NULL
     AND <field> != 'NA'
   -- additional filter placeholders as comments for dynamic filters
   ;
   ```
4. Each view must be filterable — include `WHERE 1=1` so the server can append dynamic `AND` clauses.
5. Verify the view returns data: `SELECT COUNT(*) FROM ANALYTICS.<pattern_name>`

## Field handling notes
- `ConvertedCompYearly`, `YearsCode`, `JobSat` — stored as strings; always `CAST(x AS DOUBLE)`.
- Multi-select fields (e.g. `AIModelsHaveWorkedWith`) — split on `';'`, unwind via lateral join or recursive split before grouping.
- Do not hard-code country or language lists — derive them from the data.

## What makes a good insight string
One sentence. Name the finding. Include at least two specific numbers.
Example: *"Fully remote developers earn 58% more than in-person ($116K vs $70K)."*

## Output
Write a single row to `RECIPES.CHEF`:

```sql
INSERT INTO RECIPES.CHEF (recipe_id, agent_name, status, created_at, view_count, payload)
VALUES (
    '<uuid>',
    'chef',
    'complete',
    NOW(),
    5,
    '<JSON blob>'
);
```

The `payload` JSON must have this structure:
```json
{
  "views": [
    {
      "pattern_id": 1,
      "view_name": "ANALYTICS.<pattern_name>",
      "columns": ["col_a", "col_b"],
      "filter_fields": ["field1", "field2"],
      "insight": "<one sharp sentence with numbers>",
      "key_finding": "<what this view reveals>"
    }
  ]
}
```

**Do not write any local file.** The recipe lives in Exasol only.

## Verification
After writing, confirm both:
```sql
SELECT COUNT(*) FROM RECIPES.CHEF WHERE status = 'complete';
SELECT COUNT(*) FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS';
```
First must return 1. Second must return 5.
