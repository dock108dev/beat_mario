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
local post_1_3_after_whistle_mode = os.getenv("SMB3_1_3_AFTER_WHISTLE_MODE") or "memory_return_map"
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
local post_1_fortress_second_lava_wait_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_WAIT_FRAMES") or "0")
local post_1_fortress_second_lava_backup_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_BACKUP_FRAMES") or "4")
local post_1_fortress_first_lava_start = tonumber(os.getenv("SMB3_1_FORTRESS_FIRST_LAVA_START") or "250")
local post_1_fortress_first_lava_end = tonumber(os.getenv("SMB3_1_FORTRESS_FIRST_LAVA_END") or "285")
local post_1_fortress_first_lava_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FIRST_LAVA_JUMP_FRAMES") or "58")
local post_1_fortress_second_lava_accel_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_ACCEL_FRAMES") or "0")
local post_1_fortress_second_lava_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_JUMP_FRAMES") or "100")
local post_1_fortress_second_lava_drift_left_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_DRIFT_LEFT_FRAMES") or "12")
local post_1_fortress_second_lava_cooldown_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_COOLDOWN_FRAMES") or "105")
local post_1_fortress_second_lava_stair_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_SECOND_LAVA_STAIR_JUMP_FRAMES") or "78")
local post_1_fortress_third_lava_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_THIRD_LAVA_JUMP_FRAMES") or "88")
local post_1_fortress_flat_enemy_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLAT_ENEMY_JUMP_FRAMES") or "44")
local post_1_fortress_mid_hazard_run_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_RUN_FRAMES") or "60")
local post_1_fortress_mid_hazard_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_JUMP_FRAMES") or "32")
local post_1_fortress_mid_hazard_wait_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_WAIT_FRAMES") or "0")
local post_1_fortress_mid_hazard_drift_left_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_DRIFT_LEFT_FRAMES") or "0")
local post_1_fortress_mid_hazard_start = tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_START") or "1000")
local post_1_fortress_mid_hazard_end = tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_END") or "1065")
local post_1_fortress_mid_hazard_pre_wait_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_PRE_WAIT_FRAMES") or "0")
local post_1_fortress_mid_hazard_pre_wait_start =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_PRE_WAIT_START") or "1000")
local post_1_fortress_mid_hazard_pre_wait_end =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_PRE_WAIT_END") or "1060")
local post_1_fortress_mid_hazard_followup_start =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_FOLLOWUP_START") or "1035")
local post_1_fortress_mid_hazard_followup_end =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_FOLLOWUP_END") or "1065")
local post_1_fortress_mid_hazard_followup_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MID_HAZARD_FOLLOWUP_JUMP_FRAMES") or "0")
local post_1_fortress_search_limit = tonumber(os.getenv("SMB3_1_FORTRESS_SEARCH_LIMIT") or "500")
local post_1_fortress_flight_backup_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_BACKUP_FRAMES") or "0")
local post_1_fortress_flight_run_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_RUN_FRAMES") or "0")
local post_1_fortress_flight_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_JUMP_FRAMES") or "28")
local post_1_fortress_flight_flap_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_FLAP_FRAMES") or "300")
local post_1_fortress_flight_flap_period =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_FLAP_PERIOD") or "6")
local post_1_fortress_flight_flap_press_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_FLAP_PRESS_FRAMES") or "3")
local post_1_fortress_flight_up_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_UP_FRAMES") or "120")
local post_1_fortress_flight_launch_start =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_LAUNCH_START") or "1530")
local post_1_fortress_flight_launch_end =
  tonumber(os.getenv("SMB3_1_FORTRESS_FLIGHT_LAUNCH_END") or "1660")
local post_1_fortress_final_start_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_START_X") or "1740")
local post_1_fortress_final_direct_min_p =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_DIRECT_MIN_P") or "48")
local post_1_fortress_final_back_target_x =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_TARGET_X") or "1555")
local post_1_fortress_final_back_jump_start_x =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_JUMP_START_X") or "1700")
local post_1_fortress_final_back_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_JUMP_FRAMES") or "34")
local post_1_fortress_final_back_jump_left_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_BACK_JUMP_LEFT_FRAMES") or "10")
local post_1_fortress_final_run_target_x =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_RUN_TARGET_X") or "1730")
local post_1_fortress_final_launch_x = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_LAUNCH_X") or "1700")
local post_1_fortress_final_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_JUMP_FRAMES") or "28")
local post_1_fortress_final_obstacle_jump_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_OBSTACLE_JUMP_FRAMES") or "34")
local post_1_fortress_final_flap_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FLAP_FRAMES") or "360")
local post_1_fortress_final_flap_period =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FLAP_PERIOD") or "2")
local post_1_fortress_final_flap_press_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_FLAP_PRESS_FRAMES") or "1")
local post_1_fortress_final_up_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_UP_FRAMES") or "360")
local post_1_fortress_final_config = {
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
  tail_min_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_MIN_DX") or "8"),
  tail_max_dx = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_MAX_DX") or "56"),
  tail_release_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_RELEASE_FRAMES") or "4"),
  tail_swing_frames = tonumber(os.getenv("SMB3_1_FORTRESS_FINAL_TAIL_SWING_FRAMES") or "10"),
}
local post_1_fortress_power_config = {
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
local post_1_fortress_max_frames =
  tonumber(os.getenv("SMB3_1_FORTRESS_MAX_FRAMES") or "5200")
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
  advance(180, event_prefix .. "_wait")
  for token in string.gmatch(sequence, "[^,]+") do
    step = step + 1
    local button = string.gsub(token, "^%s*(.-)%s*$", "%1")
    if button == "wait" then
      advance(60, event_prefix .. "_wait_" .. tostring(step))
    elseif button ~= "" then
      press(button, 18, event_prefix .. "_" .. tostring(step) .. "_" .. button)
      advance(60, event_prefix .. "_after_" .. tostring(step) .. "_" .. button)
    end
  end
  advance(240, event_prefix .. "_done_wait")
  log_state(event_prefix .. "_done")
end

local function navigate_1_3_to_castle()
  log_state("post_probe_1_3_to_castle_start")
  run_map_sequence(post_1_3_map_sequence, "post_probe_1_3_to_castle")
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
      held.right = true
      held.left = false
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
      held.right = true
      held.left = false
      held.B = true
      held.A = (flight_flap_frames % post_1_fortress_flight_flap_period) < post_1_fortress_flight_flap_press_frames
      held.down = false
      held.up = false
      flight_flap_frames = flight_flap_frames - 1
      if flight_flap_frames == 0 then
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
      if grounded then
        if leaf_phase == "pending"
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
        elseif cooldown == 0 and enemy ~= nil and enemy.dx >= 0 and enemy.dx < 72 and enemy.dy > -64 then
          jump_frames = 28
          cooldown = 42
          log_state("post_probe_1_fortress_jump_enemy")
        elseif cooldown == 0 and stuck_frames > 35 then
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
  advance(180, "post_probe_1_fortress_after")
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

    if m.x >= 8192 or m.y == 0 then
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

    if not first_platform_ride_started and grounded and m.x >= 240 and m.x <= 310 and m.y >= 300 and m.y <= 340 then
      first_platform_ride_started = true
      platform_ride_frames = 12
      cooldown = 0
      log_state("post_probe_1_4_first_platform_ride")
    end

    if eighth_platform_wait_frames > 0 then
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
          jump_frames = 58
          cooldown = 0
          log_state("post_probe_1_4_jump_sixth_gap")
        elseif sixth_gap_started
            and not seventh_gap_started
            and m.x >= 645
            and m.x <= 690
            and m.y >= 320
            and m.y <= 360 then
          seventh_gap_started = true
          jump_frames = 30
          cooldown = 55
          log_state("post_probe_1_4_jump_seventh_gap")
        elseif seventh_gap_started
            and not eighth_gap_started
            and m.x >= 790
            and m.x <= 825
            and m.y >= 320
            and m.y <= 360 then
          eighth_gap_started = true
          jump_frames = 70
          cooldown = 0
          log_state("post_probe_1_4_jump_eighth_gap")
        elseif eighth_gap_started
            and not ninth_gap_started
            and m.x >= 760
            and m.x <= 790
            and m.y >= 320
            and m.y <= 360 then
          ninth_gap_started = true
          jump_frames = 70
          cooldown = 85
          log_state("post_probe_1_4_jump_ninth_gap")
        elseif enemy ~= nil and enemy.id ~= 54 and enemy.dx >= 0 and enemy.dx < 90 and enemy.dy > -55 then
          jump_frames = 24
          cooldown = 36
          log_state("post_probe_1_4_jump_enemy")
        elseif stuck_frames > 35 then
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
  advance(360, "post_probe_1_4_after")
  log_state("post_probe_1_4_done")
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
        and m.x >= 220
        and m.y >= 300
        and m.y <= 340 then
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
    run_1_fortress_probe()
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
