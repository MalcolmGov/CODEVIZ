#!/usr/bin/env python3
"""
CodeViz MCP Server.

Exposes the CodeViz code-analysis platform (a Flask backend) as MCP tools so an
agent can drive the full workflow: create a scan session for a repository, scan
it, then query security findings, multi-dimensional risk scores, compliance
framework checks, refactoring opportunities, and generate/email/schedule reports.

Transport: stdio (local).

Typical workflow:
    1. codeviz_create_session(repo_path="https://github.com/owner/repo")
    2. codeviz_scan(session_id=...)            # populates artifacts
    3. codeviz_get_score(session_id=...)       # risk profile
       codeviz_get_compliance(session_id=...)  # framework checks
       codeviz_security_scan(session_id=...)   # vulnerabilities
       codeviz_refactoring_opportunities(...)  # refactors
    4. codeviz_generate_report(session_id=...) # PDF on disk

Configuration (environment variables):
    CODEVIZ_BASE_URL   Base URL of the backend (default http://localhost:8000)
    CODEVIZ_TOKEN      Optional GitHub token sent as Authorization: Bearer <token>
    CODEVIZ_TIMEOUT    Per-request timeout in seconds (default 120)
    CODEVIZ_REPORT_DIR Directory for generated reports (default ./codeviz-reports)
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator
from mcp.server.fastmcp import FastMCP

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

BASE_URL: str = os.getenv("CODEVIZ_BASE_URL", "http://localhost:8000").rstrip("/")
API_ROOT: str = f"{BASE_URL}/api"
TOKEN: str = os.getenv("CODEVIZ_TOKEN", "").strip()
TIMEOUT: float = float(os.getenv("CODEVIZ_TIMEOUT", "120"))
REPORT_DIR: Path = Path(os.getenv("CODEVIZ_REPORT_DIR", "./codeviz-reports")).expanduser()

mcp = FastMCP("codeviz_mcp")


# --------------------------------------------------------------------------- #
# Shared models / enums
# --------------------------------------------------------------------------- #

class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    JSON = "json"
    MARKDOWN = "markdown"


class _Base(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


# --------------------------------------------------------------------------- #
# Shared utilities
# --------------------------------------------------------------------------- #

class CodevizError(Exception):
    """Raised when the CodeViz backend returns an error envelope."""


def _headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {"Accept": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    if extra:
        headers.update(extra)
    return headers


async def _request_json(
    method: str,
    path: str,
    *,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call the backend and unwrap its {status, data, message} envelope.

    Returns a dict: {"data": <payload>, "message": <str|None>}.
    Raises CodevizError on an "error" envelope, httpx errors otherwise.
    """
    url = f"{API_ROOT}{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.request(
            method, url, json=json_body, params=params, headers=_headers()
        )
    # Health endpoints may return 503 with a JSON body we still want to read.
    try:
        body = resp.json()
    except Exception:
        resp.raise_for_status()
        raise CodevizError(f"Non-JSON response from {url} (HTTP {resp.status_code})")

    # Endpoints that DON'T use the envelope (health/status/info) return their
    # payload directly. Detect the envelope by the presence of "status" + either
    # "data" or "message".
    if isinstance(body, dict) and body.get("status") == "error":
        raise CodevizError(body.get("message") or f"Backend error (HTTP {resp.status_code})")
    if isinstance(body, dict) and "data" in body and "status" in body:
        return {"data": body.get("data"), "message": body.get("message")}
    # Raw payload (non-envelope endpoint)
    return {"data": body, "message": None}


async def _request_bytes(
    method: str, path: str, *, json_body: Optional[Dict[str, Any]] = None
) -> tuple[bytes, str]:
    """Call an endpoint that returns binary/text content (reports).

    Returns (content_bytes, suggested_filename).
    Raises CodevizError if the backend returns a JSON error envelope instead.
    """
    url = f"{API_ROOT}{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.request(method, url, json=json_body, headers=_headers())
    ctype = resp.headers.get("Content-Type", "")
    if "application/json" in ctype:
        try:
            body = resp.json()
            if isinstance(body, dict) and body.get("status") == "error":
                raise CodevizError(body.get("message") or "Report generation failed")
        except CodevizError:
            raise
        except Exception:
            pass
    resp.raise_for_status()
    # Parse filename from Content-Disposition if present
    disp = resp.headers.get("Content-Disposition", "")
    filename = ""
    if "filename=" in disp:
        filename = disp.split("filename=", 1)[1].strip().strip('"')
    return resp.content, filename


def _handle_error(e: Exception) -> str:
    """Consistent, actionable error formatting across all tools."""
    if isinstance(e, CodevizError):
        return f"Error: {e}"
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        if code == 404:
            return ("Error: Not found (404). Check the session_id/repo_id is correct "
                    "and that the session was created and scanned first.")
        if code == 401:
            return "Error: Unauthorized (401). Set CODEVIZ_TOKEN to a valid GitHub token."
        if code == 503:
            return "Error: A backend dependency is unavailable (503). Check /api/health."
        return f"Error: Backend request failed with HTTP {code}."
    if isinstance(e, httpx.ConnectError):
        return (f"Error: Could not connect to the CodeViz backend at {BASE_URL}. "
                "Is it running? Start it with `python main.py` in the backend/ dir, "
                "or set CODEVIZ_BASE_URL.")
    if isinstance(e, httpx.TimeoutException):
        return ("Error: Request timed out. Scans of large repos can be slow — "
                "increase CODEVIZ_TIMEOUT.")
    return f"Error: Unexpected {type(e).__name__}: {e}"


def _to_markdown(obj: Any, level: int = 0) -> str:
    """Render a JSON-ish structure as readable markdown (generic fallback)."""
    pad = "  " * level
    lines: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}- **{k}**:")
                lines.append(_to_markdown(v, level + 1))
            else:
                lines.append(f"{pad}- **{k}**: {v}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}- [{i}]")
                lines.append(_to_markdown(item, level + 1))
            else:
                lines.append(f"{pad}- {item}")
    else:
        lines.append(f"{pad}{obj}")
    return "\n".join(l for l in lines if l.strip())


def _render(payload: Dict[str, Any], fmt: ResponseFormat) -> str:
    """Format the unwrapped {data, message} result for return."""
    data = payload.get("data")
    message = payload.get("message")
    if fmt == ResponseFormat.MARKDOWN:
        md = _to_markdown(data) if data not in (None, {}, []) else "_(no data)_"
        header = f"**{message}**\n\n" if message else ""
        return f"{header}{md}"
    out: Dict[str, Any] = {"data": data}
    if message:
        out["message"] = message
    return json.dumps(out, indent=2, default=str)


# --------------------------------------------------------------------------- #
# Input models
# --------------------------------------------------------------------------- #

class SessionInput(_Base):
    session_id: str = Field(..., description="Session id returned by codeviz_create_session (e.g. 'a1b2c3d4').", min_length=1, max_length=64)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' (structured) or 'markdown' (readable).")


class CreateSessionInput(_Base):
    repo_path: str = Field(..., description="A GitHub URL (https://github.com/owner/repo) or a local filesystem path to the repository to analyze.", min_length=1)
    branch: Optional[str] = Field(default="main", description="Branch to clone/scan when repo_path is a remote URL.", max_length=200)


class AskInput(_Base):
    session_id: str = Field(..., description="Session id of a scanned repository.", min_length=1, max_length=64)
    question: str = Field(..., description="Natural-language question about the scanned repository (e.g. 'Which endpoints lack auth?').", min_length=1, max_length=2000)


class BugIdInput(_Base):
    bug_id: str = Field(..., description="Identifier of a security bug returned by codeviz_security_scan.", min_length=1, max_length=128)


class ScorePreviewInput(_Base):
    artifacts: Dict[str, Any] = Field(..., description="Raw scan-artifacts object (apis, classes, functions, etc.) to score directly, without a session.")
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' or 'markdown'.")


class ComplianceInput(_Base):
    session_id: str = Field(..., description="Session id of a scanned repository.", min_length=1, max_length=64)
    frameworks: Optional[str] = Field(default=None, description="Comma-separated framework ids to limit the check (e.g. 'owasp,soc2'). Omit to run all.", max_length=300)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' or 'markdown'.")


class FrameworkComplianceInput(_Base):
    session_id: str = Field(..., description="Session id of a scanned repository.", min_length=1, max_length=64)
    framework_id: str = Field(..., description="A single framework id (see codeviz_list_frameworks).", min_length=1, max_length=64)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' or 'markdown'.")


class OpportunityInput(_Base):
    session_id: str = Field(..., description="Session id of a scanned repository.", min_length=1, max_length=64)
    opp_index: int = Field(..., description="Zero-based index of a refactoring opportunity from codeviz_refactoring_opportunities.", ge=0, le=1000)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' or 'markdown'.")


class FormatOnlyInput(_Base):
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' or 'markdown'.")


class PingEndpointInput(_Base):
    path: str = Field(..., description="Request path to test, e.g. '/api/users' or '/health'.", min_length=1, max_length=2000)
    method: str = Field(default="GET", description="HTTP method to use (GET, POST, PUT, DELETE).", max_length=10)
    base_url: Optional[str] = Field(default=None, description="Override base URL of the target host. If omitted the backend infers it from the active session.", max_length=500)


class ReportFileInput(_Base):
    session_id: str = Field(..., description="Session id of a scanned repository.", min_length=1, max_length=64)
    output_path: Optional[str] = Field(default=None, description="Where to write the report file. Defaults to CODEVIZ_REPORT_DIR with an auto-generated name.", max_length=1000)


class EmailReportInput(_Base):
    session_id: str = Field(..., description="Session id of a scanned repository.", min_length=1, max_length=64)
    email: str = Field(..., description="Recipient email address.", pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$")


class CreateScheduleInput(_Base):
    repo_paths: List[str] = Field(..., description="One or more repo URLs/paths to include in the scheduled report.", min_length=1, max_length=50)
    recipients: List[str] = Field(..., description="Email recipients for the scheduled report.", min_length=1, max_length=50)
    frequency: str = Field(default="daily", description="'daily' or 'weekly' (ignored if cron is given).", max_length=20)
    hour: int = Field(default=6, description="Hour of day (0-23) to send when using frequency.", ge=0, le=23)
    label: Optional[str] = Field(default="", description="Human-friendly label for the schedule.", max_length=200)
    timezone: str = Field(default="UTC", description="IANA timezone name (e.g. 'Africa/Johannesburg').", max_length=64)
    cron: Optional[str] = Field(default="", description="Optional explicit cron expression overriding frequency/hour.", max_length=120)


class ScheduleIdInput(_Base):
    schedule_id: str = Field(..., description="Id of a schedule from codeviz_list_schedules.", min_length=1, max_length=128)


class AddRepoInput(_Base):
    name: str = Field(..., description="Display name for the repository.", min_length=1, max_length=200)
    url: str = Field(..., description="Repository URL.", min_length=1, max_length=500)
    branch: Optional[str] = Field(default="main", description="Default branch.", max_length=200)


class RepoIdInput(_Base):
    repo_id: str = Field(..., description="Repository id from codeviz_list_repositories.", min_length=1, max_length=128)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="'json' or 'markdown'.")


class UpdateRepoInput(_Base):
    repo_id: str = Field(..., description="Repository id to update.", min_length=1, max_length=128)
    name: Optional[str] = Field(default=None, description="New display name.", max_length=200)
    url: Optional[str] = Field(default=None, description="New URL.", max_length=500)
    branch: Optional[str] = Field(default=None, description="New default branch.", max_length=200)


class CreatePrInput(_Base):
    repo_name: str = Field(..., description="owner/repo to open the PR against.", min_length=1, max_length=200)
    pr_content: Dict[str, Any] = Field(..., description="PR content object from codeviz_refactoring_pr_content (title, description, branch).")
    github_token: str = Field(..., description="GitHub token with permission to open a PR on the target repo.", min_length=1, max_length=200)


# --------------------------------------------------------------------------- #
# Tools: health & discovery
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_health",
    annotations={"title": "Backend health check", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def codeviz_health(params: FormatOnlyInput) -> str:
    """Report the health of the CodeViz backend and its dependencies.

    Checks the Flask app, database, Redis cache, and Ollama LLM. Use this first
    to confirm the backend is reachable before starting a scan workflow.

    Returns:
        str: JSON or markdown with per-service {status, type} entries and an
        overall status of 'healthy' or 'degraded'.
    """
    try:
        return _render(await _request_json("GET", "/health"), params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_info",
    annotations={"title": "Platform info", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_info(params: FormatOnlyInput) -> str:
    """Return platform name, version, environment, and available endpoint groups.

    Returns:
        str: JSON or markdown describing the CodeViz deployment.
    """
    try:
        return _render(await _request_json("GET", "/info"), params.response_format)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: sessions & scanning
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_create_session",
    annotations={"title": "Create scan session", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def codeviz_create_session(params: CreateSessionInput) -> str:
    """Create a new analysis session for a repository.

    For a remote GitHub URL the backend clones the repo (using CODEVIZ_TOKEN for
    private repos); for a local path it uses it directly. This does NOT scan yet —
    call codeviz_scan next with the returned session_id.

    Args:
        params: repo_path (GitHub URL or local path) and optional branch.

    Returns:
        str: JSON with {session_id, repo_path}. Keep session_id for all
        subsequent calls.
    """
    try:
        body = {"repo_path": params.repo_path, "branch": params.branch or "main"}
        return _render(await _request_json("POST", "/chat/session", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_scan",
    annotations={"title": "Scan repository", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_scan(params: SessionInput) -> str:
    """Scan a session's repository to extract code artifacts.

    Populates the session with files, LOC, APIs, functions, classes, and an
    initial security-issue count. Most other tools (scoring, compliance,
    refactoring, reports) require a scan to have run first.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown with {session_id, scan_status:{files, loc, apis,
        functions, classes, security_issues}}.
    """
    try:
        return _render(await _request_json("POST", f"/chat/scan/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_artifacts",
    annotations={"title": "Get scan artifacts", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_artifacts(params: SessionInput) -> str:
    """Return the full artifact context discovered during a scan.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown of the artifacts object (apis, classes, functions,
        repo_name, etc.). Large — prefer 'json' for downstream processing.
    """
    try:
        return _render(await _request_json("GET", f"/chat/artifacts/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_ask",
    annotations={"title": "Ask about repository", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def codeviz_ask(params: AskInput) -> str:
    """Ask a natural-language question about a scanned repository.

    Uses the backend's Q&A over scan context (LLM-backed when Ollama is
    available). The repository must already be scanned.

    Args:
        params: session_id and question.

    Returns:
        str: JSON with {session_id, question, answer}.
    """
    try:
        body = {"session_id": params.session_id, "question": params.question}
        return _render(await _request_json("POST", "/chat/ask", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_history",
    annotations={"title": "Get Q&A history", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_history(params: SessionInput) -> str:
    """Return the conversation history for a session.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown with {session_id, history:[...]}.
    """
    try:
        return _render(await _request_json("GET", f"/chat/history/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_clear_session",
    annotations={"title": "Clear session", "readOnlyHint": False,
                 "destructiveHint": True, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_clear_session(params: SessionInput) -> str:
    """Delete a session and remove any temporary cloned files. Destructive.

    Args:
        params: session_id.

    Returns:
        str: JSON confirming the session was cleared.
    """
    try:
        return _render(await _request_json("POST", f"/chat/clear/{params.session_id}"),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: security
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_security_scan",
    annotations={"title": "Scan for vulnerabilities", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_security_scan(params: SessionInput) -> str:
    """Run static security analysis over a scanned session's repository.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown with {bugs:[{severity, ...}], summary:{total,
        critical, high}}.
    """
    try:
        return _render(await _request_json("POST", f"/security/scan/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_bugs",
    annotations={"title": "Get security bugs", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_bugs(params: SessionInput) -> str:
    """Return previously detected security bugs for a session.

    Note: bugs are computed on demand — if this returns an empty list, run
    codeviz_security_scan first.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown with {session_id, bugs:[...]}.
    """
    try:
        return _render(await _request_json("GET", f"/security/bugs/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_bug_fix",
    annotations={"title": "Get suggested bug fix", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def codeviz_get_bug_fix(params: BugIdInput) -> str:
    """Return a suggested before/after fix for a specific security bug.

    Args:
        params: bug_id.

    Returns:
        str: JSON with {bug_id, fix:{before, after, explanation}}.
    """
    try:
        return _render(await _request_json("GET", f"/security/fix/{params.bug_id}"),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_security_report",
    annotations={"title": "Get security report summary", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_security_report(params: SessionInput) -> str:
    """Return a severity-bucketed security summary for a session.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown with counts by severity (critical/high/medium/low).
    """
    try:
        return _render(await _request_json("GET", f"/security/report/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: risk scoring
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_get_score",
    annotations={"title": "Multi-dimensional risk score", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_score(params: SessionInput) -> str:
    """Compute the multi-dimensional risk score for a scanned session.

    Requires a prior scan. Combines complexity, security, and other dimensions
    into an overall risk profile.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown risk profile (overall score plus per-dimension
        breakdown).
    """
    try:
        return _render(await _request_json("GET", f"/scoring/{params.session_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_score_preview",
    annotations={"title": "Score arbitrary artifacts", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_score_preview(params: ScorePreviewInput) -> str:
    """Score an arbitrary artifacts object without a session (testing/demo).

    Args:
        params: artifacts (object with apis/classes/functions/etc.).

    Returns:
        str: JSON/markdown risk profile for the supplied artifacts.
    """
    try:
        body = {"artifacts": params.artifacts}
        return _render(await _request_json("POST", "/scoring/preview", json_body=body),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: compliance
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_list_frameworks",
    annotations={"title": "List compliance frameworks", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_list_frameworks(params: FormatOnlyInput) -> str:
    """List the compliance frameworks the backend can evaluate (e.g. OWASP, SOC2).

    Returns:
        str: JSON/markdown with {frameworks: {...}}. Use the framework ids with
        codeviz_get_framework_compliance.
    """
    try:
        return _render(await _request_json("GET", "/compliance/frameworks"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_compliance",
    annotations={"title": "Run compliance check", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_compliance(params: ComplianceInput) -> str:
    """Run compliance frameworks against a scanned session.

    Args:
        params: session_id, optional frameworks (comma-separated subset).

    Returns:
        str: JSON/markdown with per-framework pass/fail results and findings.
    """
    try:
        query = {"frameworks": params.frameworks} if params.frameworks else None
        return _render(
            await _request_json("GET", f"/compliance/{params.session_id}", params=query),
            params.response_format,
        )
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_framework_compliance",
    annotations={"title": "Single-framework compliance", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_framework_compliance(params: FrameworkComplianceInput) -> str:
    """Run a single named compliance framework against a scanned session.

    Args:
        params: session_id and framework_id (see codeviz_list_frameworks).

    Returns:
        str: JSON/markdown with that framework's detailed result.
    """
    try:
        return _render(
            await _request_json(
                "GET", f"/compliance/{params.session_id}/{params.framework_id}"),
            params.response_format,
        )
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: refactoring
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_refactoring_opportunities",
    annotations={"title": "List refactoring opportunities", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_refactoring_opportunities(params: SessionInput) -> str:
    """List refactoring opportunities detected in a scanned session.

    Args:
        params: session_id (and optional response_format).

    Returns:
        str: JSON/markdown with {opportunities:[{type, priority, file, ...}],
        summary:{...}}. Use an opportunity's index with codeviz_refactoring_suggest.
    """
    try:
        return _render(
            await _request_json("GET", f"/refactoring/opportunities/{params.session_id}"),
            params.response_format,
        )
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_refactoring_suggest",
    annotations={"title": "Suggest a refactoring", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def codeviz_refactoring_suggest(params: OpportunityInput) -> str:
    """Generate a concrete refactoring suggestion for one opportunity.

    Args:
        params: session_id and opp_index (from codeviz_refactoring_opportunities).

    Returns:
        str: JSON/markdown with {suggestion:{refactored_code, tests, explanation,
        confidence}}.
    """
    try:
        return _render(
            await _request_json(
                "GET", f"/refactoring/suggest/{params.session_id}/{params.opp_index}"),
            params.response_format,
        )
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_refactoring_pr_content",
    annotations={"title": "Build PR content for refactor", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_refactoring_pr_content(params: OpportunityInput) -> str:
    """Build ready-to-open PR content (title/description/branch) for a refactor.

    Args:
        params: session_id and opp_index.

    Returns:
        str: JSON/markdown with {pr_content:{title, description, branch,
        files_changed}}. Pass pr_content to codeviz_create_pr to open it.
    """
    try:
        return _render(
            await _request_json(
                "GET", f"/refactoring/pr/{params.session_id}/{params.opp_index}"),
            params.response_format,
        )
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_create_pr",
    annotations={"title": "Open refactoring PR", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def codeviz_create_pr(params: CreatePrInput) -> str:
    """Open a GitHub PR for a refactoring suggestion.

    Args:
        params: repo_name (owner/repo), pr_content (from
        codeviz_refactoring_pr_content), and github_token.

    Returns:
        str: JSON with {pr_url, status}.
    """
    try:
        body = {
            "repo_name": params.repo_name,
            "pr_content": params.pr_content,
            "github_token": params.github_token,
        }
        return _render(await _request_json("POST", "/refactoring/create-pr", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: reports & schedules
# --------------------------------------------------------------------------- #

def _resolve_report_path(session_id: str, suggested: str, output_path: Optional[str],
                         suffix: str) -> Path:
    if output_path:
        return Path(output_path).expanduser()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    name = suggested or f"codeviz-{session_id}-{datetime.now():%Y%m%d-%H%M%S}{suffix}"
    return REPORT_DIR / name


@mcp.tool(
    name="codeviz_generate_report",
    annotations={"title": "Generate PDF report", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_generate_report(params: ReportFileInput) -> str:
    """Generate a PDF report for a session and write it to disk.

    The report bundles artifacts, risk profile, and compliance results. Binary
    PDFs aren't useful inline, so the file is saved and its path returned.

    Args:
        params: session_id, optional output_path.

    Returns:
        str: JSON with {saved_to, bytes}.
    """
    try:
        content, fname = await _request_bytes("POST", f"/reports/generate/{params.session_id}")
        path = _resolve_report_path(params.session_id, fname, params.output_path, ".pdf")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return json.dumps({"data": {"saved_to": str(path), "bytes": len(content)},
                           "message": "PDF report generated"}, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_preview_report",
    annotations={"title": "Preview report (HTML)", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_preview_report(params: ReportFileInput) -> str:
    """Render the HTML report body for a session and write it to disk.

    Args:
        params: session_id, optional output_path.

    Returns:
        str: JSON with {saved_to, bytes}.
    """
    try:
        content, fname = await _request_bytes("GET", f"/reports/preview/{params.session_id}")
        path = _resolve_report_path(params.session_id, fname, params.output_path, ".html")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return json.dumps({"data": {"saved_to": str(path), "bytes": len(content)},
                           "message": "HTML report saved"}, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_email_report",
    annotations={"title": "Email a report", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def codeviz_email_report(params: EmailReportInput) -> str:
    """Generate and email a report for a session.

    Args:
        params: session_id and recipient email.

    Returns:
        str: JSON confirming {sent_to}.
    """
    try:
        body = {"email": params.email}
        return _render(
            await _request_json("POST", f"/reports/email/{params.session_id}", json_body=body),
            ResponseFormat.JSON,
        )
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_list_schedules",
    annotations={"title": "List report schedules", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_list_schedules(params: FormatOnlyInput) -> str:
    """List recurring report schedules.

    Returns:
        str: JSON/markdown with {schedules:[...]}.
    """
    try:
        return _render(await _request_json("GET", "/reports/schedules"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_create_schedule",
    annotations={"title": "Create report schedule", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def codeviz_create_schedule(params: CreateScheduleInput) -> str:
    """Create a recurring scheduled report across one or more repositories.

    Args:
        params: repo_paths, recipients, frequency/hour or explicit cron,
        plus label and timezone.

    Returns:
        str: JSON with the created schedule object (including its id).
    """
    try:
        body = {
            "repo_paths": params.repo_paths,
            "recipients": params.recipients,
            "frequency": params.frequency,
            "hour": params.hour,
            "label": params.label or "",
            "timezone": params.timezone,
            "cron": params.cron or "",
        }
        return _render(await _request_json("POST", "/reports/schedules", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_delete_schedule",
    annotations={"title": "Delete report schedule", "readOnlyHint": False,
                 "destructiveHint": True, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_delete_schedule(params: ScheduleIdInput) -> str:
    """Delete a report schedule. Destructive.

    Args:
        params: schedule_id.

    Returns:
        str: JSON confirming deletion.
    """
    try:
        return _render(await _request_json("DELETE", f"/reports/schedules/{params.schedule_id}"),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_run_schedule",
    annotations={"title": "Run schedule now", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def codeviz_run_schedule(params: ScheduleIdInput) -> str:
    """Trigger a scheduled report to run immediately.

    Args:
        params: schedule_id.

    Returns:
        str: JSON confirming the report was triggered.
    """
    try:
        return _render(
            await _request_json("POST", f"/reports/schedules/{params.schedule_id}/run"),
            ResponseFormat.JSON,
        )
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: repository registry
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_list_repositories",
    annotations={"title": "List monitored repos", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_list_repositories(params: FormatOnlyInput) -> str:
    """List repositories registered for monitoring.

    Returns:
        str: JSON/markdown with {repositories:[...], count}.
    """
    try:
        return _render(await _request_json("GET", "/repositories"), params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_list_github_repositories",
    annotations={"title": "List GitHub repos", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def codeviz_list_github_repositories(params: FormatOnlyInput) -> str:
    """List the authenticated user's GitHub repositories.

    Requires CODEVIZ_TOKEN to be a valid GitHub token; otherwise the backend
    returns a small mock list.

    Returns:
        str: JSON/markdown with {repositories:[{full_name, url, branch, ...}]}.
    """
    try:
        return _render(await _request_json("GET", "/repositories/github"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_add_repository",
    annotations={"title": "Register repository", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def codeviz_add_repository(params: AddRepoInput) -> str:
    """Register a repository for monitoring.

    Args:
        params: name, url, optional branch.

    Returns:
        str: JSON with the created repository (including its id).
    """
    try:
        body = {"name": params.name, "url": params.url, "branch": params.branch or "main"}
        return _render(await _request_json("POST", "/repositories", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_repository",
    annotations={"title": "Get repository", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_repository(params: RepoIdInput) -> str:
    """Get details for a registered repository.

    Args:
        params: repo_id (and optional response_format).

    Returns:
        str: JSON/markdown with the repository object.
    """
    try:
        return _render(await _request_json("GET", f"/repositories/{params.repo_id}"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_update_repository",
    annotations={"title": "Update repository", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_update_repository(params: UpdateRepoInput) -> str:
    """Update a registered repository's name, url, or branch.

    Args:
        params: repo_id plus any of name/url/branch to change.

    Returns:
        str: JSON with the updated repository object.
    """
    try:
        body = {k: v for k, v in
                {"name": params.name, "url": params.url, "branch": params.branch}.items()
                if v is not None}
        return _render(await _request_json("PUT", f"/repositories/{params.repo_id}", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_delete_repository",
    annotations={"title": "Delete repository", "readOnlyHint": False,
                 "destructiveHint": True, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_delete_repository(params: RepoIdInput) -> str:
    """Remove a repository from monitoring. Destructive.

    Args:
        params: repo_id.

    Returns:
        str: JSON confirming deletion.
    """
    try:
        return _render(await _request_json("DELETE", f"/repositories/{params.repo_id}"),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_scan_registered_repository",
    annotations={"title": "Scan registered repo", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def codeviz_scan_registered_repository(params: RepoIdInput) -> str:
    """Trigger a scan for a registered repository (registry workflow).

    Distinct from the session workflow (codeviz_create_session + codeviz_scan);
    this operates on a repository registered via codeviz_add_repository.

    Args:
        params: repo_id.

    Returns:
        str: JSON with {repository, scan_id}.
    """
    try:
        return _render(await _request_json("POST", f"/repositories/{params.repo_id}/scan"),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="codeviz_get_scan_history",
    annotations={"title": "Repo scan history", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def codeviz_get_scan_history(params: RepoIdInput) -> str:
    """Return scan history for a registered repository.

    Args:
        params: repo_id (and optional response_format).

    Returns:
        str: JSON/markdown with {scans:[{timestamp, total_issues, ...}], count}.
    """
    try:
        return _render(await _request_json("GET", f"/repositories/{params.repo_id}/scans"),
                       params.response_format)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Tools: diagnostics
# --------------------------------------------------------------------------- #

@mcp.tool(
    name="codeviz_ping_endpoint",
    annotations={"title": "Ping a discovered endpoint", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def codeviz_ping_endpoint(params: PingEndpointInput) -> str:
    """Test reachability of an API endpoint and report its HTTP status.

    Args:
        params: path, method, optional base_url override.

    Returns:
        str: JSON with {status_code, is_active, message}.
    """
    try:
        body = {"path": params.path, "method": params.method}
        if params.base_url:
            body["base_url"] = params.base_url
        return _render(await _request_json("POST", "/health/ping-endpoint", json_body=body),
                       ResponseFormat.JSON)
    except Exception as e:
        return _handle_error(e)


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    mcp.run()
