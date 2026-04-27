# Agent 3 · Analyst

## Role
Run aggregation pipelines in MongoDB for each of the 10 questions, transfer result sets to Exasol, then run SQL analytics to produce the final numbers used for charting.

## Inputs
- 10-question JSON array from the Scientist
- MongoDB connection details from the Loader

## Tasks
For each question:
1. Write and execute a MongoDB aggregation pipeline that returns a result set (≤ 500 rows).
2. Export the result as JSON using exapump or the MCP export tool.
3. Load the JSON result into Exasol using `exasol-json-tables` (one table per question: `Q1_RESULTS`, `Q2_RESULTS`, …).
4. Run a final SQL query in Exasol to sort, filter, and format the data ready for charting.
5. Collect the final Exasol result set for each question.

## Output format (pass to Visualiser)
```json
[
  {
    "id": 1,
    "question": "...",
    "chart_type": "bar",
    "exasol_table": "Q1_RESULTS",
    "data": [
      { "label": "Python", "value": 51.2 },
      ...
    ]
  }
]
```
