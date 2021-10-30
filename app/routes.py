import sqlite3, json
from math import sin
from app.db import DATABASE_NAME as db
from bottle import route, request, abort


VALID_KEYS=[
    'chassis_number',
    'available_fuel',
    'vehicle_mass',
    'load_mass',
    'street_slope',
    'distance',
    'time',
    'max_rpm',
    'max_horsepower',
    'fuel_consumption',
]

@route('/', method='POST')
def handle_post():
    # parse request
    try:
        values = json.load(request.body)
    except json.decoder.JSONDecodeError as err:
        abort(400, text="Error decoding JSON dictionary!\nError: %s" % err)

    # validate type
    if not isinstance(values, dict):
        abort(400, text="Not a valid JSON dictionary!")

    # validate keys
    missing_keys = VALID_KEYS - values.keys()
    if missing_keys:
        abort(400, text="Missing values!\nKeys: {keys}".format(keys=missing_keys))

    # create a log entry for the request
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("""INSERT INTO log (
        chassis_number,
        available_fuel,
        vehicle_mass,
        load_mass,
        street_slope,
        distance,
        time,
        max_rpm,
        max_horsepower,
        fuel_consumption
    ) VALUES (
        '{chassis_number}',
        {available_fuel},
        {vehicle_mass},
        {load_mass},
        {street_slope},
        {distance},
        {time},
        {max_rpm},
        {max_horsepower},
        {fuel_consumption}
    )
""".format(
        chassis_number=values.get('chassis_number', 'NULL'),
        available_fuel=values.get('available_fuel', 'NULL'),
        vehicle_mass=values.get('vehicle_mass', 'NULL'),
        load_mass=values.get('load_mass', 'NULL'),
        street_slope=values.get('street_slope', 'NULL'),
        distance=values.get('distance', 'NULL'),
        time=values.get('time', 'NULL'),
        max_rpm=values.get('max_rpm', 'NULL'),
        max_horsepower=values.get('max_horsepower', 'NULL'),
        fuel_consumption=values.get('fuel_consumption', 'NULL'),
    ))
    con.commit()
    con.close()

    # calculation
    g = 9.8
    nc = values.get('available_fuel')
    mv = values.get('vehicle_mass')
    mc = values.get('load_mass')
    an = values.get('street_slope')
    d = values.get('distance')
    t = values.get('time')
    rm = values.get('max_rpm')
    pm = values.get('max_horsepower')
    ccr = values.get('fuel_consumption')

    try:
        pnv = mv * g
        pc = mc * g
        ptv = pnv + pc
        v = d / t
        a = v / d
        fa = ptv * sin(an)
        fn = a * sin(an) * (mv + mc)
        fri = fa + fn
        pr = 0
        rr = 0
        cr = ccr / 1000 * rr
    except Exception as err:
        abort(400, "Wrong values!\nError: {error}".format(error=err))

    if pr > pm:
        abort(400, "Maximum power is not enough!\nMax: {pm} Need: {pr}".format(pm=pm, pr=pr))

    if ccr > nc:
        abort(400, "Fuel is not enough!\nHave: {nc} Need: {ccr}".format(nc=nc, ccr=ccr))

    # prepare response
    response = {
        'chassis_number': values.get('chassis_number', ''),
        'net_weight': pnv,
        'load_weight': pc,
        'total_weight': ptv,
        'max_speed': v,
        'max_acceleration': a,
        'pull_force': fa,
        'net_force': fn,
        'required_force': fri,
        'required_rpm': rr,
        'required_horsepower': pr,
        'required_fuel': cr,
    }

    return response
