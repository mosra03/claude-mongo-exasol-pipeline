# Agent 5 · Publisher

## Role
Write the web app, start the local server, and open a public cloudflared Quick Tunnel.

## Inputs
- Visualiser output: array of 10 ECharts option objects with questions and chart types.

## Tasks
1. Write `app/server.py`:
   - Python `http.server` on port 8765.
   - Serves `index.html` at `/`.
   - Serves `/api/data` returning the 10 ECharts configs as JSON.

2. Write `app/index.html`:
   - Single-page app, no build step.
   - Dark theme (`background: #1a1a2e`).
   - Header: "2025 Stack Overflow Developer Survey · AI Pipeline Analysis".
   - Navigation tabs — one tab per question (use question text as tab label, truncated to 40 chars).
   - Each tab renders one ECharts chart in a `div` sized `100% × 500px`.
   - Footer: "Powered by Claude Code · MongoDB Atlas · Exasol SaaS · Apache ECharts".
   - Fetches `/api/data` on load, initialises all charts, switches on tab click.

3. Start the server:
   ```bash
   python3 app/server.py &
   ```

4. Open cloudflared tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:8765
   ```

5. Parse the `trycloudflare.com` URL from cloudflared stdout and print it clearly.

## Output
Print the public URL and confirm all 10 charts are served.
