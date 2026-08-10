from pathlib import Path

from PIL import Image
import pytest

from smb3_agent.fceux_images import convert_gd_directory, write_contact_sheet
from smb3_agent.fceux_harness import parse_fceux_log, run_fceux_1_1


LUA_AGENT_PATH = Path("scripts/fceux_1_1_agent.lua")


def lua_function_slice(source: str, name: str, next_name: str) -> str:
    start = source.index(f"local function {name}(")
    end = source.index(f"local function {next_name}(", start)
    return source[start:end]


def test_goal_card_observation_requires_course_transition() -> None:
    source = LUA_AGENT_PATH.read_text()
    fortress_candidate = lua_function_slice(
        source,
        "continue_1_fortress_after_mid_candidate",
        "run_1_fortress_mid_search",
    )
    one_six_probe = lua_function_slice(source, "run_1_6_probe", "run_1_castle_probe")

    assert "reached_goal_card" not in fortress_candidate
    assert "evidence=object_65_disappeared" not in one_six_probe
    assert "evidence=card_internal_state_nonzero" in one_six_probe
    assert "evidence=card_internal_state_then_course_transition" in one_six_probe


def test_single_attempt_playback_skips_retry_checkpoint() -> None:
    source = LUA_AGENT_PATH.read_text()
    playback = source[source.rindex("\nbootstrap_to_level()\n") :]

    assert playback.index("if attempts == 1 then") < playback.index(
        "local checkpoint = savestate.create()"
    )
    single_start = playback.index("if attempts == 1 then")
    single_attempt = playback[single_start : playback.index("else", single_start)]
    assert "savestate." not in single_attempt
    assert 'advance(10, "attempt_1_fresh_start")' in single_attempt


def test_agent_uses_supported_fceux_shutdown_api() -> None:
    source = LUA_AGENT_PATH.read_text()

    assert source.rstrip().endswith("emu.exit()")
    assert not source.rstrip().endswith("os.exit()")


def test_parse_fceux_log_counts_successes(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_start x=24 y=384",
                "frame=20 event=agent_tick x=100 y=384",
                "frame=30 event=attempt_1_reached_end_x x=2501 y=336",
                "frame=40 event=attempt_1_goal_area x=2801 y=384",
                "frame=50 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=60 event=attempt_2_start x=24 y=384",
                "frame=70 event=agent_tick x=900 y=384",
                "frame=80 event=attempt_2_bad_state x=8192 y=0",
                "frame=90 event=post_probe_1_2_progress_x_512 x=512 y=320",
                "frame=100 event=post_probe_1_2_success_course_clear x=8192 y=0",
                "frame=110 event=post_probe_1_2_done x=490 y=320",
            ]
        )
    )

    summary = parse_fceux_log(log_path, expected_attempts=2)

    assert summary.success_count == 1
    assert summary.bad_state_count == 1
    assert summary.attempts[0].max_x == 2801
    assert summary.attempts[0].reached_end is True
    assert summary.attempts[0].goal_area is True
    assert summary.attempts[1].max_x == 900
    assert summary.attempts[1].bad_state is True
    assert summary.post_probe_max_x == 512
    assert summary.post_probe_last_event == "post_probe_1_2_done"
    assert summary.post_probe_clear is True


def test_parse_fceux_log_rejects_bridge_assisted_world_1_king_marker(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=20 event=post_probe_1_castle_enter x=96 y=32",
                "frame=30 event=post_probe_1_airship_stage_bridge x=219 y=192",
                "frame=40 event=post_probe_1_airship_success_king x=432 y=4192",
            ]
        )
    )

    summary = parse_fceux_log(log_path, expected_attempts=1)

    assert summary.success_count == 1
    assert summary.post_probe_max_x == 432
    assert summary.post_probe_last_event == "post_probe_1_airship_success_king"
    assert summary.post_probe_clear is False


def test_parse_fceux_log_accepts_world_2_with_two_whistles(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "frame=40 event=post_probe_world_2_map_two_whistles x=32768 y=0 "
        "world_number=1 object_set=0 item_0=12 item_1=12 item_2=9 "
        "evidence=world_number_1_object_set_0"
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is True


def test_parse_fceux_log_rejects_world_2_with_missing_whistle(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "frame=40 event=post_probe_world_2_map_two_whistles x=32768 y=0 "
        "world_number=1 object_set=0 item_0=12 item_1=0 item_2=9 "
        "evidence=world_number_1_object_set_0"
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_accepts_observed_world_8_arrival(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_world_2_first_whistle_started "
                "world_number=1 object_set=0 item_0=12 item_1=12",
                "frame=20 event=post_probe_world_2_first_whistle_used "
                "world_number=1 object_set=0 item_0=12 item_1=9 "
                "evidence=two_to_one_whistle_after_A_input source_world=2",
                "frame=25 event=post_probe_warp_zone_5_6_7_tier "
                "world_number=8 object_set=0 map_cursor_x=64 map_cursor_y=112 "
                "item_0=12 item_1=9 "
                "evidence=warp_cursor_64_112_after_world_2_whistle",
                "frame=30 event=post_probe_warp_zone_second_whistle_started "
                "world_number=8 object_set=0 item_0=12 item_1=9",
                "frame=40 event=post_probe_warp_zone_second_whistle_used "
                "world_number=8 object_set=0 item_0=9 item_1=8 "
                "evidence=one_to_zero_whistles_after_A_input_from_5_6_7_tier",
                "frame=42 event=post_probe_warp_zone_world_8_tier "
                "world_number=8 object_set=0 map_cursor_x=128 map_cursor_y=144 "
                "item_0=9 item_1=8 "
                "evidence=warp_cursor_128_144_after_second_whistle",
                "frame=45 event=post_probe_world_8_pipe_entered "
                "world_number=8 object_set=0 map_cursor_x=160 map_cursor_y=144 "
                "item_0=9 item_1=8 "
                "evidence=A_input_from_warp_cursor_160_144",
                "frame=50 event=post_probe_world_8_map_arrival "
                "world_number=7 object_set=0 item_0=9 item_1=8 "
                "evidence=world_number_7_object_set_0_after_warp_pipe",
            ]
        )
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is True


def test_parse_fceux_log_resets_clear_when_1_6_level_entry_starts(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_1_5_success_course_clear x=8192 y=0",
                "frame=20 event=post_probe_1_6_level_enter_wait x=40960 y=0",
                "frame=30 event=post_probe_1_6_bad_state x=40960 y=0 max_x=307",
                "frame=40 event=post_probe_1_6_done x=40960 y=0",
            ]
        )
    )

    summary = parse_fceux_log(log_path, expected_attempts=0)

    assert summary.post_probe_clear is False
    assert summary.post_probe_last_event == "post_probe_1_6_done"


def test_parse_fceux_log_rejects_1_6_discovery_as_playback(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_1_6_opening_search_success x=350 y=248 form=3",
                "frame=20 event=post_probe_1_6_goal_card x=2440 y=384 form=3 "
                "evidence=card_internal_state_nonzero card_state=1 form_before_clear=3",
                "frame=30 event=post_probe_1_6_success_course_clear x=40960 y=0 form=0 "
                "evidence=card_internal_state_then_course_transition",
                "frame=35 event=post_probe_1_6_map_returned x=40960 y=0 form=0 "
                "object_set=0 evidence=object_set_0_after_course_transition",
                "frame=40 event=post_probe_1_airship_success_king x=432 y=4192 form=0",
            ]
        )
    )

    summary = parse_fceux_log(log_path, expected_attempts=0)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_requires_raccoon_goal_evidence_for_1_6(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_1_6_goal_card x=2440 y=384 form=3 "
                "evidence=card_internal_state_nonzero card_state=1 form_before_clear=3",
                "frame=20 event=post_probe_1_6_success_course_clear x=40960 y=0 form=0 "
                "evidence=card_internal_state_then_course_transition",
                "frame=25 event=post_probe_1_6_map_returned x=40960 y=0 form=0 "
                "object_set=0 evidence=object_set_0_after_course_transition",
            ]
        )
    )

    summary = parse_fceux_log(log_path, expected_attempts=0)

    assert summary.post_probe_clear is True


def test_parse_fceux_log_accepts_observed_roamer_defeat_and_map_return(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_world_1_roamer_defeated_in_battle "
                "x=160 y=300 object_set=3 return_map=0 item_0=12 item_1=12 "
                "evidence=enemy_id_-127_removed form_after=3",
                "frame=20 event=post_probe_world_1_roamer_map_returned "
                "x=32768 y=0 object_set=0 item_0=12 item_1=12 "
                "evidence=object_set_0_after_roamer_defeat",
            ]
        )
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is True


def test_parse_fceux_log_rejects_roamer_search_as_product_proof(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=5 event=post_probe_world_1_roamer_search_success x=160 y=300",
                "frame=10 event=post_probe_world_1_roamer_defeated_in_battle "
                "x=160 y=300 object_set=3 return_map=0 item_0=12 item_1=12 "
                "evidence=enemy_id_-127_removed form_after=3",
                "frame=20 event=post_probe_world_1_roamer_map_returned "
                "x=32768 y=0 object_set=0 item_0=12 item_1=12 "
                "evidence=object_set_0_after_roamer_defeat",
            ]
        )
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_rejects_roamer_disappearance_during_death(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_world_1_roamer_defeated_in_battle "
                "x=232 y=418 object_set=3 return_map=1 item_0=12 item_1=12 "
                "evidence=enemy_id_-127_removed form_after=0",
                "frame=20 event=post_probe_world_1_roamer_map_returned "
                "x=32768 y=0 object_set=0 item_0=12 item_1=12 "
                "evidence=object_set_0_after_roamer_defeat",
            ]
        )
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_roamer_life_loss_overrides_prior_level_clear(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=5 event=post_probe_1_6_success_course_clear x=2848",
                "frame=10 event=post_probe_world_1_roamer_detected x=24",
                "frame=20 event=post_probe_1_5_bad_state x=32768",
                "frame=30 event=post_probe_world_1_roamer_life_lost x=40960",
            ]
        )
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_airship_failure_overrides_roamer_clear(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=post_probe_world_1_roamer_defeated_in_battle "
                "x=214 y=384 object_set=3 return_map=0 item_0=12 item_1=12 "
                "evidence=enemy_id_-127_removed form_after=3",
                "frame=20 event=post_probe_world_1_roamer_map_returned "
                "x=32768 y=0 object_set=0 item_0=12 item_1=12 "
                "evidence=object_set_0_after_roamer_defeat",
                "frame=30 event=post_probe_1_airship_enter_after_roamer_wait x=32768 y=0",
                "frame=40 event=post_probe_1_castle_no_entry x=32768 y=0",
                "frame=50 event=post_probe_1_castle_bad_state x=32768 y=0 max_x=0",
            ]
        )
    )

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_convert_gd_directory_and_contact_sheet(tmp_path: Path) -> None:
    image_dir = tmp_path / "gd"
    image_dir.mkdir()
    gd_path = image_dir / "000001_probe.gd"
    pixel = bytes([0, 10, 20, 30])
    gd_path.write_bytes(b"FCEUXGD0000"[:11] + pixel * (256 * 224))

    output_dir = tmp_path / "png"
    converted = convert_gd_directory(image_dir, output_dir)
    sheet_path = write_contact_sheet(converted, tmp_path / "sheet.png", columns=1)

    assert len(converted) == 1
    with Image.open(converted[0]) as converted_image:
        assert converted_image.size == (256, 224)
    with Image.open(sheet_path) as sheet:
        assert sheet.size == (256, 242)


def test_run_fceux_rejects_invalid_env_override(tmp_path: Path) -> None:
    game_path = tmp_path / "local-game-file"
    game_path.write_bytes(b"placeholder")

    with pytest.raises(ValueError):
        run_fceux_1_1(
            game_path=game_path,
            script_path=tmp_path / "script.lua",
            artifacts_dir=tmp_path / "artifacts",
            attempts=1,
            env_overrides=("NOT_A_PAIR",),
        )


def test_run_fceux_rejects_missing_game_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Local game file not found"):
        run_fceux_1_1(
            game_path=tmp_path / "missing-local-game-file",
            script_path=tmp_path / "script.lua",
            artifacts_dir=tmp_path / "artifacts",
            attempts=1,
        )
