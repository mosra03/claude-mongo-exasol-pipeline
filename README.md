# MCP Agentic Data Pipeline

A 4-agent Claude Code pipeline that exports a **MongoDB** collection into **Exasol**, builds live SQL analytics views, renders interactive ECharts visualisations, and publishes a live data app — end to end, from a single prompt.

---

## What this is

Point it at any MongoDB collection. Say **"Run full pipeline."** Four specialised agents — Scientist, Chef, Artist, Postman — discover patterns, build Exasol SQL views, render Apache ECharts charts, and publish a public URL via a cloudflared tunnel. No human steps between raw data and live app.

Built for developers who want to see what AI-native data engineering looks like in practice.

> **Why Exasol:** Exasol is the single source of truth — raw data, recipes, and analytics views all live there. Its in-memory MPP architecture delivers sub-second query performance on the full dataset, even on a free-trial instance. The data app queries Exasol live on every user interaction; no static data is baked in anywhere.

Demonstrated here on the [2025 Stack Overflow Developer Survey](https://survey.stackoverflow.co/2025) — 49,191 developers across 177 countries.

---

## How it works

![Architecture](assets/architecture.svg)

### Data flow

```
MongoDB Atlas
     ↓  scripts/load_mongodb.py  (CSV/JSON → MongoDB — once per dataset)
     ↓  scripts/ingest.py        (mongoexport → exasol-json-tables ingest-and-wrap)
     ↓
RAW_WRAPPER."survey_raw"  (Exasol — single source of truth)
     ↓  Agent 1 – Scientist
RECIPES.SCIENTIST  (Exasol table)
     ↓  Agent 2 – Chef
RECIPES.CHEF  (Exasol table)
ANALYTICS.*   (5 Exasol views)
     ↓  Agent 3 – Artist
app/server.py + app/index.html
     ↓  Agent 4 – Postman
Public URL (cloudflared)
```

| Agent | Data source | What it does |
|-------|-------------|--------------|
| **Scientist** | Exasol MCP → `RAW_WRAPPER."survey_raw"` | Explores schema, discovers 5 chart-worthy cross-dimensional patterns, writes to `RECIPES.SCIENTIST` |
| **Chef** | Exasol MCP → `RECIPES.SCIENTIST` | Runs SQL aggregations, creates `ANALYTICS` views with `WHERE 1=1` filter hooks, writes to `RECIPES.CHEF` |
| **Artist** | Exasol MCP → `RECIPES.CHEF` + `ANALYTICS.*` | Queries views for shape, generates `app/server.py` (pyexasol, live queries) and `app/index.html` (ECharts, no static data) |
| **Postman** | filesystem | Installs pyexasol, starts server on port 8080, opens cloudflared tunnel, writes `recipes/04_postman_delivery.json` |

---

## Pipeline state

Check pipeline progress at any time via SQL:

```sql
-- Raw data loaded?
SELECT COUNT(*) FROM RAW_WRAPPER."survey_raw";

-- Agent 1 complete?
SELECT status, pattern_count, created_at FROM RECIPES.SCIENTIST ORDER BY created_at DESC LIMIT 1;

-- Agent 2 complete?
SELECT status, view_count, created_at FROM RECIPES.CHEF ORDER BY created_at DESC LIMIT 1;

-- Analytics views built?
SELECT VIEW_NAME FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA = 'ANALYTICS' ORDER BY VIEW_NAME;
```

To reset and re-run from scratch:
```sql
DROP SCHEMA RECIPES CASCADE;
DROP SCHEMA ANALYTICS CASCADE;
```
Then run `python3 scripts/ingest.py` and `Run full pipeline`.

---

## Run it yourself

Works with **any** MongoDB collection — swap the Stack Overflow survey for your own data in step 1.

### Prerequisites

| Tool | Install |
|------|---------|
| Python 3.10+ | `brew install python` or [python.org](https://python.org) |
| pyexasol | `pip install pyexasol` |
| pymongo | `pip install pymongo` |
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| MongoDB Atlas | Free M0 at [cloud.mongodb.com](https://cloud.mongodb.com) |
| MongoDB Tools (mongoexport) | `brew install mongodb-database-tools` |
| exasol-json-tables | `pip install exasol-json-tables` |
| Exasol | See "Getting Exasol" below |
| Exasol MCP Server | See MCP config below |
| cloudflared | `brew install cloudflare/cloudflare/cloudflared` |

### Getting Exasol

**Option A — Exasol SaaS** *(recommended — $200 free trial, no card required)*
Sign up at [cloud.exasol.com/signup](https://cloud.exasol.com/signup)

**Option B — Exasol Personal** *(free, no expiry, single user, runs locally)*
```bash
curl https://downloads.exasol.com/exasol-personal/installer.sh | sh
```

**Option C — Exasol Community Edition** *(free VM, up to 200 GB)*
Download at [Exasol Community Edition](https://github.com/exasol-labs/exasol-labs-community-edition)

### MCP server config (`~/.claude/settings.json`)

```json
{
  "mcpServers": {
    "mongodb-mcp": {
      "command": "npx",
      "args": ["-y", "mongodb-mcp-server"],
      "env": {
        "MDB_MCP_CONNECTION_STRING": "mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/"
      }
    },
    "exasol-mcp": {
      "command": "uvx",
      "args": ["exasol-mcp"],
      "env": {
        "EXASOL_HOST": "<your-exasol-host>",
        "EXASOL_USER": "<your-user>",
        "EXASOL_PASSWORD": "<your-password>"
      }
    }
  }
}
```

> `mongodb-mcp` is used only if you re-run `scripts/ingest_exasol.py` interactively. The pipeline agents connect to Exasol only.

### Steps

1. **Load your data into MongoDB** (once per dataset):
   ```bash
   python3 scripts/load_mongodb.py --file /path/to/your/data.csv
   python3 scripts/load_mongodb.py --file /path/to/your/data.json
   ```
   Supports: `.csv` and `.json`/`.ndjson`. For the Stack Overflow example: download the 2025 survey CSV from [survey.stackoverflow.co/2025](https://survey.stackoverflow.co/2025).

2. **Clone and open in Claude Code**
   ```bash
   git clone https://github.com/mosra03/mcp-agentic-data-pipeline.git
   cd mcp-agentic-data-pipeline
   ```

3. **Create a virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install exasol-json-tables
   ```

4. **Set environment variables** — copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   # then edit .env
   ```
   Required:
   ```bash
   MONGODB_URI=mongodb+srv://...
   EXASOL_HOST=<your-cluster>.clusters.exasol.com
   EXASOL_PORT=8563
   EXASOL_USER=<your-user>
   EXASOL_PASSWORD=<your-password>
   ```

5. **Export from MongoDB and load into Exasol** (once per dataset):
   ```bash
   source venv/bin/activate
   python3 scripts/ingest.py
   ```
   This exports whatever is in MongoDB and loads it into Exasol via `exasol-json-tables`. Run this again any time you want to refresh Exasol with latest MongoDB data.

   > **Steps 1 and 5 are independent.**
   > Already have data in MongoDB? Skip step 1, run step 5 only.
   > Want to use a new dataset? Run step 1 with your new file, then step 5.
   > MongoDB IP error? Update at: MongoDB Atlas → Security → Network Access

6. **Open in Claude Code**
   ```bash
   claude
   ```

7. **Verify your MCP connections**
   ```
   /mcp
   ```
   `exasol-mcp` must show as connected. `mongodb-mcp` is optional after ingest.

8. **Run the full pipeline with one prompt**
   ```
   Run full pipeline
   ```
   Or run agents individually to debug or re-run a single stage:
   ```
   Run agent 1 - Scientist
   Run agent 2 - Chef
   Run agent 3 - Artist
   Run agent 4 - Postman
   ```

9. **Open your live URL** — printed at the end of Agent 4. Works in any browser, no login.

> The `data-pipeline-analyst` skill in `skills/` auto-loads in Claude Code, giving every agent full pipeline context without re-reading the repo each time.

---

## Dataset used

[2025 Stack Overflow Developer Survey](https://survey.stackoverflow.co/2025) — 49,191 developers, 177 countries, 173 fields. Covers compensation, AI tool adoption, remote work arrangements, job satisfaction, programming languages, and more.

---

## Built with Exasol Labs

| Tool | How it's used |
|------|---------------|
| [exasol-json-tables](https://github.com/exasol-labs/exasol-json-tables) | Ingests NDJSON from MongoDB into native Exasol tables — zero schema config required; activates JSON path syntax for nested fields |
| [exasol-agent-skills](https://github.com/exasol-labs/exasol-agent-skills) | Claude Code plugin that gives Claude deep Exasol SQL expertise (functions, types, aggregations) |
| [exapump](https://github.com/exasol-labs/exapump) | Fast CLI for bulk data import/export between local files and Exasol |
| [Exasol MCP Server](https://github.com/exasol/mcp-server) | MCP server connecting Claude Code directly to Exasol for SQL queries and schema inspection |

---

## Screenshots

<table>
  <tr>
    <td><img src="assets/chart1_ai_adoption_compensation.png" width="100%" alt="AI Adoption vs Compensation"/><br/><sub>AI Adoption vs Compensation — The Productivity Paradox</sub></td>
    <td><img src="assets/chart2_global_salary_landscape.png" width="100%" alt="Global Salary Landscape"/><br/><sub>Global Salary Landscape — A 5× Gap from US to India</sub></td>
  </tr>
  <tr>
    <td><img src="assets/chart3_remote_work_premium.png" width="100%" alt="Remote Work Premium"/><br/><sub>Remote Work Premium — Full Remote Pays 58% More</sub></td>
    <td><img src="assets/chart4_ai_model_market_share.png" width="100%" alt="AI Model Market Share"/><br/><sub>AI Model Market Share — GPT Leads, Claude #2</sub></td>
  </tr>
  <tr>
    <td><img src="assets/chart5_ai_threat_by_experience.png" width="100%" alt="AI Job Threat by Experience"/><br/><sub>AI Job Threat by Experience — Beginners Most Anxious</sub></td>
    <td></td>
  </tr>
</table>

---

## Tech stack

| Component | Role |
|-----------|------|
| **Claude Code** | Orchestrator — drives agents, validates Exasol state, enforces sequencing |
| **MongoDB Atlas M0** | Source database — stores survey data as BSON documents; exported once via mongoexport |
| **Exasol SaaS** | Single source of truth — RAW data, recipe tables, analytics views, live queries |
| **exasol-json-tables** | Loads NDJSON into Exasol with JSON path query support |
| **Exasol MCP Server** | Gives Claude Code direct query access to Exasol for all pipeline agents |
| **pyexasol** | Python driver used by the live data app server to query Exasol |
| **Apache ECharts** | Client-side charting — bar, choropleth, line, grouped bar |
| **Python http.server** | Minimal web server — serves `index.html` and `/api/query` (live Exasol queries) |
| **cloudflared Quick Tunnel** | Instant public HTTPS URL — no account or port-forwarding needed |

---

MIT License
