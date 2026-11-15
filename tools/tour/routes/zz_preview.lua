-- Every script string drawn inside the save-prompt box, one per prompt (a rendering preview, not the real screen).
-- The pointer read at 0x2CC280 is substituted with each string in turn; Option opens the prompt, Right+A picks NO to close it.
local P = 150
local T0 = 2300
local N = tonumber(os.getenv("TOUR_PREVIEW_N") or "667")
local FIRST = tonumber(os.getenv("TOUR_PREVIEW_FIRST") or "0")
local LIST = nil   -- TOUR_PREVIEW_IDS="247,248" shows just those (used by the runner to retry misses)
if os.getenv("TOUR_PREVIEW_IDS") then
  LIST = {}
  for x in os.getenv("TOUR_PREVIEW_IDS"):gmatch("%d+") do LIST[#LIST + 1] = tonumber(x) end
  N = #LIST
end
local seq, snaps = {}, {}
for i = 0, N - 1 do
  local t = T0 + i * P
  seq[#seq + 1] = {t, "Option"}
  seq[#seq + 1] = {t + 90, "Right"}
  seq[#seq + 1] = {t + 110, "Button A"}
  snaps[#snaps + 1] = t + 80
end
local function idx(f) local i = (f - T0) // P; if f >= T0 and i < N then return LIST and LIST[i + 1] or FIRST + i end end
local ROUTE = {name = "preview", stop = T0 + N * P + 30, auto = false, seq = seq, snaps = snaps,
  ptr = function(f) local i = idx(f); return i and ID_START[i] end,
  label = function(f) return "show" .. idx(f) end}
loadfile(os.getenv("TOUR_LIB"))(ROUTE)
