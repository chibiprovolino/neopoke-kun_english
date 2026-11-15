local f=0
local A=manager.machine.ioport.ports[":Controls"].fields["Button A"]
emu.register_frame_done(function()
  f=f+1
  if f%90<6 then A:set_value(1) else A:set_value(0) end
  if f%600==0 then manager.machine.video:snapshot() end
  if f>7200 then manager.machine:exit() end
end)
