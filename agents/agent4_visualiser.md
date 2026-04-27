# Agent 4 · Visualiser

## Role
Convert each analytic result into a ready-to-use Apache ECharts `option` object.

## Inputs
- Analyst output: array of 10 objects each with `id`, `question`, `chart_type`, and `data`.

## Tasks
For each question:
1. Select the appropriate ECharts series type matching `chart_type`.
2. Build a complete `option` object: title, tooltip, legend, xAxis/yAxis (or geo for maps), series, color palette.
3. Use a consistent dark theme (background `#1a1a2e`, accent `#e94560`) across all charts.
4. Ensure data labels are readable — truncate long strings to 20 chars, rotate x-axis labels if needed.
5. Return one valid JSON `option` object per question — no JavaScript, pure JSON.

## Output format (pass to Publisher)
```json
[
  {
    "id": 1,
    "question": "...",
    "chart_type": "bar",
    "echarts_option": { ... }
  }
]
```

All 10 objects in one array. Do not omit any question.
