-- Generic room trace. Env: TR_OUT, TR_SEQ "frame:Button[:hold],...", TR_SNAPS "f,f", TR_EVERY "from:to:step" (snapshots),
-- TR_TRIG "addr=val:count:step[:delay]" (snapshots once the byte first equals val),
-- TR_EVENT "id" (decimal: every room event is replaced by this event id),
-- TR_FORCE "addr=val,addr:=val" (hex; writes to that byte are replaced by val: "=" only non-zero writes, ":=" every write),
-- TR_DUMP "from:to:every" (hex range: logs which bytes in the range were ever non-zero, sampled every N frames),
-- TR_RESET "frame" (soft reset once at that frame; the script restarts, takes no input but the title presses, and logs to log2.txt),
-- TR_POKE "frame:addr=val,..." (hex addr, 8-bit), TR_HOLD "from:addr=val,..." (rewritten every frame), TR_WATCH "addr,addr" (hex, logged on change), TR_STOP
local OUT = os.getenv("TR_OUT")
local STOP = tonumber(os.getenv("TR_STOP") or "4000")
local seq, snaps, pokes, holds, watch = {}, {}, {}, {}, {}
for fr, b, h in (os.getenv("TR_SEQ") or ""):gmatch("(%d+):([%a ]+):?(%d*)") do seq[#seq + 1] = {tonumber(fr), b, tonumber(h) or 8} end
for fr in (os.getenv("TR_SNAPS") or ""):gmatch("%d+") do snaps[tonumber(fr)] = true end
local ea, eb, es = (os.getenv("TR_EVERY") or ""):match("(%d+):(%d+):(%d+)")
for fr, a, v in (os.getenv("TR_POKE") or ""):gmatch("(%d+):(%x+)=(%x+)") do pokes[#pokes + 1] = {tonumber(fr), tonumber(a, 16), tonumber(v, 16)} end
for fr, a, v in (os.getenv("TR_HOLD") or ""):gmatch("(%d+):(%x+)=(%x+)") do holds[#holds + 1] = {tonumber(fr), tonumber(a, 16), tonumber(v, 16)} end
for a in (os.getenv("TR_WATCH") or "44be,44fd,4507,44c3,4512,44ff,4520,4522,44b6"):gmatch("%x+") do watch[#watch + 1] = tonumber(a, 16) end
local ta, tv, tn, ts, td = (os.getenv("TR_TRIG") or ""):match("(%x+)=(%x+):(%d+):(%d+):?(%d*)")
local t0 = nil
local C = manager.machine.ioport.ports[":Controls"].fields
local P = manager.machine.ioport.ports[":Power"].fields["Power On"]
local sp = manager.machine.devices[":maincpu"].spaces["program"]
local EV = tonumber(os.getenv("TR_EVENT") or "")
if EV then EVTAP = sp:install_write_tap(0x44b2, 0x44b3, "ev", function(o, d, m) if m == 0xffff and d ~= 0 then return EV end if o == 0x44b2 and m == 0xff and d ~= 0 then return EV end return d end) end
FTAPS = {}
for a, op, v in (os.getenv("TR_FORCE") or ""):gmatch("(%x+)(:?=)(%x+)") do
  local A, V, all = tonumber(a, 16), tonumber(v, 16), op == ":="
  FTAPS[#FTAPS + 1] = sp:install_write_tap(A, A, "f" .. a, function(o, d, m) if all or d ~= 0 then return V end return d end)
end
local da, db, de = (os.getenv("TR_DUMP") or ""):match("(%x+):(%x+):(%d+)")
local used = {}
local RESET = tonumber(os.getenv("TR_RESET") or "")
local mark = io.open(OUT .. "/reset_done", "r")
local PHASE2 = mark ~= nil
if mark then mark:close(); seq, pokes, holds = {}, {}, {} end
local log = io.open(OUT .. (PHASE2 and "/log2.txt" or "/log.txt"), "w")
local names = {"Option", "Button A", "Button B", "Down", "Right", "Up", "Left"}
local f, last = 0, ""
emu.register_frame_done(function()
  f = f + 1
  P:set_value(f < 20 and 1 or 0)
  for _, n in ipairs(names) do C[n]:set_value(0) end
  if f > 200 and f < 2100 and f % 90 < 6 then C["Button A"]:set_value(1) end
  for _, s in ipairs(seq) do if f >= s[1] and f < s[1] + s[3] then C[s[2]]:set_value(1) end end
  for _, p in ipairs(pokes) do if p[1] == f then sp:write_u8(p[2], p[3]) end end
  for _, p in ipairs(holds) do if f >= p[1] then sp:write_u8(p[2], p[3]) end end
  if f >= 2000 then
    local t = {}
    for _, a in ipairs(watch) do t[#t + 1] = string.format("%04x=%02x", a, sp:read_u8(a)) end
    local s = table.concat(t, " ")
    if s ~= last then log:write(f .. " " .. s .. "\n"); log:flush(); last = s end
  end
  if snaps[f] or (ea and f >= tonumber(ea) and f <= tonumber(eb) and (f - tonumber(ea)) % tonumber(es) == 0) then
    manager.machine.video:snapshot(); log:write(f .. " snap\n")
  end
  if ta and not t0 and f > 2100 and sp:read_u8(tonumber(ta, 16)) == tonumber(tv, 16) then t0 = f + (tonumber(td) or 0); log:write(f .. " trigger\n") end
  if t0 and f >= t0 and (f - t0) % tonumber(ts) == 0 and (f - t0) // tonumber(ts) < tonumber(tn) then manager.machine.video:snapshot(); log:write(f .. " snap\n") end
  if t0 and f > t0 + tonumber(ts) * tonumber(tn) + 5 then log:close(); manager.machine:exit() end
  if da and f > 300 and f % tonumber(de) == 0 then for a = tonumber(da, 16), tonumber(db, 16) do if sp:read_u8(a) ~= 0 then used[a] = true end end end
  if da and f >= STOP then local t = {} for a = tonumber(da, 16), tonumber(db, 16) do t[#t + 1] = used[a] and "X" or "." end log:write("used " .. table.concat(t) .. "\n") end
  if RESET and not PHASE2 and f == RESET then log:close(); local m = io.open(OUT .. "/reset_done", "w"); m:write("x"); m:close(); manager.machine:soft_reset(); return end
  if f >= STOP then log:close(); manager.machine:exit() end
end)
