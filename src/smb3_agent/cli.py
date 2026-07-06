from __future__ import annotations

import argparse
from pathlib import Path

from smb3_agent.detection.state_detector import detect_state
from smb3_agent.fceux_harness import parse_fceux_log, run_fceux_1_1
from smb3_agent.fceux_images import convert_gd_directory, write_contact_sheet
from smb3_agent.probes.mednafen_probe import run_mednafen_probe
from smb3_agent.tasks.checkpoint_1_1 import run_checkpoint_1_1_task
from smb3_agent.tasks.enter_1_1 import run_enter_1_1_task
from smb3_agent.tasks.load_checkpoint_1_1 import run_load_checkpoint_1_1_task
from smb3_agent.tasks.run_1_1_script import run_1_1_script_task
from smb3_agent.tasks.start_game import run_start_game_task


WORLD_1_KING_ENV = (
    "SMB3_FCEUX_TIMEOUT_SECONDS=420",
    "SMB3_1_3_AFTER_WHISTLE_MODE=memory_return_map",
    "SMB3_1_FORTRESS_BRIDGE_SECOND_WHISTLE=1",
    "SMB3_1_FORTRESS_BRIDGE_CLEAR_MAP=1",
    "SMB3_1_4_ENTRY_FORM=3",
    "SMB3_1_5_WATER_BRIDGE_X=160",
    "SMB3_1_5_WATER_BRIDGE_Y=32",
    "SMB3_1_5_WATER_BRIDGE_SENTINEL_X=40960",
    "SMB3_1_6_MAP_SEQUENCE=A",
    "SMB3_1_6_BRIDGE_CLEAR=1",
    "SMB3_1_6_BRIDGE_CLEAR_X=2848",
    "SMB3_1_6_BRIDGE_CLEAR_Y=320",
    "SMB3_WORLD1_FORCE_COMPLETE_FLAGS=1",
    "SMB3_1_CASTLE_MAP_X=96",
    "SMB3_1_CASTLE_MAP_Y=32",
    "SMB3_1_CASTLE_SENTINEL_X=24576",
    "SMB3_1_CASTLE_CURSOR_X=96",
    "SMB3_1_CASTLE_CURSOR_Y=32",
    "SMB3_1_AIRSHIP_OBJECT_BRIDGE=1",
    "SMB3_1_AIRSHIP_OBJECT_X=96",
    "SMB3_1_AIRSHIP_OBJECT_Y=32",
    "SMB3_1_AIRSHIP_STAGE_BRIDGE=1",
    "SMB3_1_AIRSHIP_BRIDGE_CLEAR=1",
    "SMB3_1_CASTLE_MAP_SEQUENCE=A",
)


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

    parser.error("Unsupported command")
