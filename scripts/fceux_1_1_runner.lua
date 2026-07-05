local log_path = os.getenv("SMB3_AGENT_LOG") or "/tmp/smb3_agent_fceux_1_1.jsonl"
local attempts = tonumber(os.getenv("SMB3_AGENT_ATTEMPTS") or "1")
local log = assert(io.open(log_path, "w"))

local held = {}

local function snapshot(extra)
  local x = memory.readbyte(0x90) + memory.readbyte(0x75) * 256
  local y = memory.readbyte(0xA2) + memory.readbyte(0x87) * 256
  local scroll_x = memory.readbyte(0xFD) + memory.readbyte(0x12) * 256
  local scroll_y = memory.readbyte(0xFC)
  local on_map = memory.readbyte(0x73) == 0x20
  local air = memory.readbyte(0xD8)
  local fields = {
    "frame=" .. tostring(movie.framecount()),
    "x=" .. tostring(x),
    "y=" .. tostring(y),
    "sx=" .. tostring(x - scroll_x),
    "sy=" .. tostring(y - scroll_y),
    "scroll_x=" .. tostring(scroll_x),
    "scroll_y=" .. tostring(scroll_y),
    "air=" .. tostring(air),
    "on_map=" .. tostring(on_map),
  }
  if extra ~= nil then
    fields[#fields + 1] = "event=" .. tostring(extra)
  end
  log:write(table.concat(fields, " ") .. "\n")
  log:flush()
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
      snapshot(event)
    elseif movie.framecount() % 30 == 0 then
      snapshot(nil)
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

local function hold(button, event)
  held[button] = true
  snapshot(event or ("hold_" .. button))
end

local function release(button, event)
  held[button] = false
  snapshot(event or ("release_" .. button))
end

local function tap_a(frames)
  press("A", frames, "tap_A_" .. tostring(frames))
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
  snapshot("level_checkpoint")
end

local function run_baseline_route()
  hold("right")
  hold("B")
  advance(27, "wait_0_45")
  tap_a(11)
  advance(54, "wait_0_90")
  tap_a(10)
  advance(12, "wait_0_20")
  release("B")
  release("right")
  advance(66, "wait_1_10")
  hold("right")
  hold("B")
  advance(5, "wait_0_08")
  tap_a(14)
  advance(42, "wait_0_70")
  tap_a(12)
  advance(84, "wait_1_40")
  tap_a(11)
  advance(39, "wait_0_65")
  tap_a(11)
  advance(51, "wait_0_85")
  tap_a(5)
  advance(30, "wait_0_50")
  tap_a(13)
  advance(72, "wait_1_20")
  tap_a(11)
  advance(45, "wait_0_75")
  tap_a(13)
  advance(22, "wait_0_36")
  tap_a(5)
  advance(7, "wait_0_12")
  tap_a(18)
  advance(300, "wait_5_00")
  release("B")
  release("right")
  hold("right")
  hold("B")
  advance(6, "wait_0_10")
  tap_a(27)
  advance(54, "wait_0_90")
  tap_a(13)
  advance(21, "wait_0_35")
  release("B")
  release("right")
  advance(126, "wait_2_10")
  hold("right")
  hold("B")
  advance(6, "wait_0_10")
  tap_a(16)
  advance(48, "wait_0_80")
  tap_a(17)
  advance(150, "wait_2_50")
  tap_a(14)
  advance(33, "wait_0_55")
  tap_a(18)
  advance(60, "wait_1_00")
  tap_a(14)
  advance(180, "wait_3_00")
  release("right")
  hold("left")
  advance(33, "wait_0_55")
  tap_a(30)
  advance(21, "wait_0_35")
  release("left")
  hold("right")
  advance(480, "wait_8_00")
  release("B")
  release("right")
end

bootstrap_to_level()
local checkpoint = savestate.create()
savestate.save(checkpoint)

for attempt = 1, attempts do
  savestate.load(checkpoint)
  advance(10, "attempt_" .. tostring(attempt) .. "_start")
  run_baseline_route()
  advance(180, "attempt_" .. tostring(attempt) .. "_after")
  snapshot("attempt_" .. tostring(attempt) .. "_done")
end

log:close()
os.exit()
