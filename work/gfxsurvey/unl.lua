seq={{2300,"Button A"},{2600,"Button B"}}
dumps={2900}
stop=2901
poke={{2250,function(sp) for a=0x4561,0x45ff do sp:write_u8(a,0xff) end end}}
