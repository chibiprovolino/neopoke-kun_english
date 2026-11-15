seq={}
for _,f in ipairs({2300,3000,3700,4400,5100,5800,6500}) do seq[#seq+1]={f,"Button A"} seq[#seq+1]={f+300,"Button B"} end
dumps={}
for f=2700,7000,100 do dumps[#dumps+1]=f end
stop=7050
