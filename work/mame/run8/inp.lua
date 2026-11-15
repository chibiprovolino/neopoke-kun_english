local f=0
local C=manager.machine.ioport.ports[":Controls"].fields
local P=manager.machine.ioport.ports[":Power"].fields["Power On"]
local seq={{2300,"Option"},{2450,"Button A"},{2800,"Right"},{2900,"Button A"},{3100,"Up"},{3200,"Button A"},{3400,"Left"},{3500,"Button A"},{3700,"Down"},{3800,"Button A"},{4000,"Option"},{4200,"Button B"},{4400,"Button A"}}
emu.register_frame_done(function()
  f=f+1
  P:set_value(f<20 and 1 or 0)
  for _,n in ipairs({"Option","Button A","Button B","Down","Right","Up","Left"}) do C[n]:set_value(0) end
  if f>200 and f<1900 and f%90<6 then C["Button A"]:set_value(1) end
  for _,s in ipairs(seq) do if f>=s[1] and f<s[1]+8 then C[s[2]]:set_value(1) end end
  if f==4250 then manager.machine.video:snapshot() end
  if f>4300 then manager.machine:exit() end
end)
