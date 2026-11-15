for tag,port in pairs(manager.machine.ioport.ports) do for name,f in pairs(port.fields) do print("PORT",tag,name) end end
manager.machine:exit()
