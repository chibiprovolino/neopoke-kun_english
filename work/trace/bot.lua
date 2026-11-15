-- Automated player for the fast-unlock prototype. It plays "blind": it never reads mood or the seen flags to decide what to do.
-- Env: BOT_OUT, BOT_STOP (frames), BOT_SEED, BOT_EXIT (leave the menu after this many room actions), BOT_GAME (1 = also start a minigame now and then)
local OUT = os.getenv("BOT_OUT")
local STOP = tonumber(os.getenv("BOT_STOP") or "400000")
local EXIT_EVERY = tonumber(os.getenv("BOT_EXIT") or "6")
local PLAY = os.getenv("BOT_GAME") == "1"
math.randomseed(tonumber(os.getenv("BOT_SEED") or "1"))
local C = manager.machine.ioport.ports[":Controls"].fields
local P = manager.machine.ioport.ports[":Power"].fields["Power On"]
local cpu = manager.machine.devices[":maincpu"]
local sp = cpu.spaces["program"]
local log = io.open(OUT .. "/bot.txt", "w")
local names = {"Option", "Button A", "Button B", "Down", "Right", "Up", "Left"}
local dirs = {"Up", "Down", "Left", "Right"}
local f = 0
local held = {}                       -- button -> last frame to hold
local function press(b, n) held[b] = f + (n or 8) end
local function popcount(a, b)
  local n = 0
  for x = a, b do local v = sp:read_u8(x); while v ~= 0 do n = n + (v & 1); v = v >> 1 end end
  return n
end
local function unlocked()
  local n = 0
  for x = 0x4526, 0x4543 do if sp:read_u8(x) & 0xf0 == 0xf0 then n = n + 1 end end
  return n
end
-- watch the saved bytes the prototype reuses: who writes them?
local writers = {}
WT = sp:install_write_tap(0x4544, 0x4557, "bw", function(o, d, m)
  local pc = cpu.state["PC"].value
  local k = string.format("%06x", pc & 0xffff00)
  if not writers[k] then writers[k] = true; log:write(string.format("%d writer of %04x near pc %06x\n", f, o, pc)); log:flush() end
  return d
end)
local menu_open = false
MT = sp:install_write_tap(0x4526, 0x4543, "bm", function(o, d, m) menu_open = true; return d end)
WATCH = nil
lastw = ""
if os.getenv("BOT_WATCH") then WATCH = {} for a in os.getenv("BOT_WATCH"):gmatch("%x+") do WATCH[#WATCH + 1] = tonumber(a, 16) end end
local left_menu = false
XT = sp:install_write_tap(0x44cf, 0x44cf, "bx", function(o, d, m) if d == 0 then left_menu = true end return d end)
local hang, lastact = 0, ""
-- MAME 0.253: after a voice sample the sound CPU stops getting its timer interrupt, so its heartbeat byte (0x70c3) freezes and
-- the next sound command waits on it forever (the unpatched game does this too). Every read of the heartbeat gets a new value here.
kicks = 0
local hbreal, hbsame = -1, 0
HB = sp:install_read_tap(0x70c3, 0x70c3, "hb", function(o, d, m) if d == hbreal then hbsame = hbsame + 1 else hbreal = d; hbsame = 0 end if hbsame > 3000 then kicks = kicks + 1; return (d + kicks) & 0xff end return d end)
local state, t0, actions, cal0 = "room", 0, 0, 0
local works, lastb6, exits, rings, lastgames, lastA, stall = 0, 0, 0, 0, -1, -1, 0
local wig = nil
local function stats(tag)
  local room, vis, wg, mg = popcount(0x4544, 0x454e), popcount(0x4558, 0x4563), popcount(0x454f, 0x4551), popcount(0x4552, 0x4553)
  log:write(string.format("%d %s min=%.1f A=%d B=%d mood=%d cal=%d games=%d scenes=%d (room %d, visitors %d, wiggle %d, megaphone %d) works=%d exits=%d rings=%d staff=%d door=%d state=%d\n",
    f, tag, f / 3600, sp:read_u16(0x4520), sp:read_u8(0x4523), sp:read_i8(0x4522), sp:read_u8(0x4554), unlocked(), room + vis + wg + mg, room, vis, wg, mg,
    works, exits, rings, sp:read_u8(0x456c), sp:read_u8(0x44fd), sp:read_u8(0x44be), kicks))
  log:flush()
end
emu.register_frame_done(function()
  f = f + 1
  P:set_value(f < 20 and 1 or 0)
  for _, n in ipairs(names) do C[n]:set_value(0) end
  if f > 200 and f < 2100 and f % 90 < 6 then C["Button A"]:set_value(1) end
  if f < 2300 then return end
  for b, till in pairs(held) do if f <= till then C[b]:set_value(1) end end
  if wig and f < wig then C[(f // 4) % 2 == 0 and "Left" or "Right"]:set_value(1) end
  local b6 = sp:read_u8(0x44b6)
  if b6 == 1 and lastb6 ~= 1 then works = works + 1 end
  lastb6 = b6
  if state == "room" then
    if f - t0 >= 260 then
      t0 = f; actions = actions + 1
      if actions > EXIT_EVERY then
        state = "opening"; menu_open = false; press("Button B")
      else
        local r = math.random(100)
        lastact = f .. ":" .. r
        if r <= 60 then press("Button A"); rings = rings + 1
        elseif r <= 80 then press(dirs[math.random(4)], 80)
        elseif r <= 90 then wig = f + 120
        end
      end
    end
  elseif state == "opening" then
    if menu_open or (unlocked() >= 30 and f - t0 >= 330) then state = "menu"; t0 = f; left_menu = false   -- with all 30 unlocked no stage byte is rewritten: assume the menu opened
    elseif f - t0 >= 600 then t0 = f; press("Button B") end          -- the press was ignored (he was busy): try again
  elseif state == "menu" then
    if left_menu then state = "room"; t0 = f + 500; actions = 0; exits = exits + 1   -- left the menu; give a work scene time to play
    elseif PLAY and f - t0 == 200 and exits % 5 == 4 then press("Button A"); state = "game"; t0 = f
    elseif f - t0 >= 200 and (f - t0) % 150 == 50 then press("Button B") end
  elseif state == "game" then                                         -- mash through a minigame, then go back to the menu loop
    if (f - t0) % 20 == 0 then press(({"Button A", "Left", "Right", "Up", "Down"})[math.random(5)], 10) end
    if f - t0 > 5400 then state = "menu"; t0 = f - 200 end
  end
  if os.getenv("BOT_SNAP") and f % tonumber(os.getenv("BOT_SNAP")) == 0 and f >= tonumber(os.getenv("BOT_SNAP0") or "0") then manager.machine.video:snapshot(); log:write(f .. " snap state=" .. state .. " t0=" .. t0 .. " actions=" .. actions .. "\n") end
  if WATCH then local t = {} for _, a in ipairs(WATCH) do t[#t + 1] = string.format("%04x=%02x", a, sp:read_u8(a)) end local w = table.concat(t, " ") if w ~= lastw then log:write(f .. " " .. w .. " [" .. state .. "]" .. string.char(10)); lastw = w end end
  if os.getenv("BOT_PC") and f >= tonumber(os.getenv("BOT_PC")) and f < tonumber(os.getenv("BOT_PC")) + 40 then log:write(f .. string.format(" pc=%06x xiz=%08x sp=%08x", cpu.state["PC"].value, cpu.state["XIZ"].value, cpu.state["XSSP"] and cpu.state["XSSP"].value or 0) .. string.char(10)) end
  local pc = cpu.state["PC"].value
  if pc >= 0x2a94e9 and pc <= 0x2a94f8 then hang = hang + 1 else hang = 0 end
  if hang == 120 then stats("SOUNDHANG"); log:write(string.format("%d hang: last action %s visitor=%d room event=%d record=%d poke-kun state=%d", f, lastact, sp:read_u8(0x44ff), sp:read_u8(0x44ca), sp:read_u8(0x44cb), sp:read_u8(0x44be)) .. string.char(10)); log:close(); manager.machine:exit(); return end
  local g = unlocked()
  if g ~= lastgames then stats("unlock"); lastgames = g end
  if f % 18000 == 0 then
    stats("tick")
    local A = sp:read_u16(0x4520)
    if A == lastA then stall = stall + 1 else stall = 0 end
    lastA = A
  end
  if f >= STOP or (g >= 30 and not os.getenv("BOT_FULL")) then stats("end"); local t = {} for a = 0x4544, 0x4563 do t[#t + 1] = string.format("%02x", sp:read_u8(a)) end log:write("bitmaps " .. table.concat(t) .. string.char(10)); log:close(); manager.machine:exit() end
end)
