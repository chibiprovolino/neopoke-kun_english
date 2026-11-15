seq={{2300,"Button A"},{2600,"Button B"}}
local t=2800
for i=1,7 do seq[#seq+1]={t,"Right"}; t=t+80 end
seq[#seq+1]={t,"Up"}; local tE=t+60; t=t+80
seq[#seq+1]={t,"Button A"}; t=t+900
local tC=t-60
seq[#seq+1]={t,"Button A"}; t=t+400
dumps={3276,3279,3282,3285,3288,3291,3294,3297,3300,3303,3306,3309,3312,3315,3318,3321,3324,3327,3330,3333,3336,3339,3342,3345,3348,3351,3354}
stop=3357
every=function(sp,f) if f>2700 then sp:write_u8(0x4803,1) end end
poke={{2250,function(sp) for a=0x4558,0x4560 do sp:write_u8(a,0xff) end end}}
