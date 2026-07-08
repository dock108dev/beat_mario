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
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(render_lab_ui())
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


def render_lab_ui() -> str:
    summary = build_control_panel_summary()
    last_command = _load_yaml(LAST_COMMAND_PATH)
    locations = _list_dicts(summary.get("locations", []))
    selected = _selected_location(locations)
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

            {_teaching_panel(locations, selected)}
          </main>

          <section class="lab-bottom">
            <section class="paper-panel">
              <div class="section-title">
                <h2>Timeline / Attempt Log</h2>
                <p>Recent attempts, results, and artifacts.</p>
              </div>
              {_last_command_panel(last_command)}
            </section>
            <section class="paper-panel">
              <div class="section-title">
                <h2>Things Mario Still Gets Wrong</h2>
                <p>Demoted issue context attached to route locations.</p>
              </div>
              <div class="issue-list">
                {''.join(_issue_row(issue, summary, index) for index, issue in enumerate(summary['issues'], start=1)) or '<p class="empty">No issues yet.</p>'}
              </div>
            </section>
            <section class="paper-panel">
              <div class="section-title">
                <h2>Recent Observations</h2>
                <p>Latest notes from route review.</p>
              </div>
              {''.join(_note_row(note, summary) for note in summary['recent_notes']) or '<p class="empty">No observations yet.</p>'}
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
                <button type="submit">Run World 1</button>
              </form>
              <div class="last-result">
                <span>Last run result</span>
                <strong class="{_status_class(_last_command_status(last_command))}">{_esc(_title_status(_last_command_status(last_command)))}</strong>
              </div>
              <form method="post" action="/refresh" class="refresh-form">
                <button type="submit" class="quiet">Refresh Review</button>
              </form>
            </div>"""


def _route_item(location: dict[str, object], selected: dict[str, object]) -> str:
    location_id = str(location["id"])
    label = str(location.get("label", location_id))
    state = _route_state(location)
    selected_class = " selected" if selected.get("id") == location_id else ""
    return f"""
                <a class="route-step {_status_class(state)}{selected_class}" href="#teach-{_esc(location_id)}">
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
    if isinstance(image_path, Path):
        image_html = f'<img src="{_esc(_artifact_url(image_path))}" alt="Latest route evidence">'
    else:
        image_html = """
                <div class="empty-evidence">
                  <strong>Run World 1 to capture evidence</strong>
                  <span>When screenshots or contact sheets exist, they appear here.</span>
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
              <div class="screen-frame">
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


def _teaching_panel(locations: list[dict[str, object]], selected: dict[str, object]) -> str:
    return f"""
            <aside class="teaching-panel">
              <div class="section-title">
                <h2>Teach This Section</h2>
                <p>What should Mario do next?</p>
              </div>
              <form method="post" action="/notes">
                {''.join(_teach_section(location, selected) for location in locations)}
                <button type="submit">Save Teaching Note</button>
              </form>
              <form method="post" action="/test" class="mini-actions">
                <button type="submit" name="action" value="phase_gate" class="quiet">Phase Gate</button>
                <button type="submit" name="action" value="unit_tests" class="quiet">Unit Tests</button>
                <button type="submit" name="action" value="render_check" class="quiet">Render Check</button>
              </form>
            </aside>"""


def _teach_section(location: dict[str, object], selected: dict[str, object]) -> str:
    location_id = str(location["id"])
    label = str(location.get("label", location_id))
    open_attr = " open" if selected.get("id") == location_id else ""
    return f"""
                <details id="teach-{_esc(location_id)}" class="teach-step"{open_attr}>
                  <summary>
                    <span>{_esc(label)}</span>
                    <small>{_esc(_title_status(_route_state(location)))}</small>
                  </summary>
                  <p>{_esc(str(location.get('objective', '')))}</p>
                  <textarea name="note__{_esc(location_id)}" placeholder="Where did Mario fail, or what should he do here?"></textarea>
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
                </details>"""


def _page(*, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b1020;
      --panel: rgba(17, 24, 39, .94);
      --panel-soft: rgba(23, 32, 51, .94);
      --panel-elevated: rgba(31, 41, 55, .96);
      --text: #f8fafc;
      --muted: #94a3b8;
      --line: rgba(148, 163, 184, .24);
      --mario-red: #e53935;
      --mario-blue: #1e88e5;
      --grass-green: #43a047;
      --coin-gold: #fbbf24;
      --block-orange: #f97316;
      --status-works: #22c55e;
      --status-review: #f59e0b;
      --status-blocked: #ef4444;
      --status-unknown: #94a3b8;
      --status-bridged: #60a5fa;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(30,136,229,.22), transparent 35%),
        radial-gradient(circle at top right, rgba(251,191,36,.14), transparent 30%),
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px),
        var(--bg);
      background-size: auto, auto, 24px 24px, 24px 24px, auto;
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 28px; line-height: 1.05; margin-bottom: 5px; letter-spacing: 0; }}
    h2 {{ font-size: 16px; margin-bottom: 0; letter-spacing: 0; }}
    h3 {{ font-size: 15px; margin-bottom: 4px; letter-spacing: 0; }}
    a {{ color: inherit; }}
    button {{
      border: 1px solid rgba(96, 165, 250, .55);
      background: rgba(30, 136, 229, .88);
      color: #fff;
      border-radius: 8px;
      padding: 9px 12px;
      font-weight: 750;
      cursor: pointer;
      min-height: 38px;
    }}
    button:hover {{ background: rgba(30, 136, 229, 1); }}
    button.secondary {{
      background: rgba(15, 23, 42, .85);
      border-color: rgba(148, 163, 184, .34);
      color: #e2e8f0;
    }}
    button.primary {{
      background: linear-gradient(180deg, #e53935, #b91c1c);
      border-color: rgba(248, 113, 113, .7);
      box-shadow: 0 10px 24px rgba(229, 57, 53, .22);
    }}
    textarea, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px;
      font: inherit;
      background: rgba(15, 23, 42, .92);
      color: var(--text);
    }}
    textarea {{ min-height: 92px; resize: vertical; }}
    label {{ display: grid; gap: 6px; font-weight: 700; color: #cbd5e1; }}
    code {{
      display: block;
      overflow-x: auto;
      color: #dbeafe;
      white-space: nowrap;
    }}
    .control-page {{
      min-height: 100vh;
      padding: 20px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 18px 50px rgba(0,0,0,.28);
    }}
    .mission-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 18px;
      border-top: 2px solid rgba(251,191,36,.75);
    }}
    .mission-identity, .mission-actions, .section-head, .location-head {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    .mission-identity {{ min-width: 0; }}
    .mission-actions {{ justify-content: flex-end; flex-wrap: wrap; }}
    .mission-meta, .meta {{ margin: 0; color: var(--muted); font-size: 12px; }}
    .eyebrow {{
      margin: 0 0 4px;
      color: #fde68a;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .asset-icon {{
      width: 38px;
      height: 38px;
      display: inline-grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: 8px;
      border: 1px solid rgba(251,191,36,.42);
      background: rgba(251,191,36,.12);
      color: #fde68a;
      font-weight: 900;
      font-size: 12px;
    }}
    .asset-icon img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 7px;
    }}
    .status-strip {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }}
    .status-card {{
      background: linear-gradient(180deg, rgba(31,41,55,.98), rgba(15,23,42,.98));
      border: 1px solid var(--line);
      border-left: 4px solid var(--status-unknown);
      border-radius: 8px;
      padding: 13px;
      min-height: 104px;
    }}
    .status-card span {{ color: var(--muted); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .status-card strong {{ display: block; margin-top: 8px; font-size: 25px; line-height: 1; }}
    .status-card p {{ margin: 9px 0 0; color: var(--muted); font-size: 12px; }}
    .status-card.works {{ border-left-color: var(--status-works); }}
    .status-card.needs-review {{ border-left-color: var(--status-review); }}
    .status-card.blocked {{ border-left-color: var(--status-blocked); }}
    .status-card.bridged {{ border-left-color: var(--status-bridged); }}
    .route-panel, .layout, .lower-grid, .board {{ margin-top: 16px; }}
    .route-panel {{ padding: 14px; }}
    .section-head {{ justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
    .quick-filters {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .quick-filters input {{
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }}
    .quick-filters label {{
      color: #cbd5e1;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 12px;
      background: rgba(15,23,42,.68);
      cursor: pointer;
      display: inline-flex;
      width: auto;
      gap: 0;
    }}
    .quick-filters label:has(input:checked) {{
      color: #fff;
      border-color: rgba(251,191,36,.6);
      background: rgba(251,191,36,.16);
    }}
    .route-rail {{
      display: flex;
      gap: 10px;
      overflow-x: auto;
      padding: 4px 4px 12px;
      scrollbar-color: rgba(148,163,184,.45) transparent;
    }}
    .route-node {{
      position: relative;
      min-width: 112px;
      min-height: 126px;
      padding: 12px 10px;
      border-radius: 8px;
      background: rgba(15, 23, 42, .94);
      border: 1px solid rgba(148, 163, 184, .25);
      text-decoration: none;
      display: grid;
      gap: 6px;
      justify-items: center;
      text-align: center;
    }}
    .route-node::after {{
      content: "";
      position: absolute;
      left: calc(100% + 1px);
      top: 33px;
      width: 10px;
      height: 2px;
      background: rgba(148, 163, 184, .42);
    }}
    .route-node:last-child::after {{ display: none; }}
    .route-node strong {{ font-size: 14px; }}
    .route-node span, .route-node small {{ color: var(--muted); font-size: 11px; }}
    .route-node.works {{ border-color: rgba(34,197,94,.8); box-shadow: 0 0 0 3px rgba(34,197,94,.14); }}
    .route-node.needs-review {{ border-color: rgba(245,158,11,.8); box-shadow: 0 0 0 3px rgba(245,158,11,.14); }}
    .route-node.blocked {{ border-color: rgba(239,68,68,.9); box-shadow: 0 0 0 3px rgba(239,68,68,.18); }}
    .route-node.bridged {{ border-color: rgba(96,165,250,.86); box-shadow: 0 0 0 3px rgba(96,165,250,.16); }}
    .layout, .lower-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.18fr) minmax(330px, .82fr);
      gap: 16px;
    }}
    .run-panel, .guide-panel, .lower-grid .panel, .board {{ padding: 14px; }}
    .control-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      align-items: end;
    }}
    .button-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .command-preview {{
      margin-top: 12px;
      border: 1px solid var(--line);
      background: rgba(15,23,42,.68);
      border-radius: 8px;
      padding: 10px;
    }}
    .command-preview span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .rule-list {{ display: grid; gap: 10px; }}
    .rule-list div {{
      display: grid;
      gap: 3px;
      border-left: 3px solid rgba(67,160,71,.72);
      padding: 2px 0 2px 10px;
    }}
    .rule-list span {{ color: var(--muted); }}
    .location-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(235px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }}
    .location-card {{
      padding: 12px;
      display: grid;
      gap: 10px;
      min-height: 190px;
      background: var(--panel-soft);
      border: 1px solid var(--line);
      border-radius: 8px;
      scroll-margin-top: 18px;
    }}
    .location-card:target {{
      border-color: rgba(251,191,36,.85);
      box-shadow: 0 0 0 4px rgba(251,191,36,.18);
    }}
    .control-page:has(#filter-open:checked) .location-card:not([data-open="true"]),
    .control-page:has(#filter-blocked:checked) .location-card:not([data-status="blocked"]),
    .control-page:has(#filter-needs-review:checked) .location-card:not([data-status="needs-review"]),
    .control-page:has(#filter-works:checked) .location-card:not([data-status="works"]) {{
      display: none;
    }}
    .location-head {{ justify-content: space-between; align-items: start; }}
    .location-title {{ display: flex; gap: 9px; align-items: center; min-width: 0; }}
    .objective {{ color: var(--muted); min-height: 42px; margin-bottom: 0; }}
    .route-role {{ color: #cbd5e1; font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .badges {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      border: 1px solid rgba(148,163,184,.28);
      border-radius: 999px;
      padding: 4px 8px;
      font-size: 12px;
      color: #cbd5e1;
      background: rgba(15,23,42,.64);
      font-weight: 750;
    }}
    .badge.blocked, .badge.failed, .blocked, .high {{ color: #fecaca; border-color: rgba(239,68,68,.55); background: rgba(239,68,68,.14); }}
    .badge.needs-review, .badge.medium {{ color: #fde68a; border-color: rgba(245,158,11,.55); background: rgba(245,158,11,.14); }}
    .badge.works, .badge.passed, .badge.none {{ color: #bbf7d0; border-color: rgba(34,197,94,.55); background: rgba(34,197,94,.14); }}
    .badge.bridged {{ color: #bfdbfe; border-color: rgba(96,165,250,.55); background: rgba(96,165,250,.14); }}
    .badge.unknown {{ color: #e2e8f0; }}
    details.segment-detail {{
      border-top: 1px solid var(--line);
      padding-top: 8px;
    }}
    details.segment-detail summary {{
      cursor: pointer;
      color: #dbeafe;
      font-weight: 800;
    }}
    details.segment-detail[open] summary {{ margin-bottom: 10px; }}
    .note-tools {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }}
    .issue-table {{ display: grid; gap: 8px; }}
    .issue, .note-row, .last-command {{
      border-top: 1px solid var(--line);
      padding: 10px 0;
    }}
    .issue:first-child, .note-row:first-of-type, .last-command:first-child {{ border-top: 0; }}
    .issue {{
      display: grid;
      grid-template-columns: minmax(90px, .55fr) minmax(90px, .55fr) minmax(0, 2fr) auto;
      gap: 10px;
      align-items: start;
    }}
    .issue p, .note-row p {{ margin-bottom: 0; }}
    .last-command {{
      margin-top: 12px;
      padding-bottom: 0;
      color: var(--muted);
    }}
    .artifact-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin: 8px 0;
    }}
    .artifact-links a {{
      color: #dbeafe;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
      text-decoration: none;
      font-size: 12px;
    }}
    pre {{
      max-height: 190px;
      overflow: auto;
      white-space: pre-wrap;
      background: rgba(2,6,23,.72);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px;
      color: #dbeafe;
    }}
    .empty {{ color: var(--muted); margin-bottom: 0; }}
    .error {{ border-color: rgba(239,68,68,.55); color: #fecaca; margin: 20px; padding: 14px; }}
    @media (max-width: 980px) {{
      .mission-header, .layout, .lower-grid, .control-grid {{ grid-template-columns: 1fr; }}
      .mission-header {{ display: grid; }}
      .status-strip {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .issue {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 620px) {{
      .control-page {{ padding: 12px; }}
      .status-strip, .location-grid {{ grid-template-columns: 1fr; }}
      .mission-actions {{ justify-content: flex-start; }}
    }}
  </style>
</head>
<body>{body}</body>
</html>"""


def _location_card(location: dict[str, object]) -> str:
    location_id = str(location["id"])
    label = str(location["label"])
    objective = str(location.get("objective", ""))
    status = str(location.get("status", "unknown"))
    role = _route_role(location)
    return f"""
    <article id="{_esc(location_id)}" class="location-card" data-status="{_esc(_status_class(status))}" data-open="{str(bool(location.get('open_issues'))).lower()}">
      <div class="location-head">
        <div class="location-title">
          {_asset_icon(_icon_name_for_location(location), _icon_fallback(location), f'{label} icon')}
          <div>
            <h3>{_esc(label)}</h3>
            <span class="route-role">{_esc(role)}</span>
          </div>
        </div>
        <span id="status-{_esc(_status_class(status))}" class="badge {_status_class(status)}">{_esc(_title_status(status))}</span>
      </div>
      <p class="objective">{_esc(objective)}</p>
      <div class="badges">
        <span class="badge">{location.get('notes', 0)} notes</span>
        <span class="badge">{location.get('open_issues', 0)} open</span>
        <span class="badge">{location.get('proposals', 0)} variants</span>
      </div>
      <details class="segment-detail">
        <summary>Open Detail / Add Note</summary>
        <p class="meta">Latest evidence: {location.get('issues', 0)} issue records · {location.get('notes', 0)} notes linked.</p>
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
      </details>
    </article>"""


def render_error(message: str) -> str:
    return _page(
        title="Control Panel Error",
        body=f"""
        <div class="control-page">
          <section class="panel error">
            <h1>Control Panel Error</h1>
            <p>{_esc(message)}</p>
            <p><a href="/">Return to control panel</a></p>
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


def _issue_row(issue: dict[str, object], summary: dict[str, object], index: int) -> str:
    priority = str(issue.get("priority", "low"))
    location_label = _label_for_location(summary, str(issue.get("segment_id")))
    action = ""
    if issue.get("actionable"):
        action = f"""
        <form method="post" action="/codex-task">
          <input type="hidden" name="issue_index" value="{index}">
          <button type="submit" class="secondary">Create Codex Task</button>
        </form>"""
    return f"""
    <article class="issue">
      <div>
        <strong>{_esc(location_label)}</strong>
        <p class="meta">{_esc(str(issue.get('status', 'unknown')))}</p>
      </div>
      <div class="badges">
        <span class="badge {priority}">{_esc(priority)}</span>
        <span class="badge">{_esc(_human_issue_type(str(issue.get('type', 'unknown'))))}</span>
      </div>
      <div>
        <p>{_esc(str(issue.get('summary', '')))}</p>
        <p class="meta">{_esc(str(issue.get('proposed_next_step', '')))}</p>
      </div>
      {action}
    </article>"""


def _note_row(note: dict[str, object], summary: dict[str, object]) -> str:
    location_label = _label_for_location(summary, str(note.get("segment_id")))
    created_at = str(note.get("created_at", ""))
    time_label = created_at[11:16] if len(created_at) >= 16 else "latest"
    return f"""
    <article class="note-row">
      <div class="meta">[{_esc(time_label)}] {_esc(location_label)} · {_esc(str(note.get('severity')))}</div>
      <p>{_esc(str(note.get('text', '')))}</p>
    </article>"""


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


def _route_health(locations: list[dict[str, object]]) -> int:
    if not locations:
        return 0
    total = sum(STATUS_SCORES.get(str(location.get("status", "unknown")), 0.25) for location in locations)
    return round((total / len(locations)) * 100)


def _route_role(location: dict[str, object]) -> str:
    location_type = str(location.get("type", "segment")).replace("_", " ")
    if location.get("open_issues"):
        return f"{location_type} blocker"
    if str(location.get("status")) == "works":
        return f"{location_type} solved"
    return location_type


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
    rendered = "".join(
        f'<a href="{_esc(path.resolve().as_uri())}">{_esc(label)}</a>' for label, path in links
    )
    return f'<div class="artifact-links">{rendered}</div>'


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
