-- Burst screenshots (every 8 frames for ~400 frames) of selected dating profiles, to see portrait animation.
-- Same entry as profiles.lua. Navigation is closed-loop: press Down until the profile's name string
-- (id 110 + 7*(n-1)) has been read. TOUR_PROFILES="2,7,11,12" picks profile numbers (1 = Neo Poke-kun).
local want = {}
for x in (os.getenv("TOUR_PROFILES") or "2,7,11,12"):gmatch("%d+") do want[#want + 1] = tonumber(x) end
local seq = {{2300, "Button A"}, {2600, "Button B"}}
local t = 2800
for i = 1, 7 do seq[#seq + 1] = {t, "Right"}; t = t + 80 end
seq[#seq + 1] = {t, "Up"}; t = t + 80
seq[#seq + 1] = {t, "Button A"}; t = t + 900
seq[#seq + 1] = {t, "Button A"}; t = t + 300
local START = t
local cur, wi, lastpress, burst_from, seen_last = nil, 1, 0, nil, nil
local function every(sp, f)
  if f > 2700 then sp:write_u8(0x4803, 1) end
  if f < START or wi > #want then return end
  if LAST_ID and LAST_ID ~= seen_last then
    seen_last = LAST_ID
    if LAST_ID >= 110 and LAST_ID <= 347 and (LAST_ID - 110) % 7 == 0 then cur = (LAST_ID - 110) // 7 + 1 end
  end
  local target = want[wi]
  if burst_from then
    local k = f - burst_from
    if k > 400 then burst_from = nil; wi = wi + 1; return end
    if k % 8 == 0 then return nil, "p" .. target end
    return
  end
  if cur == target then burst_from = f; return end
  if f - lastpress > 250 then
    lastpress = f
    if cur and cur > target then return "Up" end
    return "Down"
  end
end
local ROUTE = {name = "profile_anim", stop = START + 30000, auto = false, seq = seq, snaps = {}, every = every,
 poke = {{2250, function(sp) for a = 0x4558, 0x4560 do sp:write_u8(a, 0xff) end end}}}
-- stop as soon as all bursts are done
local base = every
ROUTE.every = function(sp, f) local b, tg = base(sp, f); if wi > #want and f > START then ROUTE.stop = f end; return b, tg end
loadfile(os.getenv("TOUR_LIB"))(ROUTE)
