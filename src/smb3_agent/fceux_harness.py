from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


STATE_RE = re.compile(r"\battempt_(?P<attempt>\d+)_(?P<event>[A-Za-z0-9_]+)\b")
X_RE = re.compile(r"\bx=(?P<x>-?\d+)\b")
EVENT_RE = re.compile(r"\bevent=(?P<event>[A-Za-z0-9_]+)\b")


@dataclass(frozen=True)
class AttemptSummary:
    attempt: int
    success: bool
    bad_state: bool
    reached_end: bool
    goal_area: bool
    max_x: int


@dataclass(frozen=True)
class BatchSummary:
    attempts: tuple[AttemptSummary, ...]
    post_probe_max_x: int = -1
    post_probe_last_event: str | None = None
    post_probe_clear: bool = False
    post_probe_events: tuple[str, ...] = ()

    @property
    def success_count(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.success)

    @property
    def bad_state_count(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.bad_state)

    @property
    def total(self) -> int:
        return len(self.attempts)

    def to_text(self) -> str:
        lines = [
            f"successes={self.success_count}/{self.total}",
            f"bad_states={self.bad_state_count}/{self.total}",
        ]
        for attempt in self.attempts:
            lines.append(
                "attempt_{attempt}: success={success} reached_end={reached_end} "
                "goal_area={goal_area} bad_state={bad_state} max_x={max_x}".format(
                    attempt=attempt.attempt,
                    success=str(attempt.success).lower(),
                    reached_end=str(attempt.reached_end).lower(),
                    goal_area=str(attempt.goal_area).lower(),
                    bad_state=str(attempt.bad_state).lower(),
                    max_x=attempt.max_x,
                )
            )
        if self.post_probe_max_x >= 0:
            lines.append(f"post_probe_max_x={self.post_probe_max_x}")
        if self.post_probe_last_event is not None:
            lines.append(f"post_probe_last_event={self.post_probe_last_event}")
        lines.append(f"post_probe_clear={str(self.post_probe_clear).lower()}")
        return "\n".join(lines)


def parse_fceux_log(
    log_path: Path,
    expected_attempts: int | None = None,
    *,
    allow_bridges: bool = False,
) -> BatchSummary:
    text = log_path.read_text(errors="replace")
    seen_attempts: set[int] = set()
    success: set[int] = set()
    bad_state: set[int] = set()
    reached_end: set[int] = set()
    goal_area: set[int] = set()
    max_x: dict[int, int] = {}
    current_attempt: int | None = None
    post_probe_max_x = -1
    post_probe_last_event: str | None = None
    post_probe_clear = False
    post_probe_events: list[str] = []
    playback_contaminated = False
    valid_1_6_goal_card_seen = False
    valid_1_6_course_transition = False
    valid_world_1_roamer_defeat = False
    valid_world_2_first_whistle = False
    valid_warp_zone_5_6_7_tier = False
    valid_warp_zone_second_whistle = False
    valid_warp_zone_world_8_tier = False
    valid_world_8_pipe_entry = False
    valid_world_8_map_arrival = False
    valid_world_8_big_tanks_entry = False
    valid_world_8_big_tanks_gameplay = False
    valid_world_8_big_tanks_clear = False
    valid_world_8_big_tanks_post_clear = False
    valid_world_8_battleships_entry = False
    valid_world_8_battleships_gameplay = False
    valid_world_8_battleships_boss_defeated = False
    valid_world_8_battleships_clear = False
    valid_world_8_battleships_p_wing_preserved = False
    valid_world_8_battleships_star_used = False
    valid_world_8_battleships_swim = False
    valid_world_8_battleships_stern_wait = False
    battleships_sequence_failed = False
    hand_trap_sequence_index = 0
    hand_trap_sequence_failed = False
    hand_trap_state = 0
    valid_world_8_jet_entry = False
    valid_world_8_jet_p_wing_used = False
    valid_world_8_jet_gameplay = False
    valid_world_8_jet_boss_defeated = False
    valid_world_8_jet_clear = False

    for line in text.splitlines():
        event_match = EVENT_RE.search(line)
        event = event_match.group("event") if event_match is not None else None
        x_match = X_RE.search(line)
        if event is not None and event.startswith("post_probe_"):
            post_probe_events.append(event)
            post_probe_last_event = event
            if event.startswith("post_probe_1_6_opening_search") or event.startswith(
                "post_probe_1_6_segment_search"
            ):
                playback_contaminated = True
                post_probe_clear = False
            if event.startswith("post_probe_world_1_roamer_search"):
                playback_contaminated = True
                post_probe_clear = False
            if "_bridge" in event and not allow_bridges:
                playback_contaminated = True
                post_probe_clear = False
            if "_discovery_" in event:
                playback_contaminated = True
                post_probe_clear = False
            if event == "post_probe_world_1_roamer_detected":
                valid_world_1_roamer_defeat = False
                post_probe_clear = False
            if event in {
                "post_probe_world_1_roamer_life_lost",
                "post_probe_world_1_roamer_failed",
                "post_probe_world_1_roamer_fixed_attack_failed",
            }:
                valid_world_1_roamer_defeat = False
                post_probe_clear = False
            if event == "post_probe_1_6_goal_card":
                valid_1_6_goal_card_seen = (
                    "evidence=card_internal_state_nonzero" in line
                    and "form_before_clear=3" in line
                )
            if event == "post_probe_1_6_success_course_clear":
                valid_1_6_course_transition = (
                    valid_1_6_goal_card_seen
                    and "evidence=card_internal_state_then_course_transition" in line
                )
            if event == "post_probe_1_6_map_returned":
                post_probe_clear = (
                    valid_1_6_course_transition
                    and "evidence=object_set_0_after_course_transition" in line
                    and "object_set=0" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_1_roamer_defeated_in_battle":
                valid_world_1_roamer_defeat = (
                    "evidence=enemy_id_-127_removed" in line
                    and "form_after=3" in line
                    and "return_map=0" in line
                    and "item_0=12" in line
                    and "item_1=12" in line
                )
            if event == "post_probe_world_1_roamer_map_returned":
                post_probe_clear = (
                    valid_world_1_roamer_defeat
                    and "evidence=object_set_0_after_roamer_defeat" in line
                    and "object_set=0" in line
                    and "item_0=12" in line
                    and "item_1=12" in line
                    and not playback_contaminated
                )
            if event in {
                "post_probe_1_castle_no_entry",
                "post_probe_1_castle_bad_state",
                "post_probe_1_airship_boss_room_missing",
                "post_probe_world_2_whistle_inventory_mismatch",
                "post_probe_world_2_map_missing",
                "post_probe_world_2_first_whistle_missing",
                "post_probe_warp_zone_5_6_7_missing",
                "post_probe_warp_zone_second_whistle_missing",
                "post_probe_warp_zone_world_8_tier_missing",
                "post_probe_world_8_pipe_position_missing",
                "post_probe_world_8_map_missing",
                "post_probe_world_8_map_unstable",
            }:
                post_probe_clear = False
            elif event in {
                "post_probe_1_2_enter",
                "post_probe_1_3_enter",
                "post_probe_1_fortress_enter",
                "post_probe_1_5_enter",
                "post_probe_1_5_water_enter",
                "post_probe_1_6_enter",
                "post_probe_1_castle_enter",
            } or event.startswith("post_probe_1_fortress_enter_") or event.startswith(
                "post_probe_1_4_enter"
            ) or event.startswith("post_probe_1_5_enter") or event.startswith(
                "post_probe_1_5_water_enter"
            ) or event.startswith(
                "post_probe_1_6_enter"
            ) or event.startswith(
                "post_probe_1_6_level_enter"
            ) or event.startswith(
                "post_probe_1_castle_enter"
            ) or event.startswith(
                "post_probe_1_airship_enter_after_roamer"
            ):
                post_probe_clear = False
                post_probe_max_x = -1
            if event in {
                "post_probe_1_2_success_course_clear",
                "post_probe_1_3_whistle_room_success",
                "post_probe_1_fortress_whistle_room_success",
                "post_probe_1_4_success_course_clear",
                "post_probe_1_5_success_course_clear",
                "post_probe_1_5_water_success_course_clear",
                "post_probe_world_8_map_arrival",
            }:
                post_probe_clear = not playback_contaminated
            if event == "post_probe_1_airship_success_king" and allow_bridges:
                post_probe_clear = True
            if event == "post_probe_world_2_map_two_whistles":
                post_probe_clear = (
                    "evidence=world_number_1_object_set_0" in line
                    and "world_number=1" in line
                    and "object_set=0" in line
                    and "item_0=12" in line
                    and "item_1=12" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_2_first_whistle_started":
                valid_world_2_first_whistle = False
                post_probe_clear = False
            if event == "post_probe_world_2_first_whistle_used":
                valid_world_2_first_whistle = (
                    "evidence=two_to_one_whistle_after_A_input" in line
                    and "source_world=2" in line
                    and "world_number=1" in line
                )
            if event == "post_probe_warp_zone_5_6_7_tier":
                valid_warp_zone_5_6_7_tier = (
                    valid_world_2_first_whistle
                    and "evidence=warp_cursor_64_112_after_world_2_whistle" in line
                    and "world_number=8" in line
                    and "map_cursor_x=64" in line
                    and "map_cursor_y=112" in line
                )
            if event == "post_probe_warp_zone_second_whistle_started":
                valid_warp_zone_second_whistle = False
                post_probe_clear = False
            if event == "post_probe_warp_zone_second_whistle_used":
                valid_warp_zone_second_whistle = (
                    valid_world_2_first_whistle
                    and valid_warp_zone_5_6_7_tier
                    and "evidence=one_to_zero_whistles_after_A_input_from_5_6_7_tier"
                    in line
                )
            if event == "post_probe_warp_zone_world_8_tier":
                valid_warp_zone_world_8_tier = (
                    valid_warp_zone_second_whistle
                    and "evidence=warp_cursor_128_144_after_second_whistle" in line
                    and "world_number=8" in line
                    and "map_cursor_x=128" in line
                    and "map_cursor_y=144" in line
                )
            if event == "post_probe_world_8_pipe_entered":
                valid_world_8_pipe_entry = (
                    valid_warp_zone_world_8_tier
                    and "evidence=A_input_from_warp_cursor_160_144" in line
                    and "world_number=8" in line
                    and "map_cursor_x=160" in line
                    and "map_cursor_y=144" in line
                )
            if event == "post_probe_world_8_map_arrival":
                valid_world_8_map_arrival = (
                    valid_world_2_first_whistle
                    and valid_warp_zone_second_whistle
                    and valid_warp_zone_world_8_tier
                    and valid_world_8_pipe_entry
                    and "evidence=world_number_7_object_set_0_after_warp_pipe" in line
                    and "world_number=7" in line
                    and "object_set=0" in line
                    and all(f"item_{index}=12" not in line for index in range(10))
                    and not playback_contaminated
                )
                post_probe_clear = valid_world_8_map_arrival
            if event == "post_probe_world_8_big_tanks_started":
                valid_world_8_big_tanks_entry = False
                valid_world_8_big_tanks_gameplay = False
                valid_world_8_big_tanks_clear = False
                valid_world_8_big_tanks_post_clear = False
                post_probe_clear = False
            if event == "post_probe_world_8_big_tanks_entered":
                valid_world_8_big_tanks_entry = (
                    valid_world_8_map_arrival
                    and "evidence=normal_down_right_A_from_32_80" in line
                    and "stage_identity=world_8_big_tanks" in line
                    and "world_number=7" in line
                    and "object_set=10" in line
                    and "x=24" in line
                    and "y=368" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_big_tanks_gameplay":
                valid_world_8_big_tanks_gameplay = (
                    valid_world_8_big_tanks_entry
                    and "evidence=normal_autoscroll_gameplay" in line
                    and "world_number=7" in line
                    and "object_set=10" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_big_tanks_clear":
                valid_world_8_big_tanks_clear = (
                    valid_world_8_big_tanks_gameplay
                    and "evidence=treasure_chest_super_star_collected_with_game_return_flag"
                    in line
                    and "world_number=7" in line
                    and "object_set=10" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_big_tanks_post_clear":
                valid_world_8_big_tanks_post_clear = (
                    valid_world_8_big_tanks_clear
                    and "evidence=stable_world_8_map_after_game_clear" in line
                    and "world_number=7" in line
                    and "object_set=0" in line
                    and "map_cursor_x=64" in line
                    and "map_cursor_y=112" in line
                    and not playback_contaminated
                )
                post_probe_clear = valid_world_8_big_tanks_post_clear
            if event.startswith("post_probe_world_8_big_tanks_") and any(
                token in event
                for token in (
                    "_wrong_",
                    "_death",
                    "_stall",
                    "_timeout",
                    "_false_clear",
                    "_missing_post_clear",
                    "_unexpected_next_stage",
                    "_ambiguous_",
                    "_unstable_",
                )
            ):
                post_probe_clear = False
            if event == "post_probe_world_8_battleships_started":
                valid_world_8_battleships_entry = False
                valid_world_8_battleships_gameplay = False
                valid_world_8_battleships_boss_defeated = False
                valid_world_8_battleships_clear = False
                battleships_sequence_failed = not valid_world_8_big_tanks_post_clear
                post_probe_clear = False
            if event == "post_probe_world_8_battleships_p_wing_preserved":
                valid_world_8_battleships_p_wing_preserved = (
                    not battleships_sequence_failed
                    and "evidence=owner_directed_underwater_battleships_route" in line
                    and "p_wing_count=1" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_8_battleships_star_used":
                valid_world_8_battleships_star_used = (
                    valid_world_8_battleships_p_wing_preserved
                    and "evidence=normal_inventory_B_A_immediately_before_entry" in line
                    and "star_before=2" in line
                    and "star_after=1" in line
                    and "p_wing_preserved=1" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_8_battleships_swim_started":
                valid_world_8_battleships_swim = (
                    valid_world_8_battleships_star_used
                    and "evidence=normal_fall_into_reddish_water_after_exposed_first_ship" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_8_battleships_stern_wait":
                valid_world_8_battleships_stern_wait = (
                    valid_world_8_battleships_swim
                    and "evidence=waited_for_end_of_autoscroll_behind_final_ship" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_8_battleships_entered":
                valid_world_8_battleships_entry = (
                    valid_world_8_big_tanks_post_clear
                    and not battleships_sequence_failed
                    and "evidence=normal_right_right_automatic_entry_from_64_112" in line
                    and "map_node_x=128" in line
                    and "map_node_y=112" in line
                    and "stage_identity=world_8_battleships" in line
                    and "world_number=7" in line
                    and "object_set=10" in line
                    and "map_enter_via_id=13" in line
                    and "entry_x=0" in line
                    and "entry_y=320" in line
                    and "entry_air=0" in line
                    and not playback_contaminated
                )
                if not valid_world_8_battleships_entry:
                    battleships_sequence_failed = True
                post_probe_clear = False
            if event == "post_probe_world_8_battleships_gameplay":
                valid_world_8_battleships_gameplay = (
                    valid_world_8_battleships_entry
                    and not battleships_sequence_failed
                    and "evidence=normal_autoscroll_fleet_gameplay" in line
                    and "world_number=7" in line
                    and "object_set=10" in line
                    and not playback_contaminated
                )
                if not valid_world_8_battleships_gameplay:
                    battleships_sequence_failed = True
                post_probe_clear = False
            if event == "post_probe_world_8_battleships_boss_defeated":
                valid_world_8_battleships_boss_defeated = (
                    valid_world_8_battleships_gameplay
                    and not battleships_sequence_failed
                    and "evidence=game_owned_boss_object_75_to_defeated_transition_object_74" in line
                    and "mario_alive=1" in line
                    and "player_is_dying=0" in line
                    and "boss_object_id_75_active=0" in line
                    and "defeated_transition_object_id_74_active=1" in line
                    and not playback_contaminated
                )
                if not valid_world_8_battleships_boss_defeated:
                    battleships_sequence_failed = True
                post_probe_clear = False
            if event == "post_probe_world_8_battleships_clear":
                valid_world_8_battleships_clear = (
                    valid_world_8_battleships_boss_defeated
                    and not battleships_sequence_failed
                    and "evidence=game_owned_return_map_transition_after_defeated_boss_object" in line
                    and "mario_alive=1" in line
                    and "player_is_dying=0" in line
                    and "return_map=1" in line
                    and "boss_object_id_75_active=0" in line
                    and "defeated_transition_object_id_74_observed=1" in line
                    and "world_number=7" in line
                    and "object_set=10" in line
                    and not playback_contaminated
                )
                if not valid_world_8_battleships_clear:
                    battleships_sequence_failed = True
                post_probe_clear = False
            if event == "post_probe_world_8_battleships_post_clear":
                if not valid_world_8_battleships_clear:
                    battleships_sequence_failed = True
                post_probe_clear = (
                    valid_world_8_battleships_clear
                    and not battleships_sequence_failed
                    and "evidence=stable_world_8_map_after_boom_boom" in line
                    and "world_number=7" in line
                    and "object_set=0" in line
                    and "map_cursor_x=128" in line
                    and "map_cursor_y=112" in line
                    and "hand_trap_region_accessible=1" in line
                    and "hand_trap_entered=0" in line
                    and "player_is_dying=0" in line
                    and not playback_contaminated
                )
            if event.startswith("post_probe_world_8_battleships_") and any(
                token in event
                for token in (
                    "_wrong_",
                    "_death",
                    "_stall",
                    "_timeout",
                    "_false_clear",
                    "_missing_",
                    "_unexpected_next_stage",
                    "_ambiguous_",
                    "_unstable_",
                )
            ):
                battleships_sequence_failed = True
                post_probe_clear = False
            hand_trap_order = ("right", "center", "left")
            if event.startswith("post_probe_world_8_hand_trap_"):
                matched_trap = next(
                    (name for name in hand_trap_order if event.startswith(
                        f"post_probe_world_8_hand_trap_{name}_"
                    )),
                    None,
                )
                if matched_trap is not None:
                    expected_trap = (
                        hand_trap_order[hand_trap_sequence_index]
                        if hand_trap_sequence_index < len(hand_trap_order)
                        else None
                    )
                    suffix = event.removeprefix(
                        f"post_probe_world_8_hand_trap_{matched_trap}_"
                    )
                    entry_y = 368 if matched_trap == "center" else 320
                    cursor_x = {"right": 160, "center": 128, "left": 96}[
                        matched_trap
                    ]
                    gameplay_identity = {
                        "right": "brother_enemy_ids=-121,-127,-126,-122",
                        "center": "hazard_identity=lava_platforms_and_podoboos",
                        "left": "hazard_identity=broken_bridge_and_jumping_cheep_cheeps",
                    }[matched_trap]
                    if suffix == "started":
                        prefix_valid = (
                            valid_world_8_battleships_clear
                            if matched_trap == "right"
                            else hand_trap_sequence_index == hand_trap_order.index(matched_trap)
                        )
                        hand_trap_sequence_failed = (
                            hand_trap_sequence_failed
                            or matched_trap != expected_trap
                            or not prefix_valid
                        )
                        hand_trap_state = 0
                    elif suffix == "entered":
                        valid = (
                            not hand_trap_sequence_failed
                            and matched_trap == expected_trap
                            and hand_trap_state == 0
                            and "evidence=deliberate_A_input_from_observed_hand_tile" in line
                            and f"target_cursor_x={cursor_x}" in line
                            and "target_cursor_y=112" in line
                            and f"entry_y={entry_y}" in line
                            and "entry_x=24" in line
                            and "entry_air=0" in line
                            and "object_set=11" in line
                            and f"stage_identity=world_8_hand_trap_{matched_trap}" in line
                            and not playback_contaminated
                        )
                        hand_trap_sequence_failed = hand_trap_sequence_failed or not valid
                        hand_trap_state = 1 if valid else -1
                    elif suffix == "gameplay":
                        valid = hand_trap_state == 1 and gameplay_identity in line
                        hand_trap_sequence_failed = hand_trap_sequence_failed or not valid
                        hand_trap_state = 2 if valid else -1
                    elif suffix == "reward":
                        valid = (
                            hand_trap_state == 2
                            and "evidence=game_owned_reward_object_82_and_inventory_transition" in line
                            and "reward_item_id=3" in line
                            and "leaf_before=0" in line
                            and "leaf_after=1" in line
                        )
                        hand_trap_sequence_failed = hand_trap_sequence_failed or not valid
                        hand_trap_state = 3 if valid else -1
                    elif suffix == "post_clear":
                        valid = (
                            hand_trap_state == 3
                            and f"map_cursor_x={cursor_x}" in line
                            and "map_cursor_y=112" in line
                            and "world_number=7" in line
                            and "object_set=0" in line
                            and "player_is_dying=0" in line
                            and "lives_unchanged=1" in line
                            and "stable_frames=180" in line
                        )
                        hand_trap_sequence_failed = hand_trap_sequence_failed or not valid
                        if valid:
                            hand_trap_sequence_index += 1
                            hand_trap_state = 0
                        post_probe_clear = False
                    elif any(
                        token in suffix
                        for token in (
                            "wrong", "death", "timeout", "missing", "duplicate",
                            "automatic", "unexplained", "premature", "unstable",
                        )
                    ):
                        hand_trap_sequence_failed = True
                        post_probe_clear = False
            if event == "post_probe_world_8_jet_started":
                valid_world_8_jet_entry = False
                valid_world_8_jet_p_wing_used = False
                valid_world_8_jet_gameplay = False
                valid_world_8_jet_boss_defeated = False
                valid_world_8_jet_clear = False
                if hand_trap_sequence_index != 3 or hand_trap_sequence_failed:
                    hand_trap_sequence_failed = True
                post_probe_clear = False
            if event == "post_probe_world_8_jet_p_wing_used":
                valid_world_8_jet_p_wing_used = (
                    hand_trap_sequence_index == 3
                    and not hand_trap_sequence_failed
                    and valid_world_8_battleships_stern_wait
                    and "evidence=owner_directed_normal_inventory_use" in line
                    and "saved_from_battleships" in line
                    and "p_wing_remaining=0" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_8_jet_entered":
                valid_world_8_jet_entry = (
                    hand_trap_sequence_index == 3
                    and not hand_trap_sequence_failed
                    and valid_world_8_jet_p_wing_used
                    and "evidence=normal_left_up_then_game_owned_automatic_entry" in line
                    and "source_cursor_x=96" in line
                    and "source_cursor_y=112" in line
                    and "map_node_x=64" in line
                    and "map_node_y=80" in line
                    and "map_enter_via_id=15" in line
                    and "entry_x=0" in line
                    and "entry_y=320" in line
                    and "entry_air=0" in line
                    and "object_set=10" in line
                    and "stage_identity=world_8_jet" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_jet_gameplay":
                valid_world_8_jet_gameplay = (
                    valid_world_8_jet_entry
                    and "evidence=observed_pause_and_advance_autoscroller_controller" in line
                    and "pacing=hazard_wait_opening_wait_controlled_advance" in line
                    and "object_set=10" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_jet_boss_defeated":
                valid_world_8_jet_boss_defeated = (
                    valid_world_8_jet_gameplay
                    and "evidence=game_owned_boss_object_76_to_defeated_transition_object_74" in line
                    and "boss_object_id_76_active=0" in line
                    and "defeated_transition_object_id_74_active=1" in line
                    and "mario_alive=1" in line
                    and "player_is_dying=0" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_jet_clear":
                valid_world_8_jet_clear = (
                    valid_world_8_jet_boss_defeated
                    and "evidence=game_owned_return_map_transition_after_defeated_flying_boom_boom" in line
                    and "return_map=1" in line
                    and "mario_alive=1" in line
                    and "player_is_dying=0" in line
                    and not playback_contaminated
                )
                post_probe_clear = False
            if event == "post_probe_world_8_jet_post_clear":
                post_probe_clear = (
                    valid_world_8_jet_clear
                    and "evidence=stable_world_8_map_with_world_8_1_accessible" in line
                    and "world_number=7" in line
                    and "object_set=0" in line
                    and "map_page=2" in line
                    and "map_cursor_x=64" in line
                    and "map_cursor_y=112" in line
                    and "dark_area_traversed=1" in line
                    and "world_8_1_accessible=1" in line
                    and "world_8_1_entered=0" in line
                    and "stable_frames=180" in line
                    and not playback_contaminated
                )
            if event.startswith("post_probe_world_8_jet_") and any(
                token in event
                for token in (
                    "_wrong_", "_death", "_fall", "_stall", "_timeout",
                    "_false_", "_missing_", "_unexpected_", "_world_8_1_entered",
                )
            ):
                post_probe_clear = False
            if x_match is not None:
                x = int(x_match.group("x"))
                if 0 <= x < 8192:
                    post_probe_max_x = max(post_probe_max_x, x)

        state_match = STATE_RE.search(line)
        if state_match is not None:
            current_attempt = int(state_match.group("attempt"))
            attempt_event = state_match.group("event")
            seen_attempts.add(current_attempt)
            if attempt_event == "success_course_clear":
                success.add(current_attempt)
            elif attempt_event == "bad_state":
                bad_state.add(current_attempt)
            elif attempt_event == "reached_end_x":
                reached_end.add(current_attempt)
            elif attempt_event == "goal_area":
                goal_area.add(current_attempt)

        if current_attempt is not None and x_match is not None:
            x = int(x_match.group("x"))
            if 0 <= x < 8192:
                max_x[current_attempt] = max(x, max_x.get(current_attempt, -1))

    if expected_attempts is not None:
        attempts = range(1, expected_attempts + 1)
    else:
        attempts = range(1, max(seen_attempts or {0}) + 1)

    return BatchSummary(
        attempts=tuple(
            AttemptSummary(
                attempt=attempt,
                success=attempt in success,
                bad_state=attempt in bad_state,
                reached_end=attempt in reached_end,
                goal_area=attempt in goal_area,
                max_x=max_x.get(attempt, -1),
            )
            for attempt in attempts
        ),
        post_probe_max_x=post_probe_max_x,
        post_probe_last_event=post_probe_last_event,
        post_probe_clear=post_probe_clear,
        post_probe_events=tuple(post_probe_events),
    )


def run_fceux_1_1(
    *,
    game_path: Path,
    script_path: Path,
    artifacts_dir: Path,
    attempts: int,
    capture_images: bool = False,
    capture_ticks: bool = False,
    after_attempt_frames: int | None = None,
    post_1_1_probe: str | None = None,
    env_overrides: tuple[str, ...] = (),
    allow_bridges: bool = False,
    clean_product_env: bool = False,
    frame_sleep_seconds: float = 0.0,
    timeout_seconds: int | None = None,
) -> BatchSummary:
    if not game_path.is_file():
        raise FileNotFoundError(f"Local game file not found: {game_path}")

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    log_path = artifacts_dir / "fceux_1_1.log"
    stdout_path = artifacts_dir / "fceux_stdout.log"
    stderr_path = artifacts_dir / "fceux_stderr.log"
    image_dir = artifacts_dir / "images"

    env = os.environ.copy()
    if clean_product_env:
        env = {key: value for key, value in env.items() if not key.startswith("SMB3_")}
    env["SMB3_AGENT_LOG"] = str(log_path.resolve())
    env["SMB3_AGENT_ATTEMPTS"] = str(attempts)
    if frame_sleep_seconds > 0:
        env["SMB3_AGENT_FRAME_SLEEP_SECONDS"] = str(frame_sleep_seconds)
    else:
        env.pop("SMB3_AGENT_FRAME_SLEEP_SECONDS", None)
    if after_attempt_frames is not None:
        env["SMB3_AFTER_ATTEMPT_FRAMES"] = str(after_attempt_frames)
    if capture_ticks:
        env["SMB3_CAPTURE_TICKS"] = "1"
    if post_1_1_probe:
        env["SMB3_POST_1_1_PROBE"] = post_1_1_probe
    for item in env_overrides:
        key, separator, value = item.partition("=")
        if not key or separator != "=":
            raise ValueError(f"Invalid environment override: {item}")
        env[key] = value
    if capture_images:
        image_dir.mkdir(parents=True, exist_ok=True)
        env["SMB3_AGENT_IMAGE_DIR"] = str(image_dir.resolve())
    else:
        env.pop("SMB3_AGENT_IMAGE_DIR", None)

    effective_timeout = timeout_seconds or int(
        env.get("SMB3_FCEUX_TIMEOUT_SECONDS", "180")
    )
    started_at = datetime.now(timezone.utc)
    execution = {
        "started_at": started_at.isoformat(),
        "attempts": attempts,
        "fresh_process": True,
        "clean_product_env": clean_product_env,
        "frame_sleep_seconds": frame_sleep_seconds,
        "capture_images": capture_images,
        "capture_ticks": capture_ticks,
        "timeout_seconds": effective_timeout,
        "timed_out": False,
        "returncode": None,
        "launch_error": None,
    }
    execution_path = artifacts_dir / "fceux_execution.json"
    launch_error: OSError | None = None
    try:
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            completed = subprocess.run(
                [
                    "fceux",
                    "--no-config",
                    "1",
                    "--sound",
                    "0",
                    "--loadlua",
                    str(script_path.resolve()),
                    str(game_path.resolve()),
                ],
                check=False,
                env=env,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=effective_timeout,
            )
            execution["returncode"] = completed.returncode
    except subprocess.TimeoutExpired:
        execution["timed_out"] = True
    except OSError as exc:
        execution["launch_error"] = f"{type(exc).__name__}: {exc}"
        launch_error = exc
    finally:
        finished_at = datetime.now(timezone.utc)
        execution["finished_at"] = finished_at.isoformat()
        execution["elapsed_seconds"] = round(
            (finished_at - started_at).total_seconds(), 6
        )
        execution_path.write_text(
            json.dumps(execution, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if launch_error is not None:
        raise launch_error
    return parse_fceux_log(
        log_path, expected_attempts=attempts, allow_bridges=allow_bridges
    )
