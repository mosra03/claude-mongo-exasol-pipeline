# Agent 3 · Artist

**Job:** Generate complete Apache ECharts option configs for every chart, write the third recipe.

## Inputs
Reads `recipes/02_chef_kitchen.json` — confirm `status: "complete"` before proceeding.

## Steps
For each chart in the Chef's recipe:
1. Select the ECharts series type matching `chart_type`.
2. Build a complete `option` object: `backgroundColor`, `title`, `tooltip`, `legend`, `grid`, axis config, `series`, `visualMap` (choropleth only), color palette.
3. Apply the dark theme consistently across all charts (see below).
4. Ensure readability: truncate x-axis labels to 20 chars, rotate if > 5 categories, use `$` / `%` formatters in tooltips.
5. Output pure JSON — no JavaScript function strings; use ECharts built-in formatter templates.

## Dark theme
```json
{
  "backgroundColor": "#0f172a",
  "palette": ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171"],
  "text_primary": "#f1f5f9",
  "text_muted":   "#94a3b8",
  "surface":      "#1e293b",
  "border":       "#334155"
}
```

## Output: `recipes/03_artist_manifest.json`
```json
{
  "agent_name": "Artist",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "source_recipe": "recipes/02_chef_kitchen.json",
  "charts": [
    {
      "id": 1,
      "title": "<title>",
      "question": "<question>",
      "chart_type": "<type>",
      "insight": "<insight string from Chef>",
      "echarts_option": { }
    }
  ]
}
```
