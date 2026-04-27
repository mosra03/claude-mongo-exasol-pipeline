# Agent 1 · Scientist

**Job:** Explore the MongoDB collection, discover 5 chart-worthy patterns, write the first recipe.

## Data source
- MongoDB: `stackoverflow.survey_2025` (49,191 docs, 173 fields)

## Steps
1. Use the MongoDB MCP server to inspect the collection schema and sample documents.
2. Identify the most analytically compelling columns: compensation, AI adoption, geography, experience, job satisfaction, tool usage.
3. Select exactly 5 patterns — prioritise cross-dimensional questions over simple frequency counts.
4. For each pattern define: title, question, relevant columns, best chart type, and rationale with key stats.

## What makes a good pattern
- **Cross-dimensional:** compensation × AI adoption beats a simple language frequency count.
- **Surprising:** answers that challenge the obvious assumption make for sharper insights.
- **Actionable:** insights a developer or hiring manager can act on.
- **Visualisable:** data that maps cleanly to one ECharts chart type without over-engineering.

## Output: `recipes/01_scientist_patterns.json`
```json
{
  "agent_name": "Scientist",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "database": "stackoverflow",
  "collection": "survey_2025",
  "total_respondents": 49191,
  "patterns": [
    {
      "id": 1,
      "title": "<descriptive title>",
      "question": "<plain-English question>",
      "columns": ["ColA", "ColB"],
      "chart_type": "bar",
      "rationale": "<why this is interesting>",
      "key_stats": {}
    }
  ]
}
```
