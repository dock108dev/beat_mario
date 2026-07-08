from __future__ import annotations

import html
import json
import mimetypes
import os
import subprocess
import sys
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

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
LOCAL_ASSET_DIR = Path("public/assets/local")
ARTIFACT_DIR = Path("artifacts")
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
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            query = parse_qs(parsed.query)
            self._send_html(
                render_lab_ui(
                    selected_location_id=query.get("location", [""])[0] or None,
                    selected_note_id=query.get("note", [""])[0] or None,
                    selected_issue_id=query.get("issue", [""])[0] or None,
                    selected_mode=query.get("mode", [""])[0] or None,
                )
            )
            return
        if path == "/api/summary":
            self._send_json(build_control_panel_summary())
            return
        if path.startswith("/assets/local/"):
            self._send_local_asset(path.removeprefix("/assets/local/"))
            return
        if path.startswith("/artifacts/"):
            self._send_artifact(path.removeprefix("/artifacts/"))
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
                self._redirect(_location_url(_single(data, "return_location", default="")))
                return
            if path == "/observation-action":
                location_id = _single(data, "return_location", default="")
                _update_observation_latest(
                    _single(data, "note_id"),
                    _single(data, "action"),
                    data,
                )
                self._redirect(_location_url(location_id))
                return
            if path == "/issue-action":
                location_id = _single(data, "return_location", default="")
                _update_issue_latest(
                    _single(data, "issue_id"),
                    _single(data, "action"),
                )
                self._redirect(_location_url(location_id))
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
                issue_id = _issue_id_from_form(data)
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

    def _send_local_asset(self, asset_path: str) -> None:
        self._send_workspace_file(LOCAL_ASSET_DIR, asset_path)

    def _send_artifact(self, artifact_path: str) -> None:
        self._send_workspace_file(ARTIFACT_DIR, artifact_path)

    def _send_workspace_file(self, root: Path, requested_path: str) -> None:
        try:
            relative = Path(unquote(requested_path))
            if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
                raise ValueError
            full_path = (root / relative).resolve()
            full_path.relative_to(root.resolve())
        except ValueError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not full_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = full_path.read_bytes()
        content_type = mimetypes.guess_type(str(full_path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()


def render_lab_ui(
    *,
    selected_location_id: str | None = None,
    selected_note_id: str | None = None,
    selected_issue_id: str | None = None,
    selected_mode: str | None = None,
) -> str:
    summary = build_control_panel_summary()
    last_command = _load_yaml(LAST_COMMAND_PATH)
    locations = _list_dicts(summary.get("locations", []))
    selected = _selected_location(locations, selected_location_id=selected_location_id)
    selected_notes = _notes_for_location(summary, selected)
    selected_issues = _issues_for_location(summary, selected)
    mode = _selected_mode(selected_mode, selected_notes, selected_issues, selected_note_id, selected_issue_id)
    selected_note = _selected_note(selected_notes, selected_note_id)
    selected_issue = _selected_issue(selected_issues, selected_issue_id)
    evidence = _latest_evidence(summary, last_command, selected)
    return _page(
        title="Mario Route Lab",
        body=f"""
        <div class="route-lab">
          <header class="lab-top">
            <div class="lab-title">
              {_asset_icon('leaf_icon.png', 'LAB', 'Route lab local asset')}
              <div>
                <h1>Mario Route Lab</h1>
                <p>Current session: {_esc(str(summary.get('session_label', 'No active session')))} · World 1 / Grass Land</p>
              </div>
            </div>
            {_run_bar(last_command)}
          </header>

          <main class="lab-main">
            <aside class="route-index" aria-label="Route">
              <div class="section-title">
                <h2>Route</h2>
                <p>Where is Mario?</p>
              </div>
              <nav class="route-list">
                {''.join(_route_item(location, selected) for location in locations)}
              </nav>
            </aside>

            {_evidence_viewer(evidence, selected, last_command)}

            {_teaching_panel(selected, selected_notes, selected_issues, mode, selected_note, selected_issue)}
          </main>

          <section class="lab-bottom">
            <section class="paper-panel">
              <div class="section-title">
                <h2>Latest Attempt</h2>
              </div>
              {_last_command_panel(last_command)}
            </section>
            <section class="paper-panel">
              <div class="section-title">
                <h2>Active Problems</h2>
              </div>
              <div class="issue-list">
                {''.join(_issue_row(issue, summary, selected) for issue in _sorted_issues(summary, selected)) or '<p class="empty">No active problems yet.</p>'}
              </div>
            </section>
            <section class="paper-panel">
              <div class="section-title">
                <h2>Observation History</h2>
              </div>
              {''.join(_note_row(note, summary, selected) for note in _sorted_notes(summary, selected)) or '<p class="empty">No observations yet.</p>'}
            </section>
          </section>
        </div>
        """,
    )


def _run_bar(last_command: dict[str, object]) -> str:
    return f"""
            <div class="run-strip">
              <form method="post" action="/run" class="run-form" aria-label="Run">
                <label>Speed <select name="speed">{_options(SUPPORTED_SPEEDS, "4", suffix="x")}</select></label>
                <label>Attempts <select name="attempts">{_options(SUPPORTED_ATTEMPTS, "1")}</select></label>
                <label>Mode
                  <select name="mode">
                    <option value="show">watch route</option>
                    <option value="gate">gate run</option>
                  </select>
                </label>
                <button type="submit" class="primary-button">Run World 1</button>
              </form>
              <div class="last-result">
                <span>Last run result</span>
                <strong class="{_status_class(_last_command_status(last_command))}">{_esc(_title_status(_last_command_status(last_command)))}</strong>
              </div>
              <form method="post" action="/refresh" class="refresh-form">
                <button type="submit" class="secondary-button">Refresh Review</button>
              </form>
            </div>"""


def _route_item(location: dict[str, object], selected: dict[str, object]) -> str:
    location_id = str(location["id"])
    label = str(location.get("label", location_id))
    state = _route_state(location)
    selected_class = " route-item-selected" if selected.get("id") == location_id else ""
    return f"""
                <a class="route-step route-item status-{_state_class(state)}{selected_class}" href="{_esc(_location_url(location_id))}">
                  {_asset_icon(_icon_name_for_location(location), _icon_fallback(location), f'{label} icon')}
                  <span class="route-copy">
                    <strong>{_esc(label)}</strong>
                    <small>{_esc(_title_status(state))} · {location.get('open_issues', 0)} open · {location.get('notes', 0)} notes</small>
                  </span>
                </a>"""


def _evidence_viewer(
    evidence: dict[str, object],
    selected: dict[str, object],
    last_command: dict[str, object],
) -> str:
    image_path = evidence.get("image")
    image_html = ""
    frame_class = "screen-frame"
    if isinstance(image_path, Path):
        image_html = f'<img src="{_esc(_artifact_url(image_path))}" alt="Latest route evidence">'
    else:
        frame_class = "screen-frame no-evidence-frame"
        image_html = """
                <div class="empty-evidence">
                  <strong>No screenshot captured yet</strong>
                  <span>Run World 1 to capture screenshot/contact-sheet evidence.</span>
                </div>"""
    detail_rows = "".join(
        f"<li><strong>{_esc(label)}</strong><span>{_esc(value)}</span></li>"
        for label, value in evidence.get("details", [])
    )
    return f"""
            <section class="evidence-viewer">
              <div class="section-title">
                <h2>Evidence</h2>
                <p>What went wrong?</p>
              </div>
              <div class="{frame_class}">
                {image_html}
              </div>
              <div class="evidence-notes">
                <h3>{_esc(str(selected.get('label', 'Route')))}</h3>
                <p>{_esc(str(selected.get('objective', 'Select a route step to review what Mario should do here.')))}</p>
                <ul>
                  {detail_rows}
                  <li><strong>Latest observed state</strong><span>{_esc(_latest_observed_state(last_command))}</span></li>
                </ul>
              </div>
            </section>"""


def _teaching_panel(
    selected: dict[str, object],
    observations: list[dict[str, object]],
    issues: list[dict[str, object]],
    mode: str,
    selected_note: dict[str, object] | None,
    selected_issue: dict[str, object] | None,
) -> str:
    location_id = str(selected.get("id", ""))
    label = str(selected.get("label", "Route"))
    content = {
        "add": _add_observation_mode(selected),
        "notes": _review_notes_mode(location_id, observations, selected_note),
        "issue": _fix_issue_mode(location_id, issues, selected_issue),
    }.get(mode, _add_observation_mode(selected))
    return f"""
            <aside class="teaching-panel">
              <div class="section-title">
                <h2>Teach Mario</h2>
              </div>
              <div class="selected-location">
                <strong>{_esc(label)}</strong>
                <span class="status-pill status-{_state_class(_route_state(selected))}">{_esc(_title_status(_route_state(selected)))}</span>
                <p>{_esc(str(selected.get('objective', '')))}</p>
              </div>
              <nav class="mode-tabs segmented-control" aria-label="Teach Mario modes">
                {_mode_link(location_id, 'add', 'Add Observation', mode)}
                {_mode_link(location_id, 'notes', 'Review Notes', mode)}
                {_mode_link(location_id, 'issue', 'Fix Issue', mode)}
              </nav>
              {content}
              <form method="post" action="/test" class="mini-actions">
                <button type="submit" name="action" value="phase_gate" class="quiet">Phase Gate</button>
                <button type="submit" name="action" value="unit_tests" class="quiet">Unit Tests</button>
                <button type="submit" name="action" value="render_check" class="quiet">HTML Render Check</button>
              </form>
            </aside>"""


def _mode_link(location_id: str, mode: str, label: str, selected_mode: str) -> str:
    selected_class = " segment-active" if mode == selected_mode else ""
    return f'<a class="mode-tab{selected_class}" href="{_esc(_location_url(location_id, mode=mode))}">{_esc(label)}</a>'


def _add_observation_mode(selected: dict[str, object]) -> str:
    location_id = str(selected.get("id", ""))
    return f"""
              <section class="mode-panel">
                <form method="post" action="/notes">
                  <input type="hidden" name="return_location" value="{_esc(location_id)}">
                  <label>What happened?
                    <textarea name="note__{_esc(location_id)}" placeholder="Where did Mario fail, or what should he do here?"></textarea>
                  </label>
                  <div class="note-tools">
                    <select name="severity__{_esc(location_id)}">
                      <option value="bug">failure</option>
                      <option value="objective">expected behavior</option>
                      <option value="map_action">route instruction</option>
                      <option value="harden">validation note</option>
                      <option value="guide_detail">positive evidence</option>
                    </select>
                    <select name="anchor__{_esc(location_id)}">
                      <option value="">no anchor</option>
                      <option value="in_game_timer">timer</option>
                      <option value="frame">frame</option>
                      <option value="map_position">map position</option>
                    </select>
                  </div>
                  <button type="submit" class="secondary-button">Add Observation</button>
                </form>
              </section>"""


def _review_notes_mode(
    location_id: str,
    observations: list[dict[str, object]],
    selected_note: dict[str, object] | None,
) -> str:
    selected_note = selected_note or (observations[0] if observations else None)
    return f"""
              <section class="mode-panel">
                <div class="compact-list">
                  {''.join(_observation_compact_row(note, location_id, selected_note) for note in observations) or '<p class="empty">No observations for this location yet.</p>'}
                </div>
                {_observation_detail(selected_note, location_id) if selected_note else ''}
              </section>"""


def _fix_issue_mode(
    location_id: str,
    issues: list[dict[str, object]],
    selected_issue: dict[str, object] | None,
) -> str:
    selected_issue = selected_issue or (issues[0] if issues else None)
    return f"""
              <section class="mode-panel">
                <div class="compact-list">
                  {''.join(_issue_compact_row(issue, location_id, selected_issue) for issue in issues) or '<p class="empty">No open issues for this location.</p>'}
                </div>
                {_issue_detail(selected_issue, location_id) if selected_issue else ''}
              </section>"""


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
      --app-bg: #f7f4ec;
      --surface: #ffffff;
      --surface-alt: #f8fafc;
      --text: #1f2937;
      --muted: #64748b;
      --line: #d6d3c8;
      --line-strong: #b8ad97;
      --screen: #1b2426;
      --screen-soft: #2f3a3d;
      --blue: #2563eb;
      --blue-soft: #eff6ff;
      --navy: #1e3a5f;
      --red: #c9362c;
      --red-soft: #fff1f0;
      --green: #1f7a4d;
      --green-soft: #edf9f1;
      --amber: #b7791f;
      --amber-soft: #fff7df;
      --badge: #f4ead3;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        linear-gradient(rgba(30,58,95,.026) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,58,95,.026) 1px, transparent 1px),
        var(--app-bg);
      background-size: 22px 22px;
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 26px; line-height: 1.05; margin-bottom: 4px; letter-spacing: 0; }}
    h2 {{ font-size: 16px; margin-bottom: 2px; letter-spacing: 0; }}
    h3 {{ font-size: 15px; margin-bottom: 4px; letter-spacing: 0; }}
    a {{ color: inherit; }}
    button {{
      border: 1px solid var(--line-strong);
      background: var(--surface);
      color: var(--text);
      border-radius: 6px;
      padding: 7px 10px;
      font-weight: 750;
      cursor: pointer;
      min-height: 32px;
    }}
    button:hover {{ background: var(--surface-alt); border-color: var(--navy); }}
    .primary-button {{
      border: 1px solid #8f251f;
      background: var(--red);
      color: #fff;
      min-height: 36px;
      padding: 8px 13px;
      box-shadow: 0 1px 0 rgba(31,41,55,.12);
    }}
    .primary-button:hover {{ background: #b92f27; border-color: #7f211c; }}
    .secondary-button {{
      background: var(--surface);
      color: var(--text);
      border-color: var(--line-strong);
    }}
    button.quiet, button.small {{
      background: var(--surface);
      border-color: var(--line);
      color: var(--text);
    }}
    button.quiet:hover, button.small:hover {{ border-color: var(--line-strong); background: var(--surface-alt); }}
    button.small {{
      min-height: 26px;
      padding: 4px 7px;
      font-size: 12px;
    }}
    textarea, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      font: inherit;
      background: var(--surface);
      color: var(--text);
    }}
    textarea {{ min-height: 118px; resize: vertical; }}
    label {{ display: grid; gap: 4px; font-weight: 700; color: var(--text); }}
    code {{
      display: block;
      overflow-x: auto;
      color: var(--navy);
      white-space: nowrap;
    }}
    .route-lab {{
      min-height: 100vh;
      padding: 14px;
      max-width: 1760px;
      margin: 0 auto;
    }}
    .paper-panel, .route-index, .evidence-viewer, .teaching-panel {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 8px 22px rgba(31, 41, 55, .07);
    }}
    .lab-top {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      box-shadow: 0 8px 22px rgba(31, 41, 55, .06);
    }}
    .lab-title, .run-strip, .route-step, .section-title, .location-head {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .lab-title p, .section-title p, .meta {{ margin: 0; color: var(--muted); font-size: 12px; }}
    .section-title {{
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 10px;
    }}
    .asset-icon {{
      width: 34px;
      height: 34px;
      display: inline-grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #f8edd0;
      color: var(--navy);
      font-weight: 900;
      font-size: 11px;
    }}
    .asset-icon img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 5px;
    }}
    .run-strip {{
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .run-form {{
      display: grid;
      grid-template-columns: 92px 92px 132px auto;
      gap: 8px;
      align-items: end;
    }}
    .run-form label {{ font-size: 12px; }}
    .last-result {{
      display: grid;
      gap: 2px;
      min-width: 112px;
      padding-left: 10px;
      border-left: 1px solid var(--line);
    }}
    .last-result span {{ color: var(--muted); font-size: 11px; }}
    .last-result strong {{ font-size: 13px; }}
    .lab-main {{
      display: grid;
      grid-template-columns: 245px minmax(420px, 1fr) 340px;
      gap: 14px;
      margin-top: 14px;
      align-items: start;
    }}
    .route-index, .evidence-viewer, .teaching-panel, .paper-panel {{
      padding: 12px;
    }}
    .route-list {{
      display: grid;
      gap: 7px;
    }}
    .route-step {{
      min-height: 52px;
      padding: 8px;
      border: 1px solid #e5e7eb;
      border-radius: 7px;
      text-decoration: none;
      background: var(--surface);
    }}
    .route-step:hover {{
      border-color: var(--line-strong);
      background: var(--surface-alt);
    }}
    .route-item-selected, .route-step:target {{
      background: var(--blue-soft);
      border-color: #bfdbfe;
      box-shadow: inset 4px 0 0 var(--blue);
    }}
    .route-copy {{ display: grid; gap: 1px; min-width: 0; }}
    .route-copy small {{ color: var(--muted); font-size: 11px; }}
    .clean, .passed, .status-clean, .status-learned {{ color: var(--green); }}
    .status-validation {{ color: var(--amber); }}
    .failed, .status-failed {{ color: var(--red); }}
    .unknown, .status-unknown {{ color: var(--muted); }}
    .screen-frame {{
      min-height: 360px;
      display: grid;
      place-items: center;
      background:
        linear-gradient(135deg, rgba(255,255,255,.06) 25%, transparent 25%),
        linear-gradient(225deg, rgba(255,255,255,.06) 25%, transparent 25%),
        var(--screen);
      background-size: 18px 18px;
      border: 12px solid #293437;
      border-radius: 10px;
      box-shadow: inset 0 0 0 2px #101719;
      overflow: hidden;
    }}
    .no-evidence-frame {{ min-height: 235px; }}
    .screen-frame img {{
      max-width: 100%;
      max-height: 620px;
      display: block;
      object-fit: contain;
      background: #000;
    }}
    .empty-evidence {{
      display: grid;
      gap: 6px;
      text-align: center;
      color: #e7f6ee;
      padding: 24px;
    }}
    .empty-evidence span {{ color: #bdd4c9; }}
    .evidence-notes {{
      margin-top: 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--surface-alt);
      padding: 10px;
    }}
    .evidence-notes h3 {{ color: var(--text); }}
    .evidence-notes p {{ color: var(--text); }}
    .evidence-notes ul {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 6px;
    }}
    .evidence-notes li {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border-top: 1px solid #e5e7eb;
      padding-top: 7px;
    }}
    .evidence-notes li:first-child {{ border-top: 0; padding-top: 0; }}
    .evidence-notes li span {{ color: var(--muted); text-align: right; }}
    .selected-location {{
      background: var(--surface-alt);
      border: 1px solid #e5e7eb;
      border-radius: 7px;
      padding: 9px 10px;
      margin-bottom: 10px;
    }}
    .selected-location p {{ margin: 4px 0 0; color: var(--muted); }}
    .mode-tabs {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 4px;
      margin-bottom: 10px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface-alt);
    }}
    .mode-tab {{
      text-align: center;
      text-decoration: none;
      border-radius: 6px;
      padding: 6px 7px;
      font-weight: 800;
      font-size: 12px;
      color: var(--text);
      background: transparent;
    }}
    .mode-tab:hover {{ background: #eef2f7; }}
    .mode-tab.segment-active {{
      background: var(--navy);
      color: #fff;
    }}
    .mode-panel {{ display: grid; gap: 9px; }}
    .note-tools {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }}
    .mini-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-top: 10px;
    }}
    .lab-bottom {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr) minmax(0, .9fr);
      gap: 14px;
      margin-top: 14px;
    }}
    .issue-list, .compact-list {{ display: grid; gap: 3px; }}
    .compact-row {{
      min-height: 34px;
      align-items: center;
      padding: 5px 0;
      border-top: 1px solid #e5e7eb;
    }}
    .compact-row:first-child {{ border-top: 0; }}
    .issue-summary-row {{
      display: grid;
      grid-template-columns: 110px 72px 120px minmax(0, 1fr) 72px 58px;
      gap: 8px;
      font-size: 12px;
    }}
    .observation-summary-row {{
      display: grid;
      grid-template-columns: 48px 100px 76px minmax(0, 1fr) 76px 58px;
      gap: 8px;
      font-size: 12px;
    }}
    .issue p, .note-row p {{ margin-bottom: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .selected-row {{ background: var(--blue-soft); }}
    .compact-pick {{
      display: grid;
      grid-template-columns: 78px minmax(0, 1fr) 62px;
      gap: 7px;
      align-items: center;
      text-decoration: none;
      padding: 6px 7px;
      border-radius: 6px;
      font-size: 12px;
    }}
    .compact-pick strong {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .compact-pick:hover {{ background: var(--surface-alt); }}
    .compact-pick.selected-row {{ background: var(--blue-soft); box-shadow: inset 3px 0 0 var(--blue); }}
    .detail-panel {{
      background: var(--surface-alt);
      border: 1px solid #e5e7eb;
      border-radius: 7px;
      padding: 10px;
      display: grid;
      gap: 8px;
    }}
    .detail-head {{ display: flex; justify-content: space-between; gap: 8px; align-items: center; }}
    .row-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      align-items: center;
    }}
    .row-actions details {{ position: relative; }}
    .row-actions summary {{
      cursor: pointer;
      border-radius: 6px;
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 4px 7px;
      font-size: 12px;
      font-weight: 750;
    }}
    .edit-form {{
      display: grid;
      gap: 6px;
      margin-top: 6px;
      min-width: 220px;
    }}
    .edit-form textarea {{ min-height: 80px; }}
    .review-link {{
      color: var(--blue);
      font-weight: 800;
      text-decoration: none;
    }}
    .badges {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 7px;
      font-size: 12px;
      color: var(--text);
      background: var(--badge);
      font-weight: 750;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 3px 7px;
      font-size: 12px;
      font-weight: 800;
    }}
    .badge.high, .badge.failed, .status-pill.status-failed {{ color: var(--red); border-color: #e8b3ae; background: var(--red-soft); }}
    .badge.medium, .badge.needs-validation, .status-pill.status-validation {{ color: var(--amber); border-color: #e5c989; background: var(--amber-soft); }}
    .badge.none, .badge.clean, .badge.passed, .status-pill.status-learned {{ color: var(--green); border-color: #acd7b5; background: var(--green-soft); }}
    .artifact-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin: 8px 0;
    }}
    .artifact-links a {{
      color: var(--blue);
      border: 1px solid var(--line);
      background: var(--surface);
      border-radius: 999px;
      padding: 4px 8px;
      text-decoration: none;
      font-size: 12px;
    }}
    pre {{
      max-height: 190px;
      overflow: auto;
      white-space: pre-wrap;
      background: var(--surface-alt);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px;
      color: var(--text);
    }}
    .empty {{ color: var(--muted); margin-bottom: 0; }}
    .error {{ border-color: #e8b3ae; color: var(--red); margin: 20px; padding: 14px; }}
    @media (max-width: 1180px) {{
      .lab-main {{ grid-template-columns: 220px minmax(0, 1fr); }}
      .teaching-panel {{ grid-column: 1 / -1; }}
      .lab-bottom {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 760px) {{
      .route-lab {{ padding: 10px; }}
      .lab-top {{ display: grid; }}
      .lab-main, .run-form {{ grid-template-columns: 1fr; }}
      .screen-frame {{ min-height: 280px; }}
    }}
  </style>
</head>
<body>{body}</body>
</html>"""


def render_error(message: str) -> str:
    return _page(
        title="Mario Route Lab Error",
        body=f"""
        <div class="route-lab">
          <section class="paper-panel error">
            <h1>Mario Route Lab Error</h1>
            <p>{_esc(message)}</p>
            <p><a href="/">Return to Mario Route Lab</a></p>
          </section>
        </div>
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
        session_dir_value = ""
    else:
        notes = _list_dicts(_load_yaml(session_dir / "notes.yaml").get("notes", []))
        issues_path = session_dir / "issues.yaml"
        proposals_path = session_dir / "variant_proposals.yaml"
        issues = _list_dicts(_load_yaml(issues_path).get("issues", []))
        proposals = _list_dicts(_load_yaml(proposals_path).get("proposals", []))
        session_label = session_dir.name
        session_dir_value = str(session_dir)

    visible_notes = [note for note in notes if str(note.get("ui_state", "")) != "archived"]
    active_issues = [issue for issue in issues if _is_active_issue(issue)]
    proposal_issue_ids = {str(proposal.get("source_issue")) for proposal in proposals}
    location_rows = []
    for location in locations:
        location_id = str(location["id"])
        location_notes = [
            note for note in visible_notes if _location_id_for_artifact(str(note.get("segment_id"))) == location_id
        ]
        location_issues = [issue for issue in active_issues if _location_id_for_artifact(str(issue.get("segment_id"))) == location_id]
        issue_ids = {str(issue.get("id")) for issue in location_issues}
        location_rows.append(
            {
                **location,
                "notes": len(location_notes),
                "issues": len(location_issues),
                "open_issues": len(location_issues),
                "proposals": len(issue_ids & proposal_issue_ids),
                "status": _location_status(location, location_issues),
            }
        )

    return {
        "session_label": session_label,
        "session_dir": session_dir_value,
        "locations": location_rows,
        "notes": visible_notes,
        "issues": issues,
        "recent_notes": visible_notes[-12:],
        "totals": {
            "notes": len(visible_notes),
            "issues": len(issues),
            "open_issues": len(active_issues),
            "proposals": len(proposals),
        },
    }


def _issue_row(issue: dict[str, object], summary: dict[str, object], selected: dict[str, object]) -> str:
    priority = str(issue.get("priority", "low"))
    location_label = _label_for_location(summary, str(issue.get("segment_id")))
    location_id = _location_id_for_artifact(str(issue.get("segment_id")))
    selected_mark = " selected-row" if location_id == selected.get("id") else ""
    return f"""
    <article class="issue compact-row issue-summary-row{selected_mark}">
      <strong>{_esc(location_label)}</strong>
      <span class="badge {priority}">{_esc(priority)}</span>
      <span>{_esc(_human_issue_type(str(issue.get('type', 'unknown'))))}</span>
      <p>{_esc(_short_text(str(issue.get('summary', '')), 120))}</p>
      <span class="meta">{_esc(str(issue.get('status', 'unknown')))}</span>
      <a class="review-link" href="{_esc(_location_url(location_id, mode='issue', issue_id=str(issue.get('id', ''))))}">Review</a>
    </article>"""


def _note_row(note: dict[str, object], summary: dict[str, object], selected: dict[str, object]) -> str:
    location_label = _label_for_location(summary, str(note.get("segment_id")))
    location_id = _location_id_for_artifact(str(note.get("segment_id")))
    created_at = str(note.get("created_at", ""))
    time_label = created_at[11:16] if len(created_at) >= 16 else "latest"
    selected_mark = " selected-row" if location_id == selected.get("id") else ""
    return f"""
    <article class="note-row compact-row observation-summary-row{selected_mark}">
      <span class="meta">{_esc(time_label)}</span>
      <strong>{_esc(location_label)}</strong>
      <span>{_esc(str(note.get('severity')))}</span>
      <p>{_esc(_short_text(str(note.get('text', '')), 120))}</p>
      <span class="meta">{_esc(_title_status(str(note.get('ui_state', 'open'))))}</span>
      <a class="review-link" href="{_esc(_location_url(location_id, mode='notes', note_id=str(note.get('id', ''))))}">Review</a>
    </article>"""


def _observation_compact_row(
    note: dict[str, object],
    location_id: str,
    selected_note: dict[str, object] | None,
) -> str:
    note_id = str(note.get("id", ""))
    selected_class = " selected-row" if selected_note and selected_note.get("id") == note_id else ""
    return f"""
      <a class="compact-pick{selected_class}" href="{_esc(_location_url(location_id, mode='notes', note_id=note_id))}">
        <span>{_esc(str(note.get('severity', 'note')))}</span>
        <strong>{_esc(_short_text(str(note.get('text', '')), 76))}</strong>
        <small>{_esc(_title_status(str(note.get('ui_state', 'open'))))}</small>
      </a>"""


def _issue_compact_row(
    issue: dict[str, object],
    location_id: str,
    selected_issue: dict[str, object] | None,
) -> str:
    issue_id = str(issue.get("id", ""))
    selected_class = " selected-row" if selected_issue and selected_issue.get("id") == issue_id else ""
    return f"""
      <a class="compact-pick{selected_class}" href="{_esc(_location_url(location_id, mode='issue', issue_id=issue_id))}">
        <span class="{_esc(str(issue.get('priority', 'low')))}">{_esc(str(issue.get('priority', 'low')))}</span>
        <strong>{_esc(_short_text(str(issue.get('summary', '')), 78))}</strong>
        <small>{_esc(str(issue.get('status', 'open')))}</small>
      </a>"""


def _observation_detail(note: dict[str, object], location_id: str) -> str:
    text = str(note.get("text", ""))
    state = str(note.get("ui_state", note.get("severity", "open")))
    return f"""
    <article class="detail-panel observation-detail">
      <div>
        <strong>{_esc(str(note.get('id', 'observation')))}</strong>
        <span class="badge">{_esc(_title_status(state))}</span>
      </div>
      <p>{_esc(text)}</p>
      {_observation_actions(note, location_id)}
    </article>"""


def _observation_actions(note: dict[str, object], location_id: str) -> str:
    note_id = str(note.get("id", ""))
    severity = str(note.get("severity", "note"))
    text = str(note.get("text", ""))
    return f"""
      <div class="row-actions">
        <details>
          <summary>Edit</summary>
          <form method="post" action="/observation-action" class="edit-form">
            <input type="hidden" name="return_location" value="{_esc(location_id)}">
            <input type="hidden" name="note_id" value="{_esc(note_id)}">
            <input type="hidden" name="action" value="edit">
            <textarea name="text">{_esc(text)}</textarea>
            <select name="severity">
              {_note_severity_options(severity)}
            </select>
            <button type="submit" class="quiet">Save Edit</button>
          </form>
        </details>
        {_observation_action_button(note_id, location_id, 'resolved', 'Mark Resolved')}
        {_observation_action_button(note_id, location_id, 'expected_behavior', 'Expected')}
        {_observation_action_button(note_id, location_id, 'convert_issue', 'Convert to Issue')}
        {_observation_action_button(note_id, location_id, 'archive', 'Archive')}
        {_observation_action_button(note_id, location_id, 'delete', 'Delete')}
      </div>"""


def _observation_action_button(note_id: str, location_id: str, action: str, label: str) -> str:
    return f"""
        <form method="post" action="/observation-action">
          <input type="hidden" name="return_location" value="{_esc(location_id)}">
          <input type="hidden" name="note_id" value="{_esc(note_id)}">
          <button type="submit" name="action" value="{_esc(action)}" class="quiet small">{_esc(label)}</button>
        </form>"""


def _issue_detail(issue: dict[str, object], location_id: str) -> str:
    return f"""
    <article class="detail-panel issue-detail">
      <div class="detail-head">
        <strong>{_esc(_human_issue_type(str(issue.get('type', 'issue'))))}</strong>
        <span class="badge {str(issue.get('priority', 'low'))}">{_esc(str(issue.get('priority', 'low')))}</span>
      </div>
      <p>{_esc(str(issue.get('summary', '')))}</p>
      <p class="meta">{_esc(str(issue.get('proposed_next_step', '')))}</p>
      {_issue_action_row(issue, location_id)}
    </article>"""


def _issue_action_row(issue: dict[str, object], location_id: str) -> str:
    issue_id = str(issue.get("id", ""))
    return f"""
      <div class="row-actions">
        {_issue_action_button(issue_id, location_id, 'resolved', 'Mark Resolved')}
        {_issue_action_button(issue_id, location_id, 'expected_behavior', 'Not a Bug')}
        {_issue_action_button(issue_id, location_id, 'needs_rerun', 'Needs Rerun')}
        <form method="post" action="/codex-task">
          <input type="hidden" name="issue_id" value="{_esc(issue_id)}">
          <button type="submit" class="quiet small">Create Codex Task</button>
        </form>
        {_issue_action_button(issue_id, location_id, 'archive', 'Archive')}
        {_issue_action_button(issue_id, location_id, 'delete', 'Delete')}
      </div>"""


def _issue_action_button(issue_id: str, location_id: str, action: str, label: str) -> str:
    return f"""
        <form method="post" action="/issue-action">
          <input type="hidden" name="return_location" value="{_esc(location_id)}">
          <input type="hidden" name="issue_id" value="{_esc(issue_id)}">
          <button type="submit" name="action" value="{_esc(action)}" class="quiet small">{_esc(label)}</button>
        </form>"""


def _last_command_panel(last_command: dict[str, object]) -> str:
    if not last_command:
        return '<div class="last-command"><p>No command has run from this panel yet.</p></div>'
    status = _last_command_status(last_command)
    output = str(last_command.get("stdout") or last_command.get("stderr") or "").strip()
    command = " ".join(str(part) for part in last_command.get("command", []))
    return f"""
    <div class="last-command">
      <p><strong>Latest Output:</strong> {_esc(str(last_command.get('name', 'unknown')))} · {_esc(_title_status(status))}</p>
      <p class="meta">{_esc(str(last_command.get('ran_at', '')))}</p>
      {f'<p><code>{_esc(command)}</code></p>' if command else ''}
      {_artifact_links(output)}
      {f'<pre>{_esc(output[-4000:])}</pre>' if output else ''}
    </div>"""


def _selected_location(
    locations: list[dict[str, object]],
    *,
    selected_location_id: str | None = None,
) -> dict[str, object]:
    if selected_location_id:
        normalized = _location_id_for_artifact(selected_location_id)
        for location in locations:
            if location.get("id") == normalized:
                return location
    for location in locations:
        if location.get("open_issues"):
            return location
    for location in locations:
        if str(location.get("status")) == "blocked":
            return location
    return locations[0] if locations else {}


def _route_state(location: dict[str, object]) -> str:
    status = str(location.get("status", "unknown"))
    if status == "works":
        return "learned"
    if status == "blocked" or location.get("open_issues"):
        return "failed"
    if status in {"needs review", "bridged", "flaky"}:
        return "needs validation"
    return "unknown"


def _latest_evidence(
    summary: dict[str, object],
    last_command: dict[str, object],
    selected: dict[str, object],
) -> dict[str, object]:
    output = str(last_command.get("stdout") or last_command.get("stderr") or "")
    candidates = _artifact_paths_from_output(output)
    session_dir = summary.get("session_dir")
    if isinstance(session_dir, str) and session_dir:
        candidates.append(Path(session_dir))

    image = _first_existing_image(candidates)
    details: list[tuple[str, str]] = [
        ("Selected location", str(selected.get("label", "Route"))),
        ("Route state", _title_status(_route_state(selected))),
    ]
    artifact_root = _first_existing_path(candidates)
    if artifact_root is not None:
        details.append(("Artifact", str(artifact_root)))
    return {"image": image, "details": details}


def _artifact_paths_from_output(output: str) -> list[Path]:
    paths = []
    interesting_keys = {
        "session_dir",
        "manifest",
        "review_file",
        "report",
        "html",
        "contact_sheet",
        "artifacts_dir",
    }
    for raw_line in output.splitlines():
        if "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        if key.strip() not in interesting_keys:
            continue
        path = Path(value.strip()).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        paths.append(path)
    return paths


def _first_existing_path(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _first_existing_image(paths: list[Path]) -> Path | None:
    preferred_names = ("contact_sheet.png", "latest.png", "screenshot.png")
    search_roots = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            return path
        if path.is_dir():
            search_roots.append(path)
    for root in search_roots:
        for name in preferred_names:
            candidate = root / name
            if candidate.is_file():
                return candidate
        for candidate in sorted(root.rglob("*")):
            if candidate.is_file() and candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                return candidate
    return None


def _artifact_url(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(ARTIFACT_DIR.resolve())
    except ValueError:
        return resolved.as_uri()
    return "/artifacts/" + "/".join(relative.parts)


def _latest_observed_state(last_command: dict[str, object]) -> str:
    output = str(last_command.get("stdout") or last_command.get("stderr") or "")
    if not output:
        return "No run has been captured from this panel yet."
    interesting = [
        line
        for line in output.splitlines()
        if any(token in line.lower() for token in ("failed", "success", "metrics_passed", "primary_segment", "session_dir"))
    ]
    return interesting[-1] if interesting else output.splitlines()[-1]


def _notes_for_location(summary: dict[str, object], selected: dict[str, object]) -> list[dict[str, object]]:
    selected_id = str(selected.get("id", ""))
    notes = _list_dicts(summary.get("notes", []))
    return [
        note
        for note in notes
        if _location_id_for_artifact(str(note.get("segment_id"))) == selected_id
        and str(note.get("ui_state", "")) != "archived"
    ]


def _selected_mode(
    requested: str | None,
    notes: list[dict[str, object]],
    issues: list[dict[str, object]],
    selected_note_id: str | None,
    selected_issue_id: str | None,
) -> str:
    if selected_issue_id:
        return "issue"
    if selected_note_id:
        return "notes"
    if requested in {"add", "notes", "issue"}:
        return requested
    return "issue" if issues else "add"


def _selected_note(notes: list[dict[str, object]], note_id: str | None) -> dict[str, object] | None:
    if note_id:
        for note in notes:
            if str(note.get("id")) == note_id:
                return note
    return notes[0] if notes else None


def _selected_issue(issues: list[dict[str, object]], issue_id: str | None) -> dict[str, object] | None:
    if issue_id:
        for issue in issues:
            if str(issue.get("id")) == issue_id:
                return issue
    return issues[0] if issues else None


def _issues_for_location(summary: dict[str, object], selected: dict[str, object]) -> list[dict[str, object]]:
    selected_id = str(selected.get("id", ""))
    return [
        issue
        for issue in _list_dicts(summary.get("issues", []))
        if _location_id_for_artifact(str(issue.get("segment_id"))) == selected_id
        and _is_active_issue(issue)
    ]


def _sorted_notes(summary: dict[str, object], selected: dict[str, object]) -> list[dict[str, object]]:
    selected_id = str(selected.get("id", ""))
    notes = [
        note
        for note in _list_dicts(summary.get("notes", []))
        if str(note.get("ui_state", "")) != "archived"
    ]
    return sorted(
        notes,
        key=lambda note: (
            _location_id_for_artifact(str(note.get("segment_id"))) != selected_id,
            str(note.get("created_at", "")),
        ),
        reverse=False,
    )


def _sorted_issues(summary: dict[str, object], selected: dict[str, object]) -> list[dict[str, object]]:
    selected_id = str(selected.get("id", ""))
    issues = [issue for issue in _list_dicts(summary.get("issues", [])) if _is_active_issue(issue)]
    return sorted(
        issues,
        key=lambda issue: (
            _location_id_for_artifact(str(issue.get("segment_id"))) != selected_id,
            _priority_rank_for_ui(str(issue.get("priority", "low"))),
            str(issue.get("id", "")),
        ),
    )


def _is_active_issue(issue: dict[str, object]) -> bool:
    return str(issue.get("status", "open")) in {"open", "needs_rerun"}


def _priority_rank_for_ui(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2, "none": 3}.get(priority, 4)


def _note_severity_options(selected: str) -> str:
    labels = (
        ("bug", "failure"),
        ("objective", "expected behavior"),
        ("map_action", "route instruction"),
        ("harden", "validation note"),
        ("guide_detail", "positive evidence"),
        ("note", "note"),
    )
    return "".join(
        f'<option value="{_esc(value)}"{" selected" if value == selected else ""}>{_esc(label)}</option>'
        for value, label in labels
    )


def _short_text(value: str, limit: int) -> str:
    collapsed = " ".join(value.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: max(0, limit - 1)].rstrip() + "..."


def _last_command_status(last_command: dict[str, object]) -> str:
    if not last_command:
        return "unknown"
    try:
        return "passed" if int(last_command.get("returncode", 1)) == 0 else "failed"
    except (TypeError, ValueError):
        return "unknown"


def _title_status(status: str) -> str:
    return status.replace("_", " ").replace("-", " ").title()


def _icon_name_for_location(location: dict[str, object]) -> str:
    location_type = str(location.get("type", "level"))
    location_id = str(location.get("id", ""))
    if location_type == "map":
        return "map_icon.png"
    if location_type == "fortress":
        return "fortress_icon.png"
    if location_type == "airship":
        return "airship_icon.png"
    if location_type == "world_clear":
        return "king_icon.png"
    if "toad" in location_id:
        return "toad_house_icon.png"
    if "spade" in location_id:
        return "spade_icon.png"
    if "hammer" in location_id:
        return "hammer_bro_icon.png"
    if location_id == "world_1_3":
        return "whistle_icon.png"
    return "level_icon.png"


def _icon_fallback(location: dict[str, object]) -> str:
    location_type = str(location.get("type", "level"))
    label = str(location.get("label", "?"))
    fallbacks = {
        "map": "MAP",
        "fortress": "FORT",
        "airship": "AIR",
        "world_clear": "KING",
        "map_event": "EVT",
        "map_enemy": "HB",
    }
    return fallbacks.get(location_type, label[:3].upper())


def _asset_icon(filename: str, fallback: str, alt: str) -> str:
    asset_path = LOCAL_ASSET_DIR / filename
    if asset_path.is_file():
        return (
            '<span class="asset-icon">'
            f'<img src="/assets/local/{_esc(filename)}" alt="{_esc(alt)}">'
            "</span>"
        )
    return f'<span class="asset-icon" aria-hidden="true">{_esc(fallback)}</span>'


def _artifact_links(output: str) -> str:
    links = []
    interesting_keys = {
        "session_dir",
        "manifest",
        "notes_file",
        "review_file",
        "report",
        "html",
        "proposal",
        "proposals_file",
        "issues_file",
        "ui_summary",
    }
    for raw_line in output.splitlines():
        if "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in interesting_keys or not value:
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        links.append((key.replace("_", " "), path))
        if len(links) >= 6:
            break
    if not links:
        return ""
    rendered = "".join(f'<a href="{_esc(_artifact_url(path))}">{_esc(label)}</a>' for label, path in links)
    return f'<div class="artifact-links">{rendered}</div>'


def _run_world_1_from_form(data: dict[str, list[str]]) -> dict[str, object]:
    game_file = os.environ.get("SMB3_GAME_FILE")
    if not game_file:
        raise LabUiError("Set SMB3_GAME_FILE before running from Mario Route Lab.")
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


def _issue_id_from_form(data: dict[str, list[str]]) -> str:
    issue_id = _single(data, "issue_id", default="")
    if issue_id:
        return issue_id
    index = int(_single(data, "issue_index"))
    summary = build_control_panel_summary()
    issues = summary.get("issues", [])
    if not isinstance(issues, list) or index < 1 or index > len(issues):
        raise LabUiError("Issue selection is no longer available. Refresh the panel and try again.")
    issue = issues[index - 1]
    if not isinstance(issue, dict) or not issue.get("id"):
        raise LabUiError("Issue selection is invalid. Refresh the panel and try again.")
    return str(issue["id"])


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


def _update_observation_latest(
    note_id: str,
    action: str,
    data: dict[str, list[str]],
) -> None:
    session_dir = _latest_session_dir_required()
    notes_path = session_dir / "notes.yaml"
    notes_doc = _load_yaml(notes_path)
    notes = notes_doc.get("notes", [])
    if not isinstance(notes, list):
        raise LabUiError(f"Invalid notes file: {notes_path}")

    matched = None
    for note in notes:
        if isinstance(note, dict) and str(note.get("id")) == note_id:
            matched = note
            break
    if matched is None:
        raise LabUiError(f"Observation not found: {note_id}")

    if action == "delete":
        notes_doc["notes"] = [note for note in notes if not (isinstance(note, dict) and str(note.get("id")) == note_id)]
        _remove_note_from_issues(session_dir, note_id)
        _write_yaml(notes_path, notes_doc)
        return
    if action == "edit":
        text = _single(data, "text", default="").strip()
        if not text:
            raise LabUiError("Observation text is required")
        matched["text"] = text
        matched["severity"] = _single(data, "severity", default=str(matched.get("severity", "note")))
        matched["updated_at"] = _now()
        matched.setdefault("interpretation", {})["status"] = "pending_review"
    elif action == "resolved":
        matched["ui_state"] = "resolved"
        matched["resolved_at"] = _now()
        matched.setdefault("interpretation", {})["status"] = "resolved"
        _resolve_issues_for_note(session_dir, note_id)
    elif action == "expected_behavior":
        matched["ui_state"] = "expected_behavior"
        matched["severity"] = "guide_detail"
        matched["updated_at"] = _now()
        interpretation = matched.setdefault("interpretation", {})
        interpretation["status"] = "accepted"
        interpretation["classification"] = "expected_behavior"
        _accept_issues_for_note(session_dir, note_id)
    elif action == "convert_issue":
        matched["ui_state"] = "open"
        matched["severity"] = "bug"
        matched["updated_at"] = _now()
        matched.setdefault("interpretation", {})["status"] = "pending_review"
        _ensure_issue_for_note(session_dir, matched)
    elif action == "archive":
        matched["ui_state"] = "archived"
        matched["archived_at"] = _now()
    else:
        raise LabUiError(f"Unknown observation action: {action}")
    _write_yaml(notes_path, notes_doc)


def _update_issue_latest(issue_id: str, action: str) -> None:
    session_dir = _latest_session_dir_required()
    issues_path = session_dir / "issues.yaml"
    issues_doc = _load_yaml(issues_path)
    issues = issues_doc.get("issues", [])
    if not isinstance(issues, list):
        raise LabUiError(f"Invalid issues file: {issues_path}")

    matched = None
    for issue in issues:
        if isinstance(issue, dict) and str(issue.get("id")) == issue_id:
            matched = issue
            break
    if matched is None:
        raise LabUiError(f"Issue not found: {issue_id}")

    if action == "delete":
        issues_doc["issues"] = [issue for issue in issues if not (isinstance(issue, dict) and str(issue.get("id")) == issue_id)]
        _write_yaml(issues_path, issues_doc)
        return
    if action == "resolved":
        matched["status"] = "resolved"
        matched["actionable"] = False
        matched["resolved_at"] = _now()
    elif action == "expected_behavior":
        matched["status"] = "accepted"
        matched["actionable"] = False
        matched["type"] = "expected_behavior"
        matched["accepted_at"] = _now()
    elif action == "archive":
        matched["status"] = "archived"
        matched["actionable"] = False
        matched["archived_at"] = _now()
    elif action == "needs_rerun":
        matched["status"] = "needs_rerun"
        matched["actionable"] = True
        matched["updated_at"] = _now()
    else:
        raise LabUiError(f"Unknown issue action: {action}")
    _write_yaml(issues_path, issues_doc)


def _remove_note_from_issues(session_dir: Path, note_id: str) -> None:
    issues_path = session_dir / "issues.yaml"
    issues_doc = _load_yaml(issues_path)
    issues = issues_doc.get("issues", [])
    if not isinstance(issues, list):
        return
    kept = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        source_notes = [str(value) for value in issue.get("source_notes", [])]
        if note_id in source_notes:
            source_notes = [value for value in source_notes if value != note_id]
            issue["source_notes"] = source_notes
        if source_notes or note_id not in [str(value) for value in issue.get("source_notes", [])]:
            kept.append(issue)
    issues_doc["issues"] = [issue for issue in kept if issue.get("source_notes")]
    _write_yaml(issues_path, issues_doc)


def _resolve_issues_for_note(session_dir: Path, note_id: str) -> None:
    _update_issues_for_note(session_dir, note_id, status="resolved", actionable=False)


def _accept_issues_for_note(session_dir: Path, note_id: str) -> None:
    _update_issues_for_note(session_dir, note_id, status="accepted", actionable=False, issue_type="expected_behavior")


def _update_issues_for_note(
    session_dir: Path,
    note_id: str,
    *,
    status: str,
    actionable: bool,
    issue_type: str | None = None,
) -> None:
    issues_path = session_dir / "issues.yaml"
    issues_doc = _load_yaml(issues_path)
    issues = issues_doc.get("issues", [])
    if not isinstance(issues, list):
        return
    changed = False
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if note_id in [str(value) for value in issue.get("source_notes", [])]:
            issue["status"] = status
            issue["actionable"] = actionable
            issue["updated_at"] = _now()
            if issue_type is not None:
                issue["type"] = issue_type
            changed = True
    if changed:
        _write_yaml(issues_path, issues_doc)


def _ensure_issue_for_note(session_dir: Path, note: dict[str, object]) -> None:
    issues_path = session_dir / "issues.yaml"
    issues_doc = _load_yaml(issues_path) or {"issues": []}
    issues = issues_doc.setdefault("issues", [])
    if not isinstance(issues, list):
        raise LabUiError(f"Invalid issues file: {issues_path}")
    note_id = str(note.get("id"))
    for issue in issues:
        if isinstance(issue, dict) and note_id in [str(value) for value in issue.get("source_notes", [])]:
            issue["status"] = "open"
            issue["actionable"] = True
            issue["type"] = "user_observation"
            issue["updated_at"] = _now()
            _write_yaml(issues_path, issues_doc)
            return
    segment_id = str(note.get("segment_id", "unknown"))
    issue_id = _next_issue_id(issues, segment_id)
    issues.append(
        {
            "id": issue_id,
            "segment_id": segment_id,
            "type": "user_observation",
            "priority": "medium",
            "status": "open",
            "actionable": True,
            "source_notes": [note_id],
            "summary": str(note.get("text", "")),
            "proposed_next_step": "Patch or validate this observed route behavior.",
            "created_at": _now(),
        }
    )
    _write_yaml(issues_path, issues_doc)


def _next_issue_id(issues: list[object], segment_id: str) -> str:
    prefix = f"issue_{segment_id}_"
    indexes = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        issue_id = str(issue.get("id", ""))
        if issue_id.startswith(prefix):
            try:
                indexes.append(int(issue_id.removeprefix(prefix)))
            except ValueError:
                continue
    return f"{prefix}{(max(indexes) + 1 if indexes else 1):03d}"


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
    if any(issue.get("priority") == "high" and _is_active_issue(issue) for issue in issues):
        return "blocked"
    if any(_is_active_issue(issue) for issue in issues):
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


def _state_class(status: str) -> str:
    normalized = _status_class(status)
    if normalized in {"needs-review", "needs-validation", "bridged", "flaky"}:
        return "validation"
    return normalized


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


def _location_url(
    location_id: str,
    *,
    mode: str | None = None,
    note_id: str | None = None,
    issue_id: str | None = None,
) -> str:
    if not location_id:
        return "/"
    params = [f"location={_esc(_location_id_for_artifact(location_id))}"]
    if mode:
        params.append(f"mode={_esc(mode)}")
    if note_id:
        params.append(f"note={_esc(note_id)}")
    if issue_id:
        params.append(f"issue={_esc(issue_id)}")
    return "/?" + "&".join(params)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _latest_session_dir_required() -> Path:
    session_dir = _latest_session_dir_if_any()
    if session_dir is None:
        raise LabUiError("No active lab session is available.")
    return session_dir


def _list_dicts(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _esc(value: str) -> str:
    return html.escape(value, quote=True)
