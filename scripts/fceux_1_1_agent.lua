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

local function run_post_1_1_probe()
  if post_1_1_probe == "enter_1_2" then
    enter_1_2_from_map(600)
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
