local f=0
local C=manager.machine.ioport.ports[":Controls"].fields
local P=manager.machine.ioport.ports[":Power"].fields["Power On"]
local seq={{600,"Option"},{750,"Button A"},{900,"Down"},{960,"Button A"},{1150,"Button A"},{1350,"Button B"},{1500,"Right"},{1560,"Button A"},{1800,"Button A"},{2100,"Button A"}}
emu.register_frame_done(function()
  f=f+1
  P:set_value(f<20 and 1 or 0)
  for _,n in ipairs({"Option","Button A","Button B","Down","Right","Up","Left"}) do C[n]:set_value(0) end
  for _,s in ipairs(seq) do if f>=s[1] and f<s[1]+6 then C[s[2]]:set_value(1) end end
  if f%60==0 and f>500 then manager.machine.video:snapshot() end
  if f>2400 then manager.machine:exit() end
end)
