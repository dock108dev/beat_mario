from __future__ import annotations

import html
import json
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml

from smb3_agent.lab import (
    LabError,
    add_batch_notes_to_latest,
    build_issue_ledger_latest,
    propose_variants_from_latest,
    write_codex_task_latest,
    write_ui_summary_latest,
)


class LabUiError(ValueError):
    pass


def run_lab_ui_server(host: str = "127.0.0.1", port: int = 8765, *, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((host, port), _Handler)
    url = f"http://{host}:{server.server_port}"
    print(f"lab_ui_url={url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("lab_ui_stopped=true")


class _Handler(BaseHTTPRequestHandler):
    server_version = "SMB3LabUI/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(render_lab_ui())
            return
        if path == "/api/summary":
            self._send_json(write_ui_summary_latest().summary)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        data = self._read_form()
        try:
            if path == "/notes":
                notes = _notes_from_form(data)
                add_batch_notes_to_latest(notes)
                build_issue_ledger_latest()
                propose_variants_from_latest()
                self._redirect("/")
                return
            if path == "/refresh":
                build_issue_ledger_latest()
                propose_variants_from_latest()
                write_ui_summary_latest()
                self._redirect("/")
                return
            if path == "/codex-task":
                issue_id = _single(data, "issue_id")
                write_codex_task_latest(issue_id)
                self._redirect(f"/?selected_issue={issue_id}")
                return
        except (LabError, LabUiError) as exc:
            self._send_html(render_error(str(exc)), status=HTTPStatus.BAD_REQUEST)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_form(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return parse_qs(body, keep_blank_values=True)

    def _send_html(self, body: str, *, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, data: dict[str, object]) -> None:
        encoded = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()


def render_lab_ui() -> str:
    summary_result = write_ui_summary_latest()
    summary = summary_result.summary
    session_dir = Path(str(summary["session_dir"]))
    issues = _load_yaml(session_dir / "issues.yaml").get("issues", [])
    proposals = _load_yaml(session_dir / "variant_proposals.yaml").get("proposals", [])
    notes = _load_yaml(session_dir / "notes.yaml").get("notes", [])
    issue_by_id = {issue["id"]: issue for issue in issues if isinstance(issue, dict)}
    selected_segment = _first_segment(summary)

    return _page(
        title="World 1 Lab",
        body=f"""
        <header class="topbar">
          <div>
            <h1>World 1 Lab</h1>
            <p>{_esc(str(summary["session_id"]))}</p>
          </div>
          <form method="post" action="/refresh">
            <button type="submit">Refresh Issues</button>
          </form>
        </header>

        <section class="metrics">
          <div><strong>{summary['totals']['notes']}</strong><span>Notes</span></div>
          <div><strong>{summary['totals']['issues']}</strong><span>Issues</span></div>
          <div><strong>{summary['totals']['actionable_issues']}</strong><span>Actionable</span></div>
          <div><strong>{summary['totals']['proposals']}</strong><span>Proposals</span></div>
        </section>

        <main class="layout">
          <section class="route">
            <h2>Route Map</h2>
            <div class="route-grid">
              {''.join(_segment_card(segment, selected_segment) for segment in summary['segments'])}
            </div>
          </section>

          <section class="panel">
            <h2>Batch Notes</h2>
            <form method="post" action="/notes" class="note-form">
              {''.join(_note_input(segment) for segment in summary['segments'])}
              <button type="submit">Submit Notes</button>
            </form>
          </section>
        </main>

        <section class="lower-grid">
          <section class="panel">
            <h2>Issues</h2>
            {''.join(_issue_row(issue) for issue in issues if isinstance(issue, dict)) or '<p>No issues yet.</p>'}
          </section>
          <section class="panel">
            <h2>Proposals</h2>
            {''.join(_proposal_row(proposal, issue_by_id) for proposal in proposals if isinstance(proposal, dict)) or '<p>No proposals yet.</p>'}
          </section>
        </section>

        <section class="panel">
          <h2>Recent Notes</h2>
          {''.join(_note_row(note) for note in notes if isinstance(note, dict)) or '<p>No notes yet.</p>'}
        </section>
        """,
    )


def render_error(message: str) -> str:
    return _page(
        title="Lab UI Error",
        body=f"""
        <header class="topbar"><h1>Lab UI Error</h1></header>
        <section class="panel error"><p>{_esc(message)}</p><p><a href="/">Return to lab</a></p></section>
        """,
    )


def _page(*, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #1d232b;
      --muted: #5e6875;
      --line: #d7dce3;
      --accent: #1f6feb;
      --danger: #b42318;
      --ok: #1a7f37;
      --warn: #9a6700;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 24px; margin-bottom: 2px; }}
    h2 {{ font-size: 16px; margin-bottom: 12px; }}
    button {{
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      border-radius: 6px;
      padding: 8px 12px;
      font-weight: 650;
      cursor: pointer;
    }}
    textarea, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      font: inherit;
      background: #fff;
    }}
    textarea {{ min-height: 76px; resize: vertical; }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    .topbar p {{ margin: 0; color: var(--muted); }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      padding: 16px 20px 0;
    }}
    .metrics div, .panel, .segment-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .metrics div {{ padding: 12px; }}
    .metrics strong {{ display: block; font-size: 22px; }}
    .metrics span {{ color: var(--muted); }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr);
      gap: 16px;
      padding: 16px 20px;
    }}
    .lower-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      padding: 0 20px 16px;
    }}
    .panel {{ padding: 14px; }}
    .route-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
    }}
    .segment-card {{ padding: 12px; min-height: 128px; }}
    .segment-card h3 {{ font-size: 15px; margin-bottom: 8px; }}
    .segment-card a {{ color: var(--accent); text-decoration: none; }}
    .segment-card dl {{
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 3px 8px;
      margin: 0;
      color: var(--muted);
    }}
    .segment-card dd {{ margin: 0; color: var(--text); }}
    .note-form {{
      display: grid;
      gap: 12px;
    }}
    .note-block {{
      display: grid;
      grid-template-columns: minmax(100px, 140px) 1fr minmax(95px, 120px);
      gap: 8px;
      align-items: start;
    }}
    .note-block label {{ font-weight: 650; padding-top: 8px; }}
    .issue, .proposal, .note-row {{
      border-top: 1px solid var(--line);
      padding: 10px 0;
    }}
    .issue:first-of-type, .proposal:first-of-type, .note-row:first-of-type {{ border-top: 0; }}
    .meta {{ color: var(--muted); font-size: 12px; margin-bottom: 4px; }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      margin-right: 4px;
      font-size: 12px;
      color: var(--muted);
    }}
    .high {{ color: var(--danger); border-color: #f0b4ae; }}
    .medium {{ color: var(--warn); border-color: #eac54f; }}
    .none {{ color: var(--ok); border-color: #95d0a5; }}
    .error {{ border-color: #f0b4ae; color: var(--danger); }}
    @media (max-width: 900px) {{
      .layout, .lower-grid {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .note-block {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>{body}</body>
</html>"""


def _segment_card(segment: dict[str, object], selected_segment: str | None) -> str:
    segment_id = str(segment["id"])
    selected = " selected" if segment_id == selected_segment else ""
    return f"""
    <article class="segment-card{selected}" id="{_esc(segment_id)}">
      <h3><a href="#note-{_esc(segment_id)}">{_esc(str(segment.get('name') or segment_id))}</a></h3>
      <dl>
        <dt>Status</dt><dd>{_esc(str(segment.get('status', 'unknown')))}</dd>
        <dt>Notes</dt><dd>{segment.get('notes', 0)}</dd>
        <dt>Issues</dt><dd>{segment.get('issues', 0)}</dd>
        <dt>Open</dt><dd>{segment.get('open_issues', 0)}</dd>
        <dt>Proposals</dt><dd>{segment.get('proposals', 0)}</dd>
        <dt>Validation</dt><dd>{_esc(str(segment.get('validation_status', 'none')))}</dd>
      </dl>
    </article>"""


def _note_input(segment: dict[str, object]) -> str:
    segment_id = str(segment["id"])
    label = str(segment.get("name") or segment_id)
    return f"""
    <div class="note-block">
      <label for="note-{_esc(segment_id)}">{_esc(label)}</label>
      <textarea id="note-{_esc(segment_id)}" name="note__{_esc(segment_id)}" placeholder="Add notes for this segment"></textarea>
      <select name="severity__{_esc(segment_id)}">
        <option value="note">note</option>
        <option value="harden">harden</option>
        <option value="bug">bug</option>
      </select>
    </div>"""


def _issue_row(issue: dict[str, object]) -> str:
    priority = str(issue.get("priority", "low"))
    action = ""
    if issue.get("actionable"):
        action = f"""
        <form method="post" action="/codex-task">
          <input type="hidden" name="issue_id" value="{_esc(str(issue['id']))}">
          <button type="submit">Create Codex Task</button>
        </form>"""
    return f"""
    <article class="issue">
      <div class="meta">{_esc(str(issue['id']))}</div>
      <p><span class="badge {priority}">{_esc(priority)}</span><span class="badge">{_esc(str(issue.get('type')))}</span><span class="badge">{_esc(str(issue.get('segment_id')))}</span></p>
      <p>{_esc(str(issue.get('summary', '')))}</p>
      <p>{_esc(str(issue.get('proposed_next_step', '')))}</p>
      {action}
    </article>"""


def _proposal_row(proposal: dict[str, object], issue_by_id: dict[str, dict[str, object]]) -> str:
    issue = issue_by_id.get(str(proposal.get("source_issue")), {})
    return f"""
    <article class="proposal">
      <div class="meta">{_esc(str(proposal['variant_id']))}</div>
      <p><span class="badge">{_esc(str(proposal.get('status')))}</span><span class="badge">{_esc(str(proposal.get('priority')))}</span></p>
      <p>{_esc(str(proposal.get('reason', '')))}</p>
      <p class="meta">Issue: {_esc(str(issue.get('id', proposal.get('source_issue'))))}</p>
    </article>"""


def _note_row(note: dict[str, object]) -> str:
    return f"""
    <article class="note-row">
      <div class="meta">{_esc(str(note.get('id')))} · {_esc(str(note.get('segment_id')))} · {_esc(str(note.get('severity')))}</div>
      <p>{_esc(str(note.get('text', '')))}</p>
    </article>"""


def _notes_from_form(data: dict[str, list[str]]) -> list[dict[str, object]]:
    notes: list[dict[str, object]] = []
    for key, values in data.items():
        if not key.startswith("note__"):
            continue
        segment_id = key.removeprefix("note__")
        text = "\n".join(value.strip() for value in values if value.strip()).strip()
        if not text:
            continue
        severity = _single(data, f"severity__{segment_id}", default="note")
        for chunk in _split_note_text(text):
            notes.append(
                {
                    "segment_id": segment_id,
                    "text": chunk,
                    "severity": severity,
                }
            )
    return notes


def _split_note_text(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return chunks or [text]


def _single(data: dict[str, list[str]], key: str, *, default: str | None = None) -> str:
    values = data.get(key)
    if not values:
        if default is not None:
            return default
        raise LabUiError(f"Missing form field: {key}")
    return values[0]


def _load_yaml(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    return data


def _first_segment(summary: dict[str, object]) -> str | None:
    segments = summary.get("segments", [])
    if isinstance(segments, list) and segments:
        first = segments[0]
        if isinstance(first, dict):
            return str(first.get("id"))
    return None


def _esc(value: str) -> str:
    return html.escape(value, quote=True)
