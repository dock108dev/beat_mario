from __future__ import annotations

import argparse
from pathlib import Path

from smb3_agent.detection.state_detector import detect_state
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
    mednafen.add_argument("--game-file", default="game-file.nes", help="Path to the local NES game file")
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
    start_game.add_argument("--game-file", default="game-file.nes", help="Path to the local NES game file")
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
    enter_1_1.add_argument("--game-file", default="game-file.nes", help="Path to the local NES game file")
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
    checkpoint_1_1.add_argument("--game-file", default="game-file.nes", help="Path to the local NES game file")
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
    load_checkpoint_1_1.add_argument("--game-file", default="game-file.nes", help="Path to the local NES game file")
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
    run_1_1_script.add_argument("--game-file", default="game-file.nes", help="Path to the local NES game file")
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

    parser.error("Unsupported command")
