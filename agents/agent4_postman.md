# Agent 4 · Postman

**Job:** Write the data app, start a local Python server, open a public cloudflared tunnel, write the final recipe.

## Inputs
Reads `recipes/03_artist_manifest.json` — confirm `status: "complete"` before proceeding.

## Steps
1. **Kill any existing server** on port 8765: `lsof -ti:8765 | xargs kill -9 2>/dev/null || true`
2. **Start the server**: `python3 app/server.py &` — it reads from `recipes/03_artist_manifest.json` at `/api/data`.
3. **Verify** it's alive: `curl -s http://localhost:8765/api/data | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} charts loaded')"`
4. **Open cloudflared tunnel**: `cloudflared tunnel --url http://localhost:8765`
5. **Parse the `trycloudflare.com` URL** from stdout and print it clearly.

## Data app reference
`app/server.py` and `app/index.html` are already written. Only update them if the recipe data requires structural changes (e.g. new chart types not yet handled).

## Output: `recipes/04_postman_delivery.json`
```json
{
  "agent_name": "Postman",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "source_recipe": "recipes/03_artist_manifest.json",
  "delivery": {
    "local_url": "http://localhost:8765",
    "public_url": "https://<tunnel>.trycloudflare.com",
    "port": 8765,
    "server_file": "app/server.py",
    "app_file": "app/index.html",
    "charts_served": 5
  }
}
```
