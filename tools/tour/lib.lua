-- Shared tour helpers. A route script sets ROUTE = {name=..., seq={{frame,"Button",hold}...}, snaps={frames}, stop=frame, mash={from,to,button,period}}
-- then calls dofile(TOUR_DIR.."/lib.lua").
local R = ...
local OUT = os.getenv("TOUR_OUT") or "."
local map = dofile(os.getenv("TOUR_IDMAP"))
local f = 0
local C = manager.machine.ioport.ports[":Controls"].fields
local P = manager.machine.ioport.ports[":Power"].fields["Power On"]
local sp = manager.machine.devices[":maincpu"].spaces["program"]
local log = io.open(OUT .. "/log.txt", "w")
local pending = {}   -- ids read since last snapshot
local seen = {}
local last_new = -1
local shot = 0
-- binary search address -> ids
local function lookup(a)
  local lo, hi = 1, #map
  while lo <= hi do
    local m = (lo + hi) // 2
    local e = map[m]
    if a < e[1] then hi = m - 1 elseif a >= e[2] then lo = m + 1 else return e[3] end
  end
end
local function tapfn(offset, data, mask)
  local ids = lookup(offset)
  if ids then
    for _, id in ipairs(ids) do
      LAST_ID = id
      if not pending[id] then pending[id] = true; log:write(string.format("read %d %d\n", f, id)) end
      if not seen[id] then seen[id] = true; last_new = f end
    end
  end
  return data
end
TAPS = TAPS or {}
for _, r in ipairs({{0x2CC000, 0x2CFFFF}, {0x3EA300, 0x3F4FFF}}) do
  TAPS[#TAPS + 1] = sp:install_read_tap(r[1], r[2], "tourtxt" .. #TAPS, tapfn)
end
-- optional: R.ptr(frame) returns a CPU address to substitute for the save-prompt string pointer (0x2CC280)
ID_START = {}
for _, e in ipairs(map) do for _, id in ipairs(e[3]) do if not ID_START[id] then ID_START[id] = e[1] end end end
if R.ptr then
  TAPS[#TAPS + 1] = sp:install_read_tap(0x2CC280, 0x2CC283, "tourptr", function(offset, data, mask)
    local a = R.ptr(f)
    if a then return (a >> (8 * (offset - 0x2CC280))) & 0xFF end
    return data
  end)
end
local function snap(tag)
  shot = shot + 1
  manager.machine.video:snapshot()
  local ids = {}
  for id in pairs(pending) do ids[#ids + 1] = id end
  table.sort(ids)
  log:write(string.format("snap %d %d %s %s\n", shot, f, tag, table.concat(ids, ",")))
  log:flush()
  pending = {}
end
local names = {"Option", "Button A", "Button B", "Down", "Right", "Up", "Left"}
local snapset = {}
for _, s in ipairs(R.snaps or {}) do snapset[s] = true end
local auto_at = nil
emu.register_frame_done(function()
  f = f + 1
  P:set_value(f < 20 and 1 or 0)
  for _, n in ipairs(names) do C[n]:set_value(0) end
  -- BIOS first-run setup: mash A
  -- (up to 2100 so one press also dismisses the title screen; builds before the save-area fix skipped it by loading a bogus save)
  if f > 200 and f < 2100 and f % 90 < 6 then C["Button A"]:set_value(1) end
  for _, m in ipairs(R.mash or {}) do
    if f >= m[1] and f < m[2] and f % (m[4] or 60) < 6 then C[m[3]]:set_value(1) end
  end
  for _, s in ipairs(R.seq) do
    if f >= s[1] and f < s[1] + (s[3] or 8) then C[s[2]]:set_value(1) end
  end
  if R.every then
    local b, tag = R.every(sp, f)
    if b then C[b]:set_value(1) end
    if tag then snap(tag) end
  end
  if R.poke then for _, p in ipairs(R.poke) do if p[1] == f then p[2](sp) end end end
  if snapset[f] then snap(R.label and R.label(f) or "fixed") end
  -- auto snapshot: 45 frames after the last new string id appeared (text has finished drawing)
  if R.auto ~= false and last_new >= 0 and f == last_new + (R.autodelay or 45) then snap("auto") end
  if f >= R.stop then log:write("end " .. f .. "\n"); log:close(); manager.machine:exit() end
end)
