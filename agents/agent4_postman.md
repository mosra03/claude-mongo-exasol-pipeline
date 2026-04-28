# Agent 4 · Postman

**Job:** Install dependencies, start the data app server, open a cloudflared tunnel, write `recipes/04_postman_delivery.json`.

**Single prompt trigger:** `Run agent 4 - Postman`

## Prerequisite
Check that `app/server.py` and `app/index.html` exist:
```bash
test -f app/server.py && test -f app/index.html && echo "OK"
```
If either is missing, stop and report: **Agent 3 has not completed — run Agent 3 first.**

## Steps

1. **Install pyexasol** if not already present:
   ```bash
   pip install pyexasol --quiet
   ```

2. **Kill any existing process on port 8080**:
   ```bash
   lsof -ti:8080 | xargs kill -9 2>/dev/null || true
   ```

3. **Start the server**:
   ```bash
   python3 app/server.py --port 8080 &
   ```

4. **Wait 2 seconds** for the server to initialise.

5. **Verify the server is responding**:
   ```bash
   curl -s "http://localhost:8080/api/query?view_name=test" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Server alive')"
   ```
   A 400 response (unknown view) is acceptable — it confirms the server is running.

6. **Open cloudflared tunnel**:
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```
   Parse the `trycloudflare.com` URL from stdout (appears after `+---`).

7. **Write `recipes/04_postman_delivery.json`** (this file stays local — it holds an ephemeral URL):
   ```json
   {
     "agent_name": "Postman",
     "status": "complete",
     "timestamp": "<ISO-8601>",
     "delivery": {
       "local_url": "http://localhost:8080",
       "public_url": "https://<tunnel>.trycloudflare.com",
       "port": 8080,
       "server_file": "app/server.py",
       "app_file": "app/index.html"
     }
   }
   ```

## Notes
- `app/server.py` and `app/index.html` are written by Agent 3. Do not modify them.
- The `recipes/04_postman_delivery.json` is the only local recipe file — tunnel URLs are ephemeral and not stored in Exasol.
- If cloudflared is not installed: `brew install cloudflare/cloudflare/cloudflared`
