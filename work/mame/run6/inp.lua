local f=0
local C=manager.machine.ioport.ports[":Controls"].fields
local P=manager.machine.ioport.ports[":Power"].fields["Power On"]
local seq={{2300,"Option"},{2450,"Button A"},{2600,"Down"},{2660,"Button A"},{2850,"Button A"},
 {3300,"Button A"},{3500,"Right"},{3600,"Button A"},{3900,"Button A"},{4100,"Down"},{4200,"Button A"},{4500,"Button A"},{4800,"Button A"},{5100,"Button A"},{5400,"Button A"}}
emu.register_frame_done(function()
  f=f+1
  P:set_value(f<20 and 1 or 0)
  for _,n in ipairs({"Option","Button A","Button B","Down","Right","Up","Left"}) do C[n]:set_value(0) end
  if f>200 and f<1900 and f%90<6 then C["Button A"]:set_value(1) end
  for _,s in ipairs(seq) do if f>=s[1] and f<s[1]+6 then C[s[2]]:set_value(1) end end
  if f%90==0 and f>2900 then manager.machine.video:snapshot() end
  if f>5800 then manager.machine:exit() end
end)
