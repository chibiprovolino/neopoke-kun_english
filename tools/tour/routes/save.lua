-- Room -> Option menu -> save prompt (ids 106-109)
local ROUTE = {name="save", stop=4700,
 seq={{2300,"Option"},{2450,"Button A"},{2800,"Right"},{2900,"Button A"},{3100,"Up"},{3200,"Button A"},{3400,"Left"},{3500,"Button A"},{3700,"Down"},{3800,"Button A"},{4000,"Option"},{4200,"Button B"},{4400,"Button A"}},
 snaps={2200,2500,3000,3300,3600,3900,4100,4300,4600}}
loadfile(os.getenv("TOUR_LIB"))(ROUTE)
