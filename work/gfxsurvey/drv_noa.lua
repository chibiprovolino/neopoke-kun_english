-- generic driver: CFG env = lua file defining seq={{frame,"Button"},...}, dumps={frames}, stop=N, auto=true/false
dofile(os.getenv("CFG"))
local f=0
local C=manager.machine.ioport.ports[":Controls"].fields
local P=manager.machine.ioport.ports[":Power"].fields["Power On"]
local sp=manager.machine.devices[":maincpu"].spaces["program"]
local out=os.getenv("OUT")
local dset={} for _,x in ipairs(dumps) do dset[x]=true end
emu.register_frame_done(function()
  f=f+1
  P:set_value(f<20 and 1 or 0)
  for _,n in ipairs({"Option","Button A","Button B","Down","Right","Up","Left"}) do C[n]:set_value(0) end
  -- no auto A
  for _,s in ipairs(seq) do if f>=s[1] and f<s[1]+(s[3] or 8) then C[s[2]]:set_value(1) end end
  if every then every(sp,f) end
  if poke then for _,p in ipairs(poke) do if p[1]==f then p[2](sp) end end end
  if dset[f] then
    manager.machine.video:snapshot()
    local fh=io.open(out.."/v"..f..".bin","wb")
    local t={} for a=0x8000,0xBFFF do t[#t+1]=string.char(sp:read_u8(a)) end
    fh:write(table.concat(t)) fh:close()
  end
  if f>=stop then manager.machine:exit() end
end)
