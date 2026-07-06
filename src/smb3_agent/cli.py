from __future__ import annotations

import argparse
import os
from pathlib import Path

from smb3_agent.commands import CommandParseError, parse_command, run_command
from smb3_agent.detection.state_detector import detect_state
from smb3_agent.fceux_harness import parse_fceux_log, run_fceux_1_1
from smb3_agent.fceux_images import convert_gd_directory, write_contact_sheet
from smb3_agent.goals import (
    GoalValidationError,
    load_goal_contract,
    resolve_goal_path,
    run_goal_contract,
)
from smb3_agent.lab import (
    LabError,
    add_note_to_latest,
    build_issue_ledger_latest,
    compare_variant,
    propose_variants_from_latest,
    promote_variant,
    propose_variant_from_latest,
    review_latest_session,
    run_variant,
    start_session,
    write_codex_task_latest,
    write_ui_summary_latest,
)
from smb3_agent.lab_ui import LabUiError, render_lab_ui, run_lab_ui_server
from smb3_agent.observe import ObserveError, run_observed_segment
from smb3_agent.presets import WORLD_1_KING_ENV
from smb3_agent.probes.mednafen_probe import run_mednafen_probe
from smb3_agent.recovery import RecoveryError, simulate_recovery
from smb3_agent.review import compare_logs, review_log
from smb3_agent.segments import (
    SegmentValidationError,
    load_segment_catalog,
    render_goal_status,
    validate_goal_segments,
)
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

    goal_status = goal_subparsers.add_parser("status", help="Show a goal's route segment status")
    goal_status.add_argument("goal", help="Goal id or path to a goal YAML file")
    goal_status.add_argument(
        "--segments",
        default="data/segments/world_1.yaml",
        help="Path to the segment catalog YAML file",
    )

    segment = subparsers.add_parser("segment", help="Validate segment catalogs")
    segment_subparsers = segment.add_subparsers(dest="segment_command", required=True)

    segment_validate = segment_subparsers.add_parser("validate", help="Validate a segment catalog")
    segment_validate.add_argument("catalog", help="Path to a segment catalog YAML file")
    segment_validate.add_argument(
        "--goal",
        default="world_1_king",
        help="Optional goal id/path to cross-check against the catalog",
    )

    review = subparsers.add_parser("review", help="Review route logs and compare attempts")
    review_subparsers = review.add_subparsers(dest="review_command", required=True)

    review_log_parser = review_subparsers.add_parser("log", help="Review one route log")
    review_log_parser.add_argument("log", help="Path to a FCEUX route log")
    review_log_parser.add_argument("--attempts", type=int, default=None)

    review_compare = review_subparsers.add_parser("compare", help="Compare two route logs or artifact dirs")
    review_compare.add_argument("left", help="Left route log or artifact directory")
    review_compare.add_argument("right", help="Right route log or artifact directory")

    command = subparsers.add_parser("command", help="Parse and run user-facing game commands")
    command_subparsers = command.add_subparsers(dest="command_action", required=True)

    command_parse = command_subparsers.add_parser("parse", help="Parse a user command")
    command_parse.add_argument("text", help="User command text")

    command_run = command_subparsers.add_parser("run", help="Run a parsed user command")
    command_run.add_argument("text", help="User command text")
    command_run.add_argument("--game-file", default=None, help="Path to the local game file")
    command_run.add_argument(
        "--artifacts-dir",
        default=None,
        help="Directory for command trace and nested goal artifacts",
    )

    observe = subparsers.add_parser("observe", help="Run observed segments and write state traces")
    observe_subparsers = observe.add_subparsers(dest="observe_command", required=True)

    observe_segment = observe_subparsers.add_parser("run-segment", help="Run one segment with state tracing")
    observe_segment.add_argument("segment", help="Segment id or supported alias")
    observe_segment.add_argument("--game-file", default=None, help="Path to the local game file")
    observe_segment.add_argument("--sample-frames", type=int, default=15)
    observe_segment.add_argument(
        "--artifacts-dir",
        default=None,
        help="Directory for observed run artifacts",
    )

    recovery = subparsers.add_parser("recovery", help="Simulate recovery decisions from goal contracts")
    recovery_subparsers = recovery.add_subparsers(dest="recovery_command", required=True)

    recovery_simulate = recovery_subparsers.add_parser("simulate", help="Simulate a recovery scenario")
    recovery_simulate.add_argument("scenario", choices=["life_lost", "wrong_map_node"])
    recovery_simulate.add_argument("--goal", default="world_1_king", help="Goal id or path")

    lab = subparsers.add_parser("lab", help="Run attempt-lab sessions, notes, reviews, and variants")
    lab_subparsers = lab.add_subparsers(dest="lab_command", required=True)

    lab_start = lab_subparsers.add_parser("start", help="Start an attempt-lab session from a user command")
    lab_start.add_argument("text", help="User command text")
    lab_start.add_argument("--game-file", default=None, help="Path to the local game file")
    lab_start.add_argument("--attempts", type=int, default=1)
    lab_start.add_argument(
        "--artifacts-root",
        default="artifacts/sessions",
        help="Root directory for lab sessions",
    )
    lab_start.add_argument("--route-variant", default="world_1_baseline")
    lab_start.add_argument("--capture-images", action="store_true")
    lab_start.add_argument("--no-capture-ticks", action="store_true")

    lab_note = lab_subparsers.add_parser("note", help="Attach a human note to a lab session")
    lab_note.add_argument("target", choices=["latest"], help="Session target")
    lab_note.add_argument("text", help="Raw note text")
    lab_note.add_argument("--segment", default=None, help="Optional segment id")
    lab_note.add_argument("--attempt", type=int, default=None, help="Optional attempt number")
    lab_note.add_argument("--anchor-type", default=None, help="Optional anchor type")
    lab_note.add_argument("--anchor-value", default=None, help="Optional anchor value")
    lab_note.add_argument("--severity", default="note")

    lab_review = lab_subparsers.add_parser("review", help="Review a lab session")
    lab_review.add_argument("target", choices=["latest"], help="Session target")

    lab_issues = lab_subparsers.add_parser("issues", help="Build grouped issue ledger for a lab session")
    lab_issues.add_argument("target", choices=["latest"], help="Session target")

    lab_propose = lab_subparsers.add_parser("propose-variant", help="Create a route variant proposal")
    lab_propose.add_argument("target", choices=["latest"], help="Session target")

    lab_propose_many = lab_subparsers.add_parser(
        "propose-variants",
        help="Create route variant proposals for all actionable issues",
    )
    lab_propose_many.add_argument("target", choices=["latest"], help="Session target")

    lab_ui_summary = lab_subparsers.add_parser("ui-summary", help="Write UI-ready route map summary")
    lab_ui_summary.add_argument("target", choices=["latest"], help="Session target")

    lab_codex_task = lab_subparsers.add_parser("codex-task", help="Write a Codex-ready task packet")
    lab_codex_task.add_argument("target", choices=["latest"], help="Session target")
    lab_codex_task.add_argument("--issue", required=True, help="Issue id to package")

    lab_ui = lab_subparsers.add_parser("ui", help="Serve the local World 1 lab UI")
    lab_ui.add_argument("--host", default="127.0.0.1")
    lab_ui.add_argument("--port", type=int, default=8765)
    lab_ui.add_argument("--open", action="store_true", help="Open the UI in the default browser")

    lab_ui_render = lab_subparsers.add_parser("ui-render", help="Render the lab UI HTML once")
    lab_ui_render.add_argument("--output", default="artifacts/ui/latest.html")

    lab_run_variant = lab_subparsers.add_parser("run-variant", help="Run a route variant through validation")
    lab_run_variant.add_argument("variant_id")
    lab_run_variant.add_argument("--game-file", default=None, help="Path to the local game file")
    lab_run_variant.add_argument("--attempts", type=int, default=10)
    lab_run_variant.add_argument(
        "--artifacts-root",
        default="artifacts/sessions",
        help="Root directory for lab sessions",
    )

    lab_compare_variant = lab_subparsers.add_parser("compare-variant", help="Compare variant evidence")
    lab_compare_variant.add_argument("variant_id")

    lab_promote_variant = lab_subparsers.add_parser("promote-variant", help="Promote a passing route variant")
    lab_promote_variant.add_argument("variant_id")

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

    if args.command == "goal" and args.goal_command == "status":
        try:
            contract = load_goal_contract(resolve_goal_path(args.goal))
            catalog = load_segment_catalog(Path(args.segments))
            print(render_goal_status(contract, catalog))
        except (GoalValidationError, SegmentValidationError) as exc:
            parser.error(str(exc))
        return

    if args.command == "segment" and args.segment_command == "validate":
        try:
            catalog = load_segment_catalog(Path(args.catalog))
            if args.goal:
                contract = load_goal_contract(resolve_goal_path(args.goal))
                validate_goal_segments(contract, catalog)
        except (GoalValidationError, SegmentValidationError) as exc:
            parser.error(str(exc))
        print("valid=true")
        print(f"catalog_id={catalog.catalog_id}")
        print(f"segments={len(catalog.segments)}")
        if args.goal:
            print(f"goal_id={contract.id}")
            print(f"goal_segments={len(contract.segments)}")
        return

    if args.command == "review" and args.review_command == "log":
        print(review_log(Path(args.log), expected_attempts=args.attempts).to_text())
        return

    if args.command == "review" and args.review_command == "compare":
        print(compare_logs(_resolve_review_log(Path(args.left)), _resolve_review_log(Path(args.right))).to_text())
        return

    if args.command == "command" and args.command_action == "parse":
        try:
            print(parse_command(args.text).to_text())
        except CommandParseError as exc:
            parser.error(str(exc))
        return

    if args.command == "command" and args.command_action == "run":
        game_file = args.game_file or os.environ.get("SMB3_GAME_FILE")
        if not game_file:
            parser.error("command run requires --game-file or SMB3_GAME_FILE")
        try:
            result = run_command(
                args.text,
                game_path=Path(game_file),
                artifacts_dir=Path(args.artifacts_dir) if args.artifacts_dir else None,
            )
        except CommandParseError as exc:
            parser.error(str(exc))
        print(result.to_text())
        if not result.goal_result.metrics_passed:
            raise SystemExit(1)
        return

    if args.command == "observe" and args.observe_command == "run-segment":
        game_file = args.game_file or os.environ.get("SMB3_GAME_FILE")
        if not game_file:
            parser.error("observe run-segment requires --game-file or SMB3_GAME_FILE")
        try:
            result = run_observed_segment(
                args.segment,
                game_path=Path(game_file),
                sample_frames=args.sample_frames,
                artifacts_dir=Path(args.artifacts_dir) if args.artifacts_dir else None,
            )
        except ObserveError as exc:
            parser.error(str(exc))
        print(result.to_text())
        if result.summary.success_count != result.summary.total:
            raise SystemExit(1)
        return

    if args.command == "recovery" and args.recovery_command == "simulate":
        try:
            contract = load_goal_contract(resolve_goal_path(args.goal))
            print(simulate_recovery(contract, args.scenario).to_text())
        except (GoalValidationError, RecoveryError) as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "start":
        game_file = args.game_file or os.environ.get("SMB3_GAME_FILE")
        if not game_file:
            parser.error("lab start requires --game-file or SMB3_GAME_FILE")
        try:
            result = start_session(
                args.text,
                game_path=Path(game_file),
                attempts=args.attempts,
                artifacts_root=Path(args.artifacts_root),
                route_variant=args.route_variant,
                capture_images=args.capture_images,
                capture_ticks=not args.no_capture_ticks,
            )
        except (CommandParseError, GoalValidationError, LabError, FileNotFoundError) as exc:
            parser.error(str(exc))
        print(result.to_text())
        return

    if args.command == "lab" and args.lab_command == "note":
        try:
            print(
                add_note_to_latest(
                    args.text,
                    segment_id=args.segment,
                    attempt_number=args.attempt,
                    anchor_type=args.anchor_type,
                    anchor_value=args.anchor_value,
                    severity=args.severity,
                ).to_text()
            )
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "review":
        try:
            print(review_latest_session().to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "issues":
        try:
            print(build_issue_ledger_latest().to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "propose-variant":
        try:
            print(propose_variant_from_latest().to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "propose-variants":
        try:
            print(propose_variants_from_latest().to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "ui-summary":
        try:
            print(write_ui_summary_latest().to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "codex-task":
        try:
            print(write_codex_task_latest(args.issue).to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "ui":
        try:
            run_lab_ui_server(host=args.host, port=args.port, open_browser=args.open)
        except (LabError, LabUiError, OSError) as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "ui-render":
        try:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(render_lab_ui(), encoding="utf-8")
        except (LabError, LabUiError) as exc:
            parser.error(str(exc))
        print(f"html={output}")
        return

    if args.command == "lab" and args.lab_command == "run-variant":
        game_file = args.game_file or os.environ.get("SMB3_GAME_FILE")
        if not game_file:
            parser.error("lab run-variant requires --game-file or SMB3_GAME_FILE")
        try:
            print(
                run_variant(
                    args.variant_id,
                    game_path=Path(game_file),
                    attempts=args.attempts,
                    artifacts_root=Path(args.artifacts_root),
                ).to_text()
            )
        except (LabError, FileNotFoundError, GoalValidationError) as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "compare-variant":
        try:
            print(compare_variant(args.variant_id).to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    if args.command == "lab" and args.lab_command == "promote-variant":
        try:
            print(promote_variant(args.variant_id).to_text())
        except LabError as exc:
            parser.error(str(exc))
        return

    parser.error("Unsupported command")


def _resolve_review_log(path: Path) -> Path:
    if path.is_dir():
        return path / "fceux_1_1.log"
    return path
