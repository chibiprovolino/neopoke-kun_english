-- Unlock-logic test. Env: UT_OUT, UT_A, UT_B, UT_MOOD, UT_HOUR (BCD hex, optional), UT_SEQ "frame:Button,frame:Button", UT_STOP, UT_SNAPS "f,f"
local OUT = os.getenv("UT_OUT")
local function num(n, d) local v = os.getenv(n); if v and v ~= "" then return tonumber(v) end; return d end
local A, B, MOOD, HOUR, STOP = num("UT_A"), num("UT_B"), num("UT_MOOD"), num("UT_HOUR"), num("UT_STOP", 4000)
local HOLD = num("UT_HOLDMOOD", 0)
local seq, snaps = {}, {}
for fr, b in (os.getenv("UT_SEQ") or ""):gmatch("(%d+):([^,]+)") do seq[#seq + 1] = {tonumber(fr), b} end
for fr in (os.getenv("UT_SNAPS") or ""):gmatch("%d+") do snaps[tonumber(fr)] = true end
local C = manager.machine.ioport.ports[":Controls"].fields
local P = manager.machine.ioport.ports[":Power"].fields["Power On"]
local sp = manager.machine.devices[":maincpu"].spaces["program"]
local log = io.open(OUT .. "/log.txt", "w")
local names = {"Option", "Button A", "Button B", "Down", "Right", "Up", "Left"}
local f, last = 0, ""
local function s8(v) if v > 127 then return v - 256 end; return v end
local function state()
  local fl = {}
  for a = 0x4525, 0x4543 do fl[#fl + 1] = string.format("%02x", sp:read_u8(a)) end
  return string.format("A=%d mood=%d B=%d b6=%d c9=%02x period=%d be=%d t=%02x:%02x 4804=%02x flags=%s",
    sp:read_u16(0x4520), s8(sp:read_u8(0x4522)), sp:read_u16(0x4523), sp:read_u8(0x44b6), sp:read_u8(0x44c9),
    sp:read_u8(0x451d), sp:read_u8(0x44be), sp:read_u8(0x43a2), sp:read_u8(0x43a3), sp:read_u8(0x4804), table.concat(fl, " "))
end
emu.register_frame_done(function()
  f = f + 1
  P:set_value(f < 20 and 1 or 0)
  for _, n in ipairs(names) do C[n]:set_value(0) end
  if f > 200 and f < 1900 and f % 90 < 6 then C["Button A"]:set_value(1) end
  for _, s in ipairs(seq) do if f >= s[1] and f < s[1] + 8 then C[s[2]]:set_value(1) end end
  if HOUR and f > 100 then sp:write_u8(0x94, HOUR) end
  if f == 2250 then
    if A then sp:write_u16(0x4520, A) end
    if B then sp:write_u16(0x4523, B) end
    if MOOD then sp:write_u8(0x4522, MOOD & 0xff) end
  end
  if HOLD == 1 and f > 2250 and MOOD then sp:write_u8(0x4522, MOOD & 0xff) end
  if f >= 2240 then
    local s = state()
    if s ~= last then log:write(f .. " " .. s .. "\n"); log:flush(); last = s end
  end
  if snaps[f] then manager.machine.video:snapshot() end
  if f >= STOP then log:close(); manager.machine:exit() end
end)
