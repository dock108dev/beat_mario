from pathlib import Path

import pytest
import yaml

from smb3_agent.goals import load_goal_contract
from smb3_agent.segments import (
    SegmentValidationError,
    load_segment_catalog,
    render_goal_status,
    validate_goal_segments,
)


def test_load_world_1_segment_catalog() -> None:
    catalog = load_segment_catalog(Path("data/segments/world_1.yaml"))

    assert catalog.catalog_id == "world_1"
    assert len(catalog.segments) == 9
    assert catalog.by_id["world_1_4_clear"].status == "flaky"
    assert catalog.by_id["world_1_airship_to_king"].status == "bridged"


def test_world_1_goal_segments_are_all_cataloged() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))
    catalog = load_segment_catalog(Path("data/segments/world_1.yaml"))

    validate_goal_segments(contract, catalog)


def test_active_world_8_goal_segments_are_all_cataloged_and_solved_truthfully() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    catalog = load_segment_catalog(Path("data/segments/world_8_double_whistle.yaml"))

    validate_goal_segments(contract, catalog)
    assert catalog.by_id["world_2_map_arrival_with_two_whistles"].status == "solved"
    assert catalog.by_id["world_2_first_whistle_use"].status == "solved"
    assert catalog.by_id["world_8_map_arrival"].status == "solved"


def test_segment_catalog_rejects_unsupported_status(tmp_path: Path) -> None:
    raw = yaml.safe_load(Path("data/segments/world_1.yaml").read_text())
    raw["segments"][0]["status"] = "maybe"
    path = tmp_path / "bad_status.yaml"
    path.write_text(yaml.safe_dump(raw))

    with pytest.raises(SegmentValidationError, match="Unsupported status"):
        load_segment_catalog(path)


def test_segment_catalog_rejects_duplicate_ids(tmp_path: Path) -> None:
    raw = yaml.safe_load(Path("data/segments/world_1.yaml").read_text())
    raw["segments"][1]["id"] = raw["segments"][0]["id"]
    path = tmp_path / "duplicate.yaml"
    path.write_text(yaml.safe_dump(raw))

    with pytest.raises(SegmentValidationError, match="Duplicate segment id"):
        load_segment_catalog(path)


def test_render_goal_status_lists_route_order_and_bridge_flags() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))
    catalog = load_segment_catalog(Path("data/segments/world_1.yaml"))

    rendered = render_goal_status(contract, catalog)

    assert "goal_id=world_1_king" in rendered
    assert "goal_type=diagnostic_route" in rendered
    assert "1. id=fresh_start_to_1_1 classification=diagnostic_route" in rendered
    assert "status=solved bridged=false" in rendered
    assert "5. id=world_1_fortress_whistle classification=diagnostic_route" in rendered
    assert "6. id=world_1_4_clear classification=diagnostic_route" in rendered


def test_active_goal_status_renders_contract_order_and_roles() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    catalog = load_segment_catalog(Path("data/segments/world_8_double_whistle.yaml"))

    rendered = render_goal_status(contract, catalog)

    assert "goal_id=world_8_double_whistle" in rendered
    assert "execution_status=executable" in rendered
    assert "4. id=world_1_3_whistle classification=objective_milestone" in rendered
    assert "6. id=world_1_5_water_path classification=game_prerequisite" in rendered
    assert "world_1_4_clear" not in rendered
    assert "15. id=world_8_map_arrival classification=objective_milestone" in rendered


def test_world_8_big_tanks_catalog_adds_exactly_one_solved_segment() -> None:
    prefix = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    extension = load_goal_contract(Path("data/goals/world_8_big_tanks.yaml"))
    catalog = load_segment_catalog(extension.catalog_path)

    validate_goal_segments(extension, catalog)
    assert len(extension.segments) == len(prefix.segments) + 1
    assert catalog.by_id["world_8_big_tanks_clear"].status == "solved"


def test_world_8_battleships_catalog_adds_exactly_one_more_solved_segment() -> None:
    big_tanks = load_goal_contract(Path("data/goals/world_8_big_tanks.yaml"))
    battleships = load_goal_contract(Path("data/goals/world_8_battleships.yaml"))
    catalog = load_segment_catalog(battleships.catalog_path)

    validate_goal_segments(battleships, catalog)
    assert len(big_tanks.segments) == 16
    assert len(battleships.segments) == 17
    assert catalog.by_id["world_8_battleships_clear"].status == "solved"
    assert catalog.by_id["world_8_battleships_clear"].acceptance_event == (
        "post_probe_world_8_battleships_post_clear"
    )
    success_events = {
        condition.get("value")
        for condition in catalog.by_id[
            "world_8_battleships_clear"
        ].success_condition["conditions"]
        if condition.get("type") == "post_probe_event"
    }
    assert success_events == {
        "post_probe_world_8_battleships_entered",
        "post_probe_world_8_battleships_gameplay",
        "post_probe_world_8_battleships_clear",
        "post_probe_world_8_battleships_post_clear",
    }
