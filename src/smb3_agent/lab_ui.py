from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime, timezone
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
    start_session,
    write_codex_task_latest,
)


WORLD_1_LOCATION_PATH = Path("data/worlds/world_1_locations.yaml")
LAST_COMMAND_PATH = Path("artifacts/ui/last_command.yaml")
SUPPORTED_SPEEDS = ("1", "2", "4", "10", "25", "50", "100")
SUPPORTED_ATTEMPTS = ("1", "3", "5", "10")


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
    server_version = "SMB3ControlPanel/0.2"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(render_lab_ui())
            return
        if path == "/api/summary":
            self._send_json(build_control_panel_summary())
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        data = self._read_form()
        try:
            if path == "/notes":
                notes = _notes_from_form(data)
                if notes:
                    add_batch_notes_to_latest(notes)
                build_issue_ledger_latest()
                propose_variants_from_latest()
                self._redirect("/")
                return
            if path == "/refresh":
                build_issue_ledger_latest()
                propose_variants_from_latest()
                _write_last_command(
                    "refresh",
                    ("python", "-m", "smb3_agent", "lab", "issues", "latest"),
                    0,
                    "review artifacts refreshed",
                    "",
                )
                self._redirect("/")
                return
            if path == "/run":
                result = _run_world_1_from_form(data)
                _write_last_command(
                    "run_world_1",
                    (
                        "python",
                        "-m",
                        "smb3_agent",
                        "lab",
                        "start",
                        result["command"],
                        "--attempts",
                        str(result["attempts"]),
                    ),
                    0,
                    result["summary"],
                    "",
                )
                self._redirect("/")
                return
            if path == "/test":
                action = _single(data, "action")
                command = _test_command(action)
                completed = _run_command_capture(action, command)
                _write_last_command(
                    action,
                    command,
                    completed.returncode,
                    completed.stdout,
                    completed.stderr,
                )
                self._redirect("/")
                return
            if path == "/codex-task":
                issue_id = _single(data, "issue_id")
                write_codex_task_latest(issue_id)
                self._redirect("/")
                return
        except (LabError, LabUiError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
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
    summary = build_control_panel_summary()
    last_command = _load_yaml(LAST_COMMAND_PATH)
    return _page(
        title="World 1 Control Panel",
        body=f"""
        <header class="topbar">
          <div>
            <h1>World 1 Control Panel</h1>
            <p>{_esc(str(summary.get('session_label', 'No active session')))}</p>
          </div>
          <form method="post" action="/refresh">
            <button type="submit">Refresh Review</button>
          </form>
        </header>

        <section class="metrics">
          <div><strong>{summary['totals']['notes']}</strong><span>Notes</span></div>
          <div><strong>{summary['totals']['issues']}</strong><span>Issues</span></div>
          <div><strong>{summary['totals']['open_issues']}</strong><span>Open</span></div>
          <div><strong>{summary['totals']['proposals']}</strong><span>Variants</span></div>
        </section>

        <main class="layout">
          <section class="panel run-panel">
            <h2>Run Controls</h2>
            <form method="post" action="/run" class="control-grid">
              <label>Speed
                <select name="speed">{_options(SUPPORTED_SPEEDS, "4", suffix="x")}</select>
              </label>
              <label>Attempts
                <select name="attempts">{_options(SUPPORTED_ATTEMPTS, "1")}</select>
              </label>
              <label>Mode
                <select name="mode">
                  <option value="show">watch route</option>
                  <option value="gate">gate run</option>
                </select>
              </label>
              <button type="submit">Run World 1</button>
            </form>
            <form method="post" action="/test" class="button-row">
              <button type="submit" name="action" value="unit_tests">Unit Tests</button>
              <button type="submit" name="action" value="phase_gate">Phase Gate</button>
              <button type="submit" name="action" value="render_check">Render Check</button>
            </form>
            {_last_command_panel(last_command)}
          </section>

          <section class="panel guide-panel">
            <h2>Guide Logic</h2>
            <ul>
              <li>World 1 is Grass Land and uses map movement between playable locations.</li>
              <li>Fortresses end with Boom Boom; the World 1 fortress route also has a hidden whistle objective.</li>
              <li>Raccoon flight comes from Super Leaf form and P-meter speed, not from fire form.</li>
              <li>Airship is the world-ending moving stage and boss transition.</li>
            </ul>
          </section>
        </main>

        <section class="panel board">
          <h2>World 1 Notes</h2>
          <form method="post" action="/notes">
            <div class="location-grid">
              {''.join(_location_card(location) for location in summary['locations'])}
            </div>
            <button type="submit">Submit Notes</button>
          </form>
        </section>

        <section class="lower-grid">
          <section class="panel">
            <h2>Open Issues</h2>
            {''.join(_issue_row(issue, summary) for issue in summary['issues']) or '<p>No issues yet.</p>'}
          </section>
          <section class="panel">
            <h2>Recent Notes</h2>
            {''.join(_note_row(note, summary) for note in summary['recent_notes']) or '<p>No notes yet.</p>'}
          </section>
        </section>
        """,
    )


def render_error(message: str) -> str:
    return _page(
        title="Control Panel Error",
        body=f"""
        <header class="topbar"><h1>Control Panel Error</h1></header>
        <section class="panel error"><p>{_esc(message)}</p><p><a href="/">Return to control panel</a></p></section>
        """,
    )


def build_control_panel_summary() -> dict[str, object]:
    locations = _load_locations()
    session_dir = _latest_session_dir_if_any()
    if session_dir is None:
        notes: list[dict[str, object]] = []
        issues: list[dict[str, object]] = []
        proposals: list[dict[str, object]] = []
        session_label = "No active session"
    else:
        notes = _list_dicts(_load_yaml(session_dir / "notes.yaml").get("notes", []))
        issues_path = session_dir / "issues.yaml"
        proposals_path = session_dir / "variant_proposals.yaml"
        issues = _list_dicts(_load_yaml(issues_path).get("issues", []))
        proposals = _list_dicts(_load_yaml(proposals_path).get("proposals", []))
        session_label = session_dir.name

    proposal_issue_ids = {str(proposal.get("source_issue")) for proposal in proposals}
    location_rows = []
    for location in locations:
        location_id = str(location["id"])
        location_notes = [note for note in notes if _location_id_for_artifact(str(note.get("segment_id"))) == location_id]
        location_issues = [issue for issue in issues if _location_id_for_artifact(str(issue.get("segment_id"))) == location_id]
        issue_ids = {str(issue.get("id")) for issue in location_issues}
        location_rows.append(
            {
                **location,
                "notes": len(location_notes),
                "issues": len(location_issues),
                "open_issues": sum(1 for issue in location_issues if issue.get("status") == "open"),
                "proposals": len(issue_ids & proposal_issue_ids),
                "status": _location_status(location, location_issues),
            }
        )

    return {
        "session_label": session_label,
        "locations": location_rows,
        "issues": issues,
        "recent_notes": notes[-12:],
        "totals": {
            "notes": len(notes),
            "issues": len(issues),
            "open_issues": sum(1 for issue in issues if issue.get("status") == "open"),
            "proposals": len(proposals),
        },
    }


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
      --bg: #f4f5f7;
      --panel: #ffffff;
      --text: #20242b;
      --muted: #606b78;
      --line: #d8dde4;
      --accent: #1769aa;
      --accent-dark: #0f4f82;
      --danger: #b42318;
      --warn: #9a6700;
      --ok: #1a7f37;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.42 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 24px; margin-bottom: 2px; }}
    h2 {{ font-size: 16px; margin-bottom: 12px; }}
    h3 {{ font-size: 15px; margin-bottom: 4px; }}
    button {{
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      border-radius: 6px;
      padding: 8px 12px;
      font-weight: 650;
      cursor: pointer;
    }}
    button:hover {{ background: var(--accent-dark); }}
    textarea, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      font: inherit;
      background: #fff;
    }}
    textarea {{ min-height: 84px; resize: vertical; }}
    label {{ display: grid; gap: 5px; font-weight: 650; }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    .topbar p, .meta {{ margin: 0; color: var(--muted); font-size: 12px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      padding: 16px 20px 0;
    }}
    .metrics div, .panel, .location-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .metrics div {{ padding: 12px; }}
    .metrics strong {{ display: block; font-size: 22px; }}
    .metrics span {{ color: var(--muted); }}
    .layout, .lower-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(320px, .9fr);
      gap: 16px;
      padding: 16px 20px 0;
    }}
    .panel {{ padding: 14px; }}
    .control-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      align-items: end;
    }}
    .button-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .guide-panel ul {{ margin: 0; padding-left: 18px; color: var(--muted); }}
    .board {{ margin: 16px 20px 0; }}
    .location-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(235px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }}
    .location-card {{
      padding: 12px;
      display: grid;
      gap: 8px;
      min-height: 246px;
    }}
    .location-head {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: start;
    }}
    .objective {{ color: var(--muted); min-height: 40px; }}
    .badges {{ display: flex; flex-wrap: wrap; gap: 4px; }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      font-size: 12px;
      color: var(--muted);
      background: #fff;
    }}
    .blocked, .high {{ color: var(--danger); border-color: #f0b4ae; }}
    .needs-review, .medium {{ color: var(--warn); border-color: #eac54f; }}
    .works, .none {{ color: var(--ok); border-color: #95d0a5; }}
    .note-tools {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
    .issue, .note-row, .last-command {{
      border-top: 1px solid var(--line);
      padding: 10px 0;
    }}
    .issue:first-of-type, .note-row:first-of-type {{ border-top: 0; }}
    .last-command {{
      margin-top: 12px;
      padding-bottom: 0;
      color: var(--muted);
    }}
    pre {{
      max-height: 180px;
      overflow: auto;
      white-space: pre-wrap;
      background: #f8f9fb;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      color: var(--text);
    }}
    .error {{ border-color: #f0b4ae; color: var(--danger); margin: 20px; }}
    @media (max-width: 900px) {{
      .layout, .lower-grid, .control-grid {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>{body}</body>
</html>"""


def _location_card(location: dict[str, object]) -> str:
    location_id = str(location["id"])
    label = str(location["label"])
    objective = str(location.get("objective", ""))
    return f"""
    <article class="location-card">
      <div class="location-head">
        <div>
          <h3>{_esc(label)}</h3>
          <p class="objective">{_esc(objective)}</p>
        </div>
        <span class="badge {_status_class(str(location.get('status', 'unknown')))}">{_esc(str(location.get('status', 'unknown')))}</span>
      </div>
      <div class="badges">
        <span class="badge">{location.get('notes', 0)} notes</span>
        <span class="badge">{location.get('open_issues', 0)} open</span>
        <span class="badge">{location.get('proposals', 0)} variants</span>
      </div>
      <textarea name="note__{_esc(location_id)}" placeholder="Notes for {_esc(label)}"></textarea>
      <div class="note-tools">
        <select name="severity__{_esc(location_id)}">
          <option value="note">note</option>
          <option value="harden">harden</option>
          <option value="bug">bug</option>
          <option value="objective">objective</option>
          <option value="map_action">map action</option>
          <option value="guide_detail">guide detail</option>
        </select>
        <select name="anchor__{_esc(location_id)}">
          <option value="">no anchor</option>
          <option value="in_game_timer">timer</option>
          <option value="frame">frame</option>
          <option value="map_position">map position</option>
        </select>
      </div>
    </article>"""


def _issue_row(issue: dict[str, object], summary: dict[str, object]) -> str:
    priority = str(issue.get("priority", "low"))
    location_label = _label_for_location(summary, str(issue.get("segment_id")))
    action = ""
    if issue.get("actionable"):
        action = f"""
        <form method="post" action="/codex-task">
          <input type="hidden" name="issue_id" value="{_esc(str(issue['id']))}">
          <button type="submit">Create Codex Task</button>
        </form>"""
    return f"""
    <article class="issue">
      <div class="meta">{_esc(location_label)}</div>
      <p><span class="badge {priority}">{_esc(priority)}</span><span class="badge">{_esc(_human_issue_type(str(issue.get('type', 'unknown'))))}</span></p>
      <p>{_esc(str(issue.get('summary', '')))}</p>
      <p class="meta">{_esc(str(issue.get('proposed_next_step', '')))}</p>
      {action}
    </article>"""


def _note_row(note: dict[str, object], summary: dict[str, object]) -> str:
    location_label = _label_for_location(summary, str(note.get("segment_id")))
    return f"""
    <article class="note-row">
      <div class="meta">{_esc(location_label)} · {_esc(str(note.get('severity')))}</div>
      <p>{_esc(str(note.get('text', '')))}</p>
    </article>"""


def _last_command_panel(last_command: dict[str, object]) -> str:
    if not last_command:
        return '<div class="last-command"><p>No command has run from this panel yet.</p></div>'
    status = "passed" if int(last_command.get("returncode", 1)) == 0 else "failed"
    output = str(last_command.get("stdout") or last_command.get("stderr") or "").strip()
    return f"""
    <div class="last-command">
      <p><strong>Last Command:</strong> {_esc(str(last_command.get('name', 'unknown')))} · {_esc(status)}</p>
      <p class="meta">{_esc(str(last_command.get('ran_at', '')))}</p>
      {f'<pre>{_esc(output[-4000:])}</pre>' if output else ''}
    </div>"""


def _run_world_1_from_form(data: dict[str, list[str]]) -> dict[str, object]:
    game_file = os.environ.get("SMB3_GAME_FILE")
    if not game_file:
        raise LabUiError("Set SMB3_GAME_FILE before running from the control panel.")
    speed = _single(data, "speed", default="4")
    attempts = int(_single(data, "attempts", default="1"))
    mode = _single(data, "mode", default="show")
    if speed not in SUPPORTED_SPEEDS:
        raise LabUiError("Unsupported speed")
    if mode == "gate":
        command = f"run world 1 king gate {attempts} times at {speed}x"
    else:
        command = f"show me the route at {speed}x"
    result = start_session(
        command,
        game_path=Path(game_file),
        attempts=attempts,
        artifacts_root=Path("artifacts/sessions"),
        capture_images=False,
        capture_ticks=True,
    )
    return {
        "command": command,
        "attempts": attempts,
        "summary": result.to_text(),
    }


def _test_command(action: str) -> tuple[str, ...]:
    if action == "unit_tests":
        return (sys.executable, "-m", "pytest", "-q")
    if action == "phase_gate":
        return ("bash", "scripts/validate_phase0.sh")
    if action == "render_check":
        return (sys.executable, "-m", "smb3_agent", "lab", "ui-render", "--output", "artifacts/ui/latest.html")
    raise LabUiError(f"Unknown test action: {action}")


def _run_command_capture(action: str, command: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    timeout = 240 if action == "phase_gate" else 120
    env = dict(os.environ)
    env["PYTHON"] = sys.executable
    return subprocess.run(
        command,
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )


def _notes_from_form(data: dict[str, list[str]]) -> list[dict[str, object]]:
    notes: list[dict[str, object]] = []
    for key, values in data.items():
        if not key.startswith("note__"):
            continue
        location_id = key.removeprefix("note__")
        text = "\n".join(value.strip() for value in values if value.strip()).strip()
        if not text:
            continue
        severity = _single(data, f"severity__{location_id}", default="note")
        anchor_type = _single(data, f"anchor__{location_id}", default="") or None
        for chunk in _split_note_text(text):
            notes.append(
                {
                    "segment_id": location_id,
                    "text": chunk,
                    "severity": severity,
                    "anchor_type": anchor_type,
                }
            )
    return notes


def _split_note_text(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return chunks or [text]


def _load_locations() -> list[dict[str, object]]:
    data = _load_yaml(WORLD_1_LOCATION_PATH)
    locations = data.get("locations", [])
    if not isinstance(locations, list):
        raise LabUiError(f"Invalid location model: {WORLD_1_LOCATION_PATH}")
    return [location for location in locations if isinstance(location, dict) and location.get("id")]


def _location_status(location: dict[str, object], issues: list[dict[str, object]]) -> str:
    if any(issue.get("priority") == "high" and issue.get("status") == "open" for issue in issues):
        return "blocked"
    if any(issue.get("status") == "open" for issue in issues):
        return "needs review"
    return str(location.get("default_status", "unknown"))


def _location_id_for_artifact(value: str) -> str:
    aliases = {
        "world_1_1_clear": "world_1_1",
        "world_1_2_clear": "world_1_2",
        "world_1_3_whistle": "world_1_3",
        "world_1_fortress_whistle": "world_1_fortress",
        "world_1_4_clear": "world_1_4",
        "world_1_5_clear": "world_1_5",
        "world_1_5_water_path": "world_1_5",
        "world_1_6_clear": "world_1_6",
        "world_1_airship_to_king": "world_1_airship",
        "fortress": "world_1_fortress",
        "castle": "world_1_airship",
        "airship": "world_1_airship",
        "map": "world_1_map",
    }
    return aliases.get(value, value)


def _label_for_location(summary: dict[str, object], artifact_id: str) -> str:
    location_id = _location_id_for_artifact(artifact_id)
    for location in summary.get("locations", []):
        if isinstance(location, dict) and location.get("id") == location_id:
            return str(location.get("label", location_id))
    return "World 1"


def _human_issue_type(issue_type: str) -> str:
    return issue_type.replace("_", " ")


def _status_class(status: str) -> str:
    return status.lower().replace(" ", "-")


def _options(values: tuple[str, ...], selected: str, *, suffix: str = "") -> str:
    rendered = []
    for value in values:
        selected_attr = " selected" if value == selected else ""
        rendered.append(f'<option value="{_esc(value)}"{selected_attr}>{_esc(value + suffix)}</option>')
    return "".join(rendered)


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


def _write_last_command(
    name: str,
    command: tuple[str, ...],
    returncode: int,
    stdout: str,
    stderr: str,
) -> None:
    LAST_COMMAND_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_yaml(
        LAST_COMMAND_PATH,
        {
            "name": name,
            "command": list(command),
            "returncode": returncode,
            "stdout": stdout[-12000:],
            "stderr": stderr[-12000:],
            "ran_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )


def _write_yaml(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _latest_session_dir_if_any() -> Path | None:
    latest = Path("artifacts/sessions/latest.txt")
    if not latest.is_file():
        return None
    value = latest.read_text(encoding="utf-8").strip()
    if not value:
        return None
    path = Path(value)
    return path if path.is_dir() else None


def _list_dicts(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _esc(value: str) -> str:
    return html.escape(value, quote=True)
