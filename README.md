# MCP Agentic Data Pipeline

A 5-agent AI pipeline that analyses the **2025 Stack Overflow Developer Survey** — 49,191 developers across 177 countries — and publishes a live, interactive analytics app. Every step from raw data loading through insight generation to a public URL is coordinated by Claude Code acting as Orchestrator, with MongoDB Atlas and Exasol SaaS as the data backbone.

---

## What this pipeline does

```
Raw survey CSV
      │
      ▼
[Agent 1 · Scientist]  ──── designs 10 analytical questions
      │
      ▼
[Agent 2 · Loader]  ──────── imports CSV → MongoDB Atlas (M0)
      │
      ▼
[Agent 3 · Analyst]  ─────── queries Mongo, pushes to Exasol, runs SQL analytics
      │
      ▼
[Agent 4 · Visualiser]  ──── generates Apache ECharts JSON config per question
      │
      ▼
[Agent 5 · Publisher]  ───── writes server.py + index.html, opens cloudflared tunnel
      │
      ▼
  Public URL (no login required)
```

The Orchestrator (Claude Code) drives all five agents sequentially, passing results forward as structured context. No human intervention is required between steps.

---

## The 5 Agents

| # | Agent | Role | Key tools |
|---|-------|------|-----------|
| 1 | **Scientist** | Reads the survey schema and proposes 10 data questions worth answering | MongoDB MCP |
| 2 | **Loader** | Streams the CSV into a MongoDB Atlas M0 collection, validates row count | MongoDB MCP |
| 3 | **Analyst** | Runs aggregation pipelines in Mongo, migrates result sets to Exasol, executes SQL analytics | MongoDB MCP · Exasol MCP · exapump |
| 4 | **Visualiser** | Converts each analytic result into an Apache ECharts option object | Exasol MCP |
| 5 | **Publisher** | Writes the web app, starts a Python HTTP server, opens a cloudflared Quick Tunnel | Bash |

---

## Tech stack

| Component | Purpose |
|-----------|---------|
| **Claude Code** | Orchestration — drives agents, passes context, enforces sequencing |
| **MongoDB Atlas M0** | Source database — stores raw survey responses as BSON documents |
| **MongoDB MCP Server** | Gives Claude Code read/write access to Atlas without leaving the terminal |
| **Exasol SaaS** | Analytics engine — columnar SQL for fast aggregations over 49 k rows |
| **Exasol MCP Server** | Lets Claude Code query Exasol, inspect schemas, and stream results |
| **exasol-json-tables** | Converts JSON result sets from Mongo into Exasol-importable tables |
| **exapump** | CLI for bulk data transfer between local files and Exasol / BucketFS |
| **Apache ECharts** | Client-side charting library (bar, line, scatter, map, heatmap …) |
| **cloudflared Quick Tunnel** | Instant public HTTPS URL for the local Python server — no account needed |
| **Dataset** | [2025 Stack Overflow Developer Survey](https://survey.stackoverflow.co/) — 49,191 developers, 177 countries |

---

## Folder structure

```
mcp-agentic-data-pipeline/
├── agents/
│   ├── orchestrator.md          # Orchestrator prompt (this pipeline)
│   ├── agent1_scientist.md      # Scientist agent prompt
│   ├── agent2_loader.md         # Loader agent prompt
│   ├── agent3_analyst.md        # Analyst agent prompt
│   ├── agent4_visualiser.md     # Visualiser agent prompt
│   └── agent5_publisher.md      # Publisher agent prompt
├── app/
│   ├── server.py                # Python HTTP server (serves index.html + /api/data)
│   └── index.html               # Single-page analytics app (Apache ECharts)
├── data/
│   └── survey_results.csv       # 2025 Stack Overflow Developer Survey (add locally)
├── assets/
│   └── demo.gif                 # Pipeline demo recording
└── README.md
```

---

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.10+ | `brew install python` or [python.org](https://python.org) |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |
| MongoDB Atlas account | Free M0 cluster at [cloud.mongodb.com](https://cloud.mongodb.com) |
| MongoDB MCP Server | Configured in `~/.claude/settings.json` (see below) |
| Exasol SaaS account | Free trial at [cloud.exasol.com](https://cloud.exasol.com) |
| Exasol MCP Server | Configured in `~/.claude/settings.json` (see below) |
| exapump | `pip install exapump` |
| cloudflared | `brew install cloudflare/cloudflare/cloudflared` |

### MCP server configuration (`~/.claude/settings.json`)

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

---

## Running the pipeline with your own data

1. **Download the dataset**
   Go to [https://survey.stackoverflow.co/](https://survey.stackoverflow.co/), download the 2025 survey ZIP, and place `survey_results.csv` in the `data/` folder.

2. **Clone this repo and open in Claude Code**
   ```bash
   git clone https://github.com/<you>/mcp-agentic-data-pipeline.git
   cd mcp-agentic-data-pipeline
   claude
   ```

3. **Configure your MCP servers** as shown above, then verify connectivity:
   ```
   /mcp
   ```

4. **Start the Orchestrator**
   Paste the contents of `agents/orchestrator.md` into the Claude Code prompt and press Enter. The pipeline runs automatically from Agent 1 through Agent 5.

5. **Open your public URL**
   At the end of Agent 5 the terminal prints a `trycloudflare.com` URL. Open it in any browser — no login, no port-forwarding required.

---

## Sample questions the pipeline answers

1. What percentage of developers use AI tools in their daily workflow?
2. Which programming languages have the highest median salary?
3. How does years of experience correlate with total compensation?
4. What is the geographic distribution of professional developers?
5. Which databases are most popular among different developer roles?
6. How do remote, hybrid, and in-office developers compare on job satisfaction?
7. What is the most common path into software development (education vs. self-taught)?
8. Which cloud platforms dominate among developers who work with AI/ML?
9. How does company size affect technology stack choices?
10. What tools do the highest-paid 10% of developers have in common?

---

## Architecture diagram

```
                    ┌─────────────────────────────────┐
                    │        Claude Code CLI           │
                    │     (Orchestrator agent)         │
                    └────────────┬────────────────────┘
                                 │ coordinates
          ┌──────────────────────┼──────────────────────┐
          │                      │                       │
          ▼                      ▼                       ▼
   MongoDB MCP              Exasol MCP               Bash
   ──────────              ──────────              ──────────
   Atlas M0                Exasol SaaS             cloudflared
   (raw docs)          (analytics SQL)          (public tunnel)
          │                      │
          └──────────┬───────────┘
                     │
              exapump / JSON tables
              (ETL bridge)
                     │
                     ▼
             Apache ECharts
             (interactive charts
              in index.html)
```

---

## License

MIT — use freely, attribution appreciated.

---

*Built with Claude Code · MongoDB Atlas · Exasol SaaS · Apache ECharts · cloudflared*
