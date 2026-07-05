local log_path = os.getenv("SMB3_AGENT_LOG") or "/tmp/smb3_agent_fceux_1_1_agent.log"
local image_dir = os.getenv("SMB3_AGENT_IMAGE_DIR")
local attempts = tonumber(os.getenv("SMB3_AGENT_ATTEMPTS") or "1")
local late_gap_start = tonumber(os.getenv("SMB3_LATE_GAP_START") or "1486")
local late_gap_end = tonumber(os.getenv("SMB3_LATE_GAP_END") or "1494")
local late_gap_frames = tonumber(os.getenv("SMB3_LATE_GAP_FRAMES") or "56")
local late_gap_hold_b = os.getenv("SMB3_LATE_GAP_HOLD_B") ~= "0"
local late_gap_slow_b_frames = tonumber(os.getenv("SMB3_LATE_GAP_SLOW_B_FRAMES") or "0")
local stair_climb_frames = tonumber(os.getenv("SMB3_STAIR_CLIMB_FRAMES") or "32")
local log = assert(io.open(log_path, "w"))

local held = {}

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
    FCEU.frameadvance()
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
      FCEU.frameadvance()
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
      FCEU.frameadvance()
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
      FCEU.frameadvance()
    end
  end
  held.A = false
  held.B = false
  held.right = false
  apply()
  advance(180, "attempt_" .. tostring(attempt) .. "_after")
  log_state("attempt_" .. tostring(attempt) .. "_done")
end

bootstrap_to_level()
local checkpoint = savestate.create()
savestate.save(checkpoint)

for attempt = 1, attempts do
  savestate.load(checkpoint)
  advance(10, "attempt_" .. tostring(attempt) .. "_start")
  run_agent(attempt)
end

log:close()
os.exit()
