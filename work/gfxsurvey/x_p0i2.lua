seq={{2300,"Button A"},{2600,"Button B"},{2900,"Up"},{2980,"Right"},{3060,"Right"},{3400,"Button A"}}
dumps={3500}
stop=3700
poke={{2250,function(sp) for a=0x4500,0x4557 do sp:write_u8(a,0xff) end end}}

