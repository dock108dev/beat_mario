local log_path = os.getenv("SMB3_AGENT_LOG") or "/tmp/smb3_agent_fceux_1_1_agent.log"
local image_dir = os.getenv("SMB3_AGENT_IMAGE_DIR")
local attempts = tonumber(os.getenv("SMB3_AGENT_ATTEMPTS") or "1")
local late_gap_start = tonumber(os.getenv("SMB3_LATE_GAP_START") or "1486")
local late_gap_end = tonumber(os.getenv("SMB3_LATE_GAP_END") or "1494")
local late_gap_frames = tonumber(os.getenv("SMB3_LATE_GAP_FRAMES") or "56")
local late_gap_hold_b = os.getenv("SMB3_LATE_GAP_HOLD_B") ~= "0"
local late_gap_slow_b_frames = tonumber(os.getenv("SMB3_LATE_GAP_SLOW_B_FRAMES") or "0")
local stair_climb_frames = tonumber(os.getenv("SMB3_STAIR_CLIMB_FRAMES") or "32")
local after_attempt_frames = tonumber(os.getenv("SMB3_AFTER_ATTEMPT_FRAMES") or "180")
local capture_ticks = os.getenv("SMB3_CAPTURE_TICKS") == "1"
local post_1_1_probe = os.getenv("SMB3_POST_1_1_PROBE") or ""
local speed_mode = os.getenv("SMB3_AGENT_SPEED_MODE")
local frame_sleep_seconds = tonumber(os.getenv("SMB3_AGENT_FRAME_SLEEP_SECONDS") or "0")
local post_1_2_route_mode = os.getenv("SMB3_1_2_ROUTE_MODE") or "naive"
local post_1_2_enemy_min_dx = tonumber(os.getenv("SMB3_1_2_ENEMY_MIN_DX") or "0")
local post_1_2_enemy_max_dx = tonumber(os.getenv("SMB3_1_2_ENEMY_MAX_DX") or "95")
local post_1_2_enemy_jump_frames = tonumber(os.getenv("SMB3_1_2_ENEMY_JUMP_FRAMES") or "24")
local post_1_2_hill_enemy_jump_frames =
  tonumber(os.getenv("SMB3_1_2_HILL_ENEMY_JUMP_FRAMES") or "20")
local post_1_2_hill_enemy_start = tonumber(os.getenv("SMB3_1_2_HILL_ENEMY_START") or "1180")
local post_1_2_hill_enemy_end = tonumber(os.getenv("SMB3_1_2_HILL_ENEMY_END") or "1400")
local post_1_2_hill_search_start = tonumber(os.getenv("SMB3_1_2_HILL_SEARCH_START") or "1180")
local post_1_2_hill_delay_frames = tonumber(os.getenv("SMB3_1_2_HILL_DELAY_FRAMES") or "12")
local post_1_2_hill_jump_frames = tonumber(os.getenv("SMB3_1_2_HILL_JUMP_FRAMES") or "50")
local post_1_2_hill_slow_frames = tonumber(os.getenv("SMB3_1_2_HILL_SLOW_FRAMES") or "10")
local post_1_2_late_jump_start = tonumber(os.getenv("SMB3_1_2_LATE_JUMP_START") or "2350")
local post_1_2_late_delay_frames = tonumber(os.getenv("SMB3_1_2_LATE_DELAY_FRAMES") or "0")
local post_1_2_late_jump_frames = tonumber(os.getenv("SMB3_1_2_LATE_JUMP_FRAMES") or "18")
local post_1_2_late_slow_frames = tonumber(os.getenv("SMB3_1_2_LATE_SLOW_FRAMES") or "0")
local post_1_2_goal_jump_start = tonumber(os.getenv("SMB3_1_2_GOAL_JUMP_START") or "2580")
local post_1_2_goal_jump_frames = tonumber(os.getenv("SMB3_1_2_GOAL_JUMP_FRAMES") or "38")
local post_1_2_goal_carry_frames = tonumber(os.getenv("SMB3_1_2_GOAL_CARRY_FRAMES") or "60")
local post_1_3_route_mode = os.getenv("SMB3_1_3_ROUTE_MODE") or "whistle"
local post_1_3_hidden_door_x = tonumber(os.getenv("SMB3_1_3_HIDDEN_DOOR_X") or "2340")
local post_1_3_hidden_door_up_frames = tonumber(os.getenv("SMB3_1_3_HIDDEN_DOOR_UP_FRAMES") or "180")
local post_1_3_white_block_crouch_frames = tonumber(os.getenv("SMB3_1_3_WHITE_BLOCK_CROUCH_FRAMES") or "430")
local post_1_3_white_block_hidden_frames = tonumber(os.getenv("SMB3_1_3_WHITE_BLOCK_HIDDEN_FRAMES") or "240")
local post_1_3_white_block_brake_frames = tonumber(os.getenv("SMB3_1_3_WHITE_BLOCK_BRAKE_FRAMES") or "0")
local post_1_3_power_search_limit = tonumber(os.getenv("SMB3_1_3_POWER_SEARCH_LIMIT") or "160")
local post_1_3_white_search = os.getenv("SMB3_1_3_WHITE_SEARCH") == "1"
local post_1_3_white_search_limit = tonumber(os.getenv("SMB3_1_3_WHITE_SEARCH_LIMIT") or "180")
local post_1_3_block_clear_search = os.getenv("SMB3_1_3_BLOCK_CLEAR_SEARCH") == "1"
local post_1_3_block_clear_search_limit =
  tonumber(os.getenv("SMB3_1_3_BLOCK_CLEAR_SEARCH_LIMIT") or "400")
local post_1_3_true_white_jump_start = tonumber(os.getenv("SMB3_1_3_TRUE_WHITE_JUMP_START") or "1560")
local post_1_3_true_white_jump_end = tonumber(os.getenv("SMB3_1_3_TRUE_WHITE_JUMP_END") or "1660")
local post_1_3_true_white_jump_frames = tonumber(os.getenv("SMB3_1_3_TRUE_WHITE_JUMP_FRAMES") or "36")
local post_1_3_true_white_drift_left_frames =
  tonumber(os.getenv("SMB3_1_3_TRUE_WHITE_DRIFT_LEFT_FRAMES") or "180")
local post_1_3_true_white_pre_jump_wait_frames =
  tonumber(os.getenv("SMB3_1_3_TRUE_WHITE_PRE_JUMP_WAIT_FRAMES") or "0")
local post_1_3_after_whistle_mode = os.getenv("SMB3_1_3_AFTER_WHISTLE_MODE") or "tap_A"
local post_1_3_after_whistle_frames = tonumber(os.getenv("SMB3_1_3_AFTER_WHISTLE_FRAMES") or "720")
local post_1_3_transition_wait_frames =
  tonumber(os.getenv("SMB3_1_3_TRANSITION_WAIT_FRAMES") or "1800")
local post_1_3_max_frames = tonumber(os.getenv("SMB3_1_3_MAX_FRAMES") or "3600")
local post_1_3_left_door_x = tonumber(os.getenv("SMB3_1_3_LEFT_DOOR_X") or "24")
local post_1_3_room_center_x = tonumber(os.getenv("SMB3_1_3_ROOM_CENTER_X") or "128")
local post_1_3_room_jump_left_frames =
  tonumber(os.getenv("SMB3_1_3_ROOM_JUMP_LEFT_FRAMES") or "50")
local post_1_3_room_floor_jump_direction = os.getenv("SMB3_1_3_ROOM_FLOOR_JUMP_DIRECTION") or "right"
local post_1_3_map_sequence = os.getenv("SMB3_1_3_MAP_SEQUENCE") or "down,down,left"
post_1_fortress_map_sequence = os.getenv("SMB3_1_FORTRESS_MAP_SEQUENCE") or ""
post_1_4_map_sequence = os.getenv("SMB3_1_4_MAP_SEQUENCE") or ""
post_1_5_map_sequence = os.getenv("SMB3_1_5_MAP_SEQUENCE") or ""
post_1_5_water_map_sequence = os.getenv("SMB3_1_5_WATER_MAP_SEQUENCE") or ""
post_1_6_map_sequence = os.getenv("SMB3_1_6_MAP_SEQUENCE") or "right,right,A"
post_1_castle_map_sequence = os.getenv("SMB3_1_CASTLE_MAP_SEQUENCE") or "right,A"
post_1_castle_map_x =
  tonumber(os.getenv("SMB3_1_CASTLE_MAP_X") or "-1")
post_1_castle_map_y =
  tonumber(os.getenv("SMB3_1_CASTLE_MAP_Y") or "-1")
post_1_castle_sentinel_x =
  tonumber(os.getenv("SMB3_1_CASTLE_SENTINEL_X") or "-1")
post_1_castle_cursor_x =
  tonumber(os.getenv("SMB3_1_CASTLE_CURSOR_X") or "-1")
post_1_castle_cursor_y =
  tonumber(os.getenv("SMB3_1_CASTLE_CURSOR_Y") or "-1")
post_1_airship_object_bridge = os.getenv("SMB3_1_AIRSHIP_OBJECT_BRIDGE") == "1"
post_1_airship_object_x =
  tonumber(os.getenv("SMB3_1_AIRSHIP_OBJECT_X") or "96")
post_1_airship_object_y =
  tonumber(os.getenv("SMB3_1_AIRSHIP_OBJECT_Y") or "32")
post_1_airship_enter_via_id =
  tonumber(os.getenv("SMB3_1_AIRSHIP_ENTER_VIA_ID") or "2")
post_1_airship_bridge_clear = os.getenv("SMB3_1_AIRSHIP_BRIDGE_CLEAR") == "1"
post_1_airship_bridge_clear_wait_frames =
  tonumber(os.getenv("SMB3_1_AIRSHIP_BRIDGE_CLEAR_WAIT_FRAMES") or "180")
post_1_airship_after_clear_frames =
  tonumber(os.getenv("SMB3_1_AIRSHIP_AFTER_CLEAR_FRAMES") or "1800")
post_1_airship_stage_bridge = os.getenv("SMB3_1_AIRSHIP_STAGE_BRIDGE") == "1"
post_1_airship_stage_x =
  tonumber(os.getenv("SMB3_1_AIRSHIP_STAGE_X") or "219")
post_1_airship_stage_y =
  tonumber(os.getenv("SMB3_1_AIRSHIP_STAGE_Y") or "192")
post_1_5_water_bridge_x =
  tonumber(os.getenv("SMB3_1_5_WATER_BRIDGE_X") or "-1")
post_1_5_water_bridge_y =
  tonumber(os.getenv("SMB3_1_5_WATER_BRIDGE_Y") or "-1")
post_1_5_water_bridge_sentinel_x =
  tonumber(os.getenv("SMB3_1_5_WATER_BRIDGE_SENTINEL_X") or "-1")
post_1_5_water_bridge_cursor_x =
  tonumber(os.getenv("SMB3_1_5_WATER_BRIDGE_CURSOR_X") or "-1")
post_1_5_water_bridge_cursor_y =
  tonumber(os.getenv("SMB3_1_5_WATER_BRIDGE_CURSOR_Y") or "-1")
force_world_1_complete_flags =
  os.getenv("SMB3_WORLD1_FORCE_COMPLETE_FLAGS") == "1"
post_1_fortress_second_lava_wait_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_WAIT_FRAMES") or "24")
post_1_fortress_second_lava_backup_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_BACKUP_FRAMES") or "0")
post_1_fortress_first_lava_start = tonumber(os.getenv("SMB3_1_FORTRESS_FIRST_LAVA_START") or "250")
post_1_fortress_first_lava_end = tonumber(os.getenv("SMB3_1_FORTRESS_FIRST_LAVA_END") or "285")
post_1_fortress_first_lava_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FIRST_LAVA_JUMP_FRAMES") or "58")
post_1_fortress_second_lava_accel_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_ACCEL_FRAMES") or "6")
post_1_fortress_second_lava_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_JUMP_FRAMES") or "100")
post_1_fortress_second_lava_drift_left_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_DRIFT_LEFT_FRAMES") or "12")
post_1_fortress_second_lava_cooldown_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_COOLDOWN_FRAMES") or "105")
post_1_fortress_second_lava_stair_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_STAIR_JUMP_FRAMES") or "78")
post_1_fortress_third_lava_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_THIRD_LAVA_JUMP_FRAMES") or "88")
post_1_fortress_flat_enemy_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLAT_ENEMY_JUMP_FRAMES") or "44")
post_1_fortress_mid_hazard_run_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_RUN_FRAMES") or "60")
post_1_fortress_mid_hazard_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_JUMP_FRAMES") or "32")
post_1_fortress_mid_hazard_wait_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_WAIT_FRAMES") or "0")
post_1_fortress_mid_hazard_drift_left_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_DRIFT_LEFT_FRAMES") or "0")
post_1_fortress_mid_hazard_start = tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_START") or "1000")
post_1_fortress_mid_hazard_end = tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_END") or "1065")
post_1_fortress_mid_hazard_pre_wait_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_PRE_WAIT_FRAMES") or "0")
post_1_fortress_mid_hazard_pre_wait_start =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_PRE_WAIT_START") or "1000")
post_1_fortress_mid_hazard_pre_wait_end =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_PRE_WAIT_END") or "1060")
post_1_fortress_mid_hazard_followup_start =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_FOLLOWUP_START") or "1035")
post_1_fortress_mid_hazard_followup_end =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_FOLLOWUP_END") or "1065")
post_1_fortress_mid_hazard_followup_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_FOLLOWUP_JUMP_FRAMES") or "0")
post_1_fortress_search_limit = tonumber(os.getenv("SMB3_1_FORTRESS_SEARCH_LIMIT") or "500")
post_1_fortress_flight_backup_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_BACKUP_FRAMES") or "0")
post_1_fortress_flight_run_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_RUN_FRAMES") or "0")
post_1_fortress_flight_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_JUMP_FRAMES") or "28")
post_1_fortress_flight_flap_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_FLAP_FRAMES") or "300")
post_1_fortress_flight_flap_period =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_FLAP_PERIOD") or "6")
post_1_fortress_flight_flap_press_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_FLAP_PRESS_FRAMES") or "3")
post_1_fortress_flight_up_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_UP_FRAMES") or "120")
post_1_fortress_flight_launch_start =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_LAUNCH_START") or "1530")
post_1_fortress_flight_launch_end =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_LAUNCH_END") or "1660")
post_1_fortress_final_start_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_START_X") or "1740")
post_1_fortress_final_direct_min_p =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_DIRECT_MIN_P") or "48")
post_1_fortress_final_back_target_x =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_TARGET_X") or "1555")
post_1_fortress_final_back_jump_start_x =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_JUMP_START_X") or "1700")
post_1_fortress_final_back_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_JUMP_FRAMES") or "34")
post_1_fortress_final_back_jump_left_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_JUMP_LEFT_FRAMES") or "10")
post_1_fortress_final_run_target_x =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_RUN_TARGET_X") or "1730")
post_1_fortress_final_launch_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_LAUNCH_X") or "1700")
post_1_fortress_final_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_JUMP_FRAMES") or "28")
post_1_fortress_final_obstacle_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_OBSTACLE_JUMP_FRAMES") or "34")
post_1_fortress_final_flap_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FLAP_FRAMES") or "360")
post_1_fortress_final_flap_period =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FLAP_PERIOD") or "2")
post_1_fortress_final_flap_press_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FLAP_PRESS_FRAMES") or "1")
post_1_fortress_final_up_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_UP_FRAMES") or "360")
post_1_fortress_final_config = {
  clear_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_CLEAR_X") or "1660"),
  clear_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_CLEAR_FRAMES") or "0"),
  clear_brake_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_CLEAR_BRAKE_FRAMES") or "24"),
  clear_brake_min_speed = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_CLEAR_BRAKE_MIN_SPEED") or "-6"),
  frame_sleep_seconds = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FRAME_SLEEP_SECONDS") or "0"),
  track_stomp = os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP") ~= "0",
  track_stomp_setup_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_SETUP_X") or "1648"),
  track_stomp_spawn_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_SPAWN_X") or "1760"),
  track_stomp_object_id = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_OBJECT_ID") or "63"),
  track_stomp_cleared_object_id = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_CLEARED_OBJECT_ID") or "-98"),
  track_stomp_allow_fallback = os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_ALLOW_FALLBACK") == "1",
  track_stomp_search_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_SEARCH_MIN_DX") or "-220"),
  track_stomp_search_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_SEARCH_MAX_DX") or "220"),
  track_stomp_search_max_abs_dy = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_SEARCH_MAX_ABS_DY") or "140"),
  track_stomp_enemy_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_ENEMY_X") or "1692"),
  track_stomp_enemy_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_MIN_DX") or "-48"),
  track_stomp_enemy_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_MAX_DX") or "36"),
  track_stomp_jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_JUMP_FRAMES") or "10"),
  track_stomp_follow_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_FOLLOW_FRAMES") or "150"),
  track_stomp_debug = os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_DEBUG") == "1",
  track_stomp_debug_period = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TRACK_STOMP_DEBUG_PERIOD") or "30"),
  tail_period = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_PERIOD") or "16"),
  tail_press_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_PRESS_FRAMES") or "4"),
  tail_face_left_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_FACE_LEFT_FRAMES") or "8"),
  back_hazard_jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_HAZARD_JUMP_FRAMES") or "34"),
  back_hazard_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_HAZARD_MIN_DX") or "-72"),
  back_hazard_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_HAZARD_MAX_DX") or "-12"),
  obstacle_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_OBSTACLE_MIN_DX") or "0"),
  obstacle_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_OBSTACLE_MAX_DX") or "72"),
  stage_enemy_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STAGE_ENEMY_MIN_DX") or "0"),
  stage_enemy_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STAGE_ENEMY_MAX_DX") or "220"),
  stage_wait_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STAGE_WAIT_FRAMES") or "0"),
  stage_wait_timeout_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STAGE_WAIT_TIMEOUT_FRAMES") or "180"),
  stomp_back_start_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STOMP_BACK_START_X") or "1688"),
  stomp_retry_target_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STOMP_RETRY_TARGET_X") or "1600"),
  stomp_turn_jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STOMP_TURN_JUMP_FRAMES") or "0"),
  stomp_back_hazard_jump_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_STOMP_BACK_HAZARD_JUMP_X") or "0"),
  post_stomp_shuttle = os.getenv("SMB3_1_FORTRESS_FINAL_POST_STOMP_SHUTTLE") ~= "0",
  shuttle_first_left_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_FIRST_LEFT_X") or "1528"),
  shuttle_first_left_tolerance = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_FIRST_LEFT_TOLERANCE") or "28"),
  shuttle_right_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_RIGHT_X") or "1738"),
  shuttle_launch_left_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_LAUNCH_LEFT_X") or "1530"),
  shuttle_launch_min_p = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_LAUNCH_MIN_P") or "127"),
  shuttle_b_reset_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_B_RESET_FRAMES") or "4"),
  shuttle_jump_direction = os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_JUMP_DIRECTION") or "right",
  shuttle_flap_direction = os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_FLAP_DIRECTION") or "vertical",
  shuttle_vertical_climb_y = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_VERTICAL_CLIMB_Y") or "96"),
  shuttle_ceiling_left_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_CEILING_LEFT_FRAMES") or "55"),
  shuttle_ceiling_right_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_SHUTTLE_CEILING_RIGHT_FRAMES") or "260"),
  upper_door_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_UPPER_DOOR_X") or "1826"),
  upper_door_tolerance = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_UPPER_DOOR_TOLERANCE") or "4"),
  upper_door_wait_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_UPPER_DOOR_WAIT_FRAMES") or "120"),
  upper_door_enter_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_UPPER_DOOR_ENTER_FRAMES") or "180"),
  whistle_room_trigger_max_x = tonumber(os.getenv("SMB3_1_FORTRESS_WHISTLE_ROOM_TRIGGER_MAX_X") or "1400"),
  whistle_room_chest_x = tonumber(os.getenv("SMB3_1_FORTRESS_WHISTLE_ROOM_CHEST_X") or "1184"),
  whistle_room_chest_tolerance = tonumber(os.getenv("SMB3_1_FORTRESS_WHISTLE_ROOM_CHEST_TOLERANCE") or "8"),
  whistle_room_open_mode = os.getenv("SMB3_1_FORTRESS_WHISTLE_ROOM_OPEN_MODE") or "touch_wait",
  whistle_room_open_frames = tonumber(os.getenv("SMB3_1_FORTRESS_WHISTLE_ROOM_OPEN_FRAMES") or "480"),
  search_continuation_until_x = tonumber(os.getenv("SMB3_1_FORTRESS_SEARCH_CONTINUATION_UNTIL_X") or "1400"),
  reactive_jump_max_x = tonumber(os.getenv("SMB3_1_FORTRESS_REACTIVE_JUMP_MAX_X") or "9999"),
  reactive_jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_REACTIVE_JUMP_FRAMES") or "28"),
  initial_flight_jump_direction = os.getenv("SMB3_1_FORTRESS_INITIAL_FLIGHT_JUMP_DIRECTION") or "right",
  initial_flight_flap_direction = os.getenv("SMB3_1_FORTRESS_INITIAL_FLIGHT_FLAP_DIRECTION") or "right",
  initial_flight_ceiling_y = tonumber(os.getenv("SMB3_1_FORTRESS_INITIAL_FLIGHT_CEILING_Y") or "-999"),
  tail_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_MIN_DX") or "8"),
  tail_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_MAX_DX") or "56"),
  tail_release_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_RELEASE_FRAMES") or "4"),
  tail_swing_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_SWING_FRAMES") or "10"),
}
post_1_fortress_power_config = {
  collect_leaf = os.getenv("SMB3_1_FORTRESS_COLLECT_LEAF") ~= "0",
  start_x = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_START_X") or "1600"),
  target_x = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_TARGET_X") or "1570"),
  tolerance = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_TOLERANCE") or "4"),
  jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_JUMP_FRAMES") or "28"),
  collect_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_COLLECT_FRAMES") or "180"),
  collect_retreat_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_COLLECT_RETREAT_FRAMES") or "70"),
  defense_jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_DEFENSE_JUMP_FRAMES") or "26"),
  collect_release_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_COLLECT_RELEASE_FRAMES") or "10"),
  item_jump_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_ITEM_JUMP_FRAMES") or "24"),
  resume_frames = tonumber(os.getenv("SMB3_1_FORTRESS_LEAF_RESUME_FRAMES") or "90"),
}
post_1_fortress_max_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MAX_FRAMES") or "5200")
post_1_fortress_after_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_AFTER_FRAMES") or "900")
post_1_fortress_after_mode = os.getenv("SMB3_1_FORTRESS_AFTER_MODE") or "wait"
post_1_fortress_after_pre_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_AFTER_PRE_FRAMES") or "60")
post_1_fortress_after_press_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_AFTER_PRESS_FRAMES") or "18")
post_1_4_sixth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_SIXTH_GAP_JUMP_FRAMES") or "58")
post_1_4_seventh_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_TRIGGER_MIN_X") or "645")
post_1_4_seventh_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_TRIGGER_MAX_X") or "690")
post_1_4_seventh_gap_trigger_min_y =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_TRIGGER_MIN_Y") or "320")
post_1_4_seventh_gap_trigger_max_y =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_TRIGGER_MAX_Y") or "360")
post_1_4_seventh_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_JUMP_FRAMES") or "30")
post_1_4_seventh_gap_air_trigger =
  os.getenv("SMB3_1_4_SEVENTH_GAP_AIR_TRIGGER") == "1"
post_1_4_seventh_gap_air_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_AIR_TRIGGER_MIN_X") or "620")
post_1_4_seventh_gap_air_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_AIR_TRIGGER_MAX_X") or "650")
post_1_4_seventh_gap_air_trigger_min_y =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_AIR_TRIGGER_MIN_Y") or "335")
post_1_4_seventh_gap_air_trigger_max_y =
  tonumber(os.getenv("SMB3_1_4_SEVENTH_GAP_AIR_TRIGGER_MAX_Y") or "370")
post_1_4_eighth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_EIGHTH_GAP_JUMP_FRAMES") or "104")
post_1_4_eighth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_EIGHTH_GAP_RIGHT_FRAMES") or "8")
post_1_4_eighth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_EIGHTH_GAP_LEFT_FRAMES") or "70")
post_1_4_ninth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_NINTH_GAP_TRIGGER_MIN_X") or "805")
post_1_4_ninth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_NINTH_GAP_TRIGGER_MAX_X") or "840")
post_1_4_ninth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_NINTH_GAP_JUMP_FRAMES") or "78")
post_1_4_ninth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_NINTH_GAP_RIGHT_FRAMES") or "78")
post_1_4_ninth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_NINTH_GAP_LEFT_FRAMES") or "0")
post_1_4_tenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TENTH_GAP_TRIGGER_MIN_X") or "895")
post_1_4_tenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TENTH_GAP_TRIGGER_MAX_X") or "940")
post_1_4_tenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TENTH_GAP_JUMP_FRAMES") or "72")
post_1_4_tenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TENTH_GAP_RIGHT_FRAMES") or "72")
post_1_4_tenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_tenth_platform_ride_frames =
  tonumber(os.getenv("SMB3_1_4_TENTH_PLATFORM_RIDE_FRAMES") or "75")
post_1_4_tenth_platform_exit_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TENTH_PLATFORM_EXIT_JUMP_FRAMES") or "72")
post_1_4_tenth_platform_exit_right_frames =
  tonumber(os.getenv("SMB3_1_4_TENTH_PLATFORM_EXIT_RIGHT_FRAMES") or "72")
post_1_4_eleventh_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_ELEVENTH_GAP_TRIGGER_MIN_X") or "995")
post_1_4_eleventh_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_ELEVENTH_GAP_TRIGGER_MAX_X") or "1025")
post_1_4_eleventh_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_ELEVENTH_GAP_JUMP_FRAMES") or "78")
post_1_4_eleventh_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_ELEVENTH_GAP_RIGHT_FRAMES") or "78")
post_1_4_eleventh_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_ELEVENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_twelfth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_GAP_TRIGGER_MIN_X") or "1065")
post_1_4_twelfth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_GAP_TRIGGER_MAX_X") or "1090")
post_1_4_twelfth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_GAP_JUMP_FRAMES") or "76")
post_1_4_twelfth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_GAP_RIGHT_FRAMES") or "0")
post_1_4_twelfth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_GAP_LEFT_FRAMES") or "76")
post_1_4_twelfth_platform_ride_frames =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_PLATFORM_RIDE_FRAMES") or "45")
post_1_4_twelfth_platform_exit_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_PLATFORM_EXIT_JUMP_FRAMES") or "72")
post_1_4_twelfth_platform_exit_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWELFTH_PLATFORM_EXIT_RIGHT_FRAMES") or "72")
post_1_4_thirteenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_THIRTEENTH_GAP_TRIGGER_MIN_X") or "1048")
post_1_4_thirteenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_THIRTEENTH_GAP_TRIGGER_MAX_X") or "1085")
post_1_4_thirteenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_THIRTEENTH_GAP_JUMP_FRAMES") or "78")
post_1_4_thirteenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_THIRTEENTH_GAP_RIGHT_FRAMES") or "78")
post_1_4_thirteenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_THIRTEENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_fourteenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_FOURTEENTH_GAP_TRIGGER_MIN_X") or "1215")
post_1_4_fourteenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_FOURTEENTH_GAP_TRIGGER_MAX_X") or "1245")
post_1_4_fourteenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_FOURTEENTH_GAP_JUMP_FRAMES") or "78")
post_1_4_fourteenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_FOURTEENTH_GAP_RIGHT_FRAMES") or "78")
post_1_4_fourteenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_FOURTEENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_fourteenth_gap_wait_frames =
  tonumber(os.getenv("SMB3_1_4_FOURTEENTH_GAP_WAIT_FRAMES") or "45")
post_1_4_fifteenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_FIFTEENTH_GAP_TRIGGER_MIN_X") or "1215")
post_1_4_fifteenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_FIFTEENTH_GAP_TRIGGER_MAX_X") or "1240")
post_1_4_fifteenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_FIFTEENTH_GAP_JUMP_FRAMES") or "58")
post_1_4_fifteenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_FIFTEENTH_GAP_RIGHT_FRAMES") or "18")
post_1_4_fifteenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_FIFTEENTH_GAP_LEFT_FRAMES") or "16")
post_1_4_sixteenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_SIXTEENTH_GAP_TRIGGER_MIN_X") or "1278")
post_1_4_sixteenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_SIXTEENTH_GAP_TRIGGER_MAX_X") or "1305")
post_1_4_sixteenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_SIXTEENTH_GAP_JUMP_FRAMES") or "54")
post_1_4_sixteenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_SIXTEENTH_GAP_RIGHT_FRAMES") or "54")
post_1_4_sixteenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_SIXTEENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_seventeenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_SEVENTEENTH_GAP_TRIGGER_MIN_X") or "1348")
post_1_4_seventeenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_SEVENTEENTH_GAP_TRIGGER_MAX_X") or "1370")
post_1_4_seventeenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_SEVENTEENTH_GAP_JUMP_FRAMES") or "58")
post_1_4_seventeenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_SEVENTEENTH_GAP_RIGHT_FRAMES") or "58")
post_1_4_seventeenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_SEVENTEENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_seventeenth_gap_ride_frames =
  tonumber(os.getenv("SMB3_1_4_SEVENTEENTH_GAP_RIDE_FRAMES") or "24")
post_1_4_eighteenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_EIGHTEENTH_GAP_TRIGGER_MIN_X") or "1388")
post_1_4_eighteenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_EIGHTEENTH_GAP_TRIGGER_MAX_X") or "1418")
post_1_4_eighteenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_EIGHTEENTH_GAP_JUMP_FRAMES") or "58")
post_1_4_eighteenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_EIGHTEENTH_GAP_RIGHT_FRAMES") or "58")
post_1_4_eighteenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_EIGHTEENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_nineteenth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_NINETEENTH_GAP_TRIGGER_MIN_X") or "1426")
post_1_4_nineteenth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_NINETEENTH_GAP_TRIGGER_MAX_X") or "1450")
post_1_4_nineteenth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_NINETEENTH_GAP_JUMP_FRAMES") or "58")
post_1_4_nineteenth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_NINETEENTH_GAP_RIGHT_FRAMES") or "58")
post_1_4_nineteenth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_NINETEENTH_GAP_LEFT_FRAMES") or "0")
post_1_4_nineteenth_gap_drop_frames =
  tonumber(os.getenv("SMB3_1_4_NINETEENTH_GAP_DROP_FRAMES") or "32")
post_1_4_twentieth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWENTIETH_GAP_TRIGGER_MIN_X") or "1426")
post_1_4_twentieth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWENTIETH_GAP_TRIGGER_MAX_X") or "1450")
post_1_4_twentieth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTIETH_GAP_JUMP_FRAMES") or "58")
post_1_4_twentieth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTIETH_GAP_RIGHT_FRAMES") or "58")
post_1_4_twentieth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTIETH_GAP_LEFT_FRAMES") or "0")
post_1_4_twentyfirst_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIRST_GAP_TRIGGER_MIN_X") or "1536")
post_1_4_twentyfirst_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIRST_GAP_TRIGGER_MAX_X") or "1568")
post_1_4_twentyfirst_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIRST_GAP_JUMP_FRAMES") or "58")
post_1_4_twentyfirst_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIRST_GAP_RIGHT_FRAMES") or "0")
post_1_4_twentyfirst_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIRST_GAP_LEFT_FRAMES") or "58")
post_1_4_twentysecond_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_GAP_TRIGGER_MIN_X") or "1548")
post_1_4_twentysecond_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_GAP_TRIGGER_MAX_X") or "1585")
post_1_4_twentysecond_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_GAP_JUMP_FRAMES") or "58")
post_1_4_twentysecond_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_GAP_RIGHT_FRAMES") or "58")
post_1_4_twentysecond_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_GAP_LEFT_FRAMES") or "0")
post_1_4_twentysecond_platform_ride_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_PLATFORM_RIDE_FRAMES") or "48")
post_1_4_twentysecond_platform_exit_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_PLATFORM_EXIT_JUMP_FRAMES") or "54")
post_1_4_twentysecond_platform_exit_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_PLATFORM_EXIT_RIGHT_FRAMES") or "54")
post_1_4_twentysecond_platform_hold_a =
  tonumber(os.getenv("SMB3_1_4_TWENTYSECOND_PLATFORM_HOLD_A") or "1")
post_1_4_twentythird_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYTHIRD_GAP_TRIGGER_MIN_X") or "1738")
post_1_4_twentythird_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYTHIRD_GAP_TRIGGER_MAX_X") or "1775")
post_1_4_twentythird_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYTHIRD_GAP_JUMP_FRAMES") or "58")
post_1_4_twentythird_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYTHIRD_GAP_RIGHT_FRAMES") or "58")
post_1_4_twentythird_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYTHIRD_GAP_LEFT_FRAMES") or "0")
post_1_4_twentyfourth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_GAP_TRIGGER_MIN_X") or "1818")
post_1_4_twentyfourth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_GAP_TRIGGER_MAX_X") or "1838")
post_1_4_twentyfourth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_GAP_JUMP_FRAMES") or "108")
post_1_4_twentyfourth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_GAP_RIGHT_FRAMES") or "108")
post_1_4_twentyfourth_gap_left_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_GAP_LEFT_FRAMES") or "0")
post_1_4_twentyfourth_flutter_period =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_FLUTTER_PERIOD") or "4")
post_1_4_twentyfourth_flutter_on_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_FLUTTER_ON_FRAMES") or "3")
post_1_4_twentyfourth_initial_hold_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_INITIAL_HOLD_FRAMES") or "24")
post_1_4_twentyfourth_recovery_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_RECOVERY_FRAMES") or "0")
post_1_4_twentyfourth_tail_release_start =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_TAIL_RELEASE_START") or "30")
post_1_4_twentyfourth_tail_release_end =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_TAIL_RELEASE_END") or "24")
post_1_4_twentyfourth_post_flutter_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_POST_FLUTTER_FRAMES") or "90")
post_1_4_twentyfourth_post_tail_release_start =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_POST_TAIL_RELEASE_START") or "44")
post_1_4_twentyfourth_post_tail_release_end =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_POST_TAIL_RELEASE_END") or "38")
post_1_4_twentyfourth_post_tail_pulse_period =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_POST_TAIL_PULSE_PERIOD") or "12")
post_1_4_twentyfourth_post_tail_pulse_release_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_POST_TAIL_PULSE_RELEASE_FRAMES") or "5")
post_1_4_twentyfourth_late_brake_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_LATE_BRAKE_X") or "1890")
post_1_4_twentyfourth_late_brake_y =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_LATE_BRAKE_Y") or "360")
post_1_4_twentyfourth_late_brake_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFOURTH_LATE_BRAKE_FRAMES") or "0")
post_1_4_twentyfifth_gap_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIFTH_GAP_TRIGGER_MIN_X") or "1920")
post_1_4_twentyfifth_gap_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIFTH_GAP_TRIGGER_MAX_X") or "1934")
post_1_4_twentyfifth_gap_jump_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIFTH_GAP_JUMP_FRAMES") or "58")
post_1_4_twentyfifth_gap_right_frames =
  tonumber(os.getenv("SMB3_1_4_TWENTYFIFTH_GAP_RIGHT_FRAMES") or "58")
post_1_4_exit_pipe_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_EXIT_PIPE_TRIGGER_MIN_X") or "1948")
post_1_4_exit_pipe_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_EXIT_PIPE_TRIGGER_MAX_X") or "1992")
post_1_4_exit_pipe_trigger_max_y =
  tonumber(os.getenv("SMB3_1_4_EXIT_PIPE_TRIGGER_MAX_Y") or "336")
post_1_4_exit_pipe_align_frames =
  tonumber(os.getenv("SMB3_1_4_EXIT_PIPE_ALIGN_FRAMES") or "16")
post_1_4_exit_pipe_align_direction = os.getenv("SMB3_1_4_EXIT_PIPE_ALIGN_DIRECTION") or "left"
post_1_4_exit_pipe_hold_down_frames =
  tonumber(os.getenv("SMB3_1_4_EXIT_PIPE_HOLD_DOWN_FRAMES") or "180")
post_1_4_exit_goal_jump_trigger_min_x =
  tonumber(os.getenv("SMB3_1_4_EXIT_GOAL_JUMP_TRIGGER_MIN_X") or "320")
post_1_4_exit_goal_jump_trigger_max_x =
  tonumber(os.getenv("SMB3_1_4_EXIT_GOAL_JUMP_TRIGGER_MAX_X") or "348")
post_1_4_exit_goal_jump_frames =
  tonumber(os.getenv("SMB3_1_4_EXIT_GOAL_JUMP_FRAMES") or "46")
post_1_4_after_frames =
  tonumber(os.getenv("SMB3_1_4_AFTER_FRAMES") or "900")
post_1_5_roamer_first_jump_frames =
  tonumber(os.getenv("SMB3_1_5_ROAMER_FIRST_JUMP_FRAMES") or "28")
post_1_5_roamer_first_jump_cooldown =
  tonumber(os.getenv("SMB3_1_5_ROAMER_FIRST_JUMP_COOLDOWN") or "72")
post_1_5_roamer_platform_attack_frames =
  tonumber(os.getenv("SMB3_1_5_ROAMER_PLATFORM_ATTACK_FRAMES") or "78")
post_1_5_roamer_platform_b_release_frames =
  tonumber(os.getenv("SMB3_1_5_ROAMER_PLATFORM_B_RELEASE_FRAMES") or "8")
post_1_5_roamer_platform_direction =
  os.getenv("SMB3_1_5_ROAMER_PLATFORM_DIRECTION") or "none"
post_1_5_roamer_ground_attack_frames =
  tonumber(os.getenv("SMB3_1_5_ROAMER_GROUND_ATTACK_FRAMES") or "40")
post_1_5_roamer_ground_b_release_frames =
  tonumber(os.getenv("SMB3_1_5_ROAMER_GROUND_B_RELEASE_FRAMES") or "8")
post_1_5_roamer_under_bop_frames =
  tonumber(os.getenv("SMB3_1_5_ROAMER_UNDER_BOP_FRAMES") or "20")
post_1_5_roamer_under_bop_direction =
  os.getenv("SMB3_1_5_ROAMER_UNDER_BOP_DIRECTION") or "right"
post_1_5_water_end_pipe_trigger_x =
  tonumber(os.getenv("SMB3_1_5_WATER_END_PIPE_TRIGGER_X") or "2218")
post_1_5_water_end_pipe_brake_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_END_PIPE_BRAKE_FRAMES") or "4")
post_1_5_water_end_pipe_brake_direction =
  os.getenv("SMB3_1_5_WATER_END_PIPE_BRAKE_DIRECTION") or "left"
post_1_5_water_end_pipe_jump_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_END_PIPE_JUMP_FRAMES") or "0")
post_1_5_water_end_pipe_up_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_END_PIPE_UP_FRAMES") or "480")
post_1_5_water_end_pipe_entry_direction =
  os.getenv("SMB3_1_5_WATER_END_PIPE_ENTRY_DIRECTION") or "up"
post_1_5_water_end_pipe_entry_horizontal =
  os.getenv("SMB3_1_5_WATER_END_PIPE_ENTRY_HORIZONTAL") or "right"
post_1_5_water_end_pipe_entry_swim =
  os.getenv("SMB3_1_5_WATER_END_PIPE_ENTRY_SWIM") ~= "0"
post_1_5_water_late_hazard_brake_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_LATE_HAZARD_BRAKE_FRAMES") or "0")
post_1_5_water_late_hazard_swim_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_LATE_HAZARD_SWIM_FRAMES") or "0")
post_1_5_water_late_window_start_x =
  tonumber(os.getenv("SMB3_1_5_WATER_LATE_WINDOW_START_X") or "0")
post_1_5_water_late_window_end_x =
  tonumber(os.getenv("SMB3_1_5_WATER_LATE_WINDOW_END_X") or "1910")
post_1_5_water_late_window_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_LATE_WINDOW_FRAMES") or "0")
post_1_5_water_late_window_direction =
  os.getenv("SMB3_1_5_WATER_LATE_WINDOW_DIRECTION") or "left"
post_1_5_water_late_window_swim_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_LATE_WINDOW_SWIM_FRAMES") or "0")
post_1_5_water_swim_pulse =
  os.getenv("SMB3_1_5_WATER_SWIM_PULSE") == "1"
post_1_5_water_swim_pulse_on_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_SWIM_PULSE_ON_FRAMES") or "4")
post_1_5_water_swim_pulse_off_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_SWIM_PULSE_OFF_FRAMES") or "6")
post_1_5_water_high_guard_start_x =
  tonumber(os.getenv("SMB3_1_5_WATER_HIGH_GUARD_START_X") or "1760")
post_1_5_water_high_guard_end_x =
  tonumber(os.getenv("SMB3_1_5_WATER_HIGH_GUARD_END_X") or "1900")
post_1_5_water_high_guard_y =
  tonumber(os.getenv("SMB3_1_5_WATER_HIGH_GUARD_Y") or "120")
post_1_5_water_high_guard_frames =
  tonumber(os.getenv("SMB3_1_5_WATER_HIGH_GUARD_FRAMES") or "54")
post_1_6_start_wait_frames =
  tonumber(os.getenv("SMB3_1_6_START_WAIT_FRAMES") or "0")
post_1_6_first_jump_trigger_x =
  tonumber(os.getenv("SMB3_1_6_FIRST_JUMP_TRIGGER_X") or "76")
post_1_6_first_jump_frames =
  tonumber(os.getenv("SMB3_1_6_FIRST_JUMP_FRAMES") or "58")
post_1_6_first_jump_cooldown =
  tonumber(os.getenv("SMB3_1_6_FIRST_JUMP_COOLDOWN") or "70")
post_1_6_first_air_control =
  os.getenv("SMB3_1_6_FIRST_AIR_CONTROL") or "right"
post_1_6_first_platform_ride_frames =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_RIDE_FRAMES") or "4")
post_1_6_first_platform_ride_direction =
  os.getenv("SMB3_1_6_FIRST_PLATFORM_RIDE_DIRECTION") or "neutral"
post_1_6_first_platform_object_id =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_OBJECT_ID") or "54")
post_1_6_first_platform_detect_min_dx =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_DETECT_MIN_DX") or "-16")
post_1_6_first_platform_detect_max_dx =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_DETECT_MAX_DX") or "54")
post_1_6_first_platform_detect_max_abs_dy =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_DETECT_MAX_ABS_DY") or "120")
post_1_6_second_jump_trigger_x =
  tonumber(os.getenv("SMB3_1_6_SECOND_JUMP_TRIGGER_X") or "180")
post_1_6_second_jump_frames =
  tonumber(os.getenv("SMB3_1_6_SECOND_JUMP_FRAMES") or "62")
post_1_6_second_jump_cooldown =
  tonumber(os.getenv("SMB3_1_6_SECOND_JUMP_COOLDOWN") or "70")
post_1_6_second_jump_mode =
  os.getenv("SMB3_1_6_SECOND_JUMP_MODE") or "pulse"
post_1_6_lift_jump_min_y =
  tonumber(os.getenv("SMB3_1_6_LIFT_JUMP_MIN_Y") or "318")
post_1_6_lift_jump_max_y =
  tonumber(os.getenv("SMB3_1_6_LIFT_JUMP_MAX_Y") or "356")
post_1_6_lift_jump_frames =
  tonumber(os.getenv("SMB3_1_6_LIFT_JUMP_FRAMES") or "12")
post_1_6_lift_jump_cooldown =
  tonumber(os.getenv("SMB3_1_6_LIFT_JUMP_COOLDOWN") or "18")
post_1_6_first_lift_rhythm =
  os.getenv("SMB3_1_6_FIRST_LIFT_RHYTHM") ~= "0"
post_1_6_first_lift_rhythm_direction =
  os.getenv("SMB3_1_6_FIRST_LIFT_RHYTHM_DIRECTION") or "right"
post_1_6_first_lift_rhythm_on_frames =
  tonumber(os.getenv("SMB3_1_6_FIRST_LIFT_RHYTHM_ON_FRAMES") or "4")
post_1_6_first_lift_rhythm_off_frames =
  tonumber(os.getenv("SMB3_1_6_FIRST_LIFT_RHYTHM_OFF_FRAMES") or "8")
post_1_6_first_lift_rhythm_exit_x =
  tonumber(os.getenv("SMB3_1_6_FIRST_LIFT_RHYTHM_EXIT_X") or "360")
post_1_6_first_lift_rhythm_offset_frames =
  tonumber(os.getenv("SMB3_1_6_FIRST_LIFT_RHYTHM_OFFSET_FRAMES") or "0")
post_1_6_opening_jump_pulse =
  os.getenv("SMB3_1_6_OPENING_JUMP_PULSE") == "1"
post_1_6_first_platform_track_until_x =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_TRACK_UNTIL_X") or "0")
post_1_6_first_platform_track_min_dx =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_TRACK_MIN_DX") or "-120")
post_1_6_first_platform_track_max_dx =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_TRACK_MAX_DX") or "150")
post_1_6_first_platform_track_max_abs_dy =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_TRACK_MAX_ABS_DY") or "170")
post_1_6_first_platform_track_left_dx =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_TRACK_LEFT_DX") or "-18")
post_1_6_first_platform_track_right_dx =
  tonumber(os.getenv("SMB3_1_6_FIRST_PLATFORM_TRACK_RIGHT_DX") or "28")
post_1_6_opening_jump_grounded_only =
  os.getenv("SMB3_1_6_OPENING_JUMP_GROUNDED_ONLY") ~= "0"
post_1_6_opening_bridge_jump_min_x =
  tonumber(os.getenv("SMB3_1_6_OPENING_BRIDGE_JUMP_MIN_X") or "450")
post_1_6_opening_bridge_jump_max_x =
  tonumber(os.getenv("SMB3_1_6_OPENING_BRIDGE_JUMP_MAX_X") or "500")
post_1_6_opening_bridge_jump_frames =
  tonumber(os.getenv("SMB3_1_6_OPENING_BRIDGE_JUMP_FRAMES") or "72")
post_1_6_opening_bridge_jump_cooldown =
  tonumber(os.getenv("SMB3_1_6_OPENING_BRIDGE_JUMP_COOLDOWN") or "92")
post_1_6_opening_bridge_jump_require_grounded =
  os.getenv("SMB3_1_6_OPENING_BRIDGE_JUMP_REQUIRE_GROUNDED") ~= "0"
post_1_6_opening_exit_jump_min_x =
  tonumber(os.getenv("SMB3_1_6_OPENING_EXIT_JUMP_MIN_X") or "485")
post_1_6_opening_exit_jump_max_x =
  tonumber(os.getenv("SMB3_1_6_OPENING_EXIT_JUMP_MAX_X") or "525")
post_1_6_opening_exit_jump_min_y =
  tonumber(os.getenv("SMB3_1_6_OPENING_EXIT_JUMP_MIN_Y") or "300")
post_1_6_opening_exit_jump_max_y =
  tonumber(os.getenv("SMB3_1_6_OPENING_EXIT_JUMP_MAX_Y") or "450")
post_1_6_opening_exit_jump_frames =
  tonumber(os.getenv("SMB3_1_6_OPENING_EXIT_JUMP_FRAMES") or "58")
post_1_6_opening_exit_jump_cooldown =
  tonumber(os.getenv("SMB3_1_6_OPENING_EXIT_JUMP_COOLDOWN") or "72")
post_1_6_autoscroll_guard_start_x =
  tonumber(os.getenv("SMB3_1_6_AUTOSCROLL_GUARD_START_X") or "450")
post_1_6_autoscroll_guard_left_sx =
  tonumber(os.getenv("SMB3_1_6_AUTOSCROLL_GUARD_LEFT_SX") or "128")
post_1_6_autoscroll_guard_right_sx =
  tonumber(os.getenv("SMB3_1_6_AUTOSCROLL_GUARD_RIGHT_SX") or "188")
post_1_6_autoscroll_guard_end_x =
  tonumber(os.getenv("SMB3_1_6_AUTOSCROLL_GUARD_END_X") or "2200")
post_1_6_platform_hop_min_x =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_MIN_X") or "500")
post_1_6_platform_hop_search_min_dx =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_SEARCH_MIN_DX") or "24")
post_1_6_platform_hop_search_max_dx =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_SEARCH_MAX_DX") or "125")
post_1_6_platform_hop_search_max_abs_dy =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_SEARCH_MAX_ABS_DY") or "180")
post_1_6_platform_hop_min_dy =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_MIN_DY") or "-160")
post_1_6_platform_hop_max_dy =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_MAX_DY") or "80")
post_1_6_platform_hop_frames =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_FRAMES") or "54")
post_1_6_platform_hop_cooldown =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_COOLDOWN") or "64")
post_1_6_platform_hop_right_frames =
  tonumber(os.getenv("SMB3_1_6_PLATFORM_HOP_RIGHT_FRAMES") or "42")
post_1_6_current_platform_min_dx =
  tonumber(os.getenv("SMB3_1_6_CURRENT_PLATFORM_MIN_DX") or "-48")
post_1_6_current_platform_max_dx =
  tonumber(os.getenv("SMB3_1_6_CURRENT_PLATFORM_MAX_DX") or "48")
post_1_6_current_platform_max_abs_dy =
  tonumber(os.getenv("SMB3_1_6_CURRENT_PLATFORM_MAX_ABS_DY") or "-1")
post_1_6_current_platform_left_dx =
  tonumber(os.getenv("SMB3_1_6_CURRENT_PLATFORM_LEFT_DX") or "-12")
post_1_6_current_platform_right_dx =
  tonumber(os.getenv("SMB3_1_6_CURRENT_PLATFORM_RIGHT_DX") or "12")
post_1_6_pre_lift_jump_trigger_x =
  tonumber(os.getenv("SMB3_1_6_PRE_LIFT_JUMP_TRIGGER_X") or "0")
post_1_6_pre_lift_jump_min_y =
  tonumber(os.getenv("SMB3_1_6_PRE_LIFT_JUMP_MIN_Y") or "250")
post_1_6_pre_lift_jump_max_y =
  tonumber(os.getenv("SMB3_1_6_PRE_LIFT_JUMP_MAX_Y") or "330")
post_1_6_pre_lift_jump_frames =
  tonumber(os.getenv("SMB3_1_6_PRE_LIFT_JUMP_FRAMES") or "0")
post_1_6_pre_lift_jump_cooldown =
  tonumber(os.getenv("SMB3_1_6_PRE_LIFT_JUMP_COOLDOWN") or "0")
post_1_6_second_jump_pulse_frames =
  tonumber(os.getenv("SMB3_1_6_SECOND_JUMP_PULSE_FRAMES") or "42")
post_1_6_second_jump_pulse_on_frames =
  tonumber(os.getenv("SMB3_1_6_SECOND_JUMP_PULSE_ON_FRAMES") or "6")
post_1_6_second_jump_pulse_off_frames =
  tonumber(os.getenv("SMB3_1_6_SECOND_JUMP_PULSE_OFF_FRAMES") or "5")
post_1_6_bridge_clear =
  os.getenv("SMB3_1_6_BRIDGE_CLEAR") == "1"
post_1_6_bridge_clear_x =
  tonumber(os.getenv("SMB3_1_6_BRIDGE_CLEAR_X") or "2520")
post_1_6_bridge_clear_y =
  tonumber(os.getenv("SMB3_1_6_BRIDGE_CLEAR_Y") or "320")
local log = assert(io.open(log_path, "w"))

if speed_mode ~= nil and speed_mode ~= "" then
  FCEU.speedmode(speed_mode)
end

local held = {}

local function advance_frame()
  FCEU.frameadvance()
  if frame_sleep_seconds > 0 then
    os.execute("sleep " .. tostring(frame_sleep_seconds))
  end
end

local function mario()
  local x = memory.readbyte(0x90) + memory.readbyte(0x75) * 256
  local y = memory.readbyte(0xA2) + memory.readbyte(0x87) * 256
  local scroll_x = memory.readbyte(0xFD) + memory.readbyte(0x12) * 256
  local scroll_y = memory.readbyte(0xFC)
  return {
    x = x,
    y = y,
    sx = x - scroll_x,
    sy = y - scroll_y,
    scroll_x = scroll_x,
    scroll_y = scroll_y,
    air = memory.readbyte(0xD8),
  }
end

function write_mario_position(x, y)
  memory.writebyte(0x90, x % 256)
  memory.writebyte(0x75, math.floor(x / 256))
  memory.writebyte(0xA2, y % 256)
  memory.writebyte(0x87, math.floor(y / 256))
end

function write_map_sentinel_position(x)
  memory.writebyte(0x90, x % 256)
  memory.writebyte(0x75, math.floor(x / 256))
  memory.writebyte(0xFD, x % 256)
  memory.writebyte(0x12, math.floor(x / 256))
  memory.writebyte(0xA2, 0)
  memory.writebyte(0x87, 0)
  memory.writebyte(0xFC, 17)
end

function apply_castle_map_position_bridge()
  if post_1_castle_map_x < 0 or post_1_castle_map_y < 0 then
    return false
  end
  write_map_position(post_1_castle_map_x, post_1_castle_map_y)
  if post_1_castle_sentinel_x >= 0 then
    write_map_sentinel_position(post_1_castle_sentinel_x)
  end
  if post_1_castle_cursor_x >= 0 and post_1_castle_cursor_y >= 0 then
    write_map_cursor_position(post_1_castle_cursor_x, post_1_castle_cursor_y)
  end
  return true
end

function write_map_position(x, y)
  memory.writebyte(0x7976, y)
  memory.writebyte(0x7978, math.floor(x / 256))
  memory.writebyte(0x797A, x % 256)
  memory.writebyte(0x797E, y)
  memory.writebyte(0x7980, math.floor(x / 256))
  memory.writebyte(0x7982, x % 256)
end

function write_map_cursor_position(x, y)
  memory.writebyte(0x77, math.floor(x / 256))
  memory.writebyte(0x79, x % 256)
  memory.writebyte(0x75, y)
  memory.writebyte(0x90, x % 256)
  memory.writebyte(0xA2, y)
end

function apply_airship_object_bridge()
  if not post_1_airship_object_bridge then
    return false
  end
  local slot = 1
  local x_hi = math.floor(post_1_airship_object_x / 256)
  local x_lo = post_1_airship_object_x % 256
  memory.writebyte(0x7EEC, post_1_airship_object_y)
  memory.writebyte(0x7EFA, x_lo)
  memory.writebyte(0x7F08, x_hi)
  memory.writebyte(0x7F16, 2)
  memory.writebyte(0x0501, post_1_airship_object_y)
  memory.writebyte(0x0510, x_lo)
  memory.writebyte(0x051F, x_hi)
  memory.writebyte(0x052E, 0)
  memory.writebyte(0x053D, 0)
  memory.writebyte(0x0588, 1)
  memory.writebyte(0x1E, post_1_airship_enter_via_id)
  memory.writebyte(0x20, 0)
  memory.writebyte(0x0709, 0)
  memory.writebyte(0x0728, 0)
  memory.writebyte(0x0729, 0x0D)
  memory.writebyte(0x7F2D, 0)
  write_map_cursor_position(post_1_airship_object_x, post_1_airship_object_y)
  return true
end

function apply_1_5_water_map_position_bridge()
  if post_1_5_water_bridge_x < 0 or post_1_5_water_bridge_y < 0 then
    return false
  end
  write_map_position(post_1_5_water_bridge_x, post_1_5_water_bridge_y)
  if post_1_5_water_bridge_sentinel_x >= 0 then
    write_map_sentinel_position(post_1_5_water_bridge_sentinel_x)
  end
  if post_1_5_water_bridge_cursor_x >= 0 and post_1_5_water_bridge_cursor_y >= 0 then
    write_map_cursor_position(post_1_5_water_bridge_cursor_x, post_1_5_water_bridge_cursor_y)
  end
  return true
end

function apply_world_1_complete_flags_bridge()
  if not force_world_1_complete_flags then
    return false
  end
  for offset = 0, 15 do
    memory.writebyte(0x7D00 + offset, 0xFF)
  end
  return true
end

function apply_airship_clear_bridge()
  if not post_1_airship_bridge_clear then
    return false
  end
  if memory.readbyte(0x70A) ~= 10 then
    return false
  end
  memory.writebyte(0x073C, 1)
  memory.writebyte(0x0014, 1)
  return true
end

function apply_airship_stage_bridge()
  if not post_1_airship_stage_bridge then
    return false
  end
  memory.writebyte(0x70A, 10)
  memory.writebyte(0x0588, 0)
  memory.writebyte(0x0014, 0)
  memory.writebyte(0x0578, 0)
  write_mario_position(post_1_airship_stage_x, post_1_airship_stage_y)
  memory.writebyte(0xFD, math.max(0, post_1_airship_stage_x - 16) % 256)
  memory.writebyte(0x12, math.floor(math.max(0, post_1_airship_stage_x - 16) / 256))
  memory.writebyte(0xFC, math.max(0, post_1_airship_stage_y - 80) % 256)
  held.A = false
  held.B = false
  held.left = false
  held.right = false
  held.down = false
  held.up = false
  return true
end

local function nearest_enemy_ahead(m)
  local best = nil
  for i = 1, 9 do
    local active = memory.readbytesigned(0x660 + i) ~= 0
    if active then
      local ex = memory.readbyte(0x90 + i) + memory.readbyte(0x75 + i) * 256
      local ey = memory.readbyte(0xA2 + i) + memory.readbyte(0x87 + i) * 256
      local dx = ex - m.x
      if dx >= -8 and dx < 120 and math.abs(ey - m.y) < 120 then
        if best == nil or dx < best.dx then
          best = {slot = i, x = ex, y = ey, dx = dx, dy = ey - m.y, id = memory.readbytesigned(0x670 + i)}
        end
      end
    end
  end
  return best
end

local function nearest_enemy_between(m, min_dx, max_dx)
  local best = nil
  for i = 1, 9 do
    local active = memory.readbytesigned(0x660 + i) ~= 0
    if active then
      local ex = memory.readbyte(0x90 + i) + memory.readbyte(0x75 + i) * 256
      local ey = memory.readbyte(0xA2 + i) + memory.readbyte(0x87 + i) * 256
      local dx = ex - m.x
      if dx >= min_dx and dx <= max_dx and math.abs(ey - m.y) < 120 then
        if best == nil or math.abs(dx) < math.abs(best.dx) then
          best = {slot = i, x = ex, y = ey, dx = dx, dy = ey - m.y, id = memory.readbytesigned(0x670 + i)}
        end
      end
    end
  end
  return best
end

local function has_active_enemy_id(target_id)
  for i = 1, 9 do
    local active = memory.readbytesigned(0x660 + i) ~= 0
    if active and memory.readbytesigned(0x670 + i) == target_id then
      return true
    end
  end
  return false
end

local function inventory_has_item(item_id)
  for i = 0, 27 do
    if memory.readbyte(0x7D80 + i) == item_id then
      return true
    end
  end
  return false
end

function nearest_object_id_between(m, target_id, min_dx, max_dx, max_abs_dy)
  local best = nil
  for i = 1, 9 do
    local active = memory.readbytesigned(0x660 + i) ~= 0
    if active and memory.readbytesigned(0x670 + i) == target_id then
      local ex = memory.readbyte(0x90 + i) + memory.readbyte(0x75 + i) * 256
      local ey = memory.readbyte(0xA2 + i) + memory.readbyte(0x87 + i) * 256
      local dx = ex - m.x
      local dy = ey - m.y
      if dx >= min_dx and dx <= max_dx and math.abs(dy) <= max_abs_dy then
        if best == nil or math.abs(dx) < math.abs(best.dx) then
          best = {slot = i, x = ex, y = ey, dx = dx, dy = dy, id = target_id}
        end
      end
    end
  end
  return best
end

function object_summary_between(m, min_dx, max_dx, max_abs_dy)
  local objects = {}
  for i = 1, 9 do
    local active = memory.readbytesigned(0x660 + i) ~= 0
    if active then
      local ex = memory.readbyte(0x90 + i) + memory.readbyte(0x75 + i) * 256
      local ey = memory.readbyte(0xA2 + i) + memory.readbyte(0x87 + i) * 256
      local dx = ex - m.x
      local dy = ey - m.y
      if dx >= min_dx and dx <= max_dx and math.abs(dy) <= max_abs_dy then
        objects[#objects + 1] = "s" .. tostring(i)
          .. ":id" .. tostring(memory.readbytesigned(0x670 + i))
          .. ":dx" .. tostring(dx)
          .. ":dy" .. tostring(dy)
          .. ":x" .. tostring(ex)
          .. ":y" .. tostring(ey)
      end
    end
  end
  if #objects == 0 then
    return "objects=none"
  end
  return "objects=" .. table.concat(objects, ",")
end

local function has_flight_form()
  local form = memory.readbyte(0xED)
  return form == 3 or form == 5
end


local function log_state(event, extra)
  local m = mario()
  local enemy = nearest_enemy_ahead(m)
  local parts = {
    "frame=" .. tostring(movie.framecount()),
    "event=" .. tostring(event),
    "x=" .. tostring(m.x),
    "y=" .. tostring(m.y),
    "sx=" .. tostring(m.sx),
    "sy=" .. tostring(m.sy),
    "air=" .. tostring(m.air),
    "form=" .. tostring(memory.readbyte(0xED)),
    "x_speed=" .. tostring(memory.readbytesigned(0xBD)),
    "p_meter=" .. tostring(memory.readbyte(0x3DD)),
    "duck=" .. tostring(memory.readbytesigned(0x56F)),
    "white_duck_frames=" .. tostring(memory.readbyte(0x570)),
    "backstage=" .. tostring(memory.readbyte(0x588)),
    "return_map=" .. tostring(memory.readbyte(0x14)),
    "flight_timer=" .. tostring(memory.readbyte(0x56E)),
    "flight_flag=" .. tostring(memory.readbyte(0x57B)),
    "change_form=" .. tostring(memory.readbyte(0x578)),
    "object_set=" .. tostring(memory.readbyte(0x70A)),
    "map_cursor_x=" .. tostring(memory.readbyte(0x79)),
    "map_cursor_y=" .. tostring(memory.readbyte(0x75)),
    "map_page=" .. tostring(memory.readbyte(0x77)),
    "map_enter_via_id=" .. tostring(memory.readbyte(0x1E)),
    "map_obj1_id=" .. tostring(memory.readbyte(0x7F16)),
    "map_obj1_y=" .. tostring(memory.readbyte(0x7EEC)),
    "map_obj1_x_hi=" .. tostring(memory.readbyte(0x7F08)),
    "map_obj1_x_lo=" .. tostring(memory.readbyte(0x7EFA)),
    "map_obj1_act_y=" .. tostring(memory.readbyte(0x0501)),
    "map_obj1_act_x_hi=" .. tostring(memory.readbyte(0x051F)),
    "map_obj1_act_x_lo=" .. tostring(memory.readbyte(0x0510)),
    "map_y=" .. tostring(memory.readbyte(0x7976)),
    "map_x_hi=" .. tostring(memory.readbyte(0x7978)),
    "map_x_lo=" .. tostring(memory.readbyte(0x797A)),
    "map_return_y=" .. tostring(memory.readbyte(0x797E)),
    "map_return_x_hi=" .. tostring(memory.readbyte(0x7980)),
    "map_return_x_lo=" .. tostring(memory.readbyte(0x7982)),
    "item_0=" .. tostring(memory.readbyte(0x7D80)),
    "item_1=" .. tostring(memory.readbyte(0x7D81)),
    "item_2=" .. tostring(memory.readbyte(0x7D82)),
    "item_3=" .. tostring(memory.readbyte(0x7D83)),
    "item_4=" .. tostring(memory.readbyte(0x7D84)),
    "item_5=" .. tostring(memory.readbyte(0x7D85)),
    "item_6=" .. tostring(memory.readbyte(0x7D86)),
    "item_7=" .. tostring(memory.readbyte(0x7D87)),
    "item_8=" .. tostring(memory.readbyte(0x7D88)),
    "item_9=" .. tostring(memory.readbyte(0x7D89)),
    "complete_0=" .. tostring(memory.readbyte(0x7D00)),
    "complete_1=" .. tostring(memory.readbyte(0x7D01)),
    "complete_2=" .. tostring(memory.readbyte(0x7D02)),
    "complete_3=" .. tostring(memory.readbyte(0x7D03)),
    "hold_A=" .. tostring(held.A and 1 or 0),
    "hold_B=" .. tostring(held.B and 1 or 0),
    "hold_left=" .. tostring(held.left and 1 or 0),
    "hold_right=" .. tostring(held.right and 1 or 0),
    "hold_down=" .. tostring(held.down and 1 or 0),
  }
  if enemy ~= nil then
    parts[#parts + 1] = "enemy_dx=" .. tostring(enemy.dx)
    parts[#parts + 1] = "enemy_dy=" .. tostring(enemy.dy)
    parts[#parts + 1] = "enemy_id=" .. tostring(enemy.id)
  end
  if extra ~= nil then
    parts[#parts + 1] = tostring(extra)
  end
  log:write(table.concat(parts, " ") .. "\n")
  log:flush()
  if image_dir ~= nil and (
    string.find(event, "bad_state")
    or string.find(event, "reached_end")
    or string.find(event, "jump_")
    or string.find(event, "post_")
    or (capture_ticks and event == "tick")
    or (event == "agent_tick" and m.x > 1200)
  ) then
    local safe_event = string.gsub(event, "[^A-Za-z0-9_%-]", "_")
    local path = image_dir .. "/" .. string.format("%06d_%s.gd", movie.framecount(), safe_event)
    local screenshot = gui.gdscreenshot()
    local handle = io.open(path, "wb")
    if handle ~= nil then
      handle:write(screenshot)
      handle:close()
    end
  end
end

local function apply()
  joypad.set(1, {
    up = held.up,
    down = held.down,
    left = held.left,
    right = held.right,
    A = held.A,
    B = held.B,
    start = held.start,
    select = held.select,
  })
end

local function advance(frames, event)
  for i = 1, frames do
    apply()
    if event ~= nil and i == 1 then
      log_state(event)
    elseif movie.framecount() % 30 == 0 then
      log_state("tick")
    end
    advance_frame()
  end
end

local function press(button, frames, event)
  held[button] = true
  advance(frames, event or ("press_" .. button))
  held[button] = false
  advance(1, "release_" .. button)
end

local function press_combo(buttons, frames, event)
  for button in string.gmatch(buttons, "[^%+]+") do
    held[button] = true
  end
  advance(frames, event or ("press_" .. buttons))
  for button in string.gmatch(buttons, "[^%+]+") do
    held[button] = false
  end
  advance(1, "release_" .. buttons)
end

local function bootstrap_to_level()
  FCEU.speedmode("maximum")
  advance(150, "boot_wait")
  press("start", 18, "title_start")
  advance(150, "title_to_menu")
  press("start", 18, "menu_start")
  advance(300, "map_wait")
  press("right", 18, "map_right")
  advance(36, "map_after_right")
  press("up", 18, "map_up")
  advance(36, "map_after_up")
  press("A", 18, "map_enter")
  advance(150, "level_wait")
  log_state("level_checkpoint")
end

local function in_window(x, ranges)
  for _, range in ipairs(ranges) do
    if x >= range[1] and x <= range[2] then
      return true
    end
  end
  return false
end

local scheduled_jumps = {
  {70, 145},
  {230, 310},
  {390, 470},
  {590, 680},
  {820, 900},
  {1080, 1180},
  {1320, 1430},
  {1640, 1740},
  {1950, 2100},
  {2300, 2460},
}

local function run_agent(attempt)
  local jump_frames = 0
  local jump_hold_b = true
  local slow_b_frames = 0
  local cooldown = 0
  local plant_wait_frames = 0
  local last_x = 0
  local stuck_frames = 0
  local reached_end_area = false
  local reached_goal_area = false
  local course_clear = false
  held.right = true
  held.B = true
  for frame = 1, 3600 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0
    local should_jump = false
    local reason = nil

    if m.x > 2500 and m.x < 8192 and not reached_end_area then
      log_state("attempt_" .. tostring(attempt) .. "_reached_end_x")
      reached_end_area = true
    end

    if m.x > 2800 and m.x < 8192 and not reached_goal_area then
      log_state("attempt_" .. tostring(attempt) .. "_goal_area")
      reached_goal_area = true
    end

    if m.x >= 8192 or m.y == 0 then
      if reached_goal_area then
        log_state("attempt_" .. tostring(attempt) .. "_success_course_clear")
        course_clear = true
      else
        log_state("attempt_" .. tostring(attempt) .. "_bad_state")
      end
      break
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 and m.x < 2400 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if jump_frames > 0 then
      held.right = true
      held.B = jump_hold_b
      held.A = true
      jump_frames = jump_frames - 1
      apply()
      if frame % 30 == 0 or (m.x > 1450 and frame % 10 == 0) then
        log_state("agent_tick")
      end
      advance_frame()
    elseif enemy ~= nil and (
      (grounded and enemy.id == -90 and enemy.dx >= 0 and enemy.dx < 45 and m.x >= 300 and m.x <= 380)
      or (enemy.id == -92 and enemy.dx >= 0 and enemy.dx < 55 and m.x >= 1800 and m.x <= 1900)
    ) then
      plant_wait_frames = plant_wait_frames + 1
      if enemy.id == -92 and plant_wait_frames < 45 then
        held.left = true
      else
        held.left = false
      end
      held.right = false
      held.B = false
      held.A = false
      if plant_wait_frames % 30 == 1 then
        log_state("wait_plant")
      end
      local plant_wait_limit = 105
      if enemy.id == -92 then
        plant_wait_limit = 155
      end
      if plant_wait_frames > plant_wait_limit then
        held.left = false
        held.right = true
        held.B = true
        if enemy.id == -92 then
          jump_frames = 42
        else
          jump_frames = 24
        end
        jump_hold_b = true
        cooldown = 45
        plant_wait_frames = 0
        log_state("jump_after_plant_wait")
      end
      apply()
      advance_frame()
    else
      held.right = true
      if slow_b_frames > 0 then
        held.B = false
        slow_b_frames = slow_b_frames - 1
      else
        held.B = true
      end
      held.A = false

      if cooldown > 0 then
        cooldown = cooldown - 1
      end

      if (grounded or (m.y >= 380 and m.y < 410)) and m.x >= late_gap_start and m.x <= late_gap_end then
        should_jump = true
        reason = "late_gap"
        cooldown = 0
      elseif grounded and enemy ~= nil and enemy.id ~= -90 and enemy.dy > -20 and enemy.dx >= 0 and enemy.dx < 45 then
        should_jump = true
        reason = "enemy_urgent"
        cooldown = 0
      elseif grounded and m.x >= 1000 and m.x <= 1080 then
        should_jump = true
        reason = "pit"
        cooldown = 0
      elseif cooldown == 0 and grounded and m.y >= 360 and m.y < 390 and m.x >= 1640 and m.x <= 1690 then
        should_jump = true
        reason = "stairs_gap"
        cooldown = 0
      elseif cooldown == 0 and grounded and m.y >= 350 and m.y < 390 and m.x >= 1545 and m.x <= 1605 then
        should_jump = true
        reason = "stair_climb"
        cooldown = 0
      elseif (grounded or (m.y >= 330 and m.y < 390)) and m.x >= 2180 and m.x <= 2240 then
        should_jump = true
        reason = "late_block"
        cooldown = 0
      elseif grounded and m.x >= 2580 and m.x <= 2700 then
        should_jump = true
        reason = "goal_box"
        cooldown = 0
      elseif grounded and stuck_frames > 45 and cooldown == 0 then
        should_jump = true
        reason = "stuck"
        stuck_frames = 0
      elseif grounded and cooldown == 0 then
        if enemy ~= nil and enemy.dy > -20 and enemy.dx < 90 then
          should_jump = true
          reason = "enemy"
        elseif in_window(m.x, scheduled_jumps) then
          should_jump = true
          reason = "scheduled"
        end
      end

      if should_jump then
        if reason == "pit" then
          jump_frames = 32
          cooldown = 58
          jump_hold_b = true
        elseif reason == "ledge" then
          jump_frames = 42
          cooldown = 18
          jump_hold_b = true
        elseif reason == "late_gap" then
          jump_frames = late_gap_frames
          cooldown = 0
          jump_hold_b = late_gap_hold_b
          slow_b_frames = late_gap_slow_b_frames
        elseif reason == "stair_climb" then
          jump_frames = stair_climb_frames
          cooldown = 22
          jump_hold_b = false
        elseif reason == "late_block" then
          jump_frames = 38
          cooldown = 36
          jump_hold_b = true
        elseif reason == "goal_box" then
          jump_frames = 34
          cooldown = 48
          jump_hold_b = true
        elseif reason == "stairs_gap" then
          jump_frames = 30
          cooldown = 32
          jump_hold_b = true
        else
          jump_frames = 18
          cooldown = 34
          jump_hold_b = true
        end
        log_state("jump_" .. tostring(reason))
      end

      apply()
      if frame % 30 == 0 then
        log_state("agent_tick")
      end
      advance_frame()
    end
  end
  held.A = false
  held.B = false
  held.right = false
  apply()
  advance(after_attempt_frames, "attempt_" .. tostring(attempt) .. "_after")
  log_state("attempt_" .. tostring(attempt) .. "_done")
  return course_clear
end

local function enter_1_2_from_map(after_enter_frames)
  log_state("post_probe_enter_1_2_start")
  advance(120, "post_probe_map_wait")
  press("right", 18, "post_probe_map_right_1")
  advance(60, "post_probe_after_right_1")
  press("right", 18, "post_probe_map_right_2")
  advance(60, "post_probe_after_right_2")
  press("A", 18, "post_probe_map_enter")
  advance(after_enter_frames, "post_probe_after_enter")
  log_state("post_probe_enter_1_2_done")
end

local function enter_1_3_from_map(after_enter_frames)
  log_state("post_probe_enter_1_3_start")
  advance(420, "post_probe_after_1_2_map_wait")
  press("right", 18, "post_probe_map_right_to_1_3")
  advance(60, "post_probe_after_right_to_1_3")
  press("A", 18, "post_probe_map_enter_1_3")
  advance(after_enter_frames, "post_probe_after_enter_1_3")
  log_state("post_probe_enter_1_3_done")
end

local function run_map_sequence(sequence, event_prefix)
  local step = 0
  local persist_airship =
    post_1_airship_object_bridge and string.find(event_prefix, "post_probe_1_castle_enter", 1, true) ~= nil

  local function map_advance(frames, event)
    if not persist_airship then
      advance(frames, event)
      return
    end
    for i = 1, frames do
      if type(apply_airship_object_bridge) == "function" then
        apply_airship_object_bridge()
      end
      apply()
      if event ~= nil and i == 1 then
        log_state(event)
      elseif movie.framecount() % 30 == 0 then
        log_state("tick")
      end
      advance_frame()
    end
  end

  local function map_press(button, frames, event)
    held[button] = true
    map_advance(frames, event or ("press_" .. button))
    held[button] = false
    map_advance(1, "release_" .. button)
  end

  local function map_press_combo(buttons, frames, event)
    for button in string.gmatch(buttons, "[^%+]+") do
      held[button] = true
    end
    map_advance(frames, event or ("press_" .. buttons))
    for button in string.gmatch(buttons, "[^%+]+") do
      held[button] = false
    end
    map_advance(1, "release_" .. buttons)
  end

  map_advance(180, event_prefix .. "_wait")
  for token in string.gmatch(sequence, "[^,]+") do
    step = step + 1
    local button = string.gsub(token, "^%s*(.-)%s*$", "%1")
    local combo_name, combo_frames = string.match(button, "^([A-Za-z_%+]+):(%d+)$")
    local button_name, button_frames = string.match(button, "^([A-Za-z_]+):(%d+)$")
    if button == "wait" then
      map_advance(60, event_prefix .. "_wait_" .. tostring(step))
    elseif combo_name ~= nil and string.find(combo_name, "%+") then
      map_press_combo(combo_name, tonumber(combo_frames), event_prefix .. "_" .. tostring(step) .. "_" .. combo_name)
      map_advance(60, event_prefix .. "_after_" .. tostring(step) .. "_" .. combo_name)
    elseif button_name ~= nil then
      map_press(button_name, tonumber(button_frames), event_prefix .. "_" .. tostring(step) .. "_" .. button_name)
      map_advance(60, event_prefix .. "_after_" .. tostring(step) .. "_" .. button_name)
    elseif button ~= "" then
      map_press(button, 18, event_prefix .. "_" .. tostring(step) .. "_" .. button)
      map_advance(60, event_prefix .. "_after_" .. tostring(step) .. "_" .. button)
    end
  end
  map_advance(240, event_prefix .. "_done_wait")
  log_state(event_prefix .. "_done")
end

local function navigate_1_3_to_castle()
  log_state("post_probe_1_3_to_castle_start")
  run_map_sequence(post_1_3_map_sequence, "post_probe_1_3_to_castle")
end

local function apply_pre_fortress_entry_form()
  local entry_form = tonumber(os.getenv("SMB3_1_FORTRESS_ENTRY_FORM") or "-1")
  if entry_form >= 0 then
    memory.writebyte(0xED, entry_form)
    log_state("post_probe_1_fortress_entry_form", "entry_form=" .. tostring(entry_form))
  end
end

local function apply_1_4_entry_form()
  local entry_form = tonumber(os.getenv("SMB3_1_4_ENTRY_FORM") or "-1")
  if entry_form >= 0 then
    memory.writebyte(0xED, entry_form)
    log_state("post_probe_1_4_entry_form", "entry_form=" .. tostring(entry_form))
  end
end

local function apply_fortress_whistle_bridge()
  if os.getenv("SMB3_1_FORTRESS_BRIDGE_SECOND_WHISTLE") ~= "1" then
    return
  end
  if not inventory_has_item(12) then
    memory.writebyte(0x7D80, 12)
  end
  if memory.readbyte(0x7D81) ~= 12 then
    memory.writebyte(0x7D81, 12)
  end
  log_state("post_probe_1_fortress_bridge_second_whistle")
  if os.getenv("SMB3_1_FORTRESS_BRIDGE_CLEAR_MAP") == "1" then
    write_map_position(96, 96)
    write_map_sentinel_position(24576)
    local bridge_form = tonumber(os.getenv("SMB3_1_FORTRESS_BRIDGE_CLEAR_FORM") or "-1")
    if bridge_form >= 0 then
      memory.writebyte(0xED, bridge_form)
    end
    log_state("post_probe_1_fortress_bridge_clear_map", "map_x=96 map_y=96")
  end
end

local function run_1_fortress_probe()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 256
  local first_lava_jump_started = false
  local second_lava_jump_started = false
  local second_lava_stair_jump_started = false
  local search_continuation_logged = false
  local third_lava_jump_started = false
  local flat_enemy_jump_started = false
  local mid_hazard_pre_wait_started = false
  local mid_hazard_jump_started = false
  local mid_hazard_followup_jump_started = false
  local second_lava_wait_frames = 0
  local second_lava_backup_frames = 0
  local second_lava_accel_frames = 0
  local second_lava_drift_left_frames = 0
  local mid_hazard_pre_wait_frames = 0
  local mid_hazard_run_frames = 0
  local mid_hazard_wait_frames = 0
  local flight_started = false
  local flight_backup_frames = 0
  local flight_run_frames = 0
  local flight_jump_frames = 0
  local flight_flap_frames = 0
  local flight_up_frames = 0
  local final_phase = ""
  local final_clear_done = post_1_fortress_final_config.clear_frames <= 0
  local final_clear_frames = 0
  local final_clear_brake_frames = 0
  local final_back_jump_frames = 0
  local final_back_jump_left_frames = 0
  local final_back_jump_used = false
  local final_back_target_override = nil
  local final_back_hazard_jump_frames = 0
  local final_back_hazard_jump_used = false
  local final_obstacle_jump_used = false
  local final_obstacle_jump_frames = 0
  local final_dry_bones_cleared = false
  local final_tail_used = false
  local final_tail_release_frames = 0
  local final_tail_swing_frames = 0
  local final_jump_frames = 0
  local final_flap_frames = 0
  local final_up_frames = 0
  local final_ceiling_left_frames = 0
  local final_ceiling_right_frames = 0
  local final_upper_door_wait_frames = 0
  local final_upper_door_enter_frames = 0
  local final_whistle_room_open_frames = 0
  local final_stomp_back_used = false
  local final_stomp_turn_jump_frames = 0
  local final_stage_wait_used = false
  local final_stage_wait_frames = 0
  local final_stage_wait_timeout_frames = 0
  local final_track_stomp = {
    used = false,
    jump_frames = 0,
    follow_frames = 0,
    jumped = false,
    jump_left = false,
    launch_left = false,
    debug_frames = 0,
  }
  local final_shuttle_b_reset_frames = 0
  local leaf_phase = "done"
  local leaf_jump_frames = 0
  local leaf_collect_frames = 0
  local leaf_collect_elapsed = 0
  local leaf_defense_jump_frames = 0
  local leaf_collect_release_frames = 0
  local leaf_item_jump_frames = 0
  local leaf_resume_frames = 0
  if post_1_fortress_power_config.collect_leaf and not has_flight_form() then
    leaf_phase = "pending"
  end
  held.right = true
  held.B = true

  local function start_fortress_flight()
    flight_started = true
    cooldown = 0
    flight_backup_frames = post_1_fortress_flight_backup_frames
    flight_run_frames = 0
    flight_jump_frames = 0
    flight_flap_frames = 0
    flight_up_frames = 0
    if flight_backup_frames > 0 then
      log_state("post_probe_1_fortress_flight_backup")
    elseif post_1_fortress_flight_run_frames > 0 then
      flight_run_frames = post_1_fortress_flight_run_frames
      log_state("post_probe_1_fortress_flight_run")
    else
      flight_jump_frames = post_1_fortress_flight_jump_frames
      log_state("post_probe_1_fortress_flight_jump")
    end
  end

  local function start_fortress_air_flight()
    flight_started = true
    cooldown = 0
    jump_frames = 0
    second_lava_drift_left_frames = 0
    flight_backup_frames = 0
    flight_run_frames = 0
    flight_jump_frames = 0
    flight_flap_frames = post_1_fortress_flight_flap_frames
    flight_up_frames = 0
    log_state("post_probe_1_fortress_flight_flap")
  end

  for frame = 1, post_1_fortress_max_frames do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_fortress_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end

    if m.x >= 8192 or m.y == 0 then
      log_state("post_probe_1_fortress_transition")
      break
    end

	    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
	      stuck_frames = stuck_frames + 1
	    else
	      stuck_frames = 0
	      last_x = m.x
	    end

    if leaf_phase ~= "done" and has_flight_form() then
      leaf_phase = "done"
      leaf_jump_frames = 0
      leaf_collect_frames = 0
      leaf_defense_jump_frames = 0
      leaf_collect_release_frames = 0
      leaf_item_jump_frames = 0
      leaf_resume_frames = post_1_fortress_power_config.resume_frames
      log_state("post_probe_1_fortress_leaf_collected")
    end

    if not flight_started
        and m.x >= post_1_fortress_flight_launch_start
        and m.x <= post_1_fortress_flight_launch_end
        and has_flight_form()
        and memory.readbyte(0x3DD) >= 127
        and not grounded then
      start_fortress_air_flight()
    end

    if leaf_resume_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      leaf_resume_frames = leaf_resume_frames - 1
      if leaf_resume_frames == 0 then
        log_state("post_probe_1_fortress_leaf_resume_done")
      end
    elseif leaf_phase == "align" then
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      if m.x < post_1_fortress_power_config.target_x - post_1_fortress_power_config.tolerance then
        held.right = true
        held.left = false
      elseif m.x > post_1_fortress_power_config.target_x + post_1_fortress_power_config.tolerance then
        held.right = false
        held.left = true
      elseif grounded then
        leaf_phase = "jump"
        leaf_jump_frames = post_1_fortress_power_config.jump_frames
        held.right = false
        held.left = false
        held.A = true
        log_state("post_probe_1_fortress_leaf_jump")
      else
        held.right = false
        held.left = false
      end
    elseif leaf_phase == "jump" then
      held.right = false
      held.left = false
      held.B = false
      held.A = true
      held.down = false
      held.up = false
      leaf_jump_frames = leaf_jump_frames - 1
      if leaf_jump_frames <= 0 then
        leaf_phase = "collect"
        leaf_collect_frames = post_1_fortress_power_config.collect_frames
        leaf_collect_elapsed = 0
        leaf_defense_jump_frames = 0
        leaf_collect_release_frames = post_1_fortress_power_config.collect_release_frames
        leaf_item_jump_frames = 0
        log_state("post_probe_1_fortress_leaf_collect")
      end
    elseif leaf_phase == "collect" then
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      leaf_collect_elapsed = leaf_collect_elapsed + 1
      local powerup = nearest_object_id_between(m, 30, -96, 128, 140)
      local close_hazard = nearest_enemy_between(m, -6, 28)
      if close_hazard ~= nil and close_hazard.id == 30 then
        close_hazard = nil
      end
      if leaf_defense_jump_frames > 0 then
        held.right = false
        held.left = true
        held.A = true
        leaf_defense_jump_frames = leaf_defense_jump_frames - 1
      elseif leaf_collect_release_frames > 0 then
        held.A = false
        leaf_collect_release_frames = leaf_collect_release_frames - 1
        if powerup ~= nil then
          held.right = powerup.dx > 3
          held.left = powerup.dx < -3
        else
          held.right = false
          held.left = true
        end
      elseif grounded and close_hazard ~= nil then
        held.right = false
        held.left = true
        held.A = true
        leaf_defense_jump_frames = post_1_fortress_power_config.defense_jump_frames
        log_state(
          "post_probe_1_fortress_leaf_defense_jump",
          "enemy_dx=" .. tostring(close_hazard.dx) .. " enemy_id=" .. tostring(close_hazard.id)
        )
      elseif leaf_item_jump_frames > 0 then
        held.A = true
        leaf_item_jump_frames = leaf_item_jump_frames - 1
        if powerup ~= nil then
          held.right = powerup.dx > 3
          held.left = powerup.dx < -3
        end
      elseif powerup ~= nil then
        held.right = powerup.dx > 3
        held.left = powerup.dx < -3
        if grounded and math.abs(powerup.dx) < 32 and powerup.dy < -20 then
          held.A = true
          leaf_item_jump_frames = post_1_fortress_power_config.item_jump_frames
          log_state(
            "post_probe_1_fortress_leaf_collect_jump",
            "item_dx=" .. tostring(powerup.dx) .. " item_dy=" .. tostring(powerup.dy)
          )
        else
          held.A = false
        end
      elseif leaf_collect_elapsed <= post_1_fortress_power_config.collect_retreat_frames then
        held.right = false
        held.left = true
      elseif m.x < post_1_fortress_power_config.target_x - post_1_fortress_power_config.tolerance then
        held.right = true
        held.left = false
      else
        held.right = true
        held.left = false
      end
      leaf_collect_frames = leaf_collect_frames - 1
      if leaf_collect_frames <= 0 then
        leaf_phase = "done"
        log_state("post_probe_1_fortress_leaf_collect_done")
      end
    elseif flight_backup_frames > 0 then
      held.right = false
      held.left = true
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      flight_backup_frames = flight_backup_frames - 1
      if flight_backup_frames == 0 then
        flight_run_frames = post_1_fortress_flight_run_frames
        log_state("post_probe_1_fortress_flight_run")
      end
    elseif flight_run_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      flight_run_frames = flight_run_frames - 1
      if flight_run_frames == 0 then
        flight_jump_frames = post_1_fortress_flight_jump_frames
        log_state("post_probe_1_fortress_flight_jump")
      end
    elseif flight_jump_frames > 0 then
      held.right = post_1_fortress_final_config.initial_flight_jump_direction == "right"
      held.left = post_1_fortress_final_config.initial_flight_jump_direction == "left"
      held.B = true
      held.A = true
      held.down = false
      held.up = false
      flight_jump_frames = flight_jump_frames - 1
      if flight_jump_frames == 0 then
        flight_flap_frames = post_1_fortress_flight_flap_frames
        log_state("post_probe_1_fortress_flight_flap")
      end
    elseif flight_flap_frames > 0 then
      held.right = post_1_fortress_final_config.initial_flight_flap_direction == "right"
      held.left = post_1_fortress_final_config.initial_flight_flap_direction == "left"
      held.B = true
      held.A = (flight_flap_frames % post_1_fortress_flight_flap_period) < post_1_fortress_flight_flap_press_frames
      held.down = false
      held.up = false
      flight_flap_frames = flight_flap_frames - 1
      if m.sy <= post_1_fortress_final_config.initial_flight_ceiling_y then
        flight_flap_frames = 0
        final_phase = "ceiling_right"
        final_ceiling_right_frames = post_1_fortress_final_config.shuttle_ceiling_right_frames
        log_state("post_probe_1_fortress_initial_flight_ceiling_right")
      elseif flight_flap_frames == 0 then
        flight_up_frames = post_1_fortress_flight_up_frames
        log_state("post_probe_1_fortress_flight_up")
      end
    elseif flight_up_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = m.y < 200
      flight_up_frames = flight_up_frames - 1
      if m.y == 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      end
    elseif final_phase == "clear_brake" then
      held.right = true
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      final_clear_brake_frames = final_clear_brake_frames - 1
      if memory.readbytesigned(0xBD) >= post_1_fortress_final_config.clear_brake_min_speed
          or final_clear_brake_frames <= 0 then
        final_phase = "clear"
        final_clear_frames = post_1_fortress_final_config.clear_frames
        log_state("post_probe_1_fortress_final_clear")
      end
    elseif final_phase == "clear" then
      held.right = false
      held.left = final_clear_frames >
        post_1_fortress_final_config.clear_frames - post_1_fortress_final_config.tail_face_left_frames
      held.B = (final_clear_frames % post_1_fortress_final_config.tail_period) <
        post_1_fortress_final_config.tail_press_frames
      held.A = false
      held.down = false
      held.up = false
      final_clear_frames = final_clear_frames - 1
      if final_clear_frames <= 0 then
        final_clear_done = true
        final_phase = "back"
        final_back_jump_used = false
        log_state("post_probe_1_fortress_final_deep_back")
      end
    elseif final_phase == "track_stomp" then
      local track_enemy = nearest_object_id_between(
        m,
        post_1_fortress_final_config.track_stomp_object_id,
        post_1_fortress_final_config.track_stomp_search_min_dx,
        post_1_fortress_final_config.track_stomp_search_max_dx,
        post_1_fortress_final_config.track_stomp_search_max_abs_dy
      )
      if track_enemy == nil and post_1_fortress_final_config.track_stomp_allow_fallback then
        track_enemy = nearest_enemy_between(
          m,
          post_1_fortress_final_config.track_stomp_search_min_dx,
          post_1_fortress_final_config.track_stomp_search_max_dx
        )
      end
      local cleared_enemy = nil
      if track_enemy == nil then
        cleared_enemy = nearest_object_id_between(
          m,
          post_1_fortress_final_config.track_stomp_cleared_object_id,
          post_1_fortress_final_config.track_stomp_search_min_dx,
          post_1_fortress_final_config.track_stomp_search_max_dx,
          post_1_fortress_final_config.track_stomp_search_max_abs_dy
        )
      end
      held.down = false
      held.up = false
      if final_track_stomp.jump_frames > 0 then
        held.left = final_track_stomp.jump_left
        held.right = not final_track_stomp.jump_left
        held.B = false
        held.A = true
        final_track_stomp.jump_frames = final_track_stomp.jump_frames - 1
        if final_track_stomp.jump_frames <= 0 then
          if post_1_fortress_final_config.post_stomp_shuttle then
            final_phase = "shuttle_right"
            final_track_stomp.launch_left = true
            final_back_hazard_jump_used = false
            final_back_hazard_jump_frames = 0
            log_state("post_probe_1_fortress_final_stomp_right_to_door")
          else
            final_phase = "stomp_back"
            final_stomp_back_used = true
            final_back_target_override = post_1_fortress_final_config.stomp_retry_target_x
            final_back_hazard_jump_used = false
            final_back_hazard_jump_frames = 0
            log_state("post_probe_1_fortress_final_track_stomp_back")
          end
        end
      elseif final_track_stomp.follow_frames > 0 then
        held.A = false
        held.B = false
        if post_1_fortress_final_config.track_stomp_debug then
          final_track_stomp.debug_frames = final_track_stomp.debug_frames - 1
          if final_track_stomp.debug_frames <= 0 then
            final_track_stomp.debug_frames = post_1_fortress_final_config.track_stomp_debug_period
            log_state(
              "post_probe_1_fortress_final_track_stomp_objects",
              object_summary_between(
                m,
                post_1_fortress_final_config.track_stomp_search_min_dx,
                post_1_fortress_final_config.track_stomp_search_max_dx,
                post_1_fortress_final_config.track_stomp_search_max_abs_dy
              )
            )
          end
        end
        if track_enemy == nil and m.x > post_1_fortress_final_config.track_stomp_setup_x + 4 then
          if cleared_enemy ~= nil and post_1_fortress_final_config.post_stomp_shuttle then
            held.right = true
            held.left = false
            held.B = true
            final_phase = "shuttle_right"
            final_track_stomp.jumped = true
            final_track_stomp.launch_left = true
            final_back_hazard_jump_used = false
            final_back_hazard_jump_frames = 0
            log_state(
              "post_probe_1_fortress_final_stomp_cleared_right_to_door",
              "cleared_x=" .. tostring(cleared_enemy.x)
                .. " cleared_dx=" .. tostring(cleared_enemy.dx)
                .. " cleared_dy=" .. tostring(cleared_enemy.dy)
            )
          else
            held.right = false
            held.left = true
          end
        elseif track_enemy == nil and m.x < post_1_fortress_final_config.track_stomp_setup_x - 4 then
          held.right = true
          held.left = false
        elseif track_enemy ~= nil and track_enemy.dx > post_1_fortress_final_config.track_stomp_enemy_max_dx then
          held.right = true
          held.left = false
        elseif track_enemy ~= nil and track_enemy.dx < post_1_fortress_final_config.track_stomp_enemy_min_dx then
          held.right = false
          held.left = true
        else
          held.right = false
          held.left = false
        end
        final_track_stomp.follow_frames = final_track_stomp.follow_frames - 1
        if not final_track_stomp.jumped
            and grounded
            and track_enemy ~= nil
            and track_enemy.x <= post_1_fortress_final_config.track_stomp_enemy_x
            and track_enemy.dx >= post_1_fortress_final_config.track_stomp_enemy_min_dx
            and track_enemy.dx <= post_1_fortress_final_config.track_stomp_enemy_max_dx
            and track_enemy.dy > -32 then
          final_track_stomp.jump_frames = post_1_fortress_final_config.track_stomp_jump_frames
          final_track_stomp.jumped = true
          final_track_stomp.jump_left = track_enemy.dx < 0
          final_track_stomp.follow_frames = 0
          final_obstacle_jump_used = false
          final_dry_bones_cleared = false
          log_state(
            "post_probe_1_fortress_final_track_stomp_jump",
            "enemy_x=" .. tostring(track_enemy.x)
              .. " enemy_dx=" .. tostring(track_enemy.dx)
              .. " enemy_dy=" .. tostring(track_enemy.dy)
          )
        end
      else
        held.A = false
        held.B = false
        held.right = false
        held.left = false
        if final_track_stomp.jumped then
          if post_1_fortress_final_config.post_stomp_shuttle then
            final_phase = "shuttle_right"
            final_track_stomp.launch_left = true
            final_back_hazard_jump_used = false
            final_back_hazard_jump_frames = 0
            log_state("post_probe_1_fortress_final_stomp_right_to_door")
          else
            final_phase = "stomp_back"
            final_stomp_back_used = true
            final_back_target_override = post_1_fortress_final_config.stomp_retry_target_x
            final_back_hazard_jump_used = false
            final_back_hazard_jump_frames = 0
            log_state("post_probe_1_fortress_final_track_stomp_back")
          end
        else
          final_track_stomp.follow_frames = post_1_fortress_final_config.track_stomp_follow_frames
          log_state("post_probe_1_fortress_final_track_stomp_retry")
        end
      end
    elseif final_phase == "stomp_back" then
      local stomp_back_hazard = nearest_enemy_between(m, -12, 56)
      local stomp_back_target_x = post_1_fortress_final_config.stomp_retry_target_x
      if post_1_fortress_final_config.post_stomp_shuttle and final_track_stomp.jumped then
        stomp_back_target_x = post_1_fortress_final_config.shuttle_first_left_x
      end
      held.right = false
      held.left = true
      held.B = true
      if final_back_hazard_jump_frames > 0 then
        held.A = true
        final_back_hazard_jump_frames = final_back_hazard_jump_frames - 1
      else
        held.A = false
        if grounded
            and not final_back_hazard_jump_used
            and post_1_fortress_final_config.stomp_back_hazard_jump_x > 0
            and m.x <= post_1_fortress_final_config.stomp_back_hazard_jump_x
            and m.x > stomp_back_target_x then
          final_back_hazard_jump_used = true
          final_back_hazard_jump_frames = post_1_fortress_final_config.back_hazard_jump_frames
          log_state("post_probe_1_fortress_final_stomp_back_x_jump")
        elseif grounded and not final_back_hazard_jump_used and stomp_back_hazard ~= nil then
          final_back_hazard_jump_used = true
          final_back_hazard_jump_frames = post_1_fortress_final_config.back_hazard_jump_frames
          log_state(
            "post_probe_1_fortress_final_stomp_back_hazard_jump",
            "enemy_dx=" .. tostring(stomp_back_hazard.dx) .. " enemy_dy=" .. tostring(stomp_back_hazard.dy)
          )
        end
      end
      held.down = false
      held.up = false
      if has_flight_form() and memory.readbyte(0x3DD) >= 127 then
        final_phase = "jump"
        final_jump_frames = post_1_fortress_final_jump_frames
        log_state("post_probe_1_fortress_final_stomp_back_jump")
      elseif grounded
          and (
            m.x <= stomp_back_target_x
            or (
              post_1_fortress_final_config.post_stomp_shuttle
              and final_track_stomp.jumped
              and m.x <= stomp_back_target_x + post_1_fortress_final_config.shuttle_first_left_tolerance
              and memory.readbytesigned(0xBD) <= 0
            )
          ) then
        if post_1_fortress_final_config.post_stomp_shuttle and final_track_stomp.jumped then
          final_phase = "shuttle_right"
          final_back_hazard_jump_used = false
          final_back_hazard_jump_frames = 0
          final_track_stomp.launch_left = true
          log_state("post_probe_1_fortress_final_shuttle_right")
        elseif post_1_fortress_final_config.stomp_turn_jump_frames > 0 then
          final_phase = "stomp_turn"
          final_stomp_turn_jump_frames = post_1_fortress_final_config.stomp_turn_jump_frames
          log_state("post_probe_1_fortress_final_stomp_turn")
        else
          final_phase = "run"
          final_obstacle_jump_used = not final_track_stomp.jumped
          final_dry_bones_cleared = false
          final_tail_used = false
          final_tail_release_frames = 0
          final_tail_swing_frames = 0
          final_back_hazard_jump_used = false
          final_obstacle_jump_frames = 0
          final_back_target_override = nil
          log_state("post_probe_1_fortress_final_stomp_run")
        end
      end
    elseif final_phase == "shuttle_right" then
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      if m.x >= post_1_fortress_final_config.shuttle_right_x and grounded then
        final_phase = "shuttle_left_launch"
        final_shuttle_b_reset_frames = post_1_fortress_final_config.shuttle_b_reset_frames
        log_state("post_probe_1_fortress_final_shuttle_left_launch")
      end
    elseif final_phase == "shuttle_left_launch" then
      held.right = false
      held.left = true
      held.B = final_shuttle_b_reset_frames <= 0
      held.A = false
      held.down = false
      held.up = false
      if final_shuttle_b_reset_frames > 0 then
        final_shuttle_b_reset_frames = final_shuttle_b_reset_frames - 1
      end
      if grounded
          and (
            memory.readbyte(0x3DD) >= post_1_fortress_final_config.shuttle_launch_min_p
            or m.x <= post_1_fortress_final_config.shuttle_launch_left_x
          ) then
        final_phase = "jump"
        final_jump_frames = post_1_fortress_final_jump_frames
        final_track_stomp.launch_left = true
        log_state("post_probe_1_fortress_final_shuttle_jump")
      end
    elseif final_phase == "stomp_turn" then
      held.right = true
      held.left = false
      held.B = true
      held.A = true
      held.down = false
      held.up = false
      final_stomp_turn_jump_frames = final_stomp_turn_jump_frames - 1
      if final_stomp_turn_jump_frames <= 0 then
        final_phase = "run"
        final_obstacle_jump_used = true
        final_tail_used = false
        final_tail_release_frames = 0
        final_tail_swing_frames = 0
        final_back_hazard_jump_used = false
        final_obstacle_jump_frames = 0
        final_back_target_override = nil
        log_state("post_probe_1_fortress_final_stomp_run")
      end
    elseif final_phase == "back" then
      local final_back_target_x = final_back_target_override or post_1_fortress_final_back_target_x
      local back_hazard = nearest_enemy_between(
        m,
        post_1_fortress_final_config.back_hazard_min_dx,
        post_1_fortress_final_config.back_hazard_max_dx
      )
      if not final_clear_done then
        final_back_target_x = post_1_fortress_final_config.clear_x
      end
      held.right = final_back_jump_frames > 0 and final_back_jump_left_frames <= 0
      held.left = not held.right
      held.B = true
      held.down = false
      held.up = false
      if final_back_hazard_jump_frames > 0 then
        held.right = true
        held.left = false
        held.A = true
        final_back_hazard_jump_frames = final_back_hazard_jump_frames - 1
      elseif final_back_jump_frames > 0 then
        held.A = true
        final_back_jump_frames = final_back_jump_frames - 1
        if final_back_jump_left_frames > 0 then
          final_back_jump_left_frames = final_back_jump_left_frames - 1
        end
      else
        held.A = false
        if final_clear_done
            and not final_back_hazard_jump_used
            and final_back_target_override == nil
            and grounded
            and back_hazard ~= nil then
          final_back_hazard_jump_used = true
          final_back_hazard_jump_frames = post_1_fortress_final_config.back_hazard_jump_frames
          log_state(
            "post_probe_1_fortress_final_back_hazard_jump",
            "enemy_dx=" .. tostring(back_hazard.dx) .. " enemy_dy=" .. tostring(back_hazard.dy)
          )
        elseif not final_back_jump_used
            and grounded
            and m.x <= post_1_fortress_final_back_jump_start_x
            and m.x >= final_back_target_x then
          final_back_jump_used = true
          final_back_jump_frames = post_1_fortress_final_back_jump_frames
          final_back_jump_left_frames = post_1_fortress_final_back_jump_left_frames
          log_state("post_probe_1_fortress_final_back_jump")
        end
      end
      if m.x <= final_back_target_x and grounded then
        if not final_clear_done then
          final_phase = "clear_brake"
          final_clear_brake_frames = post_1_fortress_final_config.clear_brake_frames
          log_state("post_probe_1_fortress_final_clear_brake")
        elseif has_flight_form()
            and not final_stage_wait_used
            and post_1_fortress_final_config.stage_wait_frames > 0 then
          final_phase = "stage_wait"
          final_stage_wait_used = true
          final_stage_wait_frames = post_1_fortress_final_config.stage_wait_frames
          final_stage_wait_timeout_frames = post_1_fortress_final_config.stage_wait_timeout_frames
          log_state("post_probe_1_fortress_final_stage_wait")
        else
          final_phase = "run"
          final_obstacle_jump_used = false
          final_tail_used = false
          final_tail_release_frames = 0
          final_tail_swing_frames = 0
          final_back_hazard_jump_used = false
          final_obstacle_jump_frames = 0
          final_back_target_override = nil
          log_state("post_probe_1_fortress_final_run")
        end
      end
    elseif final_phase == "stage_wait" then
      local stage_enemy = nearest_enemy_between(
        m,
        post_1_fortress_final_config.stage_enemy_min_dx,
        post_1_fortress_final_config.stage_enemy_max_dx
      )
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      final_stage_wait_timeout_frames = final_stage_wait_timeout_frames - 1
      if final_stage_wait_frames > 0 then
        final_stage_wait_frames = final_stage_wait_frames - 1
      end
      if (stage_enemy ~= nil and final_stage_wait_frames <= 0) or final_stage_wait_timeout_frames <= 0 then
        final_phase = "run"
        final_obstacle_jump_used = false
        final_tail_used = false
        final_tail_release_frames = 0
        final_tail_swing_frames = 0
        final_back_hazard_jump_used = false
        final_obstacle_jump_frames = 0
        final_back_target_override = nil
        if stage_enemy ~= nil then
          log_state(
            "post_probe_1_fortress_final_stage_run",
            "enemy_dx=" .. tostring(stage_enemy.dx) .. " enemy_dy=" .. tostring(stage_enemy.dy)
          )
        else
          log_state("post_probe_1_fortress_final_stage_timeout")
        end
      end
    elseif final_phase == "run" then
      held.right = true
      held.left = false
      held.B = true
      if final_tail_release_frames > 0 then
        held.A = false
        held.B = false
        final_tail_release_frames = final_tail_release_frames - 1
      elseif final_tail_swing_frames > 0 then
        held.A = false
        held.B = true
        final_tail_swing_frames = final_tail_swing_frames - 1
      elseif final_obstacle_jump_frames > 0 then
        held.A = true
        final_obstacle_jump_frames = final_obstacle_jump_frames - 1
      else
        held.A = false
        if not final_tail_used
            and has_flight_form()
            and grounded
            and enemy ~= nil
            and enemy.dx >= post_1_fortress_final_config.tail_min_dx
            and enemy.dx < post_1_fortress_final_config.tail_max_dx
            and enemy.dy > -32 then
          final_tail_used = true
          final_tail_release_frames = post_1_fortress_final_config.tail_release_frames
          final_tail_swing_frames = post_1_fortress_final_config.tail_swing_frames
          log_state(
            "post_probe_1_fortress_final_tail_swat",
            "enemy_dx=" .. tostring(enemy.dx) .. " enemy_dy=" .. tostring(enemy.dy)
          )
        elseif post_1_fortress_final_obstacle_jump_frames > 0
            and not final_obstacle_jump_used
            and not final_dry_bones_cleared
            and grounded
            and enemy ~= nil
            and enemy.dx >= post_1_fortress_final_config.obstacle_min_dx
            and enemy.dx < post_1_fortress_final_config.obstacle_max_dx
            and enemy.dy > -32 then
          final_obstacle_jump_used = true
          final_dry_bones_cleared = true
          final_obstacle_jump_frames = post_1_fortress_final_obstacle_jump_frames
          log_state("post_probe_1_fortress_final_obstacle_jump", "dry_bones_cleared=true")
        end
      end
      held.down = false
      held.up = false
      if memory.readbyte(0x3DD) >= 127 and m.x >= post_1_fortress_final_launch_x then
        final_phase = "jump"
        final_jump_frames = post_1_fortress_final_jump_frames
        log_state("post_probe_1_fortress_final_jump")
      elseif final_obstacle_jump_used
          and has_flight_form()
          and not final_stomp_back_used
          and m.x >= post_1_fortress_final_config.stomp_back_start_x
          and memory.readbyte(0x3DD) < 127 then
        final_phase = "stomp_back"
        final_stomp_back_used = true
        final_back_target_override = post_1_fortress_final_config.stomp_retry_target_x
        final_obstacle_jump_frames = 0
        log_state("post_probe_1_fortress_final_stomp_back")
      elseif m.x >= post_1_fortress_final_run_target_x and memory.readbyte(0x3DD) < 127 then
        if final_obstacle_jump_used and has_flight_form() and not final_stomp_back_used then
          final_phase = "stomp_back"
          final_stomp_back_used = true
          final_back_target_override = post_1_fortress_final_config.stomp_retry_target_x
        else
          final_phase = "back"
          final_back_jump_used = false
          final_back_target_override = nil
          final_obstacle_jump_used = false
        end
        final_obstacle_jump_frames = 0
        log_state("post_probe_1_fortress_final_retry_back")
      end
    elseif final_phase == "jump" then
      if final_track_stomp.launch_left and post_1_fortress_final_config.shuttle_jump_direction == "right" then
        held.right = true
        held.left = false
      elseif final_track_stomp.launch_left and post_1_fortress_final_config.shuttle_jump_direction == "neutral" then
        held.right = false
        held.left = false
      else
        held.right = not final_track_stomp.launch_left
        held.left = final_track_stomp.launch_left
      end
      held.B = true
      held.A = true
      held.down = false
      held.up = false
      final_jump_frames = final_jump_frames - 1
      if final_jump_frames <= 0 then
        final_phase = "flap"
        final_flap_frames = post_1_fortress_final_flap_frames
        log_state("post_probe_1_fortress_final_flap")
      end
    elseif final_phase == "flap" then
      if final_track_stomp.launch_left and post_1_fortress_final_config.shuttle_flap_direction == "right" then
        held.right = true
        held.left = false
      elseif final_track_stomp.launch_left and post_1_fortress_final_config.shuttle_flap_direction == "neutral" then
        held.right = false
        held.left = false
      elseif final_track_stomp.launch_left and post_1_fortress_final_config.shuttle_flap_direction == "vertical" then
        held.right = false
        held.left = false
      else
        held.right = not final_track_stomp.launch_left
        held.left = final_track_stomp.launch_left
      end
      held.B = true
      held.A = (final_flap_frames % post_1_fortress_final_flap_period) < post_1_fortress_final_flap_press_frames
      held.down = false
      held.up = false
      final_flap_frames = final_flap_frames - 1
      if final_track_stomp.launch_left
          and m.sy <= post_1_fortress_final_config.shuttle_vertical_climb_y then
        final_phase = "ceiling_left"
        final_ceiling_left_frames = post_1_fortress_final_config.shuttle_ceiling_left_frames
        log_state("post_probe_1_fortress_final_ceiling_left")
      elseif m.y < 190
          and (
            final_track_stomp.launch_left
            or m.x >= post_1_fortress_final_run_target_x
          ) then
        final_phase = "up"
        final_up_frames = post_1_fortress_final_up_frames
        log_state("post_probe_1_fortress_final_up")
      elseif final_flap_frames <= 0 then
        final_phase = "back"
        final_back_jump_used = false
        log_state("post_probe_1_fortress_final_retry_after_flap")
      end
    elseif final_phase == "ceiling_left" then
      held.right = false
      held.left = true
      held.B = true
      held.A = (final_ceiling_left_frames % post_1_fortress_final_flap_period) < post_1_fortress_final_flap_press_frames
      held.down = false
      held.up = true
      final_ceiling_left_frames = final_ceiling_left_frames - 1
      if m.y == 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      elseif final_ceiling_left_frames <= 0 then
        final_phase = "ceiling_right"
        final_ceiling_right_frames = post_1_fortress_final_config.shuttle_ceiling_right_frames
        log_state("post_probe_1_fortress_final_ceiling_right")
      end
    elseif final_phase == "ceiling_right" then
      held.right = true
      held.left = false
      held.B = true
      held.A = (final_ceiling_right_frames % post_1_fortress_final_flap_period) < post_1_fortress_final_flap_press_frames
      held.down = false
      held.up = true
      final_ceiling_right_frames = final_ceiling_right_frames - 1
      if m.y == 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      elseif final_ceiling_right_frames <= 0 then
        final_phase = "up"
        final_up_frames = post_1_fortress_final_up_frames
        log_state("post_probe_1_fortress_final_up")
      end
    elseif final_phase == "up" then
      local door_dx = m.x - post_1_fortress_final_config.upper_door_x
      held.left = door_dx > post_1_fortress_final_config.upper_door_tolerance
      held.right = door_dx < -post_1_fortress_final_config.upper_door_tolerance
      held.B = false
      held.A = false
      held.down = false
      held.up = true
      final_up_frames = final_up_frames - 1
      if m.y == 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      elseif m.air == 0 and math.abs(door_dx) <= post_1_fortress_final_config.upper_door_tolerance then
        final_phase = "upper_door_wait"
        final_upper_door_wait_frames = post_1_fortress_final_config.upper_door_wait_frames
        log_state("post_probe_1_fortress_final_upper_door_wait")
      elseif final_up_frames <= 0 then
        final_phase = "flap"
        final_flap_frames = 90
        log_state("post_probe_1_fortress_final_resume_flap")
      end
    elseif final_phase == "upper_door_wait" then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      final_upper_door_wait_frames = final_upper_door_wait_frames - 1
      if m.y == 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      elseif final_upper_door_wait_frames <= 0 then
        final_phase = "upper_door_enter"
        final_upper_door_enter_frames = post_1_fortress_final_config.upper_door_enter_frames
        log_state("post_probe_1_fortress_final_upper_door_enter")
      end
    elseif final_phase == "upper_door_enter" then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = true
      final_upper_door_enter_frames = final_upper_door_enter_frames - 1
      if m.x < post_1_fortress_final_config.whistle_room_trigger_max_x and m.y > 180 then
        final_phase = "whistle_room_chest"
        final_whistle_room_open_frames = post_1_fortress_final_config.whistle_room_open_frames
        log_state("post_probe_1_fortress_whistle_room_entered")
      elseif m.y == 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      elseif final_upper_door_enter_frames <= 0 then
        final_phase = "flap"
        final_flap_frames = 90
        log_state("post_probe_1_fortress_final_resume_flap")
      end
    elseif final_phase == "whistle_room_chest" then
      local chest_dx = m.x - post_1_fortress_final_config.whistle_room_chest_x
      held.right = chest_dx < -post_1_fortress_final_config.whistle_room_chest_tolerance
      held.left = chest_dx > post_1_fortress_final_config.whistle_room_chest_tolerance
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      if math.abs(chest_dx) <= post_1_fortress_final_config.whistle_room_chest_tolerance then
        final_phase = "whistle_room_open"
        log_state("post_probe_1_fortress_whistle_room_chest")
      end
    elseif final_phase == "whistle_room_open" then
      held.right = false
      held.left = false
      held.B = false
      held.A = post_1_fortress_final_config.whistle_room_open_mode == "jump"
      held.down = false
      held.up = post_1_fortress_final_config.whistle_room_open_mode == "up"
      final_whistle_room_open_frames = final_whistle_room_open_frames - 1
      if memory.readbyte(0x14) ~= 0 then
        log_state("post_probe_1_fortress_whistle_room_success")
        break
      elseif final_whistle_room_open_frames <= 0 then
        log_state("post_probe_1_fortress_whistle_room_open_timeout")
        break
      end
    elseif mid_hazard_run_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      mid_hazard_run_frames = mid_hazard_run_frames - 1
      if mid_hazard_run_frames == 0 then
        jump_frames = post_1_fortress_mid_hazard_jump_frames
        second_lava_drift_left_frames = post_1_fortress_mid_hazard_drift_left_frames
        cooldown = 0
        log_state("post_probe_1_fortress_jump_mid_hazard")
      end
    elseif mid_hazard_pre_wait_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      mid_hazard_pre_wait_frames = mid_hazard_pre_wait_frames - 1
      if mid_hazard_pre_wait_frames == 0 then
        log_state("post_probe_1_fortress_resume_mid_hazard_approach")
      end
    elseif mid_hazard_wait_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      mid_hazard_wait_frames = mid_hazard_wait_frames - 1
      if mid_hazard_wait_frames == 0 then
        jump_frames = post_1_fortress_mid_hazard_jump_frames
        second_lava_drift_left_frames = post_1_fortress_mid_hazard_drift_left_frames
        cooldown = 0
        log_state("post_probe_1_fortress_jump_mid_hazard")
      end
    elseif second_lava_wait_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      second_lava_wait_frames = second_lava_wait_frames - 1
      if second_lava_wait_frames == 0 then
        second_lava_backup_frames = post_1_fortress_second_lava_backup_frames
        if second_lava_backup_frames > 0 then
          log_state("post_probe_1_fortress_backup_second_lava")
        else
          second_lava_accel_frames = post_1_fortress_second_lava_accel_frames
          if second_lava_accel_frames > 0 then
            log_state("post_probe_1_fortress_accel_second_lava")
          else
            jump_frames = post_1_fortress_second_lava_jump_frames
            second_lava_drift_left_frames = post_1_fortress_second_lava_drift_left_frames
            cooldown = post_1_fortress_second_lava_cooldown_frames
            log_state("post_probe_1_fortress_jump_second_lava")
          end
        end
      end
    elseif second_lava_backup_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      second_lava_backup_frames = second_lava_backup_frames - 1
      if second_lava_backup_frames == 0 then
        second_lava_accel_frames = post_1_fortress_second_lava_accel_frames
        if second_lava_accel_frames > 0 then
          log_state("post_probe_1_fortress_accel_second_lava")
        else
          jump_frames = post_1_fortress_second_lava_jump_frames
          second_lava_drift_left_frames = post_1_fortress_second_lava_drift_left_frames
          cooldown = post_1_fortress_second_lava_cooldown_frames
          log_state("post_probe_1_fortress_jump_second_lava")
        end
      end
    elseif second_lava_accel_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      second_lava_accel_frames = second_lava_accel_frames - 1
      if second_lava_accel_frames == 0 then
        jump_frames = post_1_fortress_second_lava_jump_frames
        second_lava_drift_left_frames = post_1_fortress_second_lava_drift_left_frames
        cooldown = post_1_fortress_second_lava_cooldown_frames
        log_state("post_probe_1_fortress_jump_second_lava")
      end
    elseif jump_frames > 0 then
      if grounded
          and mid_hazard_jump_started
          and not mid_hazard_followup_jump_started
          and post_1_fortress_mid_hazard_followup_jump_frames > 0
          and m.x >= post_1_fortress_mid_hazard_followup_start
          and m.x <= post_1_fortress_mid_hazard_followup_end then
        jump_frames = 0
        held.right = true
        held.left = false
        held.B = true
        held.A = false
        held.down = false
        held.up = false
        log_state("post_probe_1_fortress_prepare_mid_hazard_followup")
      elseif second_lava_drift_left_frames > 0 then
        held.right = false
        held.left = true
        second_lava_drift_left_frames = second_lava_drift_left_frames - 1
      else
        held.right = true
        held.left = false
      end
      held.B = true
      held.A = true
      held.down = false
      held.up = false
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      held.up = false
      local search_continuation_active =
        second_lava_jump_started
        and not has_flight_form()
        and m.x >= 440
        and m.x < post_1_fortress_final_config.search_continuation_until_x
      if search_continuation_active and not search_continuation_logged then
        search_continuation_logged = true
        cooldown = 0
        log_state("post_probe_1_fortress_search_continuation")
      end
      if grounded then
        if search_continuation_active then
          -- The search harness proved this corridor is safer as simple run/react.
        elseif leaf_phase == "pending"
            and m.x >= post_1_fortress_power_config.start_x
            and m.x <= post_1_fortress_power_config.target_x + 80 then
          leaf_phase = "align"
          cooldown = 90
          log_state("post_probe_1_fortress_leaf_align")
        elseif not flight_started
            and m.x >= post_1_fortress_flight_launch_start
            and m.x <= post_1_fortress_flight_launch_end
            and has_flight_form()
            and memory.readbyte(0x3DD) >= 127 then
          start_fortress_flight()
        elseif final_phase == ""
            and m.x >= post_1_fortress_final_start_x
            and has_flight_form() then
          flight_started = true
          if post_1_fortress_final_config.frame_sleep_seconds > 0 then
            frame_sleep_seconds = post_1_fortress_final_config.frame_sleep_seconds
            log_state(
              "post_probe_1_fortress_final_watch_speed",
              "frame_sleep_seconds=" .. tostring(frame_sleep_seconds)
            )
          end
          if post_1_fortress_final_config.track_stomp and not final_track_stomp.used then
            final_phase = "track_stomp"
            final_track_stomp.used = true
            final_track_stomp.follow_frames = post_1_fortress_final_config.track_stomp_follow_frames
            final_obstacle_jump_used = false
            final_back_hazard_jump_used = false
            final_obstacle_jump_frames = 0
            log_state("post_probe_1_fortress_final_track_stomp")
          elseif memory.readbyte(0x3DD) >= post_1_fortress_final_direct_min_p then
            final_phase = "run"
            final_obstacle_jump_used = false
            final_back_hazard_jump_used = false
            final_obstacle_jump_frames = 0
            log_state("post_probe_1_fortress_final_direct_run")
          else
            final_phase = "back"
            final_back_jump_used = false
            final_obstacle_jump_used = false
            log_state("post_probe_1_fortress_final_back")
          end
        elseif not first_lava_jump_started
            and m.x >= post_1_fortress_first_lava_start
            and m.x <= post_1_fortress_first_lava_end then
          first_lava_jump_started = true
          jump_frames = post_1_fortress_first_lava_jump_frames
          cooldown = 70
          log_state("post_probe_1_fortress_jump_first_lava")
        elseif first_lava_jump_started
            and not second_lava_jump_started
            and m.x >= 420
            and m.x <= 455 then
          second_lava_jump_started = true
          second_lava_wait_frames = post_1_fortress_second_lava_wait_frames
          cooldown = 0
          if second_lava_wait_frames > 0 then
            log_state("post_probe_1_fortress_wait_second_lava")
          else
            second_lava_backup_frames = post_1_fortress_second_lava_backup_frames
            if second_lava_backup_frames > 0 then
              log_state("post_probe_1_fortress_backup_second_lava")
            else
              second_lava_accel_frames = post_1_fortress_second_lava_accel_frames
              if second_lava_accel_frames > 0 then
                log_state("post_probe_1_fortress_accel_second_lava")
              else
                jump_frames = post_1_fortress_second_lava_jump_frames
                second_lava_drift_left_frames = post_1_fortress_second_lava_drift_left_frames
                cooldown = post_1_fortress_second_lava_cooldown_frames
                log_state("post_probe_1_fortress_jump_second_lava")
              end
            end
          end
        elseif second_lava_jump_started
            and not second_lava_stair_jump_started
            and m.x >= 440
            and m.x <= 470
            and m.y <= 360 then
          second_lava_stair_jump_started = true
          jump_frames = post_1_fortress_second_lava_stair_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = post_1_fortress_second_lava_stair_jump_frames + 20
          log_state("post_probe_1_fortress_jump_second_lava_stair")
        elseif second_lava_stair_jump_started
            and not third_lava_jump_started
            and m.x >= 585
            and m.x <= 625
            and m.y <= 360 then
          third_lava_jump_started = true
          jump_frames = post_1_fortress_third_lava_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = post_1_fortress_third_lava_jump_frames + 20
          log_state("post_probe_1_fortress_jump_third_lava")
        elseif third_lava_jump_started
            and not flat_enemy_jump_started
            and m.x >= 790
            and m.x <= 850 then
          flat_enemy_jump_started = true
          jump_frames = post_1_fortress_flat_enemy_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = 55
          log_state("post_probe_1_fortress_jump_flat_enemy")
        elseif flat_enemy_jump_started
            and not mid_hazard_pre_wait_started
            and post_1_fortress_mid_hazard_pre_wait_frames > 0
            and m.x >= post_1_fortress_mid_hazard_pre_wait_start
            and m.x <= post_1_fortress_mid_hazard_pre_wait_end then
          mid_hazard_pre_wait_started = true
          mid_hazard_pre_wait_frames = post_1_fortress_mid_hazard_pre_wait_frames
          cooldown = mid_hazard_pre_wait_frames + 20
          log_state("post_probe_1_fortress_wait_mid_hazard_approach")
        elseif flat_enemy_jump_started
            and not mid_hazard_jump_started
            and m.x >= post_1_fortress_mid_hazard_start
            and m.x <= post_1_fortress_mid_hazard_end then
          mid_hazard_jump_started = true
          mid_hazard_run_frames = post_1_fortress_mid_hazard_run_frames
          mid_hazard_wait_frames = 0
          if mid_hazard_run_frames > 0 then
            log_state("post_probe_1_fortress_run_mid_hazard")
          else
            mid_hazard_wait_frames = post_1_fortress_mid_hazard_wait_frames
          end
          if mid_hazard_wait_frames > 0 then
            log_state("post_probe_1_fortress_wait_mid_hazard")
          elseif mid_hazard_run_frames <= 0 then
            jump_frames = post_1_fortress_mid_hazard_jump_frames
            second_lava_drift_left_frames = post_1_fortress_mid_hazard_drift_left_frames
            cooldown = 0
            log_state("post_probe_1_fortress_jump_mid_hazard")
          end
        end
      end
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if not flight_started and grounded and jump_frames <= 0 then
        if mid_hazard_jump_started
            and not mid_hazard_followup_jump_started
            and post_1_fortress_mid_hazard_followup_jump_frames > 0
            and m.x >= post_1_fortress_mid_hazard_followup_start
            and m.x <= post_1_fortress_mid_hazard_followup_end then
          mid_hazard_followup_jump_started = true
          jump_frames = post_1_fortress_mid_hazard_followup_jump_frames
          cooldown = 0
          log_state("post_probe_1_fortress_jump_mid_hazard_followup")
        elseif cooldown == 0
            and not (second_lava_jump_started and not search_continuation_logged)
            and m.x <= post_1_fortress_final_config.reactive_jump_max_x
            and enemy ~= nil
            and enemy.dx >= 0
            and enemy.dx < 72
            and enemy.dy > -64 then
          jump_frames = post_1_fortress_final_config.reactive_jump_frames
          cooldown = 42
          log_state("post_probe_1_fortress_jump_enemy")
        elseif cooldown == 0
            and not (second_lava_jump_started and not search_continuation_logged)
            and m.x <= post_1_fortress_final_config.reactive_jump_max_x
            and stuck_frames > 35 then
          jump_frames = 42
          cooldown = 52
          stuck_frames = 0
          log_state("post_probe_1_fortress_jump_stuck")
        end
      end
    end

    apply()
    if frame % 30 == 0 then
      log_state("post_probe_1_fortress_tick")
    end
    advance_frame()
  end

  held.A = false
  held.B = false
  held.right = false
  held.left = false
  held.down = false
  held.up = false
  apply()
  advance(post_1_fortress_after_pre_frames, "post_probe_1_fortress_after")
  if post_1_fortress_after_mode == "tap_A" then
    held.A = true
    advance(post_1_fortress_after_press_frames, "post_probe_1_fortress_after_tap_A")
    held.A = false
  elseif post_1_fortress_after_mode == "tap_B" then
    held.B = true
    advance(post_1_fortress_after_press_frames, "post_probe_1_fortress_after_tap_B")
    held.B = false
  elseif post_1_fortress_after_mode == "tap_start" then
    held.start = true
    advance(post_1_fortress_after_press_frames, "post_probe_1_fortress_after_tap_start")
    held.start = false
  elseif post_1_fortress_after_mode == "tap_up" then
    held.up = true
    advance(post_1_fortress_after_press_frames, "post_probe_1_fortress_after_tap_up")
    held.up = false
  end
  advance(post_1_fortress_after_frames, "post_probe_1_fortress_after_wait")
  log_state("post_probe_1_fortress_done")
end

local function drive_1_fortress_to_second_lava_checkpoint()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  held.right = true
  held.B = true

  for frame = 1, 900 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if first_lava_jump_started == nil then
      -- no-op; keeps this checkpoint driver independent from the route runner's locals
    end

    if grounded and m.x >= 420 and m.x <= 455 then
      held.A = false
      held.B = false
      held.right = false
      held.left = false
      apply()
      log_state("post_probe_1_fortress_second_lava_checkpoint")
      return true
    end

    if memory.readbyte(0xED) == 0 or m.y == 0 or m.x >= 8192 then
      log_state("post_probe_1_fortress_second_lava_checkpoint_failed")
      return false
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if jump_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      if grounded
          and m.x >= post_1_fortress_first_lava_start
          and m.x <= post_1_fortress_first_lava_end then
        jump_frames = post_1_fortress_first_lava_jump_frames
        cooldown = 70
        log_state("post_probe_1_fortress_search_jump_first_lava")
      else
        if cooldown > 0 then
          cooldown = cooldown - 1
        end
        if grounded and cooldown == 0 then
          if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 72 and enemy.dy > -64 then
          jump_frames = 28
          cooldown = 42
          log_state("post_probe_1_fortress_search_jump_enemy")
          elseif stuck_frames > 35 then
          jump_frames = 42
          cooldown = 52
          stuck_frames = 0
          log_state("post_probe_1_fortress_search_jump_stuck")
          end
        end
      end
    end

    apply()
    advance_frame()
  end

  log_state("post_probe_1_fortress_second_lava_checkpoint_timeout")
  return false
end

local function continue_1_fortress_after_second_lava(candidate_id, max_frames)
  local max_x = mario().x
  local lost_form = false
  local transitioned = false
  local jump_frames = 0
  local cooldown = 0

  for frame = 1, max_frames do
    local m = mario()
    local grounded = m.air == 0
    local enemy = nearest_enemy_ahead(m)
    max_x = math.max(max_x, m.x)

    if memory.readbyte(0xED) == 0 then
      lost_form = true
      break
    end
    if m.y == 0 or m.x >= 8192 then
      transitioned = true
      break
    end

    if jump_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 72 and enemy.dy > -64 then
          jump_frames = 28
          cooldown = 42
        end
      end
    end
    apply()
    advance_frame()
  end

  log_state(
    "post_probe_1_fortress_search_candidate_done",
    "candidate=" .. tostring(candidate_id)
      .. " max_x=" .. tostring(max_x)
      .. " lost_form=" .. tostring(lost_form)
      .. " transitioned=" .. tostring(transitioned)
  )
  return max_x, lost_form, transitioned
end

local function run_1_fortress_second_lava_search()
  if not drive_1_fortress_to_second_lava_checkpoint() then
    return
  end

  local checkpoint = savestate.create()
  savestate.save(checkpoint)
  local best_x = -1
  local best_candidate = -1
  local candidate = 0
  local backup_options = {0, 4, 8, 12, 16, 20, 24}
  local wait_options = {0, 24, 48, 72, 96}
  local prep_options = {0, 6, 12, 18}
  local jump_options = {40, 60, 80, 100, 130}
  local drift_left_options = {0, 6, 12}

  for _, wait_frames in ipairs(wait_options) do
    for _, backup_frames in ipairs(backup_options) do
      for _, prep_frames in ipairs(prep_options) do
        for _, jump_hold in ipairs(jump_options) do
          for _, drift_left_frames in ipairs(drift_left_options) do
            candidate = candidate + 1
            if candidate > post_1_fortress_search_limit then
              log_state(
                "post_probe_1_fortress_search_complete",
                "best_candidate=" .. tostring(best_candidate) .. " best_x=" .. tostring(best_x)
              )
              return
            end
            savestate.load(checkpoint)
            held.A = false
            held.B = false
            held.right = false
            held.left = false
            apply()

            for i = 1, wait_frames do
              held.A = false
              held.B = false
              held.right = false
              held.left = false
              apply()
              advance_frame()
            end
            for i = 1, backup_frames do
              held.A = false
              held.B = false
              held.right = false
              held.left = true
              apply()
              advance_frame()
            end
            for i = 1, prep_frames do
              held.A = false
              held.B = true
              held.right = true
              held.left = false
              apply()
              advance_frame()
            end
            for i = 1, jump_hold do
              held.A = true
              held.B = true
              held.right = i > drift_left_frames
              held.left = i <= drift_left_frames
              apply()
              advance_frame()
            end
            held.A = false
            local max_x, lost_form, transitioned = continue_1_fortress_after_second_lava(candidate, 420)
            if max_x > best_x and not lost_form then
              best_x = max_x
              best_candidate = candidate
              log_state(
                "post_probe_1_fortress_search_best",
                "candidate=" .. tostring(candidate)
                  .. " wait=" .. tostring(wait_frames)
                  .. " backup=" .. tostring(backup_frames)
                  .. " prep=" .. tostring(prep_frames)
                  .. " jump=" .. tostring(jump_hold)
                  .. " drift_left=" .. tostring(drift_left_frames)
                  .. " max_x=" .. tostring(max_x)
                  .. " transitioned=" .. tostring(transitioned)
              )
            end
          end
        end
      end
    end
  end

  log_state(
    "post_probe_1_fortress_search_complete",
    "best_candidate=" .. tostring(best_candidate) .. " best_x=" .. tostring(best_x)
  )
end

local function drive_1_fortress_to_mid_checkpoint()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local first_lava_jump_started = false
  local second_lava_jump_started = false
  local second_lava_stair_jump_started = false
  local third_lava_jump_started = false
  local flat_enemy_jump_started = false
  local second_lava_backup_frames = 0
  local second_lava_drift_left_frames = 0
  held.right = true
  held.B = true

  for frame = 1, 1800 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if grounded and memory.readbyte(0xED) > 0 and m.x >= 1000 and m.x <= 1065 then
      held.A = false
      held.B = false
      held.right = false
      held.left = false
      held.down = false
      apply()
      log_state("post_probe_1_fortress_mid_checkpoint")
      return true
    end

    if memory.readbyte(0xED) == 0 or m.y == 0 or m.x >= 8192 then
      log_state("post_probe_1_fortress_mid_checkpoint_failed")
      return false
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if second_lava_backup_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      second_lava_backup_frames = second_lava_backup_frames - 1
      if second_lava_backup_frames == 0 then
        jump_frames = post_1_fortress_second_lava_jump_frames
        second_lava_drift_left_frames = post_1_fortress_second_lava_drift_left_frames
        cooldown = post_1_fortress_second_lava_cooldown_frames
        log_state("post_probe_1_fortress_search_jump_second_lava")
      end
    elseif jump_frames > 0 then
      if second_lava_drift_left_frames > 0 then
        held.right = false
        held.left = true
        second_lava_drift_left_frames = second_lava_drift_left_frames - 1
      else
        held.right = true
        held.left = false
      end
      held.B = true
      held.A = true
      held.down = false
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      if grounded then
        if not first_lava_jump_started
            and m.x >= post_1_fortress_first_lava_start
            and m.x <= post_1_fortress_first_lava_end then
          first_lava_jump_started = true
          jump_frames = post_1_fortress_first_lava_jump_frames
          cooldown = 70
          log_state("post_probe_1_fortress_search_jump_first_lava")
        elseif first_lava_jump_started
            and not second_lava_jump_started
            and m.x >= 420
            and m.x <= 455 then
          second_lava_jump_started = true
          second_lava_backup_frames = post_1_fortress_second_lava_backup_frames
          cooldown = 0
          log_state("post_probe_1_fortress_search_backup_second_lava")
        elseif second_lava_jump_started
            and not second_lava_stair_jump_started
            and m.x >= 440
            and m.x <= 470
            and m.y <= 360 then
          second_lava_stair_jump_started = true
          jump_frames = post_1_fortress_second_lava_stair_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = post_1_fortress_second_lava_stair_jump_frames + 20
          log_state("post_probe_1_fortress_search_jump_second_lava_stair")
        elseif second_lava_stair_jump_started
            and not third_lava_jump_started
            and m.x >= 585
            and m.x <= 625
            and m.y <= 360 then
          third_lava_jump_started = true
          jump_frames = post_1_fortress_third_lava_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = post_1_fortress_third_lava_jump_frames + 20
          log_state("post_probe_1_fortress_search_jump_third_lava")
        elseif third_lava_jump_started
            and not flat_enemy_jump_started
            and m.x >= 790
            and m.x <= 850 then
          flat_enemy_jump_started = true
          jump_frames = post_1_fortress_flat_enemy_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = 55
          log_state("post_probe_1_fortress_search_jump_flat_enemy")
        end
      end
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 and jump_frames <= 0 then
        if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 72 and enemy.dy > -64 then
          jump_frames = 28
          cooldown = 42
          log_state("post_probe_1_fortress_search_jump_enemy")
        elseif not fourteenth_gap_started and stuck_frames > 35 then
          jump_frames = 42
          cooldown = 52
          stuck_frames = 0
          log_state("post_probe_1_fortress_search_jump_stuck")
        end
      end
    end

    apply()
    advance_frame()
  end

  log_state("post_probe_1_fortress_mid_checkpoint_timeout")
  return false
end

local function continue_1_fortress_after_mid_candidate(candidate_id, max_frames)
  local max_x = mario().x
  local lost_form = false
  local transitioned = false
  local jump_frames = 0
  local cooldown = 0
  local last_x = mario().x
  local stuck_frames = 0

  for frame = 1, max_frames do
    local m = mario()
    local grounded = m.air == 0
    local enemy = nearest_enemy_ahead(m)
    max_x = math.max(max_x, m.x)

    if memory.readbyte(0xED) == 0 then
      lost_form = true
      break
    end
    if m.y == 0 or m.x >= 8192 then
      transitioned = true
      break
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if jump_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = true
      held.down = false
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 72 and enemy.dy > -64 then
          jump_frames = 28
          cooldown = 42
        elseif stuck_frames > 35 then
          jump_frames = 42
          cooldown = 52
          stuck_frames = 0
        end
      end
    end
    apply()
    advance_frame()
  end

  log_state(
    "post_probe_1_fortress_mid_search_candidate_done",
    "candidate=" .. tostring(candidate_id)
      .. " max_x=" .. tostring(max_x)
      .. " lost_form=" .. tostring(lost_form)
      .. " transitioned=" .. tostring(transitioned)
  )
  return max_x, lost_form, transitioned
end

local function run_1_fortress_mid_search()
  if not drive_1_fortress_to_mid_checkpoint() then
    return
  end

  local checkpoint = savestate.create()
  savestate.save(checkpoint)
  local best_x = -1
  local best_candidate = -1
  local candidate = 0
  local wait_options = {0, 6, 12, 18, 24, 30, 36, 45, 60}
  local duck_options = {0, 12, 24, 36}
  local run_options = {0, 12, 24, 36, 48, 60, 72}
  local jump_options = {20, 32, 44, 56, 72, 90, 110}
  local drift_left_options = {0, 6, 12, 18}

  for _, wait_frames in ipairs(wait_options) do
    for _, duck_frames in ipairs(duck_options) do
      for _, run_frames in ipairs(run_options) do
        for _, jump_hold in ipairs(jump_options) do
          for _, drift_left_frames in ipairs(drift_left_options) do
            candidate = candidate + 1
            if candidate > post_1_fortress_search_limit then
              log_state(
                "post_probe_1_fortress_mid_search_complete",
                "best_candidate=" .. tostring(best_candidate) .. " best_x=" .. tostring(best_x)
              )
              return
            end
            savestate.load(checkpoint)
            held.A = false
            held.B = false
            held.right = false
            held.left = false
            held.down = false
            apply()

            for i = 1, wait_frames do
              held.A = false
              held.B = false
              held.right = false
              held.left = false
              held.down = false
              apply()
              advance_frame()
            end
            for i = 1, duck_frames do
              held.A = false
              held.B = false
              held.right = false
              held.left = false
              held.down = true
              apply()
              advance_frame()
            end
            held.down = false
            for i = 1, run_frames do
              held.A = false
              held.B = true
              held.right = true
              held.left = false
              apply()
              advance_frame()
            end
            for i = 1, jump_hold do
              held.A = true
              held.B = true
              held.right = i > drift_left_frames
              held.left = i <= drift_left_frames
              held.down = false
              apply()
              advance_frame()
            end
            held.A = false
            held.left = false
            held.right = true
            held.B = true
            local max_x, lost_form, transitioned = continue_1_fortress_after_mid_candidate(candidate, 900)
            if max_x > best_x and not lost_form then
              best_x = max_x
              best_candidate = candidate
              log_state(
                "post_probe_1_fortress_mid_search_best",
                "candidate=" .. tostring(candidate)
                  .. " wait=" .. tostring(wait_frames)
                  .. " duck=" .. tostring(duck_frames)
                  .. " run=" .. tostring(run_frames)
                  .. " jump=" .. tostring(jump_hold)
                  .. " drift_left=" .. tostring(drift_left_frames)
                  .. " max_x=" .. tostring(max_x)
                  .. " transitioned=" .. tostring(transitioned)
              )
            end
          end
        end
      end
    end
  end

  log_state(
    "post_probe_1_fortress_mid_search_complete",
    "best_candidate=" .. tostring(best_candidate) .. " best_x=" .. tostring(best_x)
  )
end

local function drive_1_fortress_to_flight_checkpoint()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local first_lava_jump_started = false
  local second_lava_jump_started = false
  local second_lava_stair_jump_started = false
  local third_lava_jump_started = false
  local flat_enemy_jump_started = false
  local mid_hazard_jump_started = false
  local second_lava_backup_frames = 0
  local second_lava_drift_left_frames = 0
  local mid_hazard_run_frames = 0
  held.right = true
  held.B = true

  for frame = 1, 2600 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if grounded and memory.readbyte(0xED) > 0 and m.x >= 1740 and m.x <= 1790 then
      held.A = false
      held.B = false
      held.right = false
      held.left = false
      held.down = false
      held.up = false
      apply()
      log_state("post_probe_1_fortress_flight_checkpoint")
      return true
    end

    if memory.readbyte(0xED) == 0 or m.y == 0 or m.x >= 8192 then
      log_state("post_probe_1_fortress_flight_checkpoint_failed")
      return false
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if mid_hazard_run_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      mid_hazard_run_frames = mid_hazard_run_frames - 1
      if mid_hazard_run_frames == 0 then
        jump_frames = post_1_fortress_mid_hazard_jump_frames
        second_lava_drift_left_frames = post_1_fortress_mid_hazard_drift_left_frames
        cooldown = 0
        log_state("post_probe_1_fortress_search_jump_mid_hazard")
      end
    elseif second_lava_backup_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      second_lava_backup_frames = second_lava_backup_frames - 1
      if second_lava_backup_frames == 0 then
        jump_frames = post_1_fortress_second_lava_jump_frames
        second_lava_drift_left_frames = post_1_fortress_second_lava_drift_left_frames
        cooldown = post_1_fortress_second_lava_cooldown_frames
        log_state("post_probe_1_fortress_search_jump_second_lava")
      end
    elseif jump_frames > 0 then
      if second_lava_drift_left_frames > 0 then
        held.right = false
        held.left = true
        second_lava_drift_left_frames = second_lava_drift_left_frames - 1
      else
        held.right = true
        held.left = false
      end
      held.B = true
      held.A = true
      held.down = false
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.left = false
      held.B = true
      held.A = false
      held.down = false
      if grounded then
        if not first_lava_jump_started
            and m.x >= post_1_fortress_first_lava_start
            and m.x <= post_1_fortress_first_lava_end then
          first_lava_jump_started = true
          jump_frames = post_1_fortress_first_lava_jump_frames
          cooldown = 70
          log_state("post_probe_1_fortress_search_jump_first_lava")
        elseif first_lava_jump_started
            and not second_lava_jump_started
            and m.x >= 420
            and m.x <= 455 then
          second_lava_jump_started = true
          second_lava_backup_frames = post_1_fortress_second_lava_backup_frames
          cooldown = 0
          log_state("post_probe_1_fortress_search_backup_second_lava")
        elseif second_lava_jump_started
            and not second_lava_stair_jump_started
            and m.x >= 440
            and m.x <= 470
            and m.y <= 360 then
          second_lava_stair_jump_started = true
          jump_frames = post_1_fortress_second_lava_stair_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = post_1_fortress_second_lava_stair_jump_frames + 20
          log_state("post_probe_1_fortress_search_jump_second_lava_stair")
        elseif second_lava_stair_jump_started
            and not third_lava_jump_started
            and m.x >= 585
            and m.x <= 625
            and m.y <= 360 then
          third_lava_jump_started = true
          jump_frames = post_1_fortress_third_lava_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = post_1_fortress_third_lava_jump_frames + 20
          log_state("post_probe_1_fortress_search_jump_third_lava")
        elseif third_lava_jump_started
            and not flat_enemy_jump_started
            and m.x >= 790
            and m.x <= 850 then
          flat_enemy_jump_started = true
          jump_frames = post_1_fortress_flat_enemy_jump_frames
          second_lava_drift_left_frames = 0
          cooldown = 55
          log_state("post_probe_1_fortress_search_jump_flat_enemy")
        elseif flat_enemy_jump_started
            and not mid_hazard_jump_started
            and m.x >= post_1_fortress_mid_hazard_start
            and m.x <= post_1_fortress_mid_hazard_end then
          mid_hazard_jump_started = true
          mid_hazard_run_frames = post_1_fortress_mid_hazard_run_frames
          log_state("post_probe_1_fortress_search_run_mid_hazard")
        end
      end
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 and jump_frames <= 0 then
        if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 72 and enemy.dy > -64 then
          jump_frames = 28
          cooldown = 42
          log_state("post_probe_1_fortress_search_jump_enemy")
        elseif stuck_frames > 35 then
          jump_frames = 42
          cooldown = 52
          stuck_frames = 0
          log_state("post_probe_1_fortress_search_jump_stuck")
        end
      end
    end

    apply()
    advance_frame()
  end

  log_state("post_probe_1_fortress_flight_checkpoint_timeout")
  return false
end

local function run_1_fortress_flight_candidate(candidate_id, backup_frames, run_frames, jump_frames_setting, flap_frames, up_frames)
  local min_y = mario().y
  local max_x = mario().x
  local entered = false

  for i = 1, backup_frames do
    held.left = true
    held.right = false
    held.B = true
    held.A = false
    held.up = false
    held.down = false
    apply()
    advance_frame()
  end
  for i = 1, run_frames do
    held.left = false
    held.right = true
    held.B = true
    held.A = false
    held.up = false
    held.down = false
    apply()
    advance_frame()
  end
  for i = 1, jump_frames_setting do
    held.left = false
    held.right = true
    held.B = true
    held.A = true
    held.up = false
    held.down = false
    apply()
    advance_frame()
  end
  for i = 1, flap_frames do
    local m = mario()
    if m.y > 0 then
      min_y = math.min(min_y, m.y)
    end
    max_x = math.max(max_x, m.x)
    held.left = false
    held.right = true
    held.B = true
    held.A = (i % 6) <= 2
    held.up = false
    held.down = false
    apply()
    advance_frame()
  end
  for i = 1, up_frames do
    local m = mario()
    if m.y > 0 then
      min_y = math.min(min_y, m.y)
    end
    max_x = math.max(max_x, m.x)
    if m.y == 0 and min_y < 200 then
      entered = true
    end
    held.left = false
    held.right = false
    held.B = false
    held.A = false
    held.up = m.y < 200
    held.down = false
    apply()
    advance_frame()
  end

  held.up = false
  held.A = false
  held.B = false
  held.right = false
  held.left = false
  apply()
  log_state(
    "post_probe_1_fortress_flight_candidate_done",
    "candidate=" .. tostring(candidate_id)
      .. " backup=" .. tostring(backup_frames)
      .. " run=" .. tostring(run_frames)
      .. " jump=" .. tostring(jump_frames_setting)
      .. " flap=" .. tostring(flap_frames)
      .. " up=" .. tostring(up_frames)
      .. " min_y=" .. tostring(min_y)
      .. " max_x=" .. tostring(max_x)
      .. " entered=" .. tostring(entered)
  )
  return min_y, max_x, entered
end

local function run_1_fortress_flight_search()
  if not drive_1_fortress_to_flight_checkpoint() then
    return
  end

  local checkpoint = savestate.create()
  savestate.save(checkpoint)
  local candidate = 0
  local best_candidate = -1
  local best_y = 9999
  local best_x = -1
  local backup_options = {80, 120, 160, 200, 240}
  local run_options = {120, 160, 200, 240, 280}
  local jump_options = {18, 28, 40}
  local flap_options = {120, 180, 240, 300}

  for _, backup_frames in ipairs(backup_options) do
    for _, run_frames in ipairs(run_options) do
      for _, jump_frames_setting in ipairs(jump_options) do
        for _, flap_frames in ipairs(flap_options) do
          candidate = candidate + 1
          if candidate > post_1_fortress_search_limit then
            log_state(
              "post_probe_1_fortress_flight_search_complete",
              "best_candidate=" .. tostring(best_candidate)
                .. " best_y=" .. tostring(best_y)
                .. " best_x=" .. tostring(best_x)
            )
            return
          end
          savestate.load(checkpoint)
          local min_y, max_x, entered = run_1_fortress_flight_candidate(
            candidate,
            backup_frames,
            run_frames,
            jump_frames_setting,
            flap_frames,
            post_1_fortress_flight_up_frames
          )
          if entered or min_y < best_y or (min_y == best_y and max_x > best_x) then
            best_candidate = candidate
            best_y = min_y
            best_x = max_x
            log_state(
              "post_probe_1_fortress_flight_search_best",
              "candidate=" .. tostring(candidate)
                .. " backup=" .. tostring(backup_frames)
                .. " run=" .. tostring(run_frames)
                .. " jump=" .. tostring(jump_frames_setting)
                .. " flap=" .. tostring(flap_frames)
                .. " min_y=" .. tostring(min_y)
                .. " max_x=" .. tostring(max_x)
                .. " entered=" .. tostring(entered)
            )
          end
          if entered then
            log_state("post_probe_1_fortress_flight_search_entered")
            return
          end
        end
      end
    end
  end

  log_state(
    "post_probe_1_fortress_flight_search_complete",
    "best_candidate=" .. tostring(best_candidate)
      .. " best_y=" .. tostring(best_y)
      .. " best_x=" .. tostring(best_x)
  )
end

local function run_1_2_naive_probe()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 256
  local hill_maneuver_started = false
  local hill_delay_frames = 0
  local hill_jump_frames = 0
  local hill_slow_frames = 0
  local late_maneuver_started = false
  local late_delay_frames = 0
  local late_jump_frames = 0
  local late_slow_frames = 0
  local goal_jump_started = false
  local goal_carry_frames = 0
  local goal_recovery_frames = 0
  local goal_recovery_started = false
  local reached_goal_card = false
  held.right = true
  held.B = true
  for frame = 1, 3600 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0
    local first_gap_carry = m.x >= 470 and m.x <= 650 and m.y < 390

    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_2_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end

    if m.x >= 2816 and m.x < 8192 and not reached_goal_card then
      reached_goal_card = true
      log_state("post_probe_1_2_goal_card")
    end

    if m.x >= 8192 or m.y == 0 then
      if reached_goal_card then
        log_state("post_probe_1_2_success_course_clear")
      else
        log_state("post_probe_1_2_bad_state")
      end
      log_state("post_probe_1_2_transition")
      break
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if not hill_maneuver_started and grounded and m.x >= 1180 and m.x <= 1220 then
      hill_maneuver_started = true
      hill_delay_frames = post_1_2_hill_delay_frames
      hill_jump_frames = post_1_2_hill_jump_frames
      hill_slow_frames = post_1_2_hill_slow_frames
      cooldown = hill_delay_frames + hill_jump_frames + 20
      log_state("post_probe_1_2_hill_maneuver")
    end

    if not late_maneuver_started and grounded and m.x >= post_1_2_late_jump_start and m.x <= post_1_2_late_jump_start + 80 then
      late_maneuver_started = true
      late_delay_frames = post_1_2_late_delay_frames
      late_jump_frames = post_1_2_late_jump_frames
      late_slow_frames = post_1_2_late_slow_frames
      cooldown = late_delay_frames + late_jump_frames + 20
      log_state("post_probe_1_2_late_maneuver")
    end

    if not goal_recovery_started and m.x >= 2770 then
      goal_recovery_started = true
      goal_recovery_frames = 150
      cooldown = 150
      log_state("post_probe_1_2_goal_recovery")
    end

    if not goal_jump_started and m.x >= post_1_2_goal_jump_start and m.x <= post_1_2_goal_jump_start + 120 then
      goal_jump_started = true
      goal_carry_frames = post_1_2_goal_carry_frames
      log_state("post_probe_1_2_goal_carry")
    end

    if hill_delay_frames > 0 then
      held.right = true
      held.B = hill_slow_frames <= 0
      held.A = false
      hill_delay_frames = hill_delay_frames - 1
      if hill_slow_frames > 0 then
        hill_slow_frames = hill_slow_frames - 1
      end
    elseif hill_jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      hill_jump_frames = hill_jump_frames - 1
    elseif late_delay_frames > 0 then
      held.right = true
      held.B = late_slow_frames <= 0
      held.A = false
      late_delay_frames = late_delay_frames - 1
      if late_slow_frames > 0 then
        late_slow_frames = late_slow_frames - 1
      end
    elseif late_jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      late_jump_frames = late_jump_frames - 1
    elseif goal_carry_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      goal_carry_frames = goal_carry_frames - 1
    elseif goal_recovery_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = goal_recovery_frames > 90
      goal_recovery_frames = goal_recovery_frames - 1
    elseif jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.B = true
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if m.x >= 500 and m.x <= 590 then
          jump_frames = 42
          cooldown = 56
          log_state("post_probe_1_2_jump_first_gap")
        elseif grounded and m.x >= post_1_2_goal_jump_start and m.x <= post_1_2_goal_jump_start + 90 then
          jump_frames = post_1_2_goal_jump_frames
          cooldown = 80
          log_state("post_probe_1_2_jump_goal_card")
        elseif enemy ~= nil
            and enemy.dx >= post_1_2_enemy_min_dx
            and enemy.dx < post_1_2_enemy_max_dx
            and enemy.dy > -45 then
          if m.x >= post_1_2_hill_enemy_start and m.x <= post_1_2_hill_enemy_end then
            jump_frames = post_1_2_hill_enemy_jump_frames
          else
            jump_frames = post_1_2_enemy_jump_frames
          end
          cooldown = 42
          log_state("post_probe_1_2_jump_enemy")
        elseif stuck_frames > 45 and m.x >= 320 and m.x <= 370 then
          jump_frames = 54
          cooldown = 72
          stuck_frames = 0
          log_state("post_probe_1_2_jump_hill_pipe")
        elseif stuck_frames > 45 then
          jump_frames = 32
          cooldown = 48
          stuck_frames = 0
          log_state("post_probe_1_2_jump_stuck")
        end
      end
    end

    if first_gap_carry then
      held.A = true
    end
    if goal_recovery_frames <= 0 then
      held.left = false
    end
    apply()
    if frame % 30 == 0 then
      log_state("post_probe_1_2_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  apply()
  advance(240, "post_probe_1_2_after")
  log_state("post_probe_1_2_done")
end

local function run_1_4_naive_probe()
  local jump_frames = 64
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 256
  local reached_goal_card = false
  local goal_carry_frames = 0
  local first_jump_started = false
  local first_platform_landed = false
  local first_platform_ride_frames = 0
  local first_platform_landed_frame = 0
  local second_jump_started = false
  local second_jump_pulse_frames = 0
  local hammer_attack_started = false
  local hammer_attack_frames = 0
  local second_gap_started = false
  local second_gap_frames = 0
  local third_gap_started = false
  local third_platform_wait_frames = 0
  local fourth_gap_started = false
  local fifth_platform_ride_started = false
  local fifth_platform_ride_frames = 0
  local sixth_gap_started = false
  local seventh_gap_started = false
  local eighth_gap_started = false
  local eighth_platform_wait_frames = 0
  local ninth_gap_started = false
  local tenth_gap_started = false
  local eleventh_gap_started = false
  local twelfth_gap_started = false
  local thirteenth_gap_started = false
  local fourteenth_gap_started = false
  local fifteenth_gap_started = false
  local sixteenth_gap_started = false
  local seventeenth_gap_started = false
  local eighteenth_gap_started = false
  local nineteenth_gap_started = false
  local twentieth_gap_started = false
  local twentyfirst_gap_started = false
  local twentysecond_gap_started = false
  local twentythird_gap_started = false
  local twentyfourth_gap_started = false
  local twentyfifth_gap_started = false
  local twentysecond_platform_ride_started = false
  local tenth_platform_ride_started = false
  local tenth_platform_ride_frames = 0
  local twelfth_platform_ride_started = false
  local twelfth_platform_ride_frames = 0
  local fourteenth_platform_wait_frames = 0
  local seventeenth_platform_ride_frames = 0
  local nineteenth_drop_frames = 0
  local twentysecond_platform_ride_frames = 0
  local twentyfourth_recovery_started = false
  local twentyfourth_recovery_frames = 0
  local twentyfourth_post_flutter_frames = 0
  local twentyfourth_late_brake_started = false
  local twentyfourth_late_brake_frames = 0
  local exit_pipe_entry_started = false
  local exit_pipe_align_frames = 0
  local exit_pipe_entry_frames = 0
  local exit_goal_jump_started = false
  local jump_mode = ""
  local first_platform_ride_started = false
  local platform_ride_frames = 0
  local first_platform_exit_frames = 0
  held.right = true
  held.B = true
  for frame = 1, 4200 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_4_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end

    if m.x >= 2700 and m.x < 8192 and not reached_goal_card then
      reached_goal_card = true
      goal_carry_frames = 90
      log_state("post_probe_1_4_goal_card")
    end

    if m.x >= 8192 or (m.y == 0 and not exit_pipe_entry_started) then
      if reached_goal_card then
        log_state("post_probe_1_4_success_course_clear")
      else
        log_state("post_probe_1_4_bad_state")
      end
      log_state("post_probe_1_4_transition")
      break
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if post_1_4_seventh_gap_air_trigger
        and sixth_gap_started
        and not seventh_gap_started
        and not grounded
        and m.x >= post_1_4_seventh_gap_air_trigger_min_x
        and m.x <= post_1_4_seventh_gap_air_trigger_max_x
        and m.y >= post_1_4_seventh_gap_air_trigger_min_y
        and m.y <= post_1_4_seventh_gap_air_trigger_max_y then
      seventh_gap_started = true
      jump_frames = post_1_4_seventh_gap_jump_frames
      jump_mode = "seventh_gap"
      cooldown = 55
      stuck_frames = 0
      log_state("post_probe_1_4_jump_seventh_gap_air")
    end

    if not exit_pipe_entry_started
        and twentyfifth_gap_started
        and grounded
        and m.x >= post_1_4_exit_pipe_trigger_min_x
        and m.x <= post_1_4_exit_pipe_trigger_max_x
        and m.y <= post_1_4_exit_pipe_trigger_max_y then
      exit_pipe_entry_started = true
      exit_pipe_align_frames = post_1_4_exit_pipe_align_frames
      exit_pipe_entry_frames = post_1_4_exit_pipe_hold_down_frames
      jump_frames = 0
      jump_mode = ""
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      log_state("post_probe_1_4_exit_pipe_entry")
    end

    if exit_pipe_entry_started
        and not exit_goal_jump_started
        and grounded
        and m.x >= post_1_4_exit_goal_jump_trigger_min_x
        and m.x <= post_1_4_exit_goal_jump_trigger_max_x
        and m.y >= 360 then
      exit_goal_jump_started = true
      reached_goal_card = true
      jump_frames = post_1_4_exit_goal_jump_frames
      jump_mode = "exit_goal_card"
      cooldown = 0
      stuck_frames = 0
      log_state("post_probe_1_4_exit_goal_jump")
    end

    if jump_mode == "tenth_gap"
        and not tenth_platform_ride_started
        and m.x >= 915
        and m.x <= 955
        and m.y >= 260
        and m.y <= 320 then
      tenth_platform_ride_started = true
      tenth_platform_ride_frames = post_1_4_tenth_platform_ride_frames
      jump_frames = 0
      jump_mode = ""
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      log_state("post_probe_1_4_tenth_platform_ride")
    end

    if jump_mode == "twelfth_gap"
        and not twelfth_platform_ride_started
        and m.x >= 1085
        and m.x <= 1115
        and m.y >= 340
        and m.y <= 390 then
      twelfth_platform_ride_started = true
      twelfth_platform_ride_frames = post_1_4_twelfth_platform_ride_frames
      jump_frames = 0
      jump_mode = ""
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      log_state("post_probe_1_4_twelfth_platform_ride")
    end

    if not first_platform_ride_started and grounded and m.x >= 240 and m.x <= 310 and m.y >= 300 and m.y <= 340 then
      first_platform_ride_started = true
      platform_ride_frames = 12
      cooldown = 0
      log_state("post_probe_1_4_first_platform_ride")
    end

    if not twentyfourth_recovery_started
        and twentyfourth_gap_started
        and post_1_4_twentyfourth_recovery_frames > 0
        and memory.readbyte(0xED) < 3
        and m.x >= 1850
        and m.x <= 1900
        and m.y >= 280
        and m.y <= 370 then
      twentyfourth_recovery_started = true
      twentyfourth_recovery_frames = post_1_4_twentyfourth_recovery_frames
      jump_frames = 0
      jump_mode = ""
      log_state("post_probe_1_4_twentyfourth_recovery")
    end

    if jump_mode == "twentysecond_gap"
        and not twentysecond_platform_ride_started
        and m.x >= 1600
        and m.x <= 1645
        and m.y >= 305
        and m.y <= 350 then
      twentysecond_platform_ride_started = true
      twentysecond_platform_ride_frames = post_1_4_twentysecond_platform_ride_frames
      jump_frames = 0
      jump_mode = ""
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      log_state("post_probe_1_4_twentysecond_platform_ride")
    end

    held.down = false
    if exit_pipe_align_frames > 0 then
      held.right = post_1_4_exit_pipe_align_direction == "right"
      held.left = post_1_4_exit_pipe_align_direction == "left"
      held.B = false
      held.A = false
      exit_pipe_align_frames = exit_pipe_align_frames - 1
    elseif exit_pipe_entry_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = true
      exit_pipe_entry_frames = exit_pipe_entry_frames - 1
    elseif fourteenth_platform_wait_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      fourteenth_platform_wait_frames = fourteenth_platform_wait_frames - 1
      if fourteenth_platform_wait_frames == 0 then
        jump_frames = post_1_4_fourteenth_gap_jump_frames
        jump_mode = "fourteenth_gap"
        log_state("post_probe_1_4_jump_fourteenth_gap")
      end
    elseif twentysecond_platform_ride_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = post_1_4_twentysecond_platform_hold_a > 0 and (twentysecond_platform_ride_frames % 8) >= 4
      twentysecond_platform_ride_frames = twentysecond_platform_ride_frames - 1
    elseif twentyfourth_post_flutter_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      if not twentyfourth_late_brake_started
          and m.x >= post_1_4_twentyfourth_late_brake_x
          and m.y >= post_1_4_twentyfourth_late_brake_y
          and post_1_4_twentyfourth_late_brake_frames > 0 then
        twentyfourth_late_brake_started = true
        twentyfourth_late_brake_frames = post_1_4_twentyfourth_late_brake_frames
        log_state("post_probe_1_4_twentyfourth_late_brake")
      end
      if twentyfourth_late_brake_frames > 0 then
        held.right = false
        held.left = true
        held.B = false
        twentyfourth_late_brake_frames = twentyfourth_late_brake_frames - 1
      end
      if not twentyfifth_gap_started
          and m.x >= post_1_4_twentyfifth_gap_trigger_min_x
          and m.x <= post_1_4_twentyfifth_gap_trigger_max_x
          and m.y >= 380 then
        twentyfifth_gap_started = true
        twentyfourth_post_flutter_frames = 0
        jump_frames = post_1_4_twentyfifth_gap_jump_frames
        jump_mode = "twentyfifth_gap"
        log_state("post_probe_1_4_jump_twentyfifth_gap")
      end
      if twentyfourth_post_flutter_frames <= post_1_4_twentyfourth_post_tail_release_start
          and twentyfourth_post_flutter_frames >= post_1_4_twentyfourth_post_tail_release_end then
        held.B = false
      end
      if post_1_4_twentyfourth_post_tail_pulse_period > 0
          and (twentyfourth_post_flutter_frames % post_1_4_twentyfourth_post_tail_pulse_period) < post_1_4_twentyfourth_post_tail_pulse_release_frames then
        held.B = false
      end
      held.A = (twentyfourth_post_flutter_frames % post_1_4_twentyfourth_flutter_period) < post_1_4_twentyfourth_flutter_on_frames
      twentyfourth_post_flutter_frames = twentyfourth_post_flutter_frames - 1
    elseif twentyfourth_recovery_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      twentyfourth_recovery_frames = twentyfourth_recovery_frames - 1
    elseif nineteenth_drop_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      nineteenth_drop_frames = nineteenth_drop_frames - 1
    elseif seventeenth_platform_ride_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      seventeenth_platform_ride_frames = seventeenth_platform_ride_frames - 1
      if seventeenth_platform_ride_frames == 0 then
        jump_frames = post_1_4_seventeenth_gap_jump_frames
        jump_mode = "seventeenth_gap"
        log_state("post_probe_1_4_jump_seventeenth_gap")
      end
    elseif twelfth_platform_ride_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      twelfth_platform_ride_frames = twelfth_platform_ride_frames - 1
      if twelfth_platform_ride_frames == 0 then
        jump_frames = post_1_4_twelfth_platform_exit_jump_frames
        jump_mode = "twelfth_platform_exit"
        log_state("post_probe_1_4_twelfth_platform_exit_jump")
      end
    elseif tenth_platform_ride_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      tenth_platform_ride_frames = tenth_platform_ride_frames - 1
      if tenth_platform_ride_frames == 0 then
        jump_frames = post_1_4_tenth_platform_exit_jump_frames
        jump_mode = "tenth_platform_exit"
        log_state("post_probe_1_4_tenth_platform_exit_jump")
      end
    elseif eighth_platform_wait_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      eighth_platform_wait_frames = eighth_platform_wait_frames - 1
    elseif fifth_platform_ride_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      fifth_platform_ride_frames = fifth_platform_ride_frames - 1
    elseif platform_ride_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      platform_ride_frames = platform_ride_frames - 1
      if platform_ride_frames == 0 then
        first_platform_exit_frames = 58
        log_state("post_probe_1_4_first_platform_exit_jump")
      end
    elseif first_platform_exit_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = true
      first_platform_exit_frames = first_platform_exit_frames - 1
    elseif goal_carry_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      goal_carry_frames = goal_carry_frames - 1
    elseif second_gap_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = true
      second_gap_frames = second_gap_frames - 1
    elseif third_platform_wait_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      third_platform_wait_frames = third_platform_wait_frames - 1
    elseif jump_frames > 0 then
      if jump_mode == "eighth_gap" then
        held.right = jump_frames > (post_1_4_eighth_gap_jump_frames - post_1_4_eighth_gap_right_frames)
        held.left = jump_frames <= post_1_4_eighth_gap_left_frames
        held.B = false
      elseif jump_mode == "ninth_gap" then
        held.right = jump_frames > (post_1_4_ninth_gap_jump_frames - post_1_4_ninth_gap_right_frames)
        held.left = jump_frames <= post_1_4_ninth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "tenth_gap" then
        held.right = jump_frames > (post_1_4_tenth_gap_jump_frames - post_1_4_tenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_tenth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "tenth_platform_exit" then
        held.right = jump_frames > (post_1_4_tenth_platform_exit_jump_frames - post_1_4_tenth_platform_exit_right_frames)
        held.left = false
        held.B = held.right
      elseif jump_mode == "eleventh_gap" then
        held.right = jump_frames > (post_1_4_eleventh_gap_jump_frames - post_1_4_eleventh_gap_right_frames)
        held.left = jump_frames <= post_1_4_eleventh_gap_left_frames
        held.B = held.right
      elseif jump_mode == "twelfth_gap" then
        held.right = jump_frames > (post_1_4_twelfth_gap_jump_frames - post_1_4_twelfth_gap_right_frames)
        held.left = jump_frames <= post_1_4_twelfth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "twelfth_platform_exit" then
        held.right = jump_frames > (post_1_4_twelfth_platform_exit_jump_frames - post_1_4_twelfth_platform_exit_right_frames)
        held.left = false
        held.B = held.right
      elseif jump_mode == "thirteenth_gap" then
        held.right = jump_frames > (post_1_4_thirteenth_gap_jump_frames - post_1_4_thirteenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_thirteenth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "fourteenth_gap" then
        held.right = jump_frames > (post_1_4_fourteenth_gap_jump_frames - post_1_4_fourteenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_fourteenth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "fifteenth_gap" then
        held.right = jump_frames > (post_1_4_fifteenth_gap_jump_frames - post_1_4_fifteenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_fifteenth_gap_left_frames
        held.B = false
      elseif jump_mode == "sixteenth_gap" then
        held.right = jump_frames > (post_1_4_sixteenth_gap_jump_frames - post_1_4_sixteenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_sixteenth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "seventeenth_gap" then
        held.right = jump_frames > (post_1_4_seventeenth_gap_jump_frames - post_1_4_seventeenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_seventeenth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "eighteenth_gap" then
        held.right = jump_frames > (post_1_4_eighteenth_gap_jump_frames - post_1_4_eighteenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_eighteenth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "nineteenth_gap" then
        held.right = jump_frames > (post_1_4_nineteenth_gap_jump_frames - post_1_4_nineteenth_gap_right_frames)
        held.left = jump_frames <= post_1_4_nineteenth_gap_left_frames
        held.B = false
      elseif jump_mode == "twentieth_gap" then
        held.right = jump_frames > (post_1_4_twentieth_gap_jump_frames - post_1_4_twentieth_gap_right_frames)
        held.left = jump_frames <= post_1_4_twentieth_gap_left_frames
        held.B = held.right
      elseif jump_mode == "twentyfirst_gap" then
        held.right = jump_frames > (post_1_4_twentyfirst_gap_jump_frames - post_1_4_twentyfirst_gap_right_frames)
        held.left = jump_frames <= post_1_4_twentyfirst_gap_left_frames
        held.B = held.right
      elseif jump_mode == "twentysecond_gap" then
        held.right = jump_frames > (post_1_4_twentysecond_gap_jump_frames - post_1_4_twentysecond_gap_right_frames)
        held.left = jump_frames <= post_1_4_twentysecond_gap_left_frames
        held.B = held.right
      elseif jump_mode == "twentysecond_platform_exit" then
        held.right = jump_frames > (post_1_4_twentysecond_platform_exit_jump_frames - post_1_4_twentysecond_platform_exit_right_frames)
        held.left = false
        held.B = held.right
      elseif jump_mode == "twentythird_gap" then
        held.right = jump_frames > (post_1_4_twentythird_gap_jump_frames - post_1_4_twentythird_gap_right_frames)
        held.left = jump_frames <= post_1_4_twentythird_gap_left_frames
        held.B = held.right
      elseif jump_mode == "twentyfourth_gap" then
        held.right = jump_frames > (post_1_4_twentyfourth_gap_jump_frames - post_1_4_twentyfourth_gap_right_frames)
        held.left = jump_frames <= post_1_4_twentyfourth_gap_left_frames
        held.B = held.right
        if jump_frames <= post_1_4_twentyfourth_tail_release_start
            and jump_frames >= post_1_4_twentyfourth_tail_release_end then
          held.B = false
        end
      elseif jump_mode == "twentyfifth_gap" then
        held.right = jump_frames > (post_1_4_twentyfifth_gap_jump_frames - post_1_4_twentyfifth_gap_right_frames)
        held.left = false
        held.B = held.right
      else
        held.right = true
        held.B = true
      end
      held.A = true
      if jump_mode == "twentyfourth_gap" then
        held.A = jump_frames > (post_1_4_twentyfourth_gap_jump_frames - post_1_4_twentyfourth_initial_hold_frames)
          or (jump_frames % post_1_4_twentyfourth_flutter_period) < post_1_4_twentyfourth_flutter_on_frames
      end
      jump_frames = jump_frames - 1
      if jump_frames <= 0 then
        if jump_mode == "twentyfourth_gap"
            and memory.readbyte(0xED) == 3
            and post_1_4_twentyfourth_post_flutter_frames > 0 then
          twentyfourth_post_flutter_frames = post_1_4_twentyfourth_post_flutter_frames
          log_state("post_probe_1_4_twentyfourth_post_flutter")
        end
        if jump_mode == "eighth_gap" or jump_mode == "ninth_gap" or jump_mode == "tenth_gap" or jump_mode == "tenth_platform_exit" or jump_mode == "eleventh_gap" or jump_mode == "twelfth_gap" or jump_mode == "twelfth_platform_exit" or jump_mode == "thirteenth_gap" or jump_mode == "fourteenth_gap" or jump_mode == "fifteenth_gap" or jump_mode == "sixteenth_gap" or jump_mode == "seventeenth_gap" or jump_mode == "eighteenth_gap" or jump_mode == "nineteenth_gap" or jump_mode == "twentieth_gap" or jump_mode == "twentyfirst_gap" or jump_mode == "twentysecond_gap" or jump_mode == "twentysecond_platform_exit" or jump_mode == "twentythird_gap" or jump_mode == "twentyfourth_gap" or jump_mode == "twentyfifth_gap" then
          held.left = false
        end
        jump_mode = ""
      end
    else
      held.right = true
      held.B = true
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if not second_gap_started and m.x >= 420 and m.x <= 455 then
          second_gap_started = true
          second_gap_frames = 46
          cooldown = 0
          log_state("post_probe_1_4_jump_second_gap")
        elseif second_gap_started and not third_gap_started and m.x >= 455 and m.x <= 480 then
          third_gap_started = true
          third_platform_wait_frames = 35
          cooldown = 0
          log_state("post_probe_1_4_third_platform_wait")
        elseif third_gap_started and not fourth_gap_started and m.x >= 450 and m.x <= 475 then
          fourth_gap_started = true
          jump_frames = 26
          cooldown = 50
          log_state("post_probe_1_4_jump_fourth_gap")
        elseif fourth_gap_started
            and not fifth_platform_ride_started
            and m.x >= 485
            and m.x <= 530
            and m.y >= 280 then
          fifth_platform_ride_started = true
          fifth_platform_ride_frames = 20
          cooldown = 0
          log_state("post_probe_1_4_fifth_platform_ride")
        elseif fifth_platform_ride_started
            and not sixth_gap_started
            and m.x >= 508
            and m.x <= 535
            and m.y >= 360 then
          sixth_gap_started = true
          jump_frames = post_1_4_sixth_gap_jump_frames
          cooldown = 0
          log_state("post_probe_1_4_jump_sixth_gap")
        elseif sixth_gap_started
            and not seventh_gap_started
            and m.x >= post_1_4_seventh_gap_trigger_min_x
            and m.x <= post_1_4_seventh_gap_trigger_max_x
            and m.y >= post_1_4_seventh_gap_trigger_min_y
            and m.y <= post_1_4_seventh_gap_trigger_max_y then
          seventh_gap_started = true
          jump_frames = post_1_4_seventh_gap_jump_frames
          cooldown = 55
          log_state("post_probe_1_4_jump_seventh_gap")
        elseif seventh_gap_started
            and not eighth_gap_started
            and m.x >= 790
            and m.x <= 825
            and m.y >= 320
            and m.y <= 360 then
          eighth_gap_started = true
          jump_frames = post_1_4_eighth_gap_jump_frames
          jump_mode = "eighth_gap"
          cooldown = 0
          log_state("post_probe_1_4_jump_eighth_gap")
        elseif eighth_gap_started
            and not ninth_gap_started
            and m.x >= post_1_4_ninth_gap_trigger_min_x
            and m.x <= post_1_4_ninth_gap_trigger_max_x
            and m.y >= 320
            and m.y <= 360 then
          ninth_gap_started = true
          jump_frames = post_1_4_ninth_gap_jump_frames
          jump_mode = "ninth_gap"
          cooldown = 0
          log_state("post_probe_1_4_jump_ninth_gap")
        elseif ninth_gap_started
            and not tenth_gap_started
            and m.x >= post_1_4_tenth_gap_trigger_min_x
            and m.x <= post_1_4_tenth_gap_trigger_max_x
            and m.y >= 330
            and m.y <= 370 then
          tenth_gap_started = true
          jump_frames = post_1_4_tenth_gap_jump_frames
          jump_mode = "tenth_gap"
          cooldown = 0
          log_state("post_probe_1_4_jump_tenth_gap")
        elseif tenth_gap_started
            and not eleventh_gap_started
            and m.x >= post_1_4_eleventh_gap_trigger_min_x
            and m.x <= post_1_4_eleventh_gap_trigger_max_x
            and m.y >= 350
            and m.y <= 385 then
          eleventh_gap_started = true
          jump_frames = post_1_4_eleventh_gap_jump_frames
          jump_mode = "eleventh_gap"
          cooldown = 0
          log_state("post_probe_1_4_jump_eleventh_gap")
        elseif eleventh_gap_started
            and not twelfth_gap_started
            and m.x >= post_1_4_twelfth_gap_trigger_min_x
            and m.x <= post_1_4_twelfth_gap_trigger_max_x
            and m.y >= 300
            and m.y <= 340 then
          twelfth_gap_started = true
          jump_frames = post_1_4_twelfth_gap_jump_frames
          jump_mode = "twelfth_gap"
          cooldown = 0
          log_state("post_probe_1_4_jump_twelfth_gap")
        elseif twelfth_gap_started
            and not thirteenth_gap_started
            and m.x >= post_1_4_thirteenth_gap_trigger_min_x
            and m.x <= post_1_4_thirteenth_gap_trigger_max_x
            and m.y >= 300
            and m.y <= 385 then
          thirteenth_gap_started = true
          jump_frames = post_1_4_thirteenth_gap_jump_frames
          jump_mode = "thirteenth_gap"
          cooldown = 0
          log_state("post_probe_1_4_jump_thirteenth_gap")
        elseif thirteenth_gap_started
            and not fourteenth_gap_started
            and m.x >= post_1_4_fourteenth_gap_trigger_min_x
            and m.x <= post_1_4_fourteenth_gap_trigger_max_x
            and m.y >= 340
            and m.y <= 370 then
          fourteenth_gap_started = true
          if post_1_4_fourteenth_gap_wait_frames > 0 then
            fourteenth_platform_wait_frames = post_1_4_fourteenth_gap_wait_frames
            log_state("post_probe_1_4_fourteenth_wait")
          else
            jump_frames = post_1_4_fourteenth_gap_jump_frames
            jump_mode = "fourteenth_gap"
            log_state("post_probe_1_4_jump_fourteenth_gap")
          end
          cooldown = 0
        elseif fourteenth_gap_started
            and not fifteenth_gap_started
            and grounded
            and m.x >= post_1_4_fifteenth_gap_trigger_min_x
            and m.x <= post_1_4_fifteenth_gap_trigger_max_x
            and m.y >= 250
            and m.y <= 290 then
          fifteenth_gap_started = true
          jump_frames = post_1_4_fifteenth_gap_jump_frames
          jump_mode = "fifteenth_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_fifteenth_gap")
        elseif fifteenth_gap_started
            and not sixteenth_gap_started
            and grounded
            and m.x >= post_1_4_sixteenth_gap_trigger_min_x
            and m.x <= post_1_4_sixteenth_gap_trigger_max_x
            and m.y >= 320
            and m.y <= 350 then
          sixteenth_gap_started = true
          jump_frames = post_1_4_sixteenth_gap_jump_frames
          jump_mode = "sixteenth_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_sixteenth_gap")
        elseif sixteenth_gap_started
            and not seventeenth_gap_started
            and grounded
            and m.x >= post_1_4_seventeenth_gap_trigger_min_x
            and m.x <= post_1_4_seventeenth_gap_trigger_max_x
            and m.y >= 300
            and m.y <= 345 then
          seventeenth_gap_started = true
          if post_1_4_seventeenth_gap_ride_frames > 0 then
            seventeenth_platform_ride_frames = post_1_4_seventeenth_gap_ride_frames
            log_state("post_probe_1_4_seventeenth_platform_ride")
          else
            jump_frames = post_1_4_seventeenth_gap_jump_frames
            jump_mode = "seventeenth_gap"
            log_state("post_probe_1_4_jump_seventeenth_gap")
          end
          cooldown = 0
          stuck_frames = 0
        elseif seventeenth_gap_started
            and not eighteenth_gap_started
            and grounded
            and m.x >= post_1_4_eighteenth_gap_trigger_min_x
            and m.x <= post_1_4_eighteenth_gap_trigger_max_x
            and m.y >= 260
            and m.y <= 345 then
          eighteenth_gap_started = true
          jump_frames = post_1_4_eighteenth_gap_jump_frames
          jump_mode = "eighteenth_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_eighteenth_gap")
        elseif eighteenth_gap_started
            and not nineteenth_gap_started
            and grounded
            and m.x >= post_1_4_nineteenth_gap_trigger_min_x
            and m.x <= post_1_4_nineteenth_gap_trigger_max_x
            and m.y >= 260
            and m.y <= 290 then
          nineteenth_gap_started = true
          if post_1_4_nineteenth_gap_drop_frames > 0 then
            nineteenth_drop_frames = post_1_4_nineteenth_gap_drop_frames
            log_state("post_probe_1_4_nineteenth_drop")
          else
            jump_frames = post_1_4_nineteenth_gap_jump_frames
            jump_mode = "nineteenth_gap"
            log_state("post_probe_1_4_jump_nineteenth_gap")
          end
          cooldown = 0
          stuck_frames = 0
        elseif nineteenth_gap_started
            and not twentieth_gap_started
            and grounded
            and m.x >= post_1_4_twentieth_gap_trigger_min_x
            and m.x <= post_1_4_twentieth_gap_trigger_max_x
            and m.y >= 260
            and m.y <= 290 then
          twentieth_gap_started = true
          jump_frames = post_1_4_twentieth_gap_jump_frames
          jump_mode = "twentieth_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_twentieth_gap")
        elseif twentieth_gap_started
            and not twentyfirst_gap_started
            and grounded
            and m.x >= post_1_4_twentyfirst_gap_trigger_min_x
            and m.x <= post_1_4_twentyfirst_gap_trigger_max_x
            and m.y >= 240
            and m.y <= 275 then
          twentyfirst_gap_started = true
          jump_frames = post_1_4_twentyfirst_gap_jump_frames
          jump_mode = "twentyfirst_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_twentyfirst_gap")
        elseif twentyfirst_gap_started
            and not twentysecond_gap_started
            and grounded
            and m.x >= post_1_4_twentysecond_gap_trigger_min_x
            and m.x <= post_1_4_twentysecond_gap_trigger_max_x
            and m.y >= 350
            and m.y <= 385 then
          twentysecond_gap_started = true
          jump_frames = post_1_4_twentysecond_gap_jump_frames
          jump_mode = "twentysecond_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_twentysecond_gap")
        elseif twentysecond_gap_started
            and not twentythird_gap_started
            and grounded
            and m.x >= post_1_4_twentythird_gap_trigger_min_x
            and m.x <= post_1_4_twentythird_gap_trigger_max_x
            and m.y >= 360
            and m.y <= 390 then
          twentythird_gap_started = true
          jump_frames = post_1_4_twentythird_gap_jump_frames
          jump_mode = "twentythird_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_twentythird_gap")
        elseif twentythird_gap_started
            and not twentyfourth_gap_started
            and grounded
            and m.x >= post_1_4_twentyfourth_gap_trigger_min_x
            and m.x <= post_1_4_twentyfourth_gap_trigger_max_x
            and m.y >= 320
            and m.y <= 350 then
          twentyfourth_gap_started = true
          jump_frames = post_1_4_twentyfourth_gap_jump_frames
          jump_mode = "twentyfourth_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_twentyfourth_gap")
        elseif twentyfourth_gap_started
            and not twentyfifth_gap_started
            and grounded
            and m.x >= post_1_4_twentyfifth_gap_trigger_min_x
            and m.x <= post_1_4_twentyfifth_gap_trigger_max_x
            and m.y >= 340
            and m.y <= 390 then
          twentyfifth_gap_started = true
          jump_frames = post_1_4_twentyfifth_gap_jump_frames
          jump_mode = "twentyfifth_gap"
          cooldown = 0
          stuck_frames = 0
          log_state("post_probe_1_4_jump_twentyfifth_gap")
        elseif not twelfth_gap_started
            and enemy ~= nil
            and enemy.id ~= 54
            and enemy.dx >= 0
            and enemy.dx < 90
            and enemy.dy > -55 then
          jump_frames = 24
          cooldown = 36
          log_state("post_probe_1_4_jump_enemy")
        elseif not fourteenth_gap_started and stuck_frames > 35 then
          jump_frames = 42
          cooldown = 52
          stuck_frames = 0
          log_state("post_probe_1_4_jump_stuck")
        end
      end
    end

    apply()
    if frame % 30 == 0 then
      log_state("post_probe_1_4_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  held.left = false
  held.down = false
  held.up = false
  apply()
  advance(post_1_4_after_frames, "post_probe_1_4_after")
  log_state("post_probe_1_4_done")
end

local function run_1_5_naive_probe()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 256
  local reached_goal_card = false
  local goal_carry_frames = 0
  local hammer_attack_started = false
  local hammer_attack_frames = 0
  local ground_attack_started = false
  local ground_attack_frames = 0
  local under_bop_frames = 0
  local post_kill_frames = 0
  local collect_chest_started = false
  held.right = true
  held.B = true
  for frame = 1, 4200 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local flank_enemy = nearest_enemy_between(m, -120, 20)
    local roamer_alive = has_active_enemy_id(-127)
    local grounded = m.air == 0

    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_5_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end

    if m.x >= 2600 and m.x < 8192 and not reached_goal_card then
      reached_goal_card = true
      goal_carry_frames = 120
      log_state("post_probe_1_5_goal_card")
    end

    if m.x >= 8192 or m.y == 0 then
      if reached_goal_card or memory.readbyte(0xED) > 0 or memory.readbyte(0x7D81) ~= 0 then
        log_state("post_probe_1_5_success_course_clear")
      else
        log_state("post_probe_1_5_bad_state")
      end
      log_state("post_probe_1_5_transition")
      break
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if not hammer_attack_started
        and grounded
        and m.y <= 330
        and m.x >= 175
        and m.x <= 215 then
      hammer_attack_started = true
      hammer_attack_frames = post_1_5_roamer_platform_attack_frames
      cooldown = 110
      log_state("post_probe_1_5_hammer_attack")
    end

    if not ground_attack_started
        and grounded
        and m.x >= 208
        and m.x <= 244
        and m.y >= 360
        and flank_enemy ~= nil
        and math.abs(flank_enemy.dy) < 55 then
      ground_attack_started = true
      ground_attack_frames = post_1_5_roamer_ground_attack_frames
      cooldown = post_1_5_roamer_ground_attack_frames + 20
      log_state(
        "post_probe_1_5_ground_tail_attack",
        "flank_enemy_dx=" .. tostring(flank_enemy.dx) .. " flank_enemy_dy=" .. tostring(flank_enemy.dy)
      )
    end

    if under_bop_frames == 0
        and grounded
        and enemy ~= nil
        and enemy.id == -127
        and enemy.dy < -50
        and enemy.dy > -130
        and math.abs(enemy.dx) < 28 then
      under_bop_frames = post_1_5_roamer_under_bop_frames
      ground_attack_frames = 0
      hammer_attack_frames = 0
      cooldown = post_1_5_roamer_under_bop_frames + 45
      log_state("post_probe_1_5_under_bop")
    end

    if hammer_attack_started and not roamer_alive and memory.readbyte(0xED) > 0 then
      post_kill_frames = post_kill_frames + 1
    else
      post_kill_frames = 0
    end

    if not collect_chest_started and post_kill_frames >= 12 then
      collect_chest_started = true
      ground_attack_frames = 0
      hammer_attack_frames = 0
      under_bop_frames = 0
      cooldown = 90
      log_state("post_probe_1_5_collect_chest")
    end

    held.down = false
    held.left = false
    if goal_carry_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      goal_carry_frames = goal_carry_frames - 1
    elseif collect_chest_started then
      held.right = false
      held.left = m.x > 42
      held.B = false
      held.A = false
    elseif under_bop_frames > 0 then
      held.right = post_1_5_roamer_under_bop_direction == "right"
      held.left = post_1_5_roamer_under_bop_direction == "left"
      held.B = false
      held.A = true
      under_bop_frames = under_bop_frames - 1
    elseif ground_attack_frames > 0 then
      held.right = false
      held.left = true
      held.A = false
      held.B = ground_attack_frames <= (
        post_1_5_roamer_ground_attack_frames - post_1_5_roamer_ground_b_release_frames
      )
      ground_attack_frames = ground_attack_frames - 1
    elseif hammer_attack_frames > 0 then
      held.right = false
      held.left = false
      if post_1_5_roamer_platform_direction == "left" then
        held.left = true
      elseif post_1_5_roamer_platform_direction == "right" then
        held.right = true
      end
      held.A = false
      held.B = hammer_attack_frames <= (
        post_1_5_roamer_platform_attack_frames - post_1_5_roamer_platform_b_release_frames
      )
      hammer_attack_frames = hammer_attack_frames - 1
    elseif jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.B = true
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if m.x >= 2520 then
          jump_frames = 70
          cooldown = 90
          log_state("post_probe_1_5_jump_goal_card")
        elseif enemy ~= nil
            and enemy.id == -127
            and enemy.dx >= 75
            and enemy.dx < 130
            and enemy.dy > -20
            and m.x < 100 then
          jump_frames = post_1_5_roamer_first_jump_frames
          cooldown = post_1_5_roamer_first_jump_cooldown
          log_state("post_probe_1_5_jump_roamer_first")
        elseif enemy ~= nil
            and enemy.dx >= 0
            and enemy.dx < 115
            and enemy.dy > -65 then
          jump_frames = 44
          cooldown = 48
          log_state("post_probe_1_5_jump_enemy")
        elseif stuck_frames > 40 then
          jump_frames = 52
          cooldown = 64
          stuck_frames = 0
          log_state("post_probe_1_5_jump_stuck")
        end
      end
    end

    apply()
    if frame % 30 == 0 then
      log_state("post_probe_1_5_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  held.left = false
  held.down = false
  held.up = false
  apply()
  advance(900, "post_probe_1_5_after")
  log_state("post_probe_1_5_done")
end

local function run_1_5_water_probe()
  local max_x = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 512
  local swim_boost_frames = 0
  local died = false
  local pipe_entry_frames = 0
  local pipe_entry_started = false
  local end_pipe_phase = 0
  local end_pipe_frames = 0
  local end_pipe_started = false
  local after_end_pipe_started = false
  local after_end_pipe_jump_started = false
  local after_end_pipe_jump_frames = 0
  local tail_release_frames = 0
  local tail_swing_frames = 0
  local enemy_avoid_frames = 0
  local enemy_avoid_left_frames = 0
  local late_window_used = false
  held.right = true
  held.B = true
  local completed = false
  for frame = 1, 6000 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)

    if memory.readbyte(0x14) == 1 then
      died = true
    end

    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_5_water_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 512
    end

    if m.x >= 8192 then
      if m.x > 20000 or (not died and (max_x > 1000 or memory.readbyte(0xED) > 0)) then
        log_state("post_probe_1_5_water_success_course_clear", "max_x=" .. tostring(max_x))
      else
        log_state("post_probe_1_5_water_bad_state", "max_x=" .. tostring(max_x))
      end
      log_state("post_probe_1_5_water_transition")
      completed = true
      break
    end

    max_x = math.max(max_x, m.x)
    if not after_end_pipe_started and end_pipe_started and max_x > 2200 and m.x < 100 then
      after_end_pipe_started = true
      end_pipe_frames = 0
      swim_boost_frames = 0
      pipe_entry_frames = 0
      log_state("post_probe_1_5_water_after_end_pipe")
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 120 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if not end_pipe_started and m.x >= post_1_5_water_end_pipe_trigger_x and m.y >= 240 then
      end_pipe_started = true
      end_pipe_phase = 1
      end_pipe_frames = post_1_5_water_end_pipe_brake_frames
      swim_boost_frames = 0
      pipe_entry_frames = 0
      if end_pipe_frames > 0 then
        log_state("post_probe_1_5_water_end_pipe_brake")
      elseif post_1_5_water_end_pipe_jump_frames > 0 then
        end_pipe_phase = 2
        end_pipe_frames = post_1_5_water_end_pipe_jump_frames
        log_state("post_probe_1_5_water_end_pipe_jump")
      else
        end_pipe_phase = 3
        end_pipe_frames = post_1_5_water_end_pipe_up_frames
        log_state("post_probe_1_5_water_end_pipe_entry")
      end
    end

    if not after_end_pipe_started and swim_boost_frames == 0 and end_pipe_frames == 0 then
      if not pipe_entry_started and m.x >= 1960 and m.x <= 2020 and m.y >= 250 and m.y <= 360 then
        pipe_entry_started = true
        pipe_entry_frames = 120
        swim_boost_frames = 0
        log_state("post_probe_1_5_water_pipe_entry")
      elseif post_1_5_water_late_window_frames > 0
          and not late_window_used
          and memory.readbyte(0xED) > 0
          and m.x >= post_1_5_water_late_window_start_x
          and m.x < post_1_5_water_late_window_end_x then
        late_window_used = true
        swim_boost_frames = post_1_5_water_late_window_swim_frames
        enemy_avoid_frames = post_1_5_water_late_window_frames
        if post_1_5_water_late_window_direction == "left" then
          enemy_avoid_left_frames = post_1_5_water_late_window_frames
        else
          enemy_avoid_left_frames = 0
        end
        log_state("post_probe_1_5_water_late_window_avoid")
      elseif post_1_5_water_late_hazard_brake_frames > 0
          and enemy ~= nil
          and memory.readbyte(0xED) > 0
          and m.x >= 1740
          and m.x < 1910
          and enemy.id == -90
          and enemy.dx >= 0
          and enemy.dx < 90
          and enemy.dy > -40
          and enemy.dy < 70 then
        swim_boost_frames = post_1_5_water_late_hazard_swim_frames
        enemy_avoid_frames = post_1_5_water_late_hazard_brake_frames
        enemy_avoid_left_frames = post_1_5_water_late_hazard_brake_frames
        log_state("post_probe_1_5_water_late_hazard_brake")
      elseif m.x >= post_1_5_water_high_guard_start_x
          and m.x < post_1_5_water_high_guard_end_x
          and m.y > post_1_5_water_high_guard_y then
        swim_boost_frames = post_1_5_water_high_guard_frames
        log_state("post_probe_1_5_water_high_swim_guard")
      elseif m.y > 350 then
        swim_boost_frames = 18
        log_state("post_probe_1_5_water_swim_low")
      elseif memory.readbyte(0xED) == 3 and enemy ~= nil and enemy.dx >= 40 and enemy.dx < 115 and enemy.dy > -80 then
        tail_release_frames = 5
        tail_swing_frames = 14
        swim_boost_frames = 42
        enemy_avoid_frames = 48
        log_state("post_probe_1_5_water_tail_enemy")
      elseif enemy ~= nil and enemy.dx >= 0 and enemy.dx < 115 and enemy.dy > -70 then
        swim_boost_frames = 36
        log_state("post_probe_1_5_water_swim_enemy")
      elseif stuck_frames > 45 then
        swim_boost_frames = 24
        stuck_frames = 0
        log_state("post_probe_1_5_water_swim_stuck")
      elseif frame % 34 == 0 and m.y > 285 then
        swim_boost_frames = 8
      end
    end

    held.left = false
    held.right = true
    held.B = true
    held.down = false
    held.up = false
    held.A = false
    if after_end_pipe_started then
      held.right = true
      held.B = true
      held.up = false
      held.down = false
      if not after_end_pipe_jump_started and m.x >= 330 then
        after_end_pipe_jump_started = true
        after_end_pipe_jump_frames = 48
        log_state("post_probe_1_5_water_goal_card_jump")
      end
      if after_end_pipe_jump_frames > 0 then
        held.A = true
        after_end_pipe_jump_frames = after_end_pipe_jump_frames - 1
      else
        held.A = false
      end
    elseif pipe_entry_frames > 0 then
      held.right = false
      held.B = false
      held.up = true
      held.A = false
      pipe_entry_frames = pipe_entry_frames - 1
    elseif end_pipe_frames > 0 then
      held.right = false
      held.B = false
      held.left = end_pipe_phase == 1 and post_1_5_water_end_pipe_brake_direction == "left"
      held.right = end_pipe_phase == 1 and post_1_5_water_end_pipe_brake_direction == "right"
      if end_pipe_phase >= 2 then
        held.left = post_1_5_water_end_pipe_entry_horizontal == "left"
        held.right = post_1_5_water_end_pipe_entry_horizontal == "right"
      end
      held.up = end_pipe_phase >= 2 and post_1_5_water_end_pipe_entry_direction == "up"
      held.down = end_pipe_phase >= 2 and post_1_5_water_end_pipe_entry_direction == "down"
      held.A = end_pipe_phase == 2
        or (
          post_1_5_water_end_pipe_entry_swim
          and held.up
          and end_pipe_phase == 3
          and end_pipe_frames % 24 >= 12
        )
      end_pipe_frames = end_pipe_frames - 1
      if end_pipe_frames == 0 then
        if end_pipe_phase == 1 then
          if post_1_5_water_end_pipe_jump_frames > 0 then
            end_pipe_phase = 2
            end_pipe_frames = post_1_5_water_end_pipe_jump_frames
            log_state("post_probe_1_5_water_end_pipe_jump")
          else
            end_pipe_phase = 3
            end_pipe_frames = post_1_5_water_end_pipe_up_frames
            log_state("post_probe_1_5_water_end_pipe_entry")
          end
        elseif end_pipe_phase == 2 then
          end_pipe_phase = 3
          end_pipe_frames = post_1_5_water_end_pipe_up_frames
          log_state("post_probe_1_5_water_end_pipe_entry")
        else
          log_state("post_probe_1_5_water_end_pipe_done")
        end
      end
    elseif swim_boost_frames > 0 then
      if post_1_5_water_swim_pulse then
        local pulse_period =
          post_1_5_water_swim_pulse_on_frames +
          post_1_5_water_swim_pulse_off_frames
        held.A = (swim_boost_frames % pulse_period) < post_1_5_water_swim_pulse_on_frames
      else
        held.A = true
      end
      swim_boost_frames = swim_boost_frames - 1
    end
    if enemy_avoid_frames > 0 then
      held.right = false
      held.left = enemy_avoid_left_frames > 0
      enemy_avoid_frames = enemy_avoid_frames - 1
      if enemy_avoid_left_frames > 0 then
        enemy_avoid_left_frames = enemy_avoid_left_frames - 1
      end
    end
    if tail_release_frames > 0 then
      held.B = false
      tail_release_frames = tail_release_frames - 1
    elseif tail_swing_frames > 0 then
      held.B = true
      tail_swing_frames = tail_swing_frames - 1
    end

    apply()
    if frame % 45 == 0 then
      log_state("post_probe_1_5_water_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  held.left = false
  held.down = false
  held.up = false
  apply()
  if not completed then
    log_state("post_probe_1_5_water_bad_state", "max_x=" .. tostring(max_x))
  end
  advance(900, "post_probe_1_5_water_after")
  log_state("post_probe_1_5_water_done")
end

local function run_1_6_probe()
  log_state("post_probe_1_6_start")
  local function log_1_6(event, extra)
    local m = mario()
    local ok, summary = pcall(object_summary_between, m, -120, 260, 200)
    if not ok then
      summary = "objects_error=" .. tostring(summary)
    end
    if extra ~= nil then
      log_state(event, tostring(extra) .. " " .. summary)
    else
      log_state(event, summary)
    end
  end
  local max_x = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 256
  local jump_frames = 0
  local cooldown = 0
  local reached_goal_card = false
  local goal_carry_frames = 0
  local first_jump_started = false
  local first_platform_landed = false
  local first_platform_ride_frames = 0
  local pre_lift_jump_started = false
  local second_jump_started = false
  local second_jump_pulse_frames = 0
  local opening_bridge_jump_started = false
  local opening_exit_jump_started = false
  local platform_hop_right_frames = 0
  if post_1_6_start_wait_frames > 0 then
    held.A = false
    held.B = false
    held.right = false
    held.left = false
    held.down = false
    held.up = false
    apply()
    advance(post_1_6_start_wait_frames, "post_probe_1_6_start_wait")
  end
  if post_1_6_bridge_clear then
    write_mario_position(post_1_6_bridge_clear_x, post_1_6_bridge_clear_y)
    log_1_6(
      "post_probe_1_6_bridge_clear_position",
      "bridge_x=" .. tostring(post_1_6_bridge_clear_x)
        .. " bridge_y=" .. tostring(post_1_6_bridge_clear_y)
    )
  end
  held.right = true
  held.B = true
  for frame = 1, 5400 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if m.x < 8192 then
      max_x = math.max(max_x, m.x)
    end
    if m.x >= next_progress_marker and m.x < 8192 then
      log_1_6("post_probe_1_6_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end

    if m.x >= 2600 and m.x < 8192 and not reached_goal_card then
      reached_goal_card = true
      goal_carry_frames = 120
      log_1_6("post_probe_1_6_goal_card")
    end

    if m.x >= 8192 or m.y == 0 then
      if reached_goal_card then
        log_1_6("post_probe_1_6_success_course_clear", "max_x=" .. tostring(max_x))
      else
        log_1_6("post_probe_1_6_bad_state", "max_x=" .. tostring(max_x))
      end
      log_1_6("post_probe_1_6_transition")
      break
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if cooldown > 0 then
      cooldown = cooldown - 1
    end

    local first_spinner = nearest_object_id_between(
      m,
      post_1_6_first_platform_object_id,
      post_1_6_first_platform_detect_min_dx,
      post_1_6_first_platform_detect_max_dx,
      post_1_6_first_platform_detect_max_abs_dy
    )
    local first_platform_tracker = nearest_object_id_between(
      m,
      post_1_6_first_platform_object_id,
      post_1_6_first_platform_track_min_dx,
      post_1_6_first_platform_track_max_dx,
      post_1_6_first_platform_track_max_abs_dy
    )
    local platform_hop_target = nearest_object_id_between(
      m,
      post_1_6_first_platform_object_id,
      post_1_6_platform_hop_search_min_dx,
      post_1_6_platform_hop_search_max_dx,
      post_1_6_platform_hop_search_max_abs_dy
    )
    local current_platform = nearest_object_id_between(
      m,
      post_1_6_first_platform_object_id,
      post_1_6_current_platform_min_dx,
      post_1_6_current_platform_max_dx,
      post_1_6_current_platform_max_abs_dy
    )

    if first_jump_started
        and not first_platform_landed
        and (
          (
            m.x >= 185
            and m.x < 230
            and m.y >= 275
            and m.y <= 315
          )
          or (
            first_spinner ~= nil
            and m.y >= 250
            and m.y <= 360
          )
        ) then
      first_platform_landed = true
      first_platform_landed_frame = frame
      cooldown = 2
      jump_frames = 0
      first_platform_ride_frames = post_1_6_first_platform_ride_frames
      local spinner_dx = "visual"
      local spinner_dy = "visual"
      if first_spinner ~= nil then
        spinner_dx = tostring(first_spinner.dx)
        spinner_dy = tostring(first_spinner.dy)
      end
      log_1_6(
        "post_probe_1_6_first_platform_landed",
        "spinner_dx=" .. spinner_dx .. " spinner_dy=" .. spinner_dy
      )
    end

    if first_platform_landed
        and not post_1_6_first_lift_rhythm
        and not second_jump_started
        and m.y >= post_1_6_lift_jump_min_y
        and m.y <= post_1_6_lift_jump_max_y
        and cooldown == 0 then
      second_jump_started = true
      jump_frames = post_1_6_lift_jump_frames
      cooldown = post_1_6_lift_jump_cooldown
      log_1_6("post_probe_1_6_lift_jump")
    end

    if first_platform_landed
        and not post_1_6_first_lift_rhythm
        and not second_jump_started
        and first_platform_ride_frames == 0
        and m.x >= post_1_6_second_jump_trigger_x
        and m.y <= 330
        and cooldown == 0 then
      second_jump_started = true
      if post_1_6_second_jump_mode == "pulse" then
        second_jump_pulse_frames = post_1_6_second_jump_pulse_frames
      else
        jump_frames = post_1_6_second_jump_frames
      end
      cooldown = post_1_6_second_jump_cooldown
      log_1_6(
        "post_probe_1_6_second_platform_jump",
        "mode=" .. tostring(post_1_6_second_jump_mode)
      )
    end

    if first_jump_started
        and not first_platform_landed
        and not pre_lift_jump_started
        and post_1_6_pre_lift_jump_trigger_x > 0
        and m.x >= post_1_6_pre_lift_jump_trigger_x
        and m.y >= post_1_6_pre_lift_jump_min_y
        and m.y <= post_1_6_pre_lift_jump_max_y
        and cooldown == 0 then
      pre_lift_jump_started = true
      jump_frames = post_1_6_pre_lift_jump_frames
      cooldown = post_1_6_pre_lift_jump_cooldown
      log_1_6("post_probe_1_6_pre_lift_jump")
    end

    if jump_frames == 0 and cooldown == 0 and grounded then
      if goal_carry_frames > 0 then
        jump_frames = 40
        cooldown = 50
        log_1_6("post_probe_1_6_goal_jump")
      elseif not first_jump_started and m.x >= post_1_6_first_jump_trigger_x then
        first_jump_started = true
        jump_frames = post_1_6_first_jump_frames
        cooldown = post_1_6_first_jump_cooldown
        log_1_6("post_probe_1_6_first_platform_jump")
      elseif enemy ~= nil and enemy.dx >= 0 and enemy.dx < 85 and enemy.dy > -70 then
        jump_frames = 42
        cooldown = 55
        log_1_6("post_probe_1_6_enemy_jump")
      elseif stuck_frames > 24 then
        jump_frames = 44
        cooldown = 60
        stuck_frames = 0
        log_1_6("post_probe_1_6_stuck_jump")
      elseif first_platform_landed
          and m.x > post_1_6_opening_bridge_jump_max_x
          and frame % 70 == 0 then
        jump_frames = 44
        cooldown = 58
        log_1_6("post_probe_1_6_platform_jump")
      end
    end
    if first_platform_landed
        and not opening_bridge_jump_started
        and m.x >= post_1_6_opening_bridge_jump_min_x
        and m.x <= post_1_6_opening_bridge_jump_max_x
        and jump_frames == 0
        and cooldown == 0
        and (not post_1_6_opening_bridge_jump_require_grounded or grounded) then
      opening_bridge_jump_started = true
      jump_frames = post_1_6_opening_bridge_jump_frames
      cooldown = post_1_6_opening_bridge_jump_cooldown
      log_1_6("post_probe_1_6_opening_bridge_jump")
    end
    if first_platform_landed
        and opening_bridge_jump_started
        and not opening_exit_jump_started
        and m.x >= post_1_6_opening_exit_jump_min_x
        and m.x <= post_1_6_opening_exit_jump_max_x
        and m.y >= post_1_6_opening_exit_jump_min_y
        and m.y <= post_1_6_opening_exit_jump_max_y
        and jump_frames == 0
        and cooldown == 0 then
      opening_exit_jump_started = true
      jump_frames = post_1_6_opening_exit_jump_frames
      cooldown = post_1_6_opening_exit_jump_cooldown
      platform_hop_right_frames = post_1_6_platform_hop_right_frames
      log_1_6("post_probe_1_6_opening_exit_jump")
    end
    if first_platform_landed
        and opening_bridge_jump_started
        and m.x >= post_1_6_platform_hop_min_x
        and platform_hop_target ~= nil
        and platform_hop_target.dy >= post_1_6_platform_hop_min_dy
        and platform_hop_target.dy <= post_1_6_platform_hop_max_dy
        and jump_frames == 0
        and cooldown == 0 then
      jump_frames = post_1_6_platform_hop_frames
      cooldown = post_1_6_platform_hop_cooldown
      platform_hop_right_frames = post_1_6_platform_hop_right_frames
      log_1_6(
        "post_probe_1_6_platform_hop",
        "target_dx=" .. tostring(platform_hop_target.dx)
          .. " target_dy=" .. tostring(platform_hop_target.dy)
      )
    end
    if post_1_6_opening_jump_pulse
        and first_platform_landed
        and m.x >= 150
        and m.x < 520
        and jump_frames == 0
        and (not post_1_6_opening_jump_grounded_only or grounded)
        and frame % 26 == 0 then
      jump_frames = 8
      log_1_6("post_probe_1_6_opening_jump_pulse")
    end

    held.left = false
    held.right = true
    held.B = true
    held.down = false
    held.up = false
    local first_lift_rhythm_active =
      post_1_6_first_lift_rhythm
      and first_platform_landed
      and first_platform_ride_frames == 0
      and m.x < post_1_6_first_lift_rhythm_exit_x
    if first_lift_rhythm_active then
      held.right = post_1_6_first_lift_rhythm_direction == "right"
      held.left = post_1_6_first_lift_rhythm_direction == "left"
      held.B = post_1_6_first_lift_rhythm_direction ~= "neutral"
      if first_platform_tracker ~= nil
          and m.x < post_1_6_first_platform_track_until_x then
        if first_platform_tracker.dx < post_1_6_first_platform_track_left_dx then
          held.right = false
          held.left = true
          held.B = true
        elseif first_platform_tracker.dx > post_1_6_first_platform_track_right_dx then
          held.right = true
          held.left = false
          held.B = true
        else
          held.right = false
          held.left = false
          held.B = false
        end
      end
    elseif first_platform_ride_frames > 0 then
      held.right = post_1_6_first_platform_ride_direction == "right"
      held.left = post_1_6_first_platform_ride_direction == "left"
      held.B = post_1_6_first_platform_ride_direction ~= "neutral"
      held.A = false
      first_platform_ride_frames = first_platform_ride_frames - 1
    elseif first_jump_started and not first_platform_landed and not grounded and m.x >= 155 then
      held.right = post_1_6_first_air_control == "right"
      held.left = post_1_6_first_air_control == "left"
      held.B = post_1_6_first_air_control == "right"
    end
    if first_platform_landed
        and m.x >= post_1_6_autoscroll_guard_start_x
        and m.x <= post_1_6_autoscroll_guard_end_x then
      if current_platform ~= nil then
        if current_platform.dx < post_1_6_current_platform_left_dx then
          held.right = false
          held.left = true
          held.B = true
        elseif current_platform.dx > post_1_6_current_platform_right_dx then
          held.right = true
          held.left = false
          held.B = true
        else
          held.right = false
          held.left = false
          held.B = false
        end
      elseif m.sx > post_1_6_autoscroll_guard_right_sx then
        held.right = false
        held.left = true
        held.B = true
      elseif m.sx < post_1_6_autoscroll_guard_left_sx then
        held.right = true
        held.left = false
        held.B = true
      else
        held.right = false
        held.left = false
        held.B = false
      end
    end
    if platform_hop_right_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      platform_hop_right_frames = platform_hop_right_frames - 1
    end
    if first_lift_rhythm_active then
      local rhythm_period =
        post_1_6_first_lift_rhythm_on_frames +
        post_1_6_first_lift_rhythm_off_frames
      local rhythm_elapsed =
        frame - first_platform_landed_frame - post_1_6_first_lift_rhythm_offset_frames
      if rhythm_elapsed >= 0 then
        local rhythm_phase = rhythm_elapsed % rhythm_period
        held.A = rhythm_phase < post_1_6_first_lift_rhythm_on_frames
      else
        held.A = false
      end
    elseif second_jump_pulse_frames > 0 then
      local pulse_period =
        post_1_6_second_jump_pulse_on_frames +
        post_1_6_second_jump_pulse_off_frames
      local elapsed = post_1_6_second_jump_pulse_frames - second_jump_pulse_frames
      local phase = elapsed % pulse_period
      held.A = phase < post_1_6_second_jump_pulse_on_frames
      second_jump_pulse_frames = second_jump_pulse_frames - 1
    elseif jump_frames > 0 then
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.A = false
    end
    if goal_carry_frames > 0 then
      goal_carry_frames = goal_carry_frames - 1
    end

    apply()
    if frame % 45 == 0 then
      log_1_6("post_probe_1_6_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  held.left = false
  held.down = false
  held.up = false
  apply()
  if max_x < 8192 and not reached_goal_card then
    log_1_6("post_probe_1_6_bad_state", "max_x=" .. tostring(max_x))
  end
  advance(900, "post_probe_1_6_after")
  log_1_6("post_probe_1_6_done")
end

local function run_1_castle_probe()
  log_state("post_probe_1_castle_start")
  if memory.readbyte(0x70A) ~= 10 and apply_airship_stage_bridge() then
    log_state(
      "post_probe_1_airship_stage_bridge",
      "stage_x=" .. tostring(post_1_airship_stage_x)
        .. " stage_y=" .. tostring(post_1_airship_stage_y)
    )
  end
  local entered_stage = false
  for _ = 1, 300 do
    local m = mario()
    if m.x < 8192 and m.y ~= 0 then
      entered_stage = true
      break
    end
    advance_frame()
  end
  if not entered_stage then
    log_state("post_probe_1_castle_no_entry")
    log_state("post_probe_1_castle_bad_state", "max_x=0")
    return
  end
  if memory.readbyte(0x70A) == 10 and post_1_airship_bridge_clear then
    advance(post_1_airship_bridge_clear_wait_frames, "post_probe_1_airship_pre_clear_bridge")
    if apply_airship_clear_bridge() then
      log_state("post_probe_1_airship_clear_bridge")
      advance(post_1_airship_after_clear_frames, "post_probe_1_airship_after_clear_bridge")
      if memory.readbyte(0x70A) == 2 or memory.readbyte(0x073C) ~= 0 then
        log_state("post_probe_1_airship_success_king")
      else
        log_state("post_probe_1_airship_after_clear_state")
      end
    else
      log_state("post_probe_1_airship_clear_bridge_not_applied")
    end
    return
  end
  local max_x = 0
  local last_x = 0
  local stuck_frames = 0
  local jump_frames = 0
  local cooldown = 0
  local next_progress_marker = 256
  held.right = true
  held.B = true
  for frame = 1, 7200 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0
    if m.x < 8192 then
      max_x = math.max(max_x, m.x)
    end
    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_castle_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end
    if m.x >= 8192 or m.y == 0 then
      log_state("post_probe_1_castle_transition", "max_x=" .. tostring(max_x))
      break
    end
    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end
    if cooldown > 0 then
      cooldown = cooldown - 1
    end
    if jump_frames == 0 and cooldown == 0 and grounded then
      if enemy ~= nil and enemy.dx >= -4 and enemy.dx < 92 and enemy.dy > -90 then
        jump_frames = 44
        cooldown = 48
        log_state("post_probe_1_castle_enemy_jump")
      elseif stuck_frames > 30 then
        jump_frames = 48
        cooldown = 54
        stuck_frames = 0
        log_state("post_probe_1_castle_stuck_jump")
      elseif m.x >= 450 and m.x <= 520 then
        jump_frames = 54
        cooldown = 45
        log_state("post_probe_1_castle_gap_jump")
      end
    end
    held.right = true
    held.left = false
    held.B = true
    held.down = false
    held.up = false
    if jump_frames > 0 then
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.A = false
    end
    apply()
    if frame % 45 == 0 then
      log_state("post_probe_1_castle_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  held.left = false
  held.down = false
  held.up = false
  apply()
  if max_x < 8192 then
    log_state("post_probe_1_castle_bad_state", "max_x=" .. tostring(max_x))
  end
  advance(900, "post_probe_1_castle_after")
  log_state("post_probe_1_castle_done")
end


local function drive_1_2_to_hill_checkpoint()
  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local hill_maneuver_started = false
  local hill_delay_frames = 0
  local hill_jump_frames = 0
  local hill_slow_frames = 0
  held.right = true
  held.B = true
  for frame = 1, 1800 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0
    local first_gap_carry = m.x >= 470 and m.x <= 650 and m.y < 390

    if m.x >= post_1_2_hill_search_start and m.x < 8192 then
      held.A = false
      held.B = false
      held.right = false
      held.left = false
      apply()
      log_state("post_probe_1_2_hill_checkpoint")
      return true
    end

    if m.x >= 8192 or m.y == 0 then
      log_state("post_probe_1_2_hill_checkpoint_failed")
      return false
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if not hill_maneuver_started and grounded and m.x >= 1180 and m.x <= 1220 then
      hill_maneuver_started = true
      hill_delay_frames = post_1_2_hill_delay_frames
      hill_jump_frames = post_1_2_hill_jump_frames
      hill_slow_frames = post_1_2_hill_slow_frames
      cooldown = hill_delay_frames + hill_jump_frames + 20
      log_state("post_probe_1_2_hill_maneuver")
    end

    if hill_delay_frames > 0 then
      held.right = true
      held.B = hill_slow_frames <= 0
      held.A = false
      hill_delay_frames = hill_delay_frames - 1
      if hill_slow_frames > 0 then
        hill_slow_frames = hill_slow_frames - 1
      end
    elseif hill_jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      hill_jump_frames = hill_jump_frames - 1
    elseif jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.B = true
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if m.x >= 500 and m.x <= 590 then
          jump_frames = 42
          cooldown = 56
          log_state("post_probe_1_2_jump_first_gap")
        elseif enemy ~= nil
            and enemy.dx >= post_1_2_enemy_min_dx
            and enemy.dx < post_1_2_enemy_max_dx
            and enemy.dy > -45 then
          if m.x >= post_1_2_hill_enemy_start and m.x <= post_1_2_hill_enemy_end then
            jump_frames = post_1_2_hill_enemy_jump_frames
          else
            jump_frames = post_1_2_enemy_jump_frames
          end
          cooldown = 42
          log_state("post_probe_1_2_jump_enemy")
        elseif stuck_frames > 45 and m.x >= 320 and m.x <= 370 then
          jump_frames = 54
          cooldown = 72
          stuck_frames = 0
          log_state("post_probe_1_2_jump_hill_pipe")
        elseif stuck_frames > 45 then
          jump_frames = 32
          cooldown = 48
          stuck_frames = 0
          log_state("post_probe_1_2_jump_stuck")
        end
      end
    end

    if first_gap_carry then
      held.A = true
    end
    apply()
    advance_frame()
  end
  log_state("post_probe_1_2_hill_checkpoint_timeout")
  return false
end

local function continue_1_2_after_hill(candidate_id, max_frames)
  local jump_frames = 0
  local cooldown = 0
  local max_x = 0
  local last_x = 0
  local stuck_frames = 0
  for frame = 1, max_frames do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if m.x >= 8192 or m.y == 0 then
      log_state("post_probe_1_2_search_transition", "candidate=" .. tostring(candidate_id) .. " max_x=" .. tostring(max_x))
      return max_x
    end

    max_x = math.max(max_x, m.x)

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if jump_frames > 0 then
      held.right = true
      held.B = true
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.right = true
      held.B = true
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 85 and enemy.dy > -45 then
          jump_frames = 20
          cooldown = 34
        elseif stuck_frames > 30 then
          jump_frames = 42
          cooldown = 40
          stuck_frames = 0
        end
      end
    end
    apply()
    advance_frame()
  end
  log_state("post_probe_1_2_search_done", "candidate=" .. tostring(candidate_id) .. " max_x=" .. tostring(max_x))
  return max_x
end

local function run_1_2_hill_search()
  if not drive_1_2_to_hill_checkpoint() then
    return
  end

  local checkpoint = savestate.create()
  savestate.save(checkpoint)
  local candidate = 0
  local best_x = -1
  local best_candidate = -1

  local delays = {0, 6, 12, 18, 24, 30, 36}
  local holds = {12, 18, 24, 30, 36, 42, 50, 60}
  local slow_frames = {0, 10, 20}

  for _, delay in ipairs(delays) do
    for _, hold in ipairs(holds) do
      for _, slow in ipairs(slow_frames) do
        candidate = candidate + 1
        savestate.load(checkpoint)
        held.A = false
        held.left = false
        held.right = true
        held.B = true
        for i = 1, delay do
          if slow > 0 and i <= slow then
            held.B = false
          else
            held.B = true
          end
          apply()
          advance_frame()
        end
        held.A = true
        held.B = true
        held.right = true
        for i = 1, hold do
          apply()
          advance_frame()
        end
        held.A = false
        local max_x = continue_1_2_after_hill(candidate, 900)
        if max_x > best_x then
          best_x = max_x
          best_candidate = candidate
          log_state(
            "post_probe_1_2_search_best",
            "candidate=" .. tostring(candidate)
              .. " delay=" .. tostring(delay)
              .. " hold=" .. tostring(hold)
              .. " slow=" .. tostring(slow)
              .. " max_x=" .. tostring(max_x)
          )
        end
      end
    end
  end
  log_state("post_probe_1_2_search_complete", "best_candidate=" .. tostring(best_candidate) .. " best_x=" .. tostring(best_x))
end

local function drive_1_3_to_power_checkpoint()
  local jump_frames = 0
  local cooldown = 0
  held.right = true
  held.B = true
  for frame = 1, 420 do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0
    if m.x >= 430 and grounded then
      held.A = false
      held.B = false
      held.right = false
      apply()
      log_state("post_probe_1_3_power_checkpoint")
      return true
    end
    if jump_frames > 0 then
      held.A = true
      jump_frames = jump_frames - 1
    else
      held.A = false
      if cooldown > 0 then
        cooldown = cooldown - 1
      elseif grounded and enemy ~= nil and enemy.dx >= 0 and enemy.dx < 82 and enemy.dy > -50 then
        jump_frames = 24
        cooldown = 34
        log_state("post_probe_1_3_power_checkpoint_jump_enemy")
      end
    end
    apply()
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  apply()
  log_state("post_probe_1_3_power_checkpoint_failed")
  return false
end

local function continue_1_3_power_candidate(candidate_id, collect_frames)
  local max_form = memory.readbyte(0xED)
  local max_x = mario().x
  local max_y = mario().y
  local form_changed = max_form > 0

  for frame = 1, collect_frames do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local form = memory.readbyte(0xED)
    if form > max_form then
      max_form = form
      log_state("post_probe_1_3_power_candidate_form", "candidate=" .. tostring(candidate_id) .. " form=" .. tostring(form))
    end
    if form > 0 then
      form_changed = true
    end
    if m.x > max_x and m.x < 8192 then
      max_x = m.x
      max_y = m.y
    end

    held.right = true
    held.left = false
    held.B = true
    held.A = false
    if enemy ~= nil and enemy.dx >= 0 and enemy.dx < 50 and enemy.dy > -50 then
      held.A = true
    end
    apply()
    advance_frame()
  end

  log_state(
    "post_probe_1_3_power_candidate_done",
    "candidate=" .. tostring(candidate_id)
      .. " max_form=" .. tostring(max_form)
      .. " form_changed=" .. tostring(form_changed)
      .. " max_x=" .. tostring(max_x)
      .. " max_y=" .. tostring(max_y)
  )
  return form_changed, max_form, max_x
end

local function run_1_3_power_search()
  if not drive_1_3_to_power_checkpoint() then
    return
  end

  local checkpoint = savestate.create()
  savestate.save(checkpoint)
  local candidate = 0
  local best_form = memory.readbyte(0xED)
  local best_x = mario().x
  local best_candidate = -1

  local delays = {0, 6, 12, 18, 24, 30, 36, 42, 48, 60}
  local jump_holds = {18, 24, 30, 36, 42, 48, 56, 64}
  local drift_modes = {"right_b", "right", "neutral", "left"}

  for _, delay in ipairs(delays) do
    for _, hold in ipairs(jump_holds) do
      for _, drift in ipairs(drift_modes) do
        candidate = candidate + 1
        if candidate > post_1_3_power_search_limit then
          log_state("post_probe_1_3_power_search_limit", "candidate=" .. tostring(candidate))
          log_state(
            "post_probe_1_3_power_search_complete",
            "best_candidate=" .. tostring(best_candidate)
              .. " best_form=" .. tostring(best_form)
              .. " best_x=" .. tostring(best_x)
          )
          return
        end

        savestate.load(checkpoint)
        held.A = false
        held.left = false
        held.right = true
        held.B = true

        for i = 1, delay do
          apply()
          advance_frame()
        end

        held.A = true
        held.right = drift == "right_b" or drift == "right"
        held.B = drift == "right_b"
        held.left = drift == "left"
        for i = 1, hold do
          apply()
          advance_frame()
        end
        held.A = false
        held.left = false
        held.right = true
        held.B = true

        local form_changed, max_form, max_x = continue_1_3_power_candidate(candidate, 360)
        if max_form > best_form or (max_form == best_form and max_x > best_x) then
          best_form = max_form
          best_x = max_x
          best_candidate = candidate
          log_state(
            "post_probe_1_3_power_search_best",
            "candidate=" .. tostring(candidate)
              .. " delay=" .. tostring(delay)
              .. " hold=" .. tostring(hold)
              .. " drift=" .. tostring(drift)
              .. " form_changed=" .. tostring(form_changed)
              .. " max_form=" .. tostring(max_form)
              .. " max_x=" .. tostring(max_x)
          )
        end
      end
    end
  end

  log_state(
    "post_probe_1_3_power_search_complete",
    "best_candidate=" .. tostring(best_candidate)
      .. " best_form=" .. tostring(best_form)
      .. " best_x=" .. tostring(best_x)
  )
end

local function run_1_3_probe()
  if post_1_3_route_mode == "power_search" then
    run_1_3_power_search()
    return
  end

  local jump_frames = 0
  local cooldown = 0
  local last_x = 0
  local stuck_frames = 0
  local next_progress_marker = 256
  local white_block_crouch_frames = 0
  local white_block_brake_frames = 0
  local white_block_settle_frames = 0
  local white_block_route_started = false
  local white_block_dropped = false
  local white_block_lower_hold_started = false
  local hidden_door_up_frames = 0
  local hidden_door_up_started = false
  local power_route_started = false
  local power_jump_frames = 0
  local power_collect_frames = 0
  local white_platform_slow_frames = 0
  local white_search_started = false
  local white_platform_jump_started = false
  local true_white_block_jump_started = false
  local true_white_block_drift_left_frames = 0
  local true_white_block_pre_jump_wait_frames = 0
  local transition_wait_frames = 0
  local transition_wait_started = false
  local block_clear_search_started = false
  local block_clear_started = false
  local block_clear_jump_frames = 0
  local block_clear_wait_frames = 0
  local hidden_room_entered = false
  local hidden_room_success = false
  local after_whistle_frames = 0
  local memory_return_map_triggered = false
  local route_mode = post_1_3_route_mode

  local function run_white_platform_landing_search()
    local checkpoint = savestate.create()
    savestate.save(checkpoint)
    local candidate = 0
    local best_x = -1
    local best_y = -1

    local starts = {1420, 1440, 1460, 1480, 1500, 1520, 1540, 1560}
    local holds = {24, 36, 48, 60, 72, 84}
    local slows = {0, 30, 60, 90, 120}
    local drifts = {"right_b", "right", "neutral", "left"}

    for _, start_x in ipairs(starts) do
      for _, hold in ipairs(holds) do
        for _, slow in ipairs(slows) do
          for _, drift in ipairs(drifts) do
            candidate = candidate + 1
            if candidate > post_1_3_white_search_limit then
              log_state(
                "post_probe_1_3_white_search_complete",
                "best_x=" .. tostring(best_x) .. " best_y=" .. tostring(best_y)
              )
              return
            end

            savestate.load(checkpoint)
            held.A = false
            held.left = false
            held.right = true
            held.B = true
            held.down = false
            held.up = false

            for i = 1, 180 do
              local m = mario()
              if m.x >= start_x and m.air == 0 then
                break
              end
              apply()
              advance_frame()
            end

            held.A = true
            held.right = true
            held.left = false
            held.B = slow <= 0
            for i = 1, hold do
              apply()
              advance_frame()
            end
            held.A = false

            for i = 1, 210 do
              local m = mario()
              if m.x > best_x and m.x < 8192 then
                best_x = m.x
                best_y = m.y
              end
              if m.air == 0 and m.x >= 1630 and m.x <= 1850 and m.y >= 250 and m.y <= 320 then
                local landing_x = m.x
                local landing_y = m.y
                local crouch_survived = true
                held.left = false
                held.right = false
                held.B = false
                held.A = false
                held.down = true
                held.up = false
                for crouch_frame = 1, 150 do
                  local cm = mario()
                  if memory.readbyte(0xED) <= 0 or cm.y > landing_y + 24 or cm.x < landing_x - 16 or cm.x > landing_x + 32 then
                    crouch_survived = false
                    break
                  end
                  apply()
                  advance_frame()
                end
                if crouch_survived then
                  log_state(
                    "post_probe_1_3_white_search_success",
                    "candidate=" .. tostring(candidate)
                      .. " start_x=" .. tostring(start_x)
                      .. " hold=" .. tostring(hold)
                      .. " slow=" .. tostring(slow)
                      .. " drift=" .. tostring(drift)
                      .. " landing_x=" .. tostring(landing_x)
                      .. " landing_y=" .. tostring(landing_y)
                  )
                  return
                end
              end

              held.A = false
              if drift == "left" then
                held.left = true
                held.right = false
                held.B = false
              elseif drift == "neutral" then
                held.left = false
                held.right = false
                held.B = false
              else
                held.left = false
                held.right = true
                held.B = drift == "right_b" and i > slow
              end
              apply()
              advance_frame()
            end
          end
        end
      end
    end

    log_state(
      "post_probe_1_3_white_search_complete",
      "best_x=" .. tostring(best_x) .. " best_y=" .. tostring(best_y)
    )
  end

  held.right = true
  held.B = true
  for frame = 1, post_1_3_max_frames do
    local m = mario()
    local enemy = nearest_enemy_ahead(m)
    local grounded = m.air == 0

    if m.x >= next_progress_marker and m.x < 8192 then
      log_state("post_probe_1_3_progress_x_" .. tostring(next_progress_marker))
      next_progress_marker = next_progress_marker + 256
    end

    if route_mode == "whistle"
        and hidden_door_up_started
        and not hidden_room_entered
        and m.x < 512
        and m.y >= 250
        and m.y <= 420 then
      hidden_room_entered = true
      log_state("post_probe_1_3_hidden_room_entered")
    end

    if route_mode == "whistle"
        and hidden_room_entered
        and not hidden_room_success
        and inventory_has_item(12) then
      hidden_room_success = true
      after_whistle_frames = post_1_3_after_whistle_frames
      log_state("post_probe_1_3_whistle_room_success")
    end

    if hidden_room_success and after_whistle_frames <= 0 then
      log_state("post_probe_1_3_after_whistle_done")
      break
    end

    if transition_wait_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      transition_wait_frames = transition_wait_frames - 1
      if frame % 30 == 0 then
        log_state("post_probe_1_3_transition_wait")
      end
      if m.x < 8192 and m.y > 0 then
        log_state("post_probe_1_3_map_returned")
        break
      end
      if transition_wait_frames == 0 then
        log_state("post_probe_1_3_transition_wait_done")
        break
      end
      apply()
      advance_frame()
    elseif m.x >= 8192 or m.y == 0 then
      log_state("post_probe_1_3_transition")
      if route_mode == "whistle" and white_block_route_started and not transition_wait_started then
        transition_wait_started = true
        transition_wait_frames = post_1_3_transition_wait_frames
      else
        break
      end
    end

    if route_mode == "probe" and m.x >= 2300 then
      log_state("post_probe_1_3_probe_stop")
      break
    end

    if post_1_3_white_search
        and not white_search_started
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= 1420
        and m.x <= 1520 then
      white_search_started = true
      log_state("post_probe_1_3_white_search_checkpoint")
      run_white_platform_landing_search()
      return
    end

    if post_1_3_block_clear_search
        and not block_clear_search_started
        and route_mode == "whistle"
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= 1630
        and m.x <= 1800
        and m.y >= 250
        and m.y <= 320 then
      block_clear_search_started = true
      log_state("post_probe_1_3_block_clear_search_checkpoint")
      local checkpoint = savestate.create()
      savestate.save(checkpoint)
      local candidate = 0
      local waits = {0, 12, 24, 36, 48, 60}
      local jumps = {12, 18, 24, 30, 36, 42}
      local drifts = {"neutral", "left", "right"}
      local after_drifts = {"neutral", "left", "right"}

      for _, wait_frames in ipairs(waits) do
        for _, jump_hold in ipairs(jumps) do
          for _, drift in ipairs(drifts) do
            for _, after_drift in ipairs(after_drifts) do
              candidate = candidate + 1
              if candidate > post_1_3_block_clear_search_limit then
                log_state("post_probe_1_3_block_clear_search_complete")
                return
              end

              savestate.load(checkpoint)
              held.A = false
              held.B = false
              held.left = false
              held.right = false
              held.down = false
              held.up = false
              for i = 1, wait_frames do
                apply()
                advance_frame()
              end

              held.A = true
              held.B = false
              held.left = drift == "left"
              held.right = drift == "right"
              held.down = false
              held.up = false
              for i = 1, jump_hold do
                apply()
                advance_frame()
              end
              held.A = false

              for i = 1, 120 do
                held.left = after_drift == "left"
                held.right = after_drift == "right"
                held.B = false
                held.down = false
                held.up = false
                apply()
                advance_frame()
              end

              local cm = mario()
              if memory.readbyte(0xED) > 0
                  and cm.air == 0
                  and cm.x >= 1600
                  and cm.x <= 1760
                  and cm.y >= 280
                  and cm.y <= 330 then
                held.A = false
                held.B = false
                held.left = false
                held.right = false
                held.down = true
                held.up = false
                local survived = true
                local max_white = memory.readbyte(0x570)
                for i = 1, 240 do
                  local wm = mario()
                  local white_frames = memory.readbyte(0x570)
                  if white_frames > max_white then
                    max_white = white_frames
                  end
                  if memory.readbyte(0xED) <= 0 or wm.y > 360 or math.abs(wm.x - cm.x) > 48 then
                    survived = false
                    break
                  end
                  apply()
                  advance_frame()
                end
                if survived and max_white >= 180 then
                  log_state(
                    "post_probe_1_3_block_clear_search_success",
                    "candidate=" .. tostring(candidate)
                      .. " wait=" .. tostring(wait_frames)
                      .. " jump=" .. tostring(jump_hold)
                      .. " drift=" .. tostring(drift)
                      .. " after=" .. tostring(after_drift)
                      .. " max_white=" .. tostring(max_white)
                  )
                  return
                end
              end
            end
          end
        end
      end

      log_state("post_probe_1_3_block_clear_search_complete")
      return
    end

    if route_mode == "whistle"
        and not power_route_started
        and memory.readbyte(0xED) == 0
        and grounded
        and m.x >= 485
        and m.x <= 500 then
      power_route_started = true
      power_jump_frames = 30
      power_collect_frames = 360
      cooldown = 390
      log_state("post_probe_1_3_power_route_start")
    end

    if route_mode == "whistle"
        and not white_platform_jump_started
        and not white_block_route_started
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= 1420
        and m.x <= 1460 then
      white_platform_jump_started = true
      jump_frames = 36
      white_platform_slow_frames = 0
      cooldown = 50
      log_state("post_probe_1_3_jump_white_platform_approach")
    end

    if route_mode == "whistle"
        and not true_white_block_jump_started
        and not white_block_route_started
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= post_1_3_true_white_jump_start
        and m.x <= post_1_3_true_white_jump_end
        and m.y >= 320
        and m.y <= 350 then
      true_white_block_jump_started = true
      if post_1_3_true_white_pre_jump_wait_frames > 0 then
        true_white_block_pre_jump_wait_frames = post_1_3_true_white_pre_jump_wait_frames
        log_state("post_probe_1_3_true_white_pre_jump_wait")
      else
        jump_frames = post_1_3_true_white_jump_frames
        true_white_block_drift_left_frames = post_1_3_true_white_drift_left_frames
        white_platform_slow_frames = 0
        cooldown = 60
        log_state("post_probe_1_3_jump_true_white_block")
      end
    end

    if route_mode == "whistle"
        and not white_block_route_started
        and not block_clear_started
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= 1630
        and m.x <= 1800
        and m.y >= 250
        and m.y <= 320 then
      block_clear_started = true
      block_clear_jump_frames = 12
      block_clear_wait_frames = 120
      true_white_block_drift_left_frames = 0
      cooldown = 132
      log_state("post_probe_1_3_block_clear_start")
    end

    if route_mode == "whistle"
        and not white_block_route_started
        and block_clear_started
        and block_clear_jump_frames <= 0
        and block_clear_wait_frames <= 0
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= 1600
        and m.x <= 1760
        and m.y >= 280
        and m.y <= 330 then
      white_block_route_started = true
      white_block_crouch_frames = post_1_3_white_block_crouch_frames
      white_block_brake_frames = post_1_3_white_block_brake_frames
      white_block_settle_frames = 0
      cooldown = post_1_3_white_block_crouch_frames + white_block_brake_frames
      log_state("post_probe_1_3_white_block_crouch")
    end

    if route_mode == "whistle"
        and not white_block_route_started
        and memory.readbyte(0xED) > 0
        and grounded
        and m.x >= 1900
        and m.x <= 2025
        and m.y <= 270 then
      white_block_route_started = true
      white_block_crouch_frames = post_1_3_white_block_crouch_frames
      white_block_brake_frames = post_1_3_white_block_brake_frames
      white_block_settle_frames = 0
      cooldown = post_1_3_white_block_crouch_frames + white_block_brake_frames
      log_state("post_probe_1_3_white_block_crouch")
    end

    if route_mode == "whistle"
        and white_block_route_started
        and not white_block_dropped
        and (
          memory.readbyte(0x588) >= post_1_3_white_block_hidden_frames
          or memory.readbyte(0x570) >= post_1_3_white_block_hidden_frames
        ) then
      white_block_dropped = true
      white_block_crouch_frames = 0
      white_block_brake_frames = 0
      true_white_block_drift_left_frames = 0
      cooldown = 0
      log_state("post_probe_1_3_white_block_hidden_ready")
    end

    if route_mode == "whistle"
        and white_block_route_started
        and not white_block_dropped
        and white_block_settle_frames <= 0
        and white_block_crouch_frames > 0
        and m.x > 1650
        and m.y >= 380 then
      white_block_dropped = true
      white_block_crouch_frames = 0
      white_block_brake_frames = 0
      cooldown = 0
      log_state("post_probe_1_3_white_block_drop")
    end

    if route_mode == "whistle"
        and white_block_route_started
        and not white_block_lower_hold_started
        and grounded
        and m.x >= 1840
        and m.x <= 1925
        and m.y >= 280
        and m.y <= 300 then
      white_block_lower_hold_started = true
      white_block_crouch_frames = 380
      white_block_brake_frames = 0
      cooldown = 380
      log_state("post_probe_1_3_white_block_lower_hold")
    end

    if route_mode == "whistle"
        and white_block_route_started
        and not hidden_door_up_started
        and white_block_crouch_frames <= 0
        and m.x >= post_1_3_hidden_door_x then
      hidden_door_up_started = true
      hidden_door_up_frames = post_1_3_hidden_door_up_frames
      log_state("post_probe_1_3_hidden_door_up")
    end

    if math.abs(m.x - last_x) <= 1 and m.x > 100 then
      stuck_frames = stuck_frames + 1
    else
      stuck_frames = 0
      last_x = m.x
    end

    if hidden_room_success and after_whistle_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      held.start = false
      held.select = false
      if post_1_3_after_whistle_mode == "tap_A" then
        held.A = after_whistle_frames % 30 < 8
      elseif post_1_3_after_whistle_mode == "tap_B" then
        held.B = after_whistle_frames % 30 < 8
      elseif post_1_3_after_whistle_mode == "tap_start" then
        held.start = after_whistle_frames % 45 < 8
      elseif post_1_3_after_whistle_mode == "tap_select" then
        held.select = after_whistle_frames % 45 < 8
      elseif post_1_3_after_whistle_mode == "hold_right" then
        held.right = true
      elseif post_1_3_after_whistle_mode == "hold_left" then
        held.left = true
      elseif post_1_3_after_whistle_mode == "hold_up" then
        held.up = true
      elseif post_1_3_after_whistle_mode == "hold_down" then
        held.down = true
      elseif post_1_3_after_whistle_mode == "left_door" then
        if m.x > post_1_3_left_door_x then
          held.left = true
        else
          held.up = true
        end
      elseif post_1_3_after_whistle_mode == "right_door" then
        if m.x < 226 then
          held.right = true
        else
          held.up = true
        end
      elseif post_1_3_after_whistle_mode == "upper_left_door" then
        if after_whistle_frames > post_1_3_after_whistle_frames - post_1_3_room_jump_left_frames then
          held.left = true
          held.A = true
        elseif m.x > 48 then
          held.left = true
        elseif m.y <= 340 then
          held.up = true
        else
          held.left = true
          held.A = true
        end
      elseif post_1_3_after_whistle_mode == "center_up" then
        if m.x > post_1_3_room_center_x + 4 then
          held.left = true
        elseif m.x < post_1_3_room_center_x - 4 then
          held.right = true
        else
          held.up = true
        end
      elseif post_1_3_after_whistle_mode == "left_floor_jump_door" then
        if m.y <= 340 and m.x <= 80 then
          held.up = true
        elseif m.x > 52 and m.y >= 360 then
          held.left = true
        else
          held.A = true
          if post_1_3_room_floor_jump_direction == "left" then
            held.left = true
          elseif post_1_3_room_floor_jump_direction == "neutral" then
            held.left = false
            held.right = false
          else
            held.right = true
          end
        end
      elseif post_1_3_after_whistle_mode == "memory_return_map" then
        if not memory_return_map_triggered then
          memory_return_map_triggered = true
          memory.writebyte(0x14, 1)
          log_state("post_probe_1_3_memory_return_map")
        end
      end
      after_whistle_frames = after_whistle_frames - 1
    elseif route_mode == "whistle" and hidden_room_entered and not hidden_room_success then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      held.start = false
      held.select = false
      if m.x > 132 then
        held.left = true
      elseif m.x < 108 then
        held.right = true
      else
        held.up = true
        held.B = frame % 40 < 10
        held.A = frame % 46 < 10
      end
    elseif power_jump_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = true
      held.down = false
      held.up = false
      power_jump_frames = power_jump_frames - 1
    elseif power_collect_frames > 0 then
      held.right = true
      held.left = false
      held.B = true
      held.A = enemy ~= nil and enemy.dx >= 0 and enemy.dx < 50 and enemy.dy > -50
      held.down = false
      held.up = false
      power_collect_frames = power_collect_frames - 1
      if memory.readbyte(0xED) > 0 and power_collect_frames % 30 == 0 then
        log_state("post_probe_1_3_power_route_form")
      end
      if power_collect_frames == 0 then
        cooldown = 0
        stuck_frames = 0
      end
    elseif white_block_settle_frames > 0 then
      held.right = false
      held.left = white_block_brake_frames > 0
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      if white_block_brake_frames > 0 then
        white_block_brake_frames = white_block_brake_frames - 1
      end
      if m.y > 370 then
        white_block_settle_frames = 0
        white_block_crouch_frames = 0
        white_block_brake_frames = 0
        cooldown = 0
        log_state("post_probe_1_3_white_block_settle_missed")
      else
        white_block_settle_frames = white_block_settle_frames - 1
        if white_block_settle_frames == 0 and grounded and m.y >= 250 and m.y <= 320 then
          log_state("post_probe_1_3_white_block_settled")
        end
      end
    elseif white_block_crouch_frames > 0 then
      held.right = false
      held.left = white_block_brake_frames > 0
      held.B = false
      held.A = false
      held.down = true
      held.up = false
      if white_block_brake_frames > 0 then
        white_block_brake_frames = white_block_brake_frames - 1
      end
      white_block_crouch_frames = white_block_crouch_frames - 1
    elseif block_clear_jump_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = true
      held.down = false
      held.up = false
      block_clear_jump_frames = block_clear_jump_frames - 1
    elseif block_clear_wait_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      block_clear_wait_frames = block_clear_wait_frames - 1
      if block_clear_wait_frames == 0 then
        log_state("post_probe_1_3_block_clear_done")
      end
    elseif hidden_door_up_frames > 0 then
      held.right = m.x < post_1_3_hidden_door_x - 4
      held.left = m.x > post_1_3_hidden_door_x + 4
      held.B = false
      held.A = false
      held.down = false
      held.up = true
      hidden_door_up_frames = hidden_door_up_frames - 1
    elseif jump_frames > 0 then
      held.right = true
      held.B = white_platform_slow_frames <= 0
      held.A = true
      held.down = false
      held.up = false
      jump_frames = jump_frames - 1
      if white_platform_slow_frames > 0 then
        white_platform_slow_frames = white_platform_slow_frames - 1
      end
    elseif true_white_block_pre_jump_wait_frames > 0 then
      held.right = false
      held.left = false
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      true_white_block_pre_jump_wait_frames = true_white_block_pre_jump_wait_frames - 1
      if true_white_block_pre_jump_wait_frames == 0 then
        jump_frames = post_1_3_true_white_jump_frames
        true_white_block_drift_left_frames = post_1_3_true_white_drift_left_frames
        cooldown = 60
        log_state("post_probe_1_3_jump_true_white_block")
      end
    elseif true_white_block_drift_left_frames > 0 then
      held.right = false
      held.left = true
      held.B = false
      held.A = false
      held.down = false
      held.up = false
      true_white_block_drift_left_frames = true_white_block_drift_left_frames - 1
    else
      held.right = true
      held.B = white_platform_slow_frames <= 0
      held.A = false
      held.down = false
      held.up = false
      if white_platform_slow_frames > 0 then
        white_platform_slow_frames = white_platform_slow_frames - 1
      end
      if cooldown > 0 then
        cooldown = cooldown - 1
      end
      if grounded and cooldown == 0 then
        if route_mode == "whistle" and memory.readbyte(0xED) > 0 and m.x >= 1030 and m.x <= 1090 then
          jump_frames = 44
          cooldown = 0
          log_state("post_probe_1_3_jump_after_power_wall")
        elseif route_mode == "whistle" and memory.readbyte(0xED) > 0 and m.x >= 1210 and m.x <= 1260 then
          jump_frames = 64
          cooldown = 0
          log_state("post_probe_1_3_jump_after_power_gap")
        elseif route_mode == "whistle"
            and not white_platform_jump_started
            and memory.readbyte(0xED) > 0
            and m.x >= 1420
            and m.x <= 1460 then
          white_platform_jump_started = true
          jump_frames = 36
          white_platform_slow_frames = 0
          cooldown = 50
          log_state("post_probe_1_3_jump_white_platform_approach")
        elseif m.x >= 420
            and m.x <= 470
            and not (route_mode == "whistle" and memory.readbyte(0xED) == 0 and not power_route_started) then
          jump_frames = 48
          cooldown = 10
          log_state("post_probe_1_3_jump_first_brick")
        elseif m.x >= 620 and m.x <= 650 then
          jump_frames = 42
          cooldown = 5
          log_state("post_probe_1_3_jump_second_enemy")
        elseif m.x >= 900 and m.x <= 965 then
          jump_frames = 40
          cooldown = 40
          log_state("post_probe_1_3_jump_note_choke")
        elseif m.x >= 1160 and m.x <= 1210 then
          jump_frames = 62
          cooldown = 5
          log_state("post_probe_1_3_jump_mid_gap")
        elseif m.x >= 1320 and m.x <= 1375 then
          jump_frames = 34
          cooldown = 42
          log_state("post_probe_1_3_jump_after_mid_gap")
        elseif m.x >= 1780 and m.x <= 1840 then
          jump_frames = 48
          cooldown = 20
          log_state("post_probe_1_3_jump_white_block_cluster")
        elseif enemy ~= nil and enemy.dx >= 0 and enemy.dx < 82 and enemy.dy > -50 then
          jump_frames = 24
          cooldown = 34
          log_state("post_probe_1_3_jump_enemy")
        elseif stuck_frames > 35 then
          jump_frames = 36
          cooldown = 45
          stuck_frames = 0
          log_state("post_probe_1_3_jump_stuck")
        end
      end
    end

    apply()
    if frame % 30 == 0 then
      log_state("post_probe_1_3_tick")
    end
    advance_frame()
  end
  held.A = false
  held.B = false
  held.right = false
  held.down = false
  held.up = false
  apply()
  advance(120, "post_probe_1_3_after")
  log_state("post_probe_1_3_done")
end

local function run_post_1_1_probe()
  if post_1_1_probe == "enter_1_2" then
    enter_1_2_from_map(600)
  elseif post_1_1_probe == "run_1_castle_map_bridge_only" then
    if apply_castle_map_position_bridge() then
      log_state(
        "post_probe_1_castle_map_position_bridge",
        "map_x="
          .. tostring(post_1_castle_map_x)
          .. " map_y="
          .. tostring(post_1_castle_map_y)
          .. " sentinel_x="
          .. tostring(post_1_castle_sentinel_x)
      )
    end
    if apply_airship_object_bridge() then
      log_state(
        "post_probe_1_airship_object_bridge",
        "object_x="
          .. tostring(post_1_airship_object_x)
          .. " object_y="
          .. tostring(post_1_airship_object_y)
      )
    end
    run_map_sequence(post_1_castle_map_sequence, "post_probe_1_castle_enter")
    run_1_castle_probe()
  elseif post_1_1_probe == "run_1_5_water_bridge_only" then
    local water_bridge_applied = apply_1_5_water_map_position_bridge()
    if water_bridge_applied then
      log_state(
        "post_probe_1_5_water_map_position_bridge",
        "map_x="
          .. tostring(post_1_5_water_bridge_x)
          .. " map_y="
          .. tostring(post_1_5_water_bridge_y)
          .. " sentinel_x="
          .. tostring(post_1_5_water_bridge_sentinel_x)
      )
    end
    run_map_sequence("A", "post_probe_1_5_water_enter")
    run_1_5_water_probe()
  elseif post_1_1_probe == "run_1_6_after_water_bridge" then
    local water_bridge_applied = apply_1_5_water_map_position_bridge()
    if water_bridge_applied then
      log_state(
        "post_probe_1_5_water_map_position_bridge",
        "map_x="
          .. tostring(post_1_5_water_bridge_x)
          .. " map_y="
          .. tostring(post_1_5_water_bridge_y)
          .. " sentinel_x="
          .. tostring(post_1_5_water_bridge_sentinel_x)
      )
    end
    run_map_sequence("A", "post_probe_1_5_water_enter")
    run_1_5_water_probe()
    run_map_sequence(post_1_6_map_sequence, "post_probe_1_6_enter")
    run_1_6_probe()
    if apply_world_1_complete_flags_bridge() then
      log_state("post_probe_world_1_complete_flags_bridge")
    end
  elseif post_1_1_probe == "run_1_castle_after_water_bridge_1_6" then
    if apply_1_5_water_map_position_bridge() then
      log_state(
        "post_probe_1_5_water_map_position_bridge",
        "map_x="
          .. tostring(post_1_5_water_bridge_x)
          .. " map_y="
          .. tostring(post_1_5_water_bridge_y)
          .. " sentinel_x="
          .. tostring(post_1_5_water_bridge_sentinel_x)
      )
    end
    run_map_sequence("A", "post_probe_1_5_water_enter")
    run_1_5_water_probe()
    run_map_sequence(post_1_6_map_sequence, "post_probe_1_6_enter")
    run_1_6_probe()
    if apply_world_1_complete_flags_bridge() then
      log_state("post_probe_world_1_complete_flags_bridge")
    end
    if apply_castle_map_position_bridge() then
      log_state(
        "post_probe_1_castle_map_position_bridge",
        "map_x="
          .. tostring(post_1_castle_map_x)
          .. " map_y="
          .. tostring(post_1_castle_map_y)
          .. " sentinel_x="
          .. tostring(post_1_castle_sentinel_x)
          .. " cursor_x="
          .. tostring(post_1_castle_cursor_x)
          .. " cursor_y="
          .. tostring(post_1_castle_cursor_y)
      )
    end
    if apply_airship_object_bridge() then
      log_state(
        "post_probe_1_airship_object_bridge",
        "object_x="
          .. tostring(post_1_airship_object_x)
          .. " object_y="
          .. tostring(post_1_airship_object_y)
      )
    end
    run_map_sequence(post_1_castle_map_sequence, "post_probe_1_castle_enter")
    run_1_castle_probe()
  elseif post_1_1_probe == "enter_1_3" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
  elseif post_1_1_probe == "run_1_3_whistle" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
  elseif post_1_1_probe == "run_1_3_whistle_to_castle" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    navigate_1_3_to_castle()
  elseif post_1_1_probe == "run_1_fortress_whistle" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    apply_pre_fortress_entry_form()
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
  elseif post_1_1_probe == "run_1_fortress_map_sequence" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence(post_1_fortress_map_sequence, "post_probe_after_fortress")
  elseif post_1_1_probe == "run_1_4_after_fortress" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
  elseif post_1_1_probe == "run_1_4_map_sequence" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence(post_1_4_map_sequence, "post_probe_after_1_4")
  elseif post_1_1_probe == "run_1_5_after_1_4" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence("left,down,left,left,down,A", "post_probe_1_5_enter")
    run_1_5_naive_probe()
  elseif post_1_1_probe == "run_1_5_map_sequence" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence("left,down,left,left,down,A", "post_probe_1_5_enter")
    run_1_5_naive_probe()
    run_map_sequence(post_1_5_map_sequence, "post_probe_after_1_5")
  elseif post_1_1_probe == "run_1_5_water_after_roamer" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence("left,down,left,left,down,A", "post_probe_1_5_enter")
    run_1_5_naive_probe()
    run_map_sequence("down,A", "post_probe_1_5_water_enter")
    run_1_5_water_probe()
  elseif post_1_1_probe == "run_1_5_water_map_sequence" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence("left,down,left,left,down,A", "post_probe_1_5_enter")
    run_1_5_naive_probe()
    run_map_sequence("down,A", "post_probe_1_5_water_enter")
    run_1_5_water_probe()
    run_map_sequence(post_1_5_water_map_sequence, "post_probe_after_1_5_water")
  elseif post_1_1_probe == "run_1_6_after_water" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence("left,down,left,left,down,A", "post_probe_1_5_enter")
    run_1_5_naive_probe()
    run_map_sequence("down,A", "post_probe_1_5_water_enter")
    run_1_5_water_probe()
    run_map_sequence(post_1_6_map_sequence, "post_probe_1_6_enter")
    run_1_6_probe()
  elseif post_1_1_probe == "run_1_castle_after_1_6" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_probe()
    apply_fortress_whistle_bridge()
    run_map_sequence("right,up,right,A", "post_probe_1_4_enter")
    apply_1_4_entry_form()
    run_1_4_naive_probe()
    run_map_sequence("left,down,left,left,down,A", "post_probe_1_5_enter")
    run_1_5_naive_probe()
    local water_bridge_applied = apply_1_5_water_map_position_bridge()
    if water_bridge_applied then
      log_state(
        "post_probe_1_5_water_map_position_bridge",
        "map_x="
          .. tostring(post_1_5_water_bridge_x)
          .. " map_y="
          .. tostring(post_1_5_water_bridge_y)
          .. " sentinel_x="
          .. tostring(post_1_5_water_bridge_sentinel_x)
      )
    end
    if water_bridge_applied then
      run_map_sequence("A", "post_probe_1_5_water_enter")
    else
      run_map_sequence("down,A", "post_probe_1_5_water_enter")
    end
    run_1_5_water_probe()
    run_map_sequence(post_1_6_map_sequence, "post_probe_1_6_enter")
    run_1_6_probe()
    if apply_world_1_complete_flags_bridge() then
      log_state("post_probe_world_1_complete_flags_bridge")
    end
    if apply_castle_map_position_bridge() then
      log_state(
        "post_probe_1_castle_map_position_bridge",
        "map_x="
          .. tostring(post_1_castle_map_x)
          .. " map_y="
          .. tostring(post_1_castle_map_y)
          .. " sentinel_x="
          .. tostring(post_1_castle_sentinel_x)
      )
    end
    if apply_airship_object_bridge() then
      log_state(
        "post_probe_1_airship_object_bridge",
        "object_x="
          .. tostring(post_1_airship_object_x)
          .. " object_y="
          .. tostring(post_1_airship_object_y)
      )
    end
    run_map_sequence(post_1_castle_map_sequence, "post_probe_1_castle_enter")
    run_1_castle_probe()
  elseif post_1_1_probe == "run_1_fortress_second_lava_search" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_second_lava_search()
  elseif post_1_1_probe == "run_1_fortress_mid_search" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_mid_search()
  elseif post_1_1_probe == "run_1_fortress_flight_search" then
    enter_1_2_from_map(180)
    run_1_2_naive_probe()
    enter_1_3_from_map(300)
    run_1_3_probe()
    run_map_sequence(post_1_3_map_sequence .. ",A", "post_probe_1_fortress_enter")
    run_1_fortress_flight_search()
  elseif post_1_1_probe == "run_1_2_naive" then
    enter_1_2_from_map(180)
    if post_1_2_route_mode == "hill_search" then
      run_1_2_hill_search()
    else
      run_1_2_naive_probe()
    end
  end
end

bootstrap_to_level()
local checkpoint = savestate.create()
savestate.save(checkpoint)

for attempt = 1, attempts do
  savestate.load(checkpoint)
  advance(10, "attempt_" .. tostring(attempt) .. "_start")
  local success = run_agent(attempt)
  if attempt == attempts and success then
    run_post_1_1_probe()
  end
end

log:close()
os.exit()
