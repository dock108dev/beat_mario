from __future__ import annotations

import argparse
import os
from pathlib import Path

from smb3_agent.detection.state_detector import detect_state
from smb3_agent.fceux_harness import parse_fceux_log, run_fceux_1_1
from smb3_agent.fceux_images import convert_gd_directory, write_contact_sheet
from smb3_agent.goals import (
    GoalValidationError,
    load_goal_contract,
    resolve_goal_path,
    run_goal_contract,
)
from smb3_agent.presets import WORLD_1_KING_ENV
from smb3_agent.probes.mednafen_probe import run_mednafen_probe
from smb3_agent.tasks.checkpoint_1_1 import run_checkpoint_1_1_task
from smb3_agent.tasks.enter_1_1 import run_enter_1_1_task
from smb3_agent.tasks.load_checkpoint_1_1 import run_load_checkpoint_1_1_task
from smb3_agent.tasks.run_1_1_script import run_1_1_script_task
from smb3_agent.tasks.start_game import run_start_game_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="smb3_agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe", help="Run backend readiness probes")
    probe_subparsers = probe.add_subparsers(dest="backend", required=True)

    mednafen = probe_subparsers.add_parser("mednafen", help="Probe local Mednafen control/capture")
    mednafen.add_argument("--game-file", required=True, help="Path to the local game file")
    mednafen.add_argument(
        "--artifacts-dir",
        default="artifacts/probes",
        help="Directory for screenshots and probe metadata",
    )
    mednafen.add_argument("--startup-seconds", type=float, default=3.0)
    mednafen.add_argument("--after-start-seconds", type=float, default=3.0)

    detect = subparsers.add_parser("detect", help="Classify a captured game screenshot")
    detect.add_argument("--image", required=True, help="Path to a game screenshot")
    detect.add_argument(
        "--fixtures-dir",
        default="data/fixtures/state",
        help="Directory containing state fixture screenshots",
    )

    task = subparsers.add_parser("task", help="Run scripted game tasks")
    task_subparsers = task.add_subparsers(dest="task_name", required=True)

    start_game = task_subparsers.add_parser("start-game", help="Start a fresh game and capture evidence")
    start_game.add_argument("--game-file", required=True, help="Path to the local game file")
    start_game.add_argument(
        "--artifacts-dir",
        default="artifacts/tasks/start-game",
        help="Directory for screenshots and task metadata",
    )
    start_game.add_argument(
        "--fixtures-dir",
        default="data/fixtures/state",
        help="Directory for stable detector fixture screenshots",
    )
    start_game.add_argument("--startup-seconds", type=float, default=3.0)

    enter_1_1 = task_subparsers.add_parser("enter-1-1", help="Start a fresh game and enter World 1-1")
    enter_1_1.add_argument("--game-file", required=True, help="Path to the local game file")
    enter_1_1.add_argument(
        "--artifacts-dir",
        default="artifacts/tasks/enter-1-1",
        help="Directory for screenshots and task metadata",
    )
    enter_1_1.add_argument(
        "--fixtures-dir",
        default="data/fixtures/state",
        help="Directory for stable detector fixture screenshots",
    )
    enter_1_1.add_argument("--startup-seconds", type=float, default=3.0)

    checkpoint_1_1 = task_subparsers.add_parser(
        "checkpoint-1-1",
        help="Start a fresh game, enter World 1-1, and save Mednafen state slot 1",
    )
    checkpoint_1_1.add_argument("--game-file", required=True, help="Path to the local game file")
    checkpoint_1_1.add_argument(
        "--artifacts-dir",
        default="artifacts/tasks/checkpoint-1-1",
        help="Directory for screenshots and task metadata",
    )
    checkpoint_1_1.add_argument(
        "--fixtures-dir",
        default="data/fixtures/state",
        help="Directory for stable detector fixture screenshots",
    )
    checkpoint_1_1.add_argument("--startup-seconds", type=float, default=3.0)
    checkpoint_1_1.add_argument("--slot", type=int, default=0)

    load_checkpoint_1_1 = task_subparsers.add_parser(
        "load-checkpoint-1-1",
        help="Load saved Mednafen state slot 0 and verify World 1-1",
    )
    load_checkpoint_1_1.add_argument("--game-file", required=True, help="Path to the local game file")
    load_checkpoint_1_1.add_argument(
        "--artifacts-dir",
        default="artifacts/tasks/load-checkpoint-1-1",
        help="Directory for screenshots and task metadata",
    )
    load_checkpoint_1_1.add_argument(
        "--fixtures-dir",
        default="data/fixtures/state",
        help="Directory containing state fixture screenshots",
    )
    load_checkpoint_1_1.add_argument("--startup-seconds", type=float, default=3.0)
    load_checkpoint_1_1.add_argument("--slot", type=int, default=0)

    run_1_1_script = task_subparsers.add_parser(
        "run-1-1-script",
        help="Load the 1-1 checkpoint and execute a YAML input script",
    )
    run_1_1_script.add_argument("--game-file", required=True, help="Path to the local game file")
    run_1_1_script.add_argument(
        "--script",
        default="data/routes/scripts/world_1_1_draft.yaml",
        help="YAML input script to execute from the 1-1 checkpoint",
    )
    run_1_1_script.add_argument(
        "--artifacts-dir",
        default="artifacts/tasks/run-1-1-script",
        help="Directory for screenshots, input trace, and task metadata",
    )
    run_1_1_script.add_argument(
        "--fixtures-dir",
        default="data/fixtures/state",
        help="Directory containing state fixture screenshots",
    )
    run_1_1_script.add_argument("--startup-seconds", type=float, default=3.0)
    run_1_1_script.add_argument("--slot", type=int, default=0)
    run_1_1_script.add_argument(
        "--save-final-slot",
        type=int,
        default=None,
        help="Save the emulator state to this slot after the script and final capture",
    )
    run_1_1_script.add_argument(
        "--sample-interval-seconds",
        type=float,
        default=0.1,
        help="Seconds between captured evidence frames while the input script runs; use 0 to disable sampling",
    )

    fceux_1_1 = task_subparsers.add_parser(
        "fceux-1-1",
        help="Run the memory-aware FCEUX World 1-1 route",
    )
    fceux_1_1.add_argument("--game-file", required=True, help="Path to the local game file")
    fceux_1_1.add_argument(
        "--script",
        default="scripts/fceux_1_1_agent.lua",
        help="Lua route script to load in FCEUX",
    )
    fceux_1_1.add_argument(
        "--artifacts-dir",
        default="artifacts/fceux/cli_1_1",
        help="Directory for route logs and optional screenshots",
    )
    fceux_1_1.add_argument("--attempts", type=int, default=10)
    fceux_1_1.add_argument("--capture-images", action="store_true")
    fceux_1_1.add_argument("--capture-ticks", action="store_true")
    fceux_1_1.add_argument("--after-attempt-frames", type=int, default=None)
    fceux_1_1.add_argument(
        "--post-1-1-probe",
        choices=[
            "enter_1_2",
            "enter_1_3",
            "run_1_2_naive",
            "run_1_3_whistle",
            "run_1_3_whistle_to_castle",
            "run_1_fortress_whistle",
            "run_1_fortress_map_sequence",
            "run_1_4_after_fortress",
            "run_1_4_map_sequence",
            "run_1_5_after_1_4",
            "run_1_5_map_sequence",
            "run_1_5_water_after_roamer",
            "run_1_5_water_map_sequence",
            "run_1_6_after_water",
            "run_1_castle_after_1_6",
            "run_1_castle_map_bridge_only",
            "run_1_5_water_bridge_only",
            "run_1_6_after_water_bridge",
            "run_1_castle_after_water_bridge_1_6",
            "run_1_fortress_second_lava_search",
            "run_1_fortress_mid_search",
            "run_1_fortress_flight_search",
        ],
        default=None,
        help="Optional probe to run after the final successful 1-1 clear",
    )
    fceux_1_1.add_argument(
        "--set-env",
        action="append",
        default=[],
        help="Set an environment override for the Lua route, formatted KEY=VALUE",
    )
    fceux_1_1.add_argument(
        "--require-perfect",
        action="store_true",
        help="Exit non-zero unless every attempt clears the level",
    )
    fceux_1_1.add_argument(
        "--require-post-probe-clear",
        action="store_true",
        help="Exit non-zero unless the optional post-1-1 probe reports a course clear",
    )

    fceux_world_1_king = task_subparsers.add_parser(
        "fceux-world-1-king",
        help="Run the verified FCEUX World 1 route through the king transition",
    )
    fceux_world_1_king.add_argument("--game-file", required=True, help="Path to the local game file")
    fceux_world_1_king.add_argument(
        "--script",
        default="scripts/fceux_1_1_agent.lua",
        help="Lua route script to load in FCEUX",
    )
    fceux_world_1_king.add_argument(
        "--artifacts-dir",
        default="artifacts/fceux/world_1_king",
        help="Directory for route logs and optional screenshots",
    )
    fceux_world_1_king.add_argument("--attempts", type=int, default=10)
    fceux_world_1_king.add_argument("--capture-images", action="store_true")
    fceux_world_1_king.add_argument("--capture-ticks", action="store_true")
    fceux_world_1_king.add_argument(
        "--set-env",
        action="append",
        default=[],
        help="Set an environment override for the Lua route, formatted KEY=VALUE",
    )
    fceux_world_1_king.add_argument(
        "--require-perfect",
        action="store_true",
        help="Exit non-zero unless every 1-1 attempt clears",
    )

    review_fceux = task_subparsers.add_parser(
        "review-fceux-log",
        help="Summarize a FCEUX route log",
    )
    review_fceux.add_argument("--log", required=True, help="Path to a FCEUX route log")
    review_fceux.add_argument("--attempts", type=int, default=None)

    fceux_contact_sheet = task_subparsers.add_parser(
        "fceux-contact-sheet",
        help="Convert FCEUX screenshots to PNG and write a contact sheet",
    )
    fceux_contact_sheet.add_argument("--input-dir", required=True, help="Directory containing .gd screenshots")
    fceux_contact_sheet.add_argument(
        "--output-dir",
        default=None,
        help="Directory for converted PNG screenshots; defaults to INPUT_DIR/png",
    )
    fceux_contact_sheet.add_argument(
        "--sheet",
        default=None,
        help="Path for the contact sheet; defaults to OUTPUT_DIR/contact_sheet.png",
    )
    fceux_contact_sheet.add_argument("--columns", type=int, default=4)

    goal = subparsers.add_parser("goal", help="Validate and run goal contracts")
    goal_subparsers = goal.add_subparsers(dest="goal_command", required=True)

    goal_validate = goal_subparsers.add_parser("validate", help="Validate a goal contract file or id")
    goal_validate.add_argument("goal", help="Goal id or path to a goal YAML file")

    goal_run = goal_subparsers.add_parser("run", help="Run a goal contract")
    goal_run.add_argument("goal", help="Goal id or path to a goal YAML file")
    goal_run.add_argument("--game-file", default=None, help="Path to the local game file")
    goal_run.add_argument("--attempts", type=int, default=3)
    goal_run.add_argument(
        "--artifacts-dir",
        default=None,
        help="Directory for this goal attempt; defaults to a timestamped goal artifact directory",
    )
    goal_run.add_argument("--capture-images", action="store_true")
    goal_run.add_argument("--capture-ticks", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "probe" and args.backend == "mednafen":
        run_mednafen_probe(
            game_path=Path(args.game_file),
            artifacts_dir=Path(args.artifacts_dir),
            startup_seconds=args.startup_seconds,
            after_start_seconds=args.after_start_seconds,
        )
        return

    if args.command == "detect":
        detection = detect_state(Path(args.image), Path(args.fixtures_dir))
        print(detection.to_json())
        return

    if args.command == "task" and args.task_name == "start-game":
        run_start_game_task(
            game_path=Path(args.game_file),
            artifacts_dir=Path(args.artifacts_dir),
            fixtures_dir=Path(args.fixtures_dir),
            startup_seconds=args.startup_seconds,
        )
        return

    if args.command == "task" and args.task_name == "enter-1-1":
        run_enter_1_1_task(
            game_path=Path(args.game_file),
            artifacts_dir=Path(args.artifacts_dir),
            fixtures_dir=Path(args.fixtures_dir),
            startup_seconds=args.startup_seconds,
        )
        return

    if args.command == "task" and args.task_name == "checkpoint-1-1":
        run_checkpoint_1_1_task(
            game_path=Path(args.game_file),
            artifacts_dir=Path(args.artifacts_dir),
            fixtures_dir=Path(args.fixtures_dir),
            startup_seconds=args.startup_seconds,
            slot=args.slot,
        )
        return

    if args.command == "task" and args.task_name == "load-checkpoint-1-1":
        run_load_checkpoint_1_1_task(
            game_path=Path(args.game_file),
            artifacts_dir=Path(args.artifacts_dir),
            fixtures_dir=Path(args.fixtures_dir),
            startup_seconds=args.startup_seconds,
            slot=args.slot,
        )
        return

    if args.command == "task" and args.task_name == "run-1-1-script":
        run_1_1_script_task(
            game_path=Path(args.game_file),
            script_path=Path(args.script),
            artifacts_dir=Path(args.artifacts_dir),
            fixtures_dir=Path(args.fixtures_dir),
            startup_seconds=args.startup_seconds,
            slot=args.slot,
            save_final_slot=args.save_final_slot,
            sample_interval_seconds=args.sample_interval_seconds,
        )
        return

    if args.command == "task" and args.task_name == "fceux-1-1":
        summary = run_fceux_1_1(
            game_path=Path(args.game_file),
            script_path=Path(args.script),
            artifacts_dir=Path(args.artifacts_dir),
            attempts=args.attempts,
            capture_images=args.capture_images,
            capture_ticks=args.capture_ticks,
            after_attempt_frames=args.after_attempt_frames,
            post_1_1_probe=args.post_1_1_probe,
            env_overrides=tuple(args.set_env),
        )
        print(summary.to_text())
        if args.require_perfect and summary.success_count != summary.total:
            raise SystemExit(1)
        if args.require_post_probe_clear and not summary.post_probe_clear:
            raise SystemExit(1)
        return

    if args.command == "task" and args.task_name == "fceux-world-1-king":
        summary = run_fceux_1_1(
            game_path=Path(args.game_file),
            script_path=Path(args.script),
            artifacts_dir=Path(args.artifacts_dir),
            attempts=args.attempts,
            capture_images=args.capture_images,
            capture_ticks=args.capture_ticks,
            post_1_1_probe="run_1_castle_after_1_6",
            env_overrides=WORLD_1_KING_ENV + tuple(args.set_env),
        )
        print(summary.to_text())
        if args.require_perfect and (summary.success_count != summary.total or not summary.post_probe_clear):
            raise SystemExit(1)
        return

    if args.command == "task" and args.task_name == "review-fceux-log":
        summary = parse_fceux_log(Path(args.log), expected_attempts=args.attempts)
        print(summary.to_text())
        return

    if args.command == "task" and args.task_name == "fceux-contact-sheet":
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir) if args.output_dir else input_dir / "png"
        sheet_path = Path(args.sheet) if args.sheet else output_dir / "contact_sheet.png"
        converted = convert_gd_directory(input_dir, output_dir)
        write_contact_sheet(converted, sheet_path, columns=args.columns)
        print(f"converted={len(converted)}")
        print(f"sheet={sheet_path}")
        return

    if args.command == "goal" and args.goal_command == "validate":
        try:
            contract = load_goal_contract(resolve_goal_path(args.goal))
        except GoalValidationError as exc:
            parser.error(str(exc))
        print("valid=true")
        print(f"goal_id={contract.id}")
        print(f"preset={contract.preset}")
        print(f"segments={len(contract.segments)}")
        print(f"bridged_segments={len(contract.bridged_segments)}")
        return

    if args.command == "goal" and args.goal_command == "run":
        try:
            contract = load_goal_contract(resolve_goal_path(args.goal))
        except GoalValidationError as exc:
            parser.error(str(exc))

        game_file = args.game_file or os.environ.get("SMB3_GAME_FILE")
        if not game_file:
            parser.error("goal run requires --game-file or SMB3_GAME_FILE")

        result = run_goal_contract(
            contract,
            game_path=Path(game_file),
            attempts=args.attempts,
            artifacts_dir=Path(args.artifacts_dir) if args.artifacts_dir else None,
            capture_images=args.capture_images,
            capture_ticks=args.capture_ticks,
        )
        print(f"goal_id={result.contract.id}")
        print(f"artifacts_dir={result.artifacts_dir}")
        print(result.summary.to_text())
        print(f"metrics_passed={str(result.metrics_passed).lower()}")
        if result.contract.runner.get("require_perfect") and not result.metrics_passed:
            raise SystemExit(1)
        return

    parser.error("Unsupported command")
