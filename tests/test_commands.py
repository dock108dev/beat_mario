from pathlib import Path

import pytest

from smb3_agent.commands import CommandParseError, parse_command, run_command
from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult


def test_parse_world_1_king_gate_command() -> None:
    command = parse_command("run world 1 king gate 3 times")

    assert command.action == "run_goal"
    assert command.goal == "world_1_king"
    assert command.attempts == 3
    assert command.run_mode == "gate"
    assert command.validation_policy == "require_goal_metrics"
    assert "goal=world_1_king" in command.to_text()


def test_parse_world_1_king_gate_defaults_to_one_attempt() -> None:
    command = parse_command("run world 1 king gate")

    assert command.attempts == 1


def test_parse_show_route_command() -> None:
    command = parse_command("show me the route at 4x")

    assert command.action == "show_route"
    assert command.goal == "world_1_king"
    assert command.speed == 4
    assert command.validation_policy == "review_only"


def test_parse_review_latest_failed_command() -> None:
    command = parse_command("review the latest failed run")

    assert command.action == "review_latest_failed"
    assert command.run_mode == "review"


def test_parse_continue_after_life_loss_command() -> None:
    command = parse_command("continue after losing a life if the route allows it")

    assert command.action == "set_recovery_policy"
    assert command.recovery_policy == "continue_after_life_loss_if_allowed"


def test_parse_unsupported_command() -> None:
    with pytest.raises(CommandParseError, match="Unsupported command"):
        parse_command("please improvise a route")


def test_command_module_imports_path_for_future_trace_type() -> None:
    assert Path("artifacts/commands").parts[-1] == "commands"


def test_run_command_writes_trace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run_goal_contract(contract, *, game_path, attempts, artifacts_dir, capture_images=False, capture_ticks=False):
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

    monkeypatch.setattr("smb3_agent.commands.run_goal_contract", fake_run_goal_contract)
    game_file = tmp_path / "local-game-file"
    game_file.write_text("placeholder")

    result = run_command(
        "run world 1 king gate",
        game_path=game_file,
        artifacts_dir=tmp_path / "command",
    )

    assert result.trace_path.is_file()
    assert result.goal_result.metrics_passed is True
    assert "trace_path=" in result.to_text()
