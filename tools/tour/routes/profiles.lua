-- Dating profile catalog (ids 110-347).
-- Minigame menu (room: A, then B) has a hidden 7th page "E" shown while RAM 0x4803 != 0. Selecting it opens the catalog.
-- Profile unlock flags are bits 1-69 of RAM 0x4558; all are set so every profile can be browsed. Down = next profile.
local seq, snaps = {{2300, "Button A"}, {2600, "Button B"}}, {}
local t = 2800
for i = 1, 7 do seq[#seq + 1] = {t, "Right"}; t = t + 80 end
snaps[#snaps + 1] = t - 10
seq[#seq + 1] = {t, "Up"}; t = t + 80; snaps[#snaps + 1] = t - 10
seq[#seq + 1] = {t, "Button A"}
for _, d in ipairs({60, 150, 300, 500, 800}) do snaps[#snaps + 1] = t + d end
t = t + 900
seq[#seq + 1] = {t, "Button A"}; snaps[#snaps + 1] = t + 100; snaps[#snaps + 1] = t + 250; t = t + 400
for i = 1, 36 do seq[#seq + 1] = {t, "Down"}; snaps[#snaps + 1] = t + 120; t = t + 400; snaps[#snaps + 1] = t - 10 end
local ROUTE = {name = "profiles", stop = t + 50, auto = false, seq = seq, snaps = snaps,
 every = function(sp, f) if f > 2700 then sp:write_u8(0x4803, 1) end end,
 poke = {{2250, function(sp) for a = 0x4558, 0x4560 do sp:write_u8(a, 0xff) end end}}}
loadfile(os.getenv("TOUR_LIB"))(ROUTE)
