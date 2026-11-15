seq={{2300,"Button A"},{2600,"Button B"}}
local t=2800
for i=1,7 do seq[#seq+1]={t,"Right"}; t=t+80 end
seq[#seq+1]={t,"Up"}; t=t+80
seq[#seq+1]={t,"Button A"}; t=t+900
seq[#seq+1]={t,"Button A"}; t=t+400
dumps={t,t+300}
stop=t+301
every=function(sp,f) if f>2700 then sp:write_u8(0x4803,1) end end
poke={{2250,function(sp) for a=0x4558,0x4560 do sp:write_u8(a,0xff) end end}}
