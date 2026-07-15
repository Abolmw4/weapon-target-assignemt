from math import sin, cos, atan2, radians, degrees, sqrt
from typing import Tuple, Dict

import numpy as np

############################################################
# WGS84
############################################################

WGS84_A = 6378137.0
WGS84_B = 6356752.314245

WGS84_E2 = 1 - (WGS84_B ** 2) / (WGS84_A ** 2)

############################################################
# Geodetic -> ECEF
############################################################


def geodetic_to_ecef(position: Tuple[float, float, float]) -> np.ndarray:

    lat_deg, lon_deg, h = position

    lat = radians(lat_deg)
    lon = radians(lon_deg)

    sin_lat = sin(lat)
    cos_lat = cos(lat)

    sin_lon = sin(lon)
    cos_lon = cos(lon)

    N = WGS84_A / sqrt(1 - WGS84_E2 * sin_lat ** 2)

    x = (N + h) * cos_lat * cos_lon

    y = (N + h) * cos_lat * sin_lon

    z = (N * (1 - WGS84_E2) + h) * sin_lat

    return np.array([x, y, z], dtype=float)


############################################################
# ECEF -> Geodetic
############################################################

def ecef_to_geodetic(ecef) -> np.ndarray:

    x, y, z = ecef

    lon = atan2(y, x)

    p = sqrt(x * x + y * y)

    lat = atan2(z, p * (1 - WGS84_E2))

    for _ in range(5):

        N = WGS84_A / sqrt(1 - WGS84_E2 * sin(lat) ** 2)

        h = p / cos(lat) - N

        lat = atan2(z, p * (1 - WGS84_E2 * (N / (N + h))))

    return (degrees(lat), degrees(lon), h)


############################################################
# Local ENU basis
############################################################

def enu_basis(lat_deg, lon_deg):
    lat = radians(lat_deg)
    lon = radians(lon_deg)

    east = np.array([-sin(lon), cos(lon), 0])

    north = np.array([-sin(lat) * cos(lon), -sin(lat) * sin(lon), cos(lat)])

    up = np.array([cos(lat) * cos(lon), cos(lat) * sin(lon), sin(lat)])

    return east, north, up


############################################################
# Velocity in ECEF
############################################################

def target_velocity_ecef(lat: float, lon: float, speed: float, heading: float, vertical_speed=0.0):

    east, north, up = enu_basis(lat, lon)

    heading = radians(heading)

    horizontal = (east * sin(heading) + north * cos(heading))

    velocity = horizontal * speed + up * vertical_speed

    return velocity


############################################################
# Intercept time

############################################################

def solve_intercept_time(R, V, missile_speed):

    a = np.dot(V, V) - missile_speed ** 2

    b = 2 * np.dot(R, V)

    c = np.dot(R, R)

    delta = b * b - 4 * a * c

    if delta < 0:
        return None

    t1 = (-b + sqrt(delta)) / (2 * a)

    t2 = (-b - sqrt(delta)) / (2 * a)

    valid = [t for t in [t1, t2] if t > 0]

    if len(valid) == 0:
        return None

    return min(valid)


############################################################
# Azimuth
############################################################

def calculate_azimuth(weapon_ecef, kill_ecef, weapon_lat, weapon_lon):

    east, north, up = enu_basis(weapon_lat, weapon_lon)

    vec = kill_ecef - weapon_ecef

    e = np.dot(vec, east)

    n = np.dot(vec, north)

    az = degrees(atan2(e, n))

    if az < 0:
        az += 360

    return az


############################################################
# Elevation
############################################################

def calculate_elevation(weapon_ecef, kill_ecef, weapon_lat, weapon_lon):

    east, north, up = enu_basis(weapon_lat, weapon_lon)

    vec = kill_ecef - weapon_ecef

    e = np.dot(vec, east)

    n = np.dot(vec, north)

    u = np.dot(vec, up)

    horizontal = sqrt(e * e + n * n)

    return degrees(atan2(u, horizontal))


############################################################
# Fire Control Solution
############################################################

def fire_control_solution(weapon_position, target_position, target_speed, target_heading, missile_speed, vertical_speed=0.0):

    ########################################################
    # Convert to ECEF
    ########################################################

    weapon = geodetic_to_ecef(weapon_position)

    target = geodetic_to_ecef(target_position)

    ########################################################
    # Target velocity
    ########################################################

    velocity = target_velocity_ecef(target_position[0], target_position[1], target_speed, target_heading, vertical_speed)

    ########################################################
    # Relative vector
    ########################################################

    R = target - weapon

    ########################################################
    # Solve intercept
    ########################################################

    kill_time = solve_intercept_time(R, velocity, missile_speed)

    if kill_time is None:

        return {"status": False, "reason": "No intercept solution."}

    ########################################################
    # Kill point
    ########################################################

    kill_point = target + velocity * kill_time

    ########################################################
    # Launch point
    ########################################################

    launch_time = 0.0

    launch_point = target.copy()

    ########################################################
    # Missile distance
    ########################################################

    missile_distance = np.linalg.norm(kill_point - weapon)

    ########################################################
    # Fire angles
    ########################################################

    azimuth = calculate_azimuth(weapon, kill_point, weapon_position[0], weapon_position[1])

    elevation = calculate_elevation(weapon, kill_point, weapon_position[0], weapon_position[1])

    ########################################################
    # Convert back
    ########################################################

    kill_geo = ecef_to_geodetic(kill_point)

    launch_geo = ecef_to_geodetic(launch_point)

    return {
        "status": True,
        "launch_time": launch_time,
        "launch_point": launch_geo,
        "kill_time": kill_time,
        "kill_point": kill_geo,
        "missile_distance": missile_distance,
        "azimuth": azimuth,
        "elevation": elevation
    }

if __name__ == "__main__":
    print(fire_control_solution())
