seq={{2300,"Button A"},{2600,"Button B"},{2950,"Up"},{3030,"Right"},{3100,"Right"},{3170,"Right"},{3240,"Right"},{3310,"Right"},{3380,"Right"},{3450,"Right"},{3520,"Right"},{3590,"Right"},{3660,"Right"},{3730,"Right"},{3800,"Right"},{3870,"Right"},{3940,"Right"},{4010,"Right"},{4080,"Right"},{4150,"Right"},{4220,"Right"},{4290,"Right"},{4360,"Right"},{4430,"Right"},{4500,"Right"},{4570,"Right"},{4640,"Right"},{4810,"Button A"},{5310,"Button A"},{5710,"Button A"},{6310,"Button A"},{6910,"Right"},{7210,"Button A"}}
dumps={6110,6210,6310,6410,6510,6610,6710,6810,6910,7010,7110,7210,7310,7410,7510,7610,7710,7810,7910,8010,8110,8210,8310,8410,8510,8610,8710,8810,8910,9010}
stop=9110
poke={{2250,function(sp) for a=0x4500,0x4557 do sp:write_u8(a,0xff) end end}}

