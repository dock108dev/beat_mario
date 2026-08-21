from __future__ import annotations

import http.client
import logging
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult, load_goal_contract
from smb3_agent.lab import add_batch_notes_to_latest, build_issue_ledger_latest, start_session
from smb3_agent.lab_ui import (
    _Handler,
    _location_url,
    _new_lab_ui_server,
    _selected_location,
    _update_issue_latest,
    _update_observation_latest,
    build_control_panel_summary,
    render_lab_ui,
    run_lab_ui_server,
)


def test_route_lab_refuses_non_loopback_bind() -> None:
    with pytest.raises(ValueError, match="may bind only"):
        run_lab_ui_server(host="0.0.0.0", port=0)


def test_route_lab_rejects_malformed_form_and_logs_client_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with caplog.at_level(logging.WARNING, logger="smb3_agent.lab_ui"):
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_port, timeout=5
            )
            connection.putrequest("POST", "/notes")
            connection.putheader("Content-Length", "invalid")
            connection.endheaders()
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 400
    assert "Invalid Content-Length header" in body
    assert "route_lab_request_failed" in caplog.text
    assert "error_type=LabUiError" in caplog.text


def test_route_lab_returns_generic_500_and_logs_unexpected_traceback(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def crash(_handler: _Handler) -> None:
        raise RuntimeError("private unexpected detail")

    monkeypatch.setattr(_Handler, "_handle_get", crash)
    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with caplog.at_level(logging.ERROR, logger="smb3_agent.lab_ui"):
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_port, timeout=5
            )
            connection.request("GET", "/")
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 500
    assert "Unexpected Route Lab failure" in body
    assert "private unexpected detail" not in body
    assert "RuntimeError: private unexpected detail" in caplog.text


def test_route_lab_rejects_untrusted_host_and_missing_csrf() -> None:
    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.putrequest("GET", "/api/summary", skip_host=True)
        connection.putheader("Host", "attacker.example")
        connection.endheaders()
        host_response = connection.getresponse()
        host_response.read()
        connection.close()

        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request(
            "POST",
            "/refresh",
            body="",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        csrf_response = connection.getresponse()
        csrf_body = csrf_response.read().decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert host_response.status == 403
    assert csrf_response.status == 403
    assert "Invalid or missing Route Lab CSRF token" in csrf_body


def test_route_lab_sets_security_headers_and_renders_csrf_token() -> None:
    csrf_token = "fixed-test-csrf-token"
    html = render_lab_ui(csrf_token=csrf_token)

    post_forms = html.count('<form method="post"')
    assert post_forms >= 1
    assert html.count(f'name="csrf_token" value="{csrf_token}"') == post_forms

    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request("GET", "/api/summary")
        response = connection.getresponse()
        response.read()
        headers = dict(response.getheaders())
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 200
    assert headers["Content-Security-Policy"].startswith("default-src 'none'")
    assert headers["Cache-Control"] == "no-store"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"


def test_route_lab_rejects_wrong_content_type() -> None:
    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request(
            "POST",
            "/refresh",
            body='{"csrf_token":"unused"}',
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 415
    assert "application/x-www-form-urlencoded" in body


def test_route_lab_rejects_overlapping_state_change() -> None:
    server = _new_lab_ui_server("127.0.0.1", 0)
    action_lock = getattr(server, "action_lock")
    action_lock.acquire()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request(
            "POST",
            "/refresh",
            body=f"csrf_token={getattr(server, 'csrf_token')}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        connection.close()
    finally:
        action_lock.release()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 409
    assert "Another Route Lab action is already running" in body


def test_route_lab_serves_html_as_text_and_blocks_unsafe_artifact_type(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    artifacts.joinpath("report.html").write_text("<script>alert(1)</script>")
    artifacts.joinpath("unsafe.svg").write_text("<svg></svg>")
    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request("GET", "/artifacts/report.html")
        html_response = connection.getresponse()
        html_response.read()
        html_content_type = html_response.getheader("Content-Type")
        connection.close()

        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request("GET", "/artifacts/unsafe.svg")
        svg_response = connection.getresponse()
        svg_response.read()
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert html_response.status == 200
    assert html_content_type == "text/plain; charset=utf-8"
    assert svg_response.status == 404


def test_route_lab_rejects_oversized_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("smb3_agent.lab_ui.MAX_SERVED_FILE_BYTES", 4)
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    artifacts.joinpath("large.log").write_text("12345")
    server = _new_lab_ui_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=5
        )
        connection.request("GET", "/artifacts/large.log")
        response = connection.getresponse()
        response.read()
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 413


def test_location_url_percent_encodes_untrusted_parameters() -> None:
    location = _location_url("route\r\nInjected: value", issue_id="issue/one")

    assert "\r" not in location
    assert "\n" not in location
    assert "%0D%0A" in location
    assert "issue%2Fone" in location


def test_route_lab_renders_route_evidence_and_teaching_workflow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [{"segment_id": "world_1_1", "text": "1-1 falls into hole.", "severity": "harden"}]
    )
    build_issue_ledger_latest()

    html = render_lab_ui()

    assert "Mario Route Lab" in html
    assert "Run World 8 Route" in html
    assert "World 2-first double-whistle route to World 8" in html
    assert "Route" in html
    assert "Evidence" in html
    assert "Teach Mario" in html
    assert "Active Problems" in html
    assert "Observation History" in html
    assert "Fix Issue" in html
    assert "No screenshot captured yet" in html
    assert "Mark Resolved" in html
    assert "Needs Rerun" in html
    assert "Create Codex Task" in html
    assert "1-1" in html
    assert "1-3" in html
    assert "Fortress" in html
    assert "Airship / King" in html
    assert "King" in html
    assert "World 2 Map" in html
    assert "World 8 Map" in html
    assert "1-4" not in html
    assert "Unit Tests" in html
    assert "Phase Gate" in html
    assert 'href="/?location=world_1_fortress"' in html
    assert html.count('class="primary-button"') == 1
    assert "secondary-button" in html
    assert "segmented-control" in html
    assert "segment-active" in html
    assert "route-item-selected" in html
    assert "status-failed" in html
    assert "status-learned" in html
    assert "status-validation" in html
    assert html.count("Mark Resolved") == 1
    assert html.count("Needs Rerun") == 1
    assert html.count("Create Codex Task") == 1
    assert "issue-summary-row" in html
    assert "observation-summary-row" in html
    assert "World 1 Control Panel" not in html
    assert "World 1 Mission Control" not in html
    assert "Run Controls" not in html
    assert "World 1 Notes" not in html
    assert "Route Health" not in html
    assert "Teach This Section" not in html
    assert "Things Mario Still Gets Wrong" not in html
    assert "World 1-3 Whistle" not in html
    assert "World 1 Fortress Whistle" not in html

    notes_html = render_lab_ui(selected_location_id="world_1_1", selected_mode="notes")
    assert "Convert to Issue" in notes_html
    assert notes_html.count("Convert to Issue") == 1
    assert "detail-panel observation-detail" in notes_html

    add_html = render_lab_ui(selected_location_id="world_1_1", selected_mode="add")
    assert 'name="note__world_1_1"' in add_html
    assert add_html.count('name="note__') == 1
    assert "Add Observation" in add_html


def test_control_panel_groups_notes_by_human_location(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [
            {
                "segment_id": "world_1_1",
                "text": "1-1 falls into hole at 283 on clock.",
                "severity": "harden",
            },
            {
                "segment_id": "world_1_fortress",
                "text": "Fortress needs Raccoon flight, not fire form.",
                "severity": "guide_detail",
            },
        ]
    )
    build_issue_ledger_latest()

    summary = build_control_panel_summary()
    locations = {location["id"]: location for location in summary["locations"]}

    assert locations["world_1_1"]["notes"] == 1
    assert locations["world_1_1"]["open_issues"] == 1
    assert locations["world_1_fortress"]["notes"] == 1
    assert locations["world_1_fortress"]["issues"] == 0
    assert locations["world_1_fortress"]["open_issues"] == 0
    assert summary["totals"]["notes"] == 2


def test_route_lab_defaults_to_first_open_issue_location(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [{"segment_id": "world_1_1", "text": "1-1 falls into hole.", "severity": "harden"}]
    )
    build_issue_ledger_latest()

    summary = build_control_panel_summary()
    selected = _selected_location(summary["locations"])

    assert selected["id"] == "world_1_1"


def test_route_lab_uses_active_goal_contract_order() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))

    summary = build_control_panel_summary()
    displayed_segments = tuple(str(location["segment_id"]) for location in summary["locations"])
    labels = tuple(str(location["label"]) for location in summary["locations"])

    assert summary["goal_id"] == "world_8_double_whistle"
    assert displayed_segments == contract.segments
    assert "1-4" not in labels
    assert "World 2 Map" in labels
    assert "World 8 Map" in labels


def test_route_lab_surfaces_big_tanks_without_changing_the_default_goal() -> None:
    default = build_control_panel_summary()
    big_tanks = build_control_panel_summary("world_8_big_tanks")
    html = render_lab_ui(goal_id="world_8_big_tanks")

    assert default["goal_id"] == "world_8_double_whistle"
    assert len(default["locations"]) == 15
    assert big_tanks["goal_id"] == "world_8_big_tanks"
    assert len(big_tanks["locations"]) == 16
    assert big_tanks["locations"][-1]["label"] == "World 8 Big Tanks"
    assert "World 8 Big Tanks" in html
    assert 'href="/?goal=world_8_big_tanks&amp;location=world_8_big_tanks"' in html
    assert "World 2-first double-whistle route through World 8 Big Tanks" in html


def test_route_lab_renders_and_switches_to_battleships() -> None:
    default = build_control_panel_summary()
    big_tanks = build_control_panel_summary("world_8_big_tanks")
    battleships = build_control_panel_summary("world_8_battleships")
    html = render_lab_ui(goal_id="world_8_battleships")

    assert len(default["locations"]) == 15
    assert len(big_tanks["locations"]) == 16
    assert battleships["goal_id"] == "world_8_battleships"
    assert len(battleships["locations"]) == 17
    assert battleships["locations"][-1]["label"] == "World 8-Battleships"
    assert 'href="/?goal=world_8_battleships&amp;location=world_8_battleships"' in html
    assert "World 2-first double-whistle route through World 8-Battleships" in html


def test_route_lab_renders_exactly_21_hand_traps_jet_locations() -> None:
    summary = build_control_panel_summary("world_8_hand_traps_jet")
    html = render_lab_ui(goal_id="world_8_hand_traps_jet")

    assert summary["goal_id"] == "world_8_hand_traps_jet"
    assert len(summary["locations"]) == 21
    assert [location["id"] for location in summary["locations"][-4:]] == [
        "world_8_hand_trap_right",
        "world_8_hand_trap_center",
        "world_8_hand_trap_left",
        "world_8_jet",
    ]
    assert "World 8 Right Hand Trap" in html
    assert "World 8 Center Hand Trap" in html
    assert "World 8 Left Hand Trap" in html
    assert "World 8-Jet" in html
    assert 'href="/?goal=world_8_hand_traps_jet&amp;location=world_8_jet"' in html


def test_route_lab_renders_and_switches_to_exactly_23_world_8_8_2_locations() -> None:
    summary = build_control_panel_summary("world_8_8_2")
    html = render_lab_ui(goal_id="world_8_8_2")

    assert summary["goal_id"] == "world_8_8_2"
    assert len(summary["locations"]) == 23
    assert [location["id"] for location in summary["locations"][-2:]] == [
        "world_8_1",
        "world_8_2",
    ]
    assert "World 8-1" in html
    assert "World 8-2" in html
    assert "World 2-first double-whistle route through World 8-2 and Fortress access" in html
    assert 'href="/?goal=world_8_8_2&amp;location=world_8_2"' in html


def test_route_lab_renders_exactly_25_world_8_super_tanks_locations() -> None:
    summary = build_control_panel_summary("world_8_super_tanks")
    html = render_lab_ui(goal_id="world_8_super_tanks")

    assert summary["goal_id"] == "world_8_super_tanks"
    assert len(summary["locations"]) == 25
    assert [location["id"] for location in summary["locations"][-2:]] == [
        "world_8_fortress",
        "world_8_super_tanks",
    ]
    assert "World 8-Fortress" in html
    assert "World 8-Super Tanks" in html
    assert "through Super Tanks and Bowser&#x27;s Castle access" in html
    assert (
        'href="/?goal=world_8_super_tanks&amp;location=world_8_super_tanks"'
        in html
    )


def test_route_lab_renders_exactly_26_finish_game_locations() -> None:
    summary = build_control_panel_summary("world_8_finish_game")
    html = render_lab_ui(goal_id="world_8_finish_game")

    assert summary["goal_id"] == "world_8_finish_game"
    assert len(summary["locations"]) == 26
    assert summary["locations"][-1]["id"] == "world_8_bowser_castle"
    assert "World 8-Bowser&#x27;s Castle and Ending" in html
    assert "Princess rescue, credits, and ending" in html
    assert (
        'href="/?goal=world_8_finish_game&amp;location=world_8_bowser_castle"'
        in html
    )


def test_observation_lifecycle_delete_and_resolve(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [
            {"segment_id": "world_1_1", "text": "delete me", "severity": "harden"},
            {"segment_id": "world_1_fortress", "text": "resolve me", "severity": "harden"},
        ]
    )
    build_issue_ledger_latest()

    _update_observation_latest("note_001", "delete", {})
    _update_observation_latest("note_002", "resolved", {})

    notes = yaml.safe_load(_latest_session_file("notes.yaml").read_text())["notes"]
    issues = yaml.safe_load(_latest_session_file("issues.yaml").read_text())["issues"]

    assert [note["id"] for note in notes] == ["note_002"]
    assert notes[0]["ui_state"] == "resolved"
    assert all("note_001" not in issue.get("source_notes", []) for issue in issues)
    assert any(issue["status"] == "resolved" for issue in issues)


def test_issue_lifecycle_resolved_and_expected_behavior(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [
            {"segment_id": "world_1_1", "text": "1-1 falls into hole.", "severity": "harden"},
            {"segment_id": "world_1_fortress", "text": "Fortress fails.", "severity": "bug"},
        ]
    )
    build_issue_ledger_latest()

    issues = yaml.safe_load(_latest_session_file("issues.yaml").read_text())["issues"]
    first_issue_id = issues[0]["id"]
    second_issue_id = issues[1]["id"]

    _update_issue_latest(first_issue_id, "resolved")
    _update_issue_latest(second_issue_id, "expected_behavior")

    updated = {issue["id"]: issue for issue in yaml.safe_load(_latest_session_file("issues.yaml").read_text())["issues"]}
    assert updated[first_issue_id]["status"] == "resolved"
    assert updated[first_issue_id]["actionable"] is False
    assert updated[second_issue_id]["status"] == "accepted"
    assert updated[second_issue_id]["type"] == "expected_behavior"
    assert updated[second_issue_id]["actionable"] is False


def _prepare_ui_lab(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("data/worlds").mkdir(parents=True)
    tmp_path.joinpath("data/segments").mkdir(parents=True)
    tmp_path.joinpath("artifacts/sessions").mkdir(parents=True)
    tmp_path.joinpath("local-game-file").write_text("placeholder")
    tmp_path.joinpath("data/worlds/world_1_locations.yaml").write_text(
        yaml.safe_dump(
            {
                "world": 1,
                "name": "Grass Land",
                "locations": [
                    {
                        "id": "world_1_1",
                        "segment_id": "world_1_1_clear",
                        "label": "1-1",
                        "default_status": "works",
                        "objective": "Clear the level.",
                    },
                    {
                        "id": "world_1_3",
                        "segment_id": "world_1_3_whistle",
                        "label": "1-3",
                        "default_status": "works",
                        "objective": "Get the hidden item route.",
                    },
                    {
                        "id": "world_1_fortress",
                        "segment_id": "world_1_fortress_whistle",
                        "label": "Fortress",
                        "default_status": "blocked",
                        "objective": "Use flight above the ceiling.",
                    },
                    {
                        "id": "world_1_airship",
                        "segment_id": "world_1_airship_to_king",
                        "label": "Airship / King",
                        "default_status": "needs review",
                        "objective": "Complete the moving stage.",
                    },
                    {
                        "id": "world_2_map",
                        "segment_id": "world_2_map_arrival_with_two_whistles",
                        "label": "World 2 Map",
                        "default_status": "blocked",
                        "objective": "Arrive with both whistles.",
                    },
                    {
                        "id": "world_8_map",
                        "segment_id": "world_8_map_arrival",
                        "label": "World 8 Map",
                        "default_status": "blocked",
                        "objective": "Confirm genuine World 8 arrival.",
                    },
                ],
            }
        )
    )
    tmp_path.joinpath("data/segments/world_1.yaml").write_text(
        yaml.safe_dump(
            {
                "catalog_id": "world_1",
                "segments": [
                    {"id": "world_1_1_clear", "name": "World 1-1", "status": "solved"},
                    {"id": "world_1_3_whistle", "name": "World 1-3 Whistle", "status": "solved"},
                    {
                        "id": "world_1_fortress_whistle",
                        "name": "World 1 Fortress Whistle",
                        "status": "bridged",
                    },
                ],
            }
        )
    )
    monkeypatch.setattr(
        "smb3_agent.lab.load_goal_contract",
        lambda path: SimpleNamespace(
            id="world_8_double_whistle",
            catalog_path=Path("data/segments/world_1.yaml"),
        ),
    )
    monkeypatch.setattr("smb3_agent.lab.resolve_goal_path", lambda goal: Path(f"data/goals/{goal}.yaml"))
    monkeypatch.setattr("smb3_agent.lab.run_goal_contract", _fake_run_goal_contract)
    route_steps = (
        SimpleNamespace(id="world_1_1_clear", classification="game_prerequisite", execution_mode="normal_gameplay"),
        SimpleNamespace(id="world_1_3_whistle", classification="objective_milestone", execution_mode="normal_gameplay"),
        SimpleNamespace(id="world_1_fortress_whistle", classification="objective_milestone", execution_mode="normal_gameplay"),
        SimpleNamespace(id="world_1_airship_to_king", classification="game_prerequisite", execution_mode="planned"),
        SimpleNamespace(id="world_2_map_arrival_with_two_whistles", classification="objective_milestone", execution_mode="planned"),
        SimpleNamespace(id="world_8_map_arrival", classification="objective_milestone", execution_mode="planned"),
    )
    fake_contract = SimpleNamespace(
        id="world_8_double_whistle",
        display_name="World 8 Arrival",
        display_subtitle="World 2-first double-whistle route to World 8",
        catalog_path=Path("data/segments/world_8_double_whistle.yaml"),
        segments=tuple(step.id for step in route_steps),
        route_steps=route_steps,
        goal_type="product_goal",
        execution_status="planned",
        objective={"target": "world_8_map_arrival"},
    )
    fake_catalog = SimpleNamespace(
        by_id={
            "world_1_1_clear": SimpleNamespace(status="solved"),
            "world_1_3_whistle": SimpleNamespace(status="solved"),
            "world_1_fortress_whistle": SimpleNamespace(status="bridged"),
            "world_1_airship_to_king": SimpleNamespace(status="bridged"),
            "world_2_map_arrival_with_two_whistles": SimpleNamespace(status="planned"),
            "world_8_map_arrival": SimpleNamespace(status="planned"),
        }
    )
    monkeypatch.setattr("smb3_agent.lab_ui.load_goal_contract", lambda path: fake_contract)
    monkeypatch.setattr(
        "smb3_agent.lab_ui.load_product_goal_contracts",
        lambda: (fake_contract,),
    )
    monkeypatch.setattr("smb3_agent.lab_ui.resolve_goal_path", lambda goal: Path(f"data/goals/{goal}.yaml"))
    monkeypatch.setattr("smb3_agent.lab_ui.load_segment_catalog", lambda path: fake_catalog)


def _latest_session_file(name: str) -> Path:
    session_dir = Path("artifacts/sessions/latest.txt").read_text().strip()
    return Path(session_dir) / name


def _fake_run_goal_contract(
    contract,
    *,
    game_path,
    attempts,
    artifacts_dir,
    capture_images=False,
    capture_ticks=False,
    env_overrides=(),
):
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.joinpath("fceux_1_1.log").write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_start x=24 y=384",
                "frame=50 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=80 event=post_probe_1_airship_success_king x=432 y=4192",
            ]
        )
    )
    return GoalRunResult(
        contract=contract,
        summary=BatchSummary(
            attempts=(
                AttemptSummary(
                    attempt=1,
                    success=True,
                    bad_state=False,
                    reached_end=True,
                    goal_area=True,
                    max_x=2848,
                ),
            ),
            post_probe_last_event="post_probe_1_airship_success_king",
            post_probe_clear=True,
        ),
        artifacts_dir=artifacts_dir,
        metrics_passed=True,
    )
