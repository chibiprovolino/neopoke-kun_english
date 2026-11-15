seq={}
for f=2300,4300,250 do seq[#seq+1]={f,"Button B"} end
seq[#seq+1]={4500,"Right"} seq[#seq+1]={4650,"Right"} seq[#seq+1]={4800,"Right"}
dumps={2400,2900,3400,3900,4400,4600,4750,4900}
stop=5000
poke={{2500,function(sp) local t={} for a=0x4520,0x456C do t[#t+1]=string.format("%02x",sp:read_u8(a)) end
  local f=io.open(os.getenv("OUT").."/ram.txt","w") f:write(table.concat(t," ")) f:close() end}}
