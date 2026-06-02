# CodeViz MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes the
CodeViz backend as agent-callable tools. An MCP client (Claude Desktop, etc.) can
drive the full CodeViz workflow — create a scan session for a repo, scan it, then
pull security findings, multi-dimensional risk scores, compliance framework checks,
refactoring opportunities, and generate / email / schedule reports.

- **Language / SDK:** Python, [`mcp`](https://pypi.org/project/mcp/) (FastMCP)
- **Transport:** stdio (local)
- **Server name:** `codeviz_mcp`
- **Wraps:** the CodeViz Flask API (`/api/*`)

> **Why `mcp_server/` and not `mcp/`?** A top-level folder literally named `mcp`
> becomes an implicit namespace package that shadows the installed `mcp` SDK, so
> `from mcp.server.fastmcp import FastMCP` would break when run from the repo root.

## Prerequisites

The CodeViz backend must be running and reachable. From the repo root:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py        # serves http://localhost:8000
```

## Install

```bash
cd mcp_server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` (or export the variables):

| Variable | Default | Purpose |
| --- | --- | --- |
| `CODEVIZ_BASE_URL` | `http://localhost:8000` | Backend base URL |
| `CODEVIZ_TOKEN` | _(empty)_ | GitHub token sent as `Authorization: Bearer …` (private repos, GitHub repo listing) |
| `CODEVIZ_TIMEOUT` | `120` | Per-request timeout (seconds); raise for large scans |
| `CODEVIZ_REPORT_DIR` | `./codeviz-reports` | Where generated PDF/HTML reports are written |

## Run

```bash
python codeviz_mcp.py     # speaks MCP over stdio
```

### Claude Desktop config

Add to `claude_desktop_config.json` (use absolute paths):

```json
{
  "mcpServers": {
    "codeviz": {
      "command": "/abs/path/to/CODEVIZ/mcp_server/.venv/bin/python",
      "args": ["/abs/path/to/CODEVIZ/mcp_server/codeviz_mcp.py"],
      "env": {
        "CODEVIZ_BASE_URL": "http://localhost:8000",
        "CODEVIZ_TOKEN": ""
      }
    }
  }
}
```

## Typical workflow

1. `codeviz_health` — confirm the backend is up.
2. `codeviz_create_session` — pass a GitHub URL or local path → get a `session_id`.
3. `codeviz_scan` — scan the session (required before the analysis tools).
4. Analyze:
   - `codeviz_get_score` — multi-dimensional risk profile
   - `codeviz_security_scan` / `codeviz_get_security_report`
   - `codeviz_get_compliance` / `codeviz_get_framework_compliance`
   - `codeviz_refactoring_opportunities` → `codeviz_refactoring_suggest`
5. `codeviz_generate_report` — write a PDF to `CODEVIZ_REPORT_DIR`.

## Tools (37)

**Health / discovery:** `codeviz_health`, `codeviz_info`, `codeviz_ping_endpoint`

**Sessions / scanning:** `codeviz_create_session`, `codeviz_scan`,
`codeviz_get_artifacts`, `codeviz_ask`, `codeviz_get_history`, `codeviz_clear_session`

**Security:** `codeviz_security_scan`, `codeviz_get_bugs`, `codeviz_get_bug_fix`,
`codeviz_get_security_report`

**Risk scoring:** `codeviz_get_score`, `codeviz_score_preview`

**Compliance:** `codeviz_list_frameworks`, `codeviz_get_compliance`,
`codeviz_get_framework_compliance`

**Refactoring:** `codeviz_refactoring_opportunities`, `codeviz_refactoring_suggest`,
`codeviz_refactoring_pr_content`, `codeviz_create_pr`

**Reports / schedules:** `codeviz_generate_report`, `codeviz_preview_report`,
`codeviz_email_report`, `codeviz_list_schedules`, `codeviz_create_schedule`,
`codeviz_delete_schedule`, `codeviz_run_schedule`

**Repository registry:** `codeviz_list_repositories`,
`codeviz_list_github_repositories`, `codeviz_add_repository`,
`codeviz_get_repository`, `codeviz_update_repository`, `codeviz_delete_repository`,
`codeviz_scan_registered_repository`, `codeviz_get_scan_history`

## Notes

- Most read tools accept `response_format` = `json` (default, structured) or
  `markdown` (readable).
- Report tools return binary/HTML, so the server writes the file to disk and
  returns its path.
- Tool annotations mark read-only vs. destructive operations
  (`codeviz_clear_session`, `codeviz_delete_schedule`, `codeviz_delete_repository`
  are destructive).
- Auth/OAuth login endpoints are intentionally omitted — they are browser-redirect
  flows; use `CODEVIZ_TOKEN` for authenticated calls instead.
