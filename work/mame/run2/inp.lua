local f=0
local C=manager.machine.ioport.ports[":Controls"].fields
local P=manager.machine.ioport.ports[":Power"].fields["Power On"]
emu.register_frame_done(function()
  f=f+1
  if f<20 then P:set_value(1) else P:set_value(0) end
  if f>200 and f%90<6 then C["Button A"]:set_value(1) else C["Button A"]:set_value(0) end
  if f%150==0 then manager.machine.video:snapshot() end
  if f>3000 then manager.machine:exit() end
end)
