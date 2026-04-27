# Orchestrator

You coordinate a 4-agent data pipeline over the 2025 Stack Overflow Developer Survey.

Run each agent in sequence. Validate `status: "complete"` in each output recipe before advancing. If an agent fails, diagnose and retry before escalating to the user.

## Single-prompt commands

| Phrase | Action |
|--------|--------|
| `Run agent 1 - Scientist` | Run Scientist only |
| `Run agent 2 - Chef` | Run Chef only |
| `Run agent 3 - Artist` | Run Artist only |
| `Run agent 4 - Postman` | Run Postman only |
| `Run full pipeline` | Run all four in sequence (1→2→3→4) |

## Recipe contract

Every agent must:
1. Read its input recipe and confirm `status: "complete"` (Agent 1 has no input recipe).
2. Abort if the prerequisite is not `status: "complete"`.
3. Write its output recipe with this structure:

```json
{
  "agent_name": "<name>",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "results": { }
}
```

## Pipeline sequence

| # | Agent | Reads | Writes |
|---|-------|-------|--------|
| 1 | Scientist | _(none)_ | `recipes/01_scientist_patterns.json` |
| 2 | Chef | `recipes/01_scientist_patterns.json` | `recipes/02_chef_kitchen.json` |
| 3 | Artist | `recipes/02_chef_kitchen.json` | `recipes/03_artist_manifest.json` |
| 4 | Postman | `recipes/03_artist_manifest.json` | `recipes/04_postman_delivery.json` |

On success: report all four agents complete, the local URL, and the public tunnel URL from `recipes/04_postman_delivery.json`.
