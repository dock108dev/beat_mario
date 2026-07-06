from pathlib import Path

import yaml

from smb3_agent.goals import load_goal_contract
from smb3_agent.recovery import simulate_recovery


def test_simulate_life_lost_continues_when_policy_allows() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))

    decision = simulate_recovery(contract, "life_lost")

    assert decision.decision == "continue_next_life"
    assert decision.action == "reclassify_state"
    assert "allows continuing" in decision.reason


def test_simulate_wrong_map_node_corrects_when_bridge_allowed() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))

    decision = simulate_recovery(contract, "wrong_map_node")

    assert decision.decision == "correct_known_state"
    assert "permits bridge" in decision.reason


def test_simulate_wrong_map_node_stops_when_bridge_disallowed(tmp_path: Path) -> None:
    raw = yaml.safe_load(Path("data/goals/world_1_king.yaml").read_text())
    raw["constraints"]["allow_bridge_steps"] = False
    path = tmp_path / "goal.yaml"
    path.write_text(yaml.safe_dump(raw))
    contract = load_goal_contract(path)

    decision = simulate_recovery(contract, "wrong_map_node")

    assert decision.decision == "stop"
    assert "not allowed" in decision.reason

