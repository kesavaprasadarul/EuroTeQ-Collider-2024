import osrm
import shapely.wkt
import geojson
from requests import get, post
from pandas import json_normalize
from geopy import distance
from shapely.wkt import loads
import math
import json
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

osrm.RequestConfig
distance.GeodesicDistance.ELLIPSOID = 'WGS-84'
d = distance.distance

def get_elevation(lat = None, long = None):
    '''
        script for returning elevation in m from lat, long
    '''
    if lat is None or long is None: return None
    
    query = ('http://localhost:9967/api/v1/lookup'
             f'?locations={str(lat)},{str(long)}')
    
    # Request with a timeout for slow responses
    r = get(query, timeout = 20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = json_normalize(r.json(), 'results')['elevation'].values[0]
    else: 
        elevation = None
    return elevation

def get_bulk_elevation(payload):
    query = 'http://localhost:9967/api/v1/lookup'
    r = post(query, json=payload, timeout = 20)
    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = r.json()
    else: 
        msg = r.content
        elevation = None
    return elevation

class CO2Engine():
    class CO2Profile():
        def __init__(self): # Initial values based on Volvo FMX84
            self.idle_fuel_usage_l = 3.02 #F MX Idle
            self.mass_vehicle = 32000 # in kilograms
            self.mass_load = 10000 # in kilograms
            self.accel_gravity = 9.81 # m/s^2
            self.accel_vehicle = 1 # m/s^2
            self.wheel_radius = 1
            self.radius_tyre = 0.515 # 515mm Tyre radius: FMX84 
            self.torque_engine_max = 2600 # Nm, ATO2612 gearbox output, D11 380 hp (279 kW)
            self.load_nominal = 0.5
            self.milage_per_liter = 5.4746 #kmpl, community average with 11.8km per 100km, assumed at 60% load (load_nominal)
            self.mileage_modifer = 5 #the vehicle can go plus or minus modifer amount
            self.displacement_d13 = 12.8 # dm^3 or litre, D13 variant
            self.axle_ratio_highest = 4.11 # maximum torque conversion at rear for power delivery, RSS1370A; compatible with ATO2612
            self.emission_co2 = 3.17 # g per g of diesel
            self.diesel_l_to_g = 850.8 #g per l
            self.num_wheels = 6
            self.tire_pressure = 240 #kPa 
            self.rolling_pressure_ratio = 0.01 #https://x-engineer.org/rolling-resistance/
            pass
    
    def __init__(self, co2Profile: CO2Profile) -> None:
        self.co2profile = co2Profile
        self.distanceAccumulated_m = 0
        self.co2Accumulated_g = 0
        self.fuelAccumulated_l = 0
        pass

    def Reset(self):
        self.distanceAccumulated_m = 0
        self.co2Accumulated_g = 0
        self.fuelAccumulated_l = 0
        pass

    def GetFuelEmissionsCharacteristics(self, distance_m, theta_deg):
        mass_total = self.co2profile.mass_vehicle + self.co2profile.mass_load
        force_engine = mass_total * self.co2profile.accel_vehicle
        force_weight = mass_total * self.co2profile.accel_gravity
        force_angular = (mass_total * self.co2profile.accel_gravity * math.sin(math.radians(theta_deg))) + (self.co2profile.rolling_pressure_ratio *mass_total * self.co2profile.accel_gravity * math.cos(math.radians(theta_deg)))
        force_engine_max = (self.co2profile.torque_engine_max * self.co2profile.axle_ratio_highest) / self.co2profile.radius_tyre
        load = force_angular / force_engine_max
        load_offset = load - self.co2profile.load_nominal
        milage_compensated = max(self.co2profile.milage_per_liter - self.co2profile.mileage_modifer, (self.co2profile.milage_per_liter - ((load_offset)* self.co2profile.mileage_modifer)))
        fuel_consumed = ((distance_m * 0.001) / milage_compensated)
        co2_consumption = self.co2profile.emission_co2 * (fuel_consumed * self.co2profile.diesel_l_to_g)
        fuel_consumed_raw = ((distance_m * 0.001) / self.co2profile.milage_per_liter)
        co2_consumption_raw = self.co2profile.emission_co2 * (fuel_consumed_raw * self.co2profile.diesel_l_to_g)
        return {"co2_consumption_g": max(0,co2_consumption), "co2_consumption_raw": co2_consumption_raw, "fuel_consumed_l": max(0,fuel_consumed), "fuel_consumed_raw": fuel_consumed_raw, "distance": distance_m, "theta": theta_deg , "load_off": load_offset}
    
    def AccumulateFuelConsumption(self, distance_m, theta_deg, duration):
        self.distanceAccumulated_m += distance_m
        co2Characteristics = self.GetFuelEmissionsCharacteristics(distance_m=distance_m, theta_deg=theta_deg)
        self.fuelAccumulated_l += co2Characteristics['fuel_consumed_l']
        self.co2Accumulated_g = self.co2profile.emission_co2 * ((self.fuelAccumulated_l + (self.co2profile.idle_fuel_usage_l*duration/3600)) * self.co2profile.diesel_l_to_g)
        print(co2Characteristics)
        return co2Characteristics


def getDistanceInfo(point1, point2):
    engine = CO2Engine(CO2Engine.CO2Profile())
    route = osrm.simple_route(point1, point2,
                        output='route', overview="full", geometry='wkt', alternatives=True, steps=True)
    unwrapped_pathDBs = []
    for routeAlt in route:
        engine.Reset()
        g1 = shapely.wkt.loads(routeAlt['geometry'])
        g2 = geojson.Feature(geometry=g1, properties={})
        locations_payload = []
        path_db={}

        distance = -1
        previousGeometry = ()
        for val in g2.geometry['coordinates']:
            val_payload = {"latitude": val[1], "longitude": val[0]}
            if not val[1] in path_db:
                path_db[val[1]] = {}
            if not val[0] in path_db[val[1]]:
                path_db[val[1]][val[0]] = {}
            if distance == -1:
                path_db[val[1]][val[0]]['refPoint'] = None
                path_db[val[1]][val[0]]['distance'] = 0
                distance = 0
                previousGeometry = (val[1],val[0])
            else:
                delta_distance = d(previousGeometry, (val[1],val[0])).meters
                path_db[val[1]][val[0]]['refPoint'] = [ previousGeometry[0], previousGeometry[1]]
                path_db[val[1]][val[0]]['distance'] = delta_distance
                distance += delta_distance
                previousGeometry = (val[1],val[0])
            locations_payload.append(val_payload)
        
        chunks = [locations_payload[x:x+2000] for x in range(0, len(locations_payload), 2000)]
        elevation_results=[]
        for chunk_payload in chunks:
            elevation_payload = {"locations": chunk_payload}
            # print(elevation_payload)
            dataPayload = json.dumps(elevation_payload)
            # print(dataPayload)
            elevation_results += get_bulk_elevation(elevation_payload)['results']
        for val in elevation_results:
            path_db[val['latitude']][val['longitude']]['elevation'] = val['elevation']
        unwrapped_pathdb = {}
        for lat in path_db:
            for long in path_db[lat]:
                unwrapped_pathdb[str((lat,long))] = path_db[lat][long]
        cumulative_altitude_change = -1
        previousElevation = 0

        for item in unwrapped_pathdb:
            if cumulative_altitude_change == -1:
                cumulative_altitude_change = unwrapped_pathdb[item]['elevation']
                previousElevation = unwrapped_pathdb[item]['elevation']
                unwrapped_pathdb[item]['angleChange'] = 0
                co2char = engine.AccumulateFuelConsumption(unwrapped_pathdb[item]['distance'], -unwrapped_pathdb[item]['angleChange'], routeAlt['duration'])
                unwrapped_pathdb[item]['co2Delta_g'] = co2char['co2_consumption_g']
                unwrapped_pathdb[item]['fuelUsageDelta_l'] = co2char['fuel_consumed_l']
                
            else:
                delta_altitude = previousElevation - unwrapped_pathdb[item]['elevation']
                cumulative_altitude_change += delta_altitude
                if unwrapped_pathdb[item]['distance'] == 0:
                    unwrapped_pathdb[item]['angleChange'] = 0
                else:
                    unwrapped_pathdb[item]['angleChange'] = math.degrees(math.atan(delta_altitude / unwrapped_pathdb[item]['distance']))
                previousElevation = unwrapped_pathdb[item]['elevation']
                co2char = engine.AccumulateFuelConsumption(unwrapped_pathdb[item]['distance'], -unwrapped_pathdb[item]['angleChange'], routeAlt['duration'])
                unwrapped_pathdb[item]['co2Delta_g'] = co2char['co2_consumption_g']
                unwrapped_pathdb[item]['fuelUsageDelta_l'] = co2char['fuel_consumed_l']
        
        routePayload = {
            "geometryJSON": g2,
            "cumulative_polygon_distance": distance,
            "cumulative_altitude_change": cumulative_altitude_change,
            "processed_paths": unwrapped_pathdb,
            "cumulative_co2_kg": engine.co2Accumulated_g / 1000,
            "cumulative_fuel_l": engine.fuelAccumulated_l
        }
        unwrapped_pathDBs.append(routePayload)
    
    httpPayload = {
        # "osrm_output": route,
        "number_routes": len(route),
        "processed_paths": unwrapped_pathDBs
    }
    return httpPayload


@app.route('/route', methods = ['GET', 'POST', 'DELETE'])
@cross_origin()
def user():
    if request.method == 'POST':
        """modify/update the information for <user_id>"""
        # you can use <user_id>, which is a str but could
        # changed to be int or whatever you want, along
        # with your lxml knowledge to make the required
        # changes
        data = request.json # a multidict containing POST data
        print(data)
        point1 = [float(x) for x in str(data['point1']).strip().strip('[').strip(']').replace("'", '').replace('"', '').split(',')]
        point2 = [float(x) for x in str(data['point2']).strip().strip('[').strip(']').replace("'", '').replace('"', '').split(',')]
        res = getDistanceInfo(point1, point2)
        return res

