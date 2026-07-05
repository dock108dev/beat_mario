local log_path = os.getenv("SMB3_AGENT_LOG") or "artifacts/fceux_probe.log"
local log = io.open(log_path, "w")
log:write("lua started\n")
log:write("frame=" .. tostring(movie.framecount()) .. "\n")
log:close()
os.exit()
