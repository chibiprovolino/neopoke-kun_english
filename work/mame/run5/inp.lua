local f=0
local C=manager.machine.ioport.ports[":Controls"].fields
local P=manager.machine.ioport.ports[":Power"].fields["Power On"]
local seq={{2300,"Option"},{2450,"Button A"},{2600,"Down"},{2660,"Button A"},{2850,"Button A"},{3050,"Button B"},{3200,"Right"},{3260,"Button A"},{3500,"Button A"},{3800,"Button A"}}
emu.register_frame_done(function()
  f=f+1
  P:set_value(f<20 and 1 or 0)
  for _,n in ipairs({"Option","Button A","Button B","Down","Right","Up","Left"}) do C[n]:set_value(0) end
  if f>200 and f<1900 and f%90<6 then C["Button A"]:set_value(1) end
  for _,s in ipairs(seq) do if f>=s[1] and f<s[1]+6 then C[s[2]]:set_value(1) end end
  if f%60==0 and f>2000 then manager.machine.video:snapshot() end
  if f>4200 then manager.machine:exit() end
end)
