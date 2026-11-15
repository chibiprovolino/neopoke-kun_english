-- Opens the prototype's hidden debug menu: once the save prompt task exists, its resume address
-- (task object +0) is redirected to 0x21783a, the routine the debug sub-screens use to return to the menu.
local ROUTE = {name="debugmenu", stop=3000, autodelay=30,
 seq={{2300,"Option"}},
 poke={{2370,function(sp) local o=sp:read_u32(0x482b); sp:write_u32(o,0x21783a) end}},
 snaps={2360,2400,2450,2550,2700,2900}}
loadfile(os.getenv("TOUR_LIB"))(ROUTE)
