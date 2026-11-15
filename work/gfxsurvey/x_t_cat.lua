seq={{2300,"Button A"},{2600,"Button B"},{2950,"Right"},{3030,"Right"},{3110,"Right"},{3190,"Right"},{3270,"Right"},{3350,"Right"},{3430,"Right"},{3510,"Up"},{3590,"Button A"}}
dumps={4400}
stop=4500
poke={{2250,function(sp) for a=0x4500,0x4557 do sp:write_u8(a,0xff) end end}}

