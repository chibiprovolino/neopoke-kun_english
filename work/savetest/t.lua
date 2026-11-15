-- Save-area test. Env: ST_OUT, ST_SEQ "frame:Button,...", ST_STOP, ST_SNAPS "f,f", ST_CODE (CPU address of the VWF code, hex)
local OUT = os.getenv("ST_OUT")
local STOP = tonumber(os.getenv("ST_STOP") or "6000")
local CODE = tonumber(os.getenv("ST_CODE") or "0x3f5000")
local RESET = tonumber(os.getenv("ST_RESET") or "0")
local seq, snaps = {}, {}
for fr, b in (os.getenv("ST_SEQ") or ""):gmatch("(%d+):([^,]+)") do seq[#seq + 1] = {tonumber(fr), b} end
for fr in (os.getenv("ST_SNAPS") or ""):gmatch("%d+") do snaps[tonumber(fr)] = true end
local C = manager.machine.ioport.ports[":Controls"].fields
local P = manager.machine.ioport.ports[":Power"].fields["Power On"]
local sp = manager.machine.devices[":maincpu"].spaces["program"]
local log = io.open(OUT .. "/log.txt", "w")
local names = {"Option", "Button A", "Button B", "Down", "Right", "Up", "Left"}
local f, last = 0, ""
local function state()
  local s = {}
  for i = 0, 31 do
    local b = sp:read_u8(0x3f8000 + i * 256)
    s[#s + 1] = b == 0xff and "." or (b == 0 and "S" or "x")
  end
  local sum = 0
  for a = CODE, CODE + 0x15b do sum = (sum + sp:read_u8(a)) & 0xffff end
  return string.format("slots=%s vwf@%06x: %02x %02x %02x %02x sum=%04x A=%d", table.concat(s), CODE,
    sp:read_u8(CODE), sp:read_u8(CODE + 1), sp:read_u8(CODE + 2), sp:read_u8(CODE + 3), sum, sp:read_u16(0x4520))
end
emu.register_frame_done(function()
  f = f + 1
  if f == RESET then sp:write_u16(0x4520, 0); manager.machine:soft_reset() end
  P:set_value((f < 20 or (RESET > 0 and f > RESET and f < RESET + 20)) and 1 or 0)
  if RESET > 0 and f > RESET + 200 and f < RESET + 1900 and f % 90 < 6 then C["Button A"]:set_value(1) end
  for _, n in ipairs(names) do C[n]:set_value(0) end
  if f > 200 and f < 1900 and f % 90 < 6 then C["Button A"]:set_value(1) end
  for _, s in ipairs(seq) do if f >= s[1] and f < s[1] + 8 then C[s[2]]:set_value(1) end end
  if f == 2250 then sp:write_u16(0x4520, 123) end   -- marker so a real save is recognisable
  if f >= 2000 and f % 10 == 0 then
    local s = state()
    if s ~= last then log:write(f .. " " .. s .. "\n"); log:flush(); last = s end
  end
  if snaps[f] then manager.machine.video:snapshot() end
  if f >= STOP then log:close(); manager.machine:exit() end
end)
