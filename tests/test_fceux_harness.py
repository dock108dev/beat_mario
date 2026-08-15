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


def _world_8_big_tanks_lines() -> list[str]:
    return [
        "frame=10 event=post_probe_world_2_first_whistle_started "
        "world_number=1 object_set=0 item_0=12 item_1=12",
        "frame=20 event=post_probe_world_2_first_whistle_used "
        "world_number=1 object_set=0 item_0=12 item_1=9 "
        "evidence=two_to_one_whistle_after_A_input source_world=2",
        "frame=25 event=post_probe_warp_zone_5_6_7_tier "
        "world_number=8 object_set=0 map_cursor_x=64 map_cursor_y=112 "
        "item_0=12 item_1=9 evidence=warp_cursor_64_112_after_world_2_whistle",
        "frame=30 event=post_probe_warp_zone_second_whistle_started "
        "world_number=8 object_set=0 item_0=12 item_1=9",
        "frame=40 event=post_probe_warp_zone_second_whistle_used "
        "world_number=8 object_set=0 item_0=9 item_1=8 "
        "evidence=one_to_zero_whistles_after_A_input_from_5_6_7_tier",
        "frame=42 event=post_probe_warp_zone_world_8_tier "
        "world_number=8 object_set=0 map_cursor_x=128 map_cursor_y=144 "
        "item_0=9 item_1=8 evidence=warp_cursor_128_144_after_second_whistle",
        "frame=45 event=post_probe_world_8_pipe_entered "
        "world_number=8 object_set=0 map_cursor_x=160 map_cursor_y=144 "
        "item_0=9 item_1=8 evidence=A_input_from_warp_cursor_160_144",
        "frame=50 event=post_probe_world_8_map_arrival "
        "world_number=7 object_set=0 map_cursor_x=32 map_cursor_y=80 "
        "item_0=9 item_1=8 evidence=world_number_7_object_set_0_after_warp_pipe",
        "frame=55 event=post_probe_world_8_big_tanks_started",
        "frame=60 event=post_probe_world_8_big_tanks_entered x=24 y=368 "
        "world_number=7 object_set=10 stage_identity=world_8_big_tanks "
        "evidence=normal_down_right_A_from_32_80",
        "frame=70 event=post_probe_world_8_big_tanks_gameplay x=600 y=300 "
        "world_number=7 object_set=10 evidence=normal_autoscroll_gameplay",
        "frame=80 event=post_probe_world_8_big_tanks_boss_defeated "
        "world_number=7 object_set=10 "
        "evidence=enemy_minus_126_object_state_6_game_enforced_stomp",
        "frame=90 event=post_probe_world_8_big_tanks_clear "
        "world_number=7 object_set=10 "
        "evidence=treasure_chest_super_star_collected_with_game_return_flag",
        "frame=100 event=post_probe_world_8_big_tanks_post_clear "
        "world_number=7 object_set=0 map_cursor_x=64 map_cursor_y=112 "
        "evidence=stable_world_8_map_after_game_clear",
    ]


def _world_8_battleships_lines() -> list[str]:
    return _world_8_big_tanks_lines() + [
        "frame=110 event=post_probe_world_8_battleships_started "
        "world_number=7 object_set=0 map_cursor_x=64 map_cursor_y=112",
        "frame=120 event=post_probe_world_8_battleships_entered x=0 y=320 "
        "entry_x=0 entry_y=320 entry_air=0 world_number=7 object_set=10 "
        "map_enter_via_id=13 map_node_x=128 map_node_y=112 "
        "stage_identity=world_8_battleships "
        "evidence=normal_right_right_automatic_entry_from_64_112",
        "frame=130 event=post_probe_world_8_battleships_gameplay x=600 y=200 "
        "world_number=7 object_set=10 evidence=normal_autoscroll_fleet_gameplay",
        "frame=140 event=post_probe_world_8_battleships_boss_defeated "
        "world_number=7 object_set=10 mario_alive=1 player_is_dying=0 "
        "starting_lives=5 current_lives=5 boss_object_id_75_active=0 "
        "defeated_transition_object_id_74_active=1 boss_state_transitions=4 "
        "evidence=game_owned_boss_object_75_to_defeated_transition_object_74",
        "frame=150 event=post_probe_world_8_battleships_clear "
        "world_number=7 object_set=10 mario_alive=1 player_is_dying=0 "
        "starting_lives=5 current_lives=5 return_map=1 "
        "boss_object_id_75_active=0 defeated_transition_object_id_74_observed=1 "
        "boss_state_transitions=4 "
        "evidence=game_owned_return_map_transition_after_defeated_boss_object",
        "frame=160 event=post_probe_world_8_battleships_post_clear "
        "world_number=7 object_set=0 map_cursor_x=128 map_cursor_y=112 "
        "hand_trap_region_accessible=1 hand_trap_entered=0 player_is_dying=0 "
        "starting_lives=5 current_lives=5 "
        "evidence=stable_world_8_map_after_boom_boom",
    ]


def _world_8_hand_traps_jet_lines() -> list[str]:
    lines = _world_8_battleships_lines()
    lines.extend(
        [
            "frame=161 event=post_probe_world_8_battleships_p_wing_preserved "
            "p_wing_count=1 evidence=owner_directed_underwater_battleships_route",
            "frame=162 event=post_probe_world_8_battleships_star_used "
            "star_before=2 star_after=1 p_wing_preserved=1 "
            "evidence=normal_inventory_B_A_immediately_before_entry",
            "frame=163 event=post_probe_world_8_battleships_swim_started "
            "evidence=normal_fall_into_reddish_water_after_exposed_first_ship",
            "frame=164 event=post_probe_world_8_battleships_stern_wait "
            "evidence=waited_for_end_of_autoscroll_behind_final_ship",
        ]
    )
    frame = 170
    trap_specs = (
        ("right", 160, 320, "brother_enemy_ids=-121,-127,-126,-122"),
        ("center", 128, 368, "hazard_identity=lava_platforms_and_podoboos"),
        ("left", 96, 320, "hazard_identity=broken_bridge_and_jumping_cheep_cheeps"),
    )
    for name, cursor_x, entry_y, gameplay_identity in trap_specs:
        lines.extend(
            [
                f"frame={frame} event=post_probe_world_8_hand_trap_{name}_started",
                f"frame={frame + 1} event=post_probe_world_8_hand_trap_{name}_entered "
                f"world_number=7 object_set=11 target_cursor_x={cursor_x} "
                f"target_cursor_y=112 entry_x=24 entry_y={entry_y} entry_air=0 "
                f"stage_identity=world_8_hand_trap_{name} "
                "evidence=deliberate_A_input_from_observed_hand_tile",
                f"frame={frame + 2} event=post_probe_world_8_hand_trap_{name}_gameplay "
                f"world_number=7 object_set=11 {gameplay_identity}",
                f"frame={frame + 3} event=post_probe_world_8_hand_trap_{name}_reward "
                "world_number=7 object_set=11 reward_item_id=3 leaf_before=0 leaf_after=1 "
                "evidence=game_owned_reward_object_82_and_inventory_transition",
                f"frame={frame + 4} event=post_probe_world_8_hand_trap_{name}_post_clear "
                f"world_number=7 object_set=0 map_cursor_x={cursor_x} map_cursor_y=112 "
                "player_is_dying=0 lives_unchanged=1 stable_frames=180 "
                "evidence=stable_world_8_map_after_game_clear",
            ]
        )
        frame += 10
    lines.extend(
        [
            f"frame={frame} event=post_probe_world_8_jet_started",
            f"frame={frame + 1} event=post_probe_world_8_jet_p_wing_used "
            "p_wing_remaining=0 evidence=owner_directed_normal_inventory_use "
            "saved_from_battleships",
            f"frame={frame + 2} event=post_probe_world_8_jet_entered "
            "world_number=7 object_set=10 source_cursor_x=96 source_cursor_y=112 "
            "map_node_x=64 map_node_y=80 map_enter_via_id=15 entry_x=0 entry_y=320 "
            "entry_air=0 stage_identity=world_8_jet "
            "evidence=normal_left_up_then_game_owned_automatic_entry",
            f"frame={frame + 3} event=post_probe_world_8_jet_gameplay "
            "world_number=7 object_set=10 p_wing_active=1 "
            "pacing=hazard_wait_opening_wait_controlled_advance "
            "evidence=observed_pause_and_advance_autoscroller_controller",
            f"frame={frame + 4} event=post_probe_world_8_jet_boss_defeated "
            "world_number=7 object_set=10 boss_object_id_76_active=0 "
            "defeated_transition_object_id_74_active=1 mario_alive=1 player_is_dying=0 "
            "evidence=game_owned_boss_object_76_to_defeated_transition_object_74",
            f"frame={frame + 5} event=post_probe_world_8_jet_clear "
            "world_number=7 object_set=10 return_map=1 mario_alive=1 player_is_dying=0 "
            "evidence=game_owned_return_map_transition_after_defeated_flying_boom_boom",
            f"frame={frame + 6} event=post_probe_world_8_jet_post_clear "
            "world_number=7 object_set=0 map_page=2 map_cursor_x=64 map_cursor_y=112 "
            "dark_area_traversed=1 world_8_1_accessible=1 world_8_1_entered=0 "
            "stable_frames=180 player_is_dying=0 "
            "evidence=stable_world_8_map_with_world_8_1_accessible",
        ]
    )
    return lines


def _world_8_8_2_lines() -> list[str]:
    return _world_8_hand_traps_jet_lines() + [
        "frame=240 event=post_probe_world_8_8_2_started accepted_form=0 "
        "accepted_item_0=3 evidence=accepted_21_segment_jet_post_clear_boundary",
        "frame=241 event=post_probe_world_8_1_entered world_number=7 object_set=1 "
        "stage_identity=world_8_1 entry_id=0 entry_object_set=1 entry_x=0 "
        "entry_y=384 entry_air=0 entry_form=0 "
        "evidence=normal_A_input_from_world_8_1_map_node",
        "frame=242 event=post_probe_world_8_1_gameplay world_number=7 object_set=1 "
        "hazards=bill_blasters_bullet_bills_piranha_plants_koopas_pits_boo "
        "evidence=normal_dark_level_progression",
        "frame=243 event=post_probe_world_8_1_goal_card world_number=7 object_set=1 "
        "goal_object_id=65 goal_seen=1 goal_card_state=4 goal_card_object_slot=7 "
        "form_before_clear=0 cards_before_touch=2,0,0 cards_at_touch=2,3,0 "
        "mario_alive=1 player_is_dying=0 starting_lives=5 current_lives=5 "
        "evidence=game_owned_goal_object_65_internal_state_after_touch",
        "frame=244 event=post_probe_world_8_1_course_clear world_number=7 object_set=0 "
        "goal_object_id=65 goal_card_state=4 form_before_clear=0 "
        "cards_at_map_return=2,3,0 mario_alive=1 player_is_dying=0 "
        "lives_unchanged=1 "
        "evidence=goal_card_touch_then_game_owned_return_to_world_map",
        "frame=245 event=post_probe_world_8_1_post_clear world_number=7 object_set=0 "
        "map_page=2 map_cursor_x=64 map_cursor_y=112 world_8_2_accessible=1 "
        "world_8_2_entered=0 stable_frames=180 "
        "evidence=stable_world_8_map_after_goal_card_course_clear",
        "frame=246 event=post_probe_world_8_2_entered world_number=7 object_set=14 "
        "stage_identity=world_8_2 entry_id=0 entry_object_set=14 entry_x=0 "
        "entry_y=112 entry_air=0 entry_form=0 "
        "evidence=normal_A_input_from_accessible_world_8_2_map_node",
        "frame=247 event=post_probe_world_8_2_gameplay world_number=7 object_set=14 "
        "quicksand_shortcut=first_sandfall_right_pipe "
        "angry_sun_handling=suppressed_by_normal_in_level_shortcut "
        "hazards=venus_fire_traps_slopes_pits_spawned_enemies "
        "evidence=normal_world_8_2_progression",
        "frame=248 event=post_probe_world_8_2_goal_card world_number=7 object_set=14 "
        "goal_object_id=65 goal_seen=1 goal_card_state=4 goal_card_object_slot=7 "
        "form_before_clear=0 cards_before_touch=2,3,0 cards_at_touch=2,3,1 "
        "mario_alive=1 player_is_dying=0 starting_lives=5 current_lives=5 "
        "evidence=game_owned_goal_object_65_internal_state_after_touch",
        "frame=249 event=post_probe_world_8_2_course_clear world_number=7 object_set=0 "
        "goal_object_id=65 goal_card_state=4 form_before_clear=0 "
        "cards_at_map_return=0,0,0 card_transition=three_cards_converted_by_game "
        "mario_alive=1 player_is_dying=0 lives_unchanged=1 "
        "evidence=goal_card_touch_then_game_owned_return_to_world_map",
        "frame=250 event=post_probe_world_8_2_post_clear world_number=7 object_set=0 "
        "map_page=2 map_cursor_x=64 map_cursor_y=144 fortress_accessible=1 "
        "fortress_entered=0 stable_frames=180 "
        "evidence=normal_right_input_reached_accessible_world_8_fortress_node",
    ]


def _world_8_super_tanks_lines() -> list[str]:
    return _world_8_8_2_lines() + [
        "frame=251 event=post_probe_world_8_super_tanks_started world_number=7 "
        "object_set=0 map_page=2 map_cursor_x=64 map_cursor_y=144 "
        "fortress_accessible=1 fortress_entered=0 "
        "evidence=accepted_23_segment_world_8_2_post_clear_boundary",
        "frame=252 event=post_probe_world_8_fortress_entered "
        "stage_identity=world_8_fortress source_cursor_x=64 source_cursor_y=144 "
        "mario_alive=1 player_is_dying=0 "
        "evidence=normal_A_input_from_accessible_world_8_fortress_node",
        "frame=253 event=post_probe_world_8_fortress_gameplay "
        "room_transitions_observed=1 hazards=doors_conveyors_lava_spikes_roto_discs "
        "evidence=normal_fortress_door_and_hazard_traversal",
        "frame=254 event=post_probe_world_8_fortress_switch_activated "
        "hidden_boss_door_exposed=1 evidence=game_owned_switch_block_activation",
        "frame=255 event=post_probe_world_8_fortress_boss_room_entered "
        "boss_form=grounded boom_boom_active=1 mario_alive=1 "
        "evidence=normal_hidden_boss_door_entry",
        "frame=256 event=post_probe_world_8_fortress_boss_defeated "
        "boss_form=grounded magic_ball_available=1 mario_alive=1 player_is_dying=0 "
        "evidence=game_owned_boom_boom_defeated_transition",
        "frame=257 event=post_probe_world_8_fortress_magic_ball "
        "magic_ball_touched=1 mario_alive=1 "
        "evidence=normal_input_touched_game_owned_magic_ball",
        "frame=258 event=post_probe_world_8_fortress_clear return_map=1 "
        "mario_alive=1 player_is_dying=0 "
        "evidence=game_owned_fortress_destruction_and_return_map_transition",
        "frame=259 event=post_probe_world_8_fortress_post_clear "
        "world_number=7 object_set=0 map_page=2 fortress_cleared=1 "
        "super_tanks_accessible=1 super_tanks_entered=0 stable_frames=180 "
        "evidence=stable_world_8_map_with_super_tanks_accessible",
        "frame=260 event=post_probe_world_8_super_tanks_entered "
        "stage_identity=world_8_super_tanks distinct_vehicle_identity=1 "
        "mario_alive=1 player_is_dying=0 "
        "evidence=game_owned_automatic_entry_after_fortress_clear",
        "frame=261 event=post_probe_world_8_super_tanks_gameplay "
        "moving_tank_geometry_observed=1 overhead_airships_observed=1 "
        "evidence=normal_super_tanks_convoy_progression",
        "frame=262 event=post_probe_world_8_super_tanks_final_pipe "
        "boss_room_transition=1 evidence=normal_input_entered_final_warp_pipe",
        "frame=263 event=post_probe_world_8_super_tanks_boss_defeated "
        "boss_form=flying magic_ball_available=1 mario_alive=1 player_is_dying=0 "
        "evidence=game_owned_boom_boom_defeated_transition",
        "frame=264 event=post_probe_world_8_super_tanks_magic_ball "
        "magic_ball_touched=1 mario_alive=1 "
        "evidence=normal_input_touched_game_owned_magic_ball",
        "frame=265 event=post_probe_world_8_super_tanks_clear return_map=1 "
        "mario_alive=1 player_is_dying=0 "
        "evidence=game_owned_super_tanks_return_map_transition",
        "frame=266 event=post_probe_world_8_super_tanks_post_clear "
        "world_number=7 object_set=0 map_page=3 map_cursor_x=96 map_cursor_y=112 "
        "bowser_castle_accessible=1 bowser_castle_entered=0 stable_frames=180 "
        "evidence=stable_world_8_map_with_bowser_castle_accessible",
    ]


def _parse_lines(tmp_path: Path, lines: list[str]):
    log_path = tmp_path / "fceux.log"
    log_path.write_text("\n".join(lines) + "\n")
    return parse_fceux_log(log_path)


def test_parse_fceux_log_accepts_exact_hand_traps_and_jet_sequence(
    tmp_path: Path,
) -> None:
    summary = _parse_lines(tmp_path, _world_8_hand_traps_jet_lines())

    assert summary.post_probe_clear is True
    assert summary.post_probe_last_event == "post_probe_world_8_jet_post_clear"


def test_parse_fceux_log_accepts_distinct_world_8_1_and_8_2_goal_cards(
    tmp_path: Path,
) -> None:
    summary = _parse_lines(tmp_path, _world_8_8_2_lines())

    assert summary.post_probe_clear is True
    assert summary.post_probe_last_event == "post_probe_world_8_2_post_clear"


def test_parse_fceux_log_accepts_ordered_fortress_and_super_tanks_boss_proofs(
    tmp_path: Path,
) -> None:
    summary = _parse_lines(tmp_path, _world_8_super_tanks_lines())

    assert summary.post_probe_clear is True
    assert summary.post_probe_last_event == "post_probe_world_8_super_tanks_post_clear"


@pytest.mark.parametrize(
    "event_to_remove",
    [
        "post_probe_world_8_fortress_switch_activated",
        "post_probe_world_8_fortress_magic_ball",
        "post_probe_world_8_fortress_post_clear",
        "post_probe_world_8_super_tanks_gameplay",
        "post_probe_world_8_super_tanks_final_pipe",
        "post_probe_world_8_super_tanks_magic_ball",
    ],
)
def test_parse_fceux_log_rejects_missing_fortress_or_super_tanks_proof(
    tmp_path: Path, event_to_remove: str
) -> None:
    lines = [line for line in _world_8_super_tanks_lines() if f"event={event_to_remove} " not in line]

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


def test_parse_fceux_log_rejects_cross_level_boss_or_death_proof(tmp_path: Path) -> None:
    lines = _world_8_super_tanks_lines()
    lines = [
        line.replace("boss_form=flying", "boss_form=grounded")
        .replace("mario_alive=1 player_is_dying=0", "mario_alive=0 player_is_dying=1")
        if "event=post_probe_world_8_super_tanks_boss_defeated " in line
        else line
        for line in lines
    ]

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


@pytest.mark.parametrize(
    ("needle", "replacement"),
    [
        ("goal_card_state=4", "goal_card_state=0"),
        ("cards_before_touch=2,3,0", "cards_before_touch=2,0,0"),
        ("cards_at_map_return=0,0,0", "cards_at_map_return=2,3,1"),
        ("fortress_accessible=1", "fortress_accessible=0"),
        ("fortress_entered=0", "fortress_entered=1"),
        ("map_cursor_x=64 map_cursor_y=144", "map_cursor_x=32 map_cursor_y=144"),
    ],
)
def test_parse_fceux_log_rejects_invalid_goal_card_or_final_map_proof(
    tmp_path: Path, needle: str, replacement: str
) -> None:
    lines = _world_8_8_2_lines()
    index = next(index for index, line in enumerate(lines) if needle in line)
    lines[index] = lines[index].replace(needle, replacement)

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


@pytest.mark.parametrize(
    "failure_event",
    [
        "post_probe_world_8_1_death",
        "post_probe_world_8_1_stall",
        "post_probe_world_8_1_timeout",
        "post_probe_world_8_2_death",
        "post_probe_world_8_2_stall",
        "post_probe_world_8_2_timeout",
        "post_probe_world_8_fortress_entered",
    ],
)
def test_parse_fceux_log_rejects_world_8_1_8_2_fail_closed_events(
    tmp_path: Path, failure_event: str
) -> None:
    lines = _world_8_8_2_lines()
    lines.append(f"frame=999 event={failure_event}")

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


def test_world_8_1_goal_card_cannot_cross_satisfy_world_8_2(tmp_path: Path) -> None:
    lines = _world_8_8_2_lines()
    index = next(
        index
        for index, line in enumerate(lines)
        if "event=post_probe_world_8_2_goal_card " in line
    )
    lines[index] = lines[index].replace(
        "event=post_probe_world_8_2_goal_card",
        "event=post_probe_world_8_1_goal_card",
    )

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


def test_goal_touch_requires_course_clear_before_map_return(tmp_path: Path) -> None:
    original = _world_8_8_2_lines()
    course_index = next(
        index
        for index, line in enumerate(original)
        if "event=post_probe_world_8_2_course_clear " in line
    )
    goal_index = next(
        index
        for index, line in enumerate(original)
        if "event=post_probe_world_8_2_goal_card " in line
    )
    cases = (
        original[:course_index] + original[course_index + 1 :],
        original[:goal_index] + original[goal_index + 1 :],
        original[:course_index]
        + ["frame=248 event=post_probe_world_8_2_death"]
        + original[course_index:],
    )

    for index, lines in enumerate(cases):
        case_dir = tmp_path / str(index)
        case_dir.mkdir()
        assert _parse_lines(case_dir, lines).post_probe_clear is False


def test_world_8_2_entry_before_world_8_1_post_clear_is_rejected(
    tmp_path: Path,
) -> None:
    lines = _world_8_8_2_lines()
    post_index = next(
        index
        for index, line in enumerate(lines)
        if "event=post_probe_world_8_1_post_clear " in line
    )
    entry_index = next(
        index
        for index, line in enumerate(lines)
        if "event=post_probe_world_8_2_entered " in line
    )
    entry = lines.pop(entry_index)
    lines.insert(post_index, entry)

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


@pytest.mark.parametrize(
    "failure_event",
    [
        "post_probe_world_8_hand_trap_right_death",
        "post_probe_world_8_hand_trap_center_death",
        "post_probe_world_8_hand_trap_left_death",
        "post_probe_world_8_jet_death",
        "post_probe_world_8_jet_fall",
        "post_probe_world_8_jet_gameplay_stall",
        "post_probe_world_8_jet_timeout",
        "post_probe_world_8_jet_world_8_1_entered",
    ],
)
def test_parse_fceux_log_rejects_hand_trap_and_jet_fail_closed_events(
    tmp_path: Path, failure_event: str
) -> None:
    lines = _world_8_hand_traps_jet_lines()
    lines.append(f"frame=999 event={failure_event}")

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


@pytest.mark.parametrize(
    ("needle", "replacement"),
    [
        (
            "evidence=deliberate_A_input_from_observed_hand_tile",
            "evidence=unobserved_automatic_entry",
        ),
        ("stage_identity=world_8_hand_trap_center", "stage_identity=world_8_hand_trap_right"),
        ("leaf_after=1", "leaf_after=2"),
        ("boss_object_id_76_active=0", "boss_object_id_76_active=1"),
        ("map_page=2 map_cursor_x=64", "map_page=1 map_cursor_x=96"),
    ],
)
def test_parse_fceux_log_rejects_wrong_hand_or_jet_identity(
    tmp_path: Path, needle: str, replacement: str
) -> None:
    lines = _world_8_hand_traps_jet_lines()
    index = next(index for index, line in enumerate(lines) if needle in line)
    lines[index] = lines[index].replace(needle, replacement)

    assert _parse_lines(tmp_path, lines).post_probe_clear is False


def test_parse_fceux_log_rejects_missing_duplicate_and_reordered_trap_events(
    tmp_path: Path,
) -> None:
    original = _world_8_hand_traps_jet_lines()
    reward_index = next(
        index
        for index, line in enumerate(original)
        if "event=post_probe_world_8_hand_trap_center_reward " in line
    )
    right_entry = next(
        line
        for line in original
        if "event=post_probe_world_8_hand_trap_right_entered " in line
    )
    center_started_index = next(
        index
        for index, line in enumerate(original)
        if "event=post_probe_world_8_hand_trap_center_started" in line
    )
    right_started_index = next(
        index
        for index, line in enumerate(original)
        if "event=post_probe_world_8_hand_trap_right_started" in line
    )
    cases = [
        original[:reward_index] + original[reward_index + 1 :],
        original[:center_started_index] + [right_entry] + original[center_started_index:],
        original[:right_started_index]
        + [original[center_started_index]]
        + original[right_started_index:],
    ]

    for index, lines in enumerate(cases):
        case_dir = tmp_path / str(index)
        case_dir.mkdir()
        assert _parse_lines(case_dir, lines).post_probe_clear is False


def test_parse_fceux_log_rejects_premature_jet_and_missing_post_clear(
    tmp_path: Path,
) -> None:
    original = _world_8_hand_traps_jet_lines()
    left_started_index = next(
        index
        for index, line in enumerate(original)
        if "event=post_probe_world_8_hand_trap_left_started" in line
    )
    premature = (
        original[:left_started_index]
        + ["frame=199 event=post_probe_world_8_jet_started"]
        + original[left_started_index:]
    )
    no_post_clear = original[:-1]

    premature_dir = tmp_path / "premature"
    missing_dir = tmp_path / "missing"
    premature_dir.mkdir()
    missing_dir.mkdir()
    assert _parse_lines(premature_dir, premature).post_probe_clear is False
    assert _parse_lines(missing_dir, no_post_clear).post_probe_clear is False


def test_parse_fceux_log_accepts_exact_big_tanks_completion_sequence(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(_world_8_big_tanks_lines()))

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is True
    assert summary.post_probe_last_event == "post_probe_world_8_big_tanks_post_clear"


def test_parse_fceux_log_rejects_big_tanks_death_after_boss_disappearance(
    tmp_path: Path,
) -> None:
    lines = _world_8_big_tanks_lines()[:-2]
    lines.append(
        "frame=90 event=post_probe_world_8_big_tanks_death "
        "world_number=7 object_set=10 failure_classification=death"
    )
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False
    assert summary.post_probe_last_event == "post_probe_world_8_big_tanks_death"


def test_parse_fceux_log_rejects_big_tanks_false_clear_without_chest_proof(
    tmp_path: Path,
) -> None:
    lines = _world_8_big_tanks_lines()
    lines[-2] = (
        "frame=90 event=post_probe_world_8_big_tanks_clear "
        "world_number=7 object_set=10 evidence=enemy_disappeared"
    )
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_requires_big_tanks_milestones_in_order(
    tmp_path: Path,
) -> None:
    lines = _world_8_big_tanks_lines()
    lines[-5], lines[-4] = lines[-4], lines[-5]
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False


def test_parse_fceux_log_accepts_exact_battleships_completion_sequence(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(_world_8_battleships_lines()))

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is True
    assert summary.post_probe_last_event == "post_probe_world_8_battleships_post_clear"


@pytest.mark.parametrize(
    ("line_index", "replacement"),
    (
        (-5, "frame=120 event=post_probe_world_8_battleships_wrong_stage"),
        (
            -5,
            "frame=120 event=post_probe_world_8_battleships_entered x=24 y=368 "
            "entry_x=24 entry_y=368 entry_air=0 world_number=7 object_set=10 "
            "map_enter_via_id=12 stage_identity=world_8_battleships "
            "evidence=normal_right_right_automatic_entry_from_64_112",
        ),
        (-3, "frame=140 event=post_probe_world_8_battleships_death failure_classification=death"),
        (
            -2,
            "frame=150 event=post_probe_world_8_battleships_clear world_number=7 "
            "object_set=10 evidence=enemy_disappearance",
        ),
        (-2, "frame=150 event=post_probe_world_8_battleships_gameplay_stall"),
        (-2, "frame=150 event=post_probe_world_8_battleships_timeout"),
        (-1, "frame=160 event=post_probe_world_8_battleships_unexpected_next_stage"),
    ),
)
def test_parse_fceux_log_rejects_battleships_fail_closed_events(
    tmp_path: Path,
    line_index: int,
    replacement: str,
) -> None:
    lines = _world_8_battleships_lines()
    lines[line_index] = replacement
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    assert parse_fceux_log(log_path).post_probe_clear is False


@pytest.mark.parametrize("missing_index", (-5, -4, -2, -1))
def test_parse_fceux_log_requires_all_battleships_acceptance_events(
    tmp_path: Path,
    missing_index: int,
) -> None:
    lines = _world_8_battleships_lines()
    del lines[missing_index]
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    assert parse_fceux_log(log_path).post_probe_clear is False


def test_parse_fceux_log_rejects_battleships_event_reordering(tmp_path: Path) -> None:
    lines = _world_8_battleships_lines()
    lines[-5], lines[-4] = lines[-4], lines[-5]
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    assert parse_fceux_log(log_path).post_probe_clear is False


@pytest.mark.parametrize(
    "failure_event",
    (
        "post_probe_world_8_big_tanks_wrong_stage",
        "post_probe_world_8_big_tanks_missing_post_clear",
    ),
)
def test_parse_fceux_log_rejects_big_tanks_stage_and_post_clear_failures(
    tmp_path: Path,
    failure_event: str,
) -> None:
    lines = _world_8_big_tanks_lines()[:-1]
    lines.append(
        f"frame=100 event={failure_event} world_number=7 object_set=10"
    )
    log_path = tmp_path / "route.log"
    log_path.write_text("\n".join(lines))

    summary = parse_fceux_log(log_path)

    assert summary.post_probe_clear is False
    assert summary.post_probe_last_event == failure_event


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
