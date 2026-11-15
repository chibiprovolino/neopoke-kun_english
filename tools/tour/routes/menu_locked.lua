local ROUTE = {name="menu_locked", stop=5040, autodelay=30,
 seq={{2300,"Button A"},{2600,"Button B"},{2800,"Right"},{2880,"Right"},{2960,"Right"},{3040,"Right"},{3120,"Right"},{3200,"Right"},{3280,"Right"},{3360,"Right"},{3440,"Right"},{3520,"Right"},{3600,"Right"},{3680,"Right"},{3760,"Down"},{3840,"Down"},{3920,"Down"},{4000,"Down"},{4080,"Down"},{4160,"Down"},{4240,"Button A"}},
 snaps={2840,2920,3000,3080,3160,3240,3320,3400,3480,3560,3640,3720,3800,3880,3960,4040,4120,4200,4300,4440,4640,4940}}
loadfile(os.getenv("TOUR_LIB"))(ROUTE)
