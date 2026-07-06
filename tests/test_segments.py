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
    assert "1. id=fresh_start_to_1_1 status=solved bridged=false" in rendered
    assert "5. id=world_1_fortress_whistle status=bridged bridged=true" in rendered
    assert "6. id=world_1_4_clear status=flaky bridged=false" in rendered

