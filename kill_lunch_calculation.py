# from math import sin, cos, atan2, radians, degrees, sqrt
# from typing import Tuple, Dict

# import numpy as np

# ############################################################
# # WGS84
# ############################################################

# WGS84_A = 6378137.0
# WGS84_B = 6356752.314245

# WGS84_E2 = 1 - (WGS84_B ** 2) / (WGS84_A ** 2)

# ############################################################
# # Geodetic -> ECEF
# ############################################################


# def geodetic_to_ecef(position: Tuple[float, float, float]) -> np.ndarray:

#     lat_deg, lon_deg, h = position

#     lat = radians(lat_deg)
#     lon = radians(lon_deg)

#     sin_lat = sin(lat)
#     cos_lat = cos(lat)

#     sin_lon = sin(lon)
#     cos_lon = cos(lon)

#     N = WGS84_A / sqrt(1 - WGS84_E2 * sin_lat ** 2)

#     x = (N + h) * cos_lat * cos_lon

#     y = (N + h) * cos_lat * sin_lon

#     z = (N * (1 - WGS84_E2) + h) * sin_lat

#     return np.array([x, y, z], dtype=float)


# ############################################################
# # ECEF -> Geodetic
# ############################################################

# def ecef_to_geodetic(ecef) -> np.ndarray:

#     x, y, z = ecef

#     lon = atan2(y, x)

#     p = sqrt(x * x + y * y)

#     lat = atan2(z, p * (1 - WGS84_E2))

#     for _ in range(5):

#         N = WGS84_A / sqrt(1 - WGS84_E2 * sin(lat) ** 2)

#         h = p / cos(lat) - N

#         lat = atan2(z, p * (1 - WGS84_E2 * (N / (N + h))))

#     return (degrees(lat), degrees(lon), h)


# ############################################################
# # Local ENU basis
# ############################################################

# def enu_basis(lat_deg, lon_deg):
#     lat = radians(lat_deg)
#     lon = radians(lon_deg)

#     east = np.array([-sin(lon), cos(lon), 0])

#     north = np.array([-sin(lat) * cos(lon), -sin(lat) * sin(lon), cos(lat)])

#     up = np.array([cos(lat) * cos(lon), cos(lat) * sin(lon), sin(lat)])

#     return east, north, up


# ############################################################
# # Velocity in ECEF
# ############################################################

# def target_velocity_ecef(lat: float, lon: float, speed: float, heading: float, vertical_speed=0.0):

#     east, north, up = enu_basis(lat, lon)

#     heading = radians(heading)

#     horizontal = (east * sin(heading) + north * cos(heading))

#     velocity = horizontal * speed + up * vertical_speed

#     return velocity


# ############################################################
# # Intercept time

# ############################################################

# def solve_intercept_time(R, V, missile_speed):

#     a = np.dot(V, V) - missile_speed ** 2
#     b = 2 * np.dot(R, V)
#     c = np.dot(R, R)

#     EPS = 1e-8

#     if abs(a) < EPS:

#         if abs(b) < EPS:
#             return None

#         t = -c / b

#         if t > 0:
#             return t

#         return None

#     delta = b * b - 4 * a * c

#     if delta < 0:
#         return None

#     sqrt_delta = sqrt(delta)

#     t1 = (-b + sqrt_delta) / (2 * a)
#     t2 = (-b - sqrt_delta) / (2 * a)

#     valid = [t for t in (t1, t2) if t > 0]

#     if not valid:
#         return None

#     return min(valid)
# ############################################################
# # Azimuth
# ############################################################

# def calculate_azimuth(weapon_ecef, kill_ecef, weapon_lat, weapon_lon):

#     east, north, up = enu_basis(weapon_lat, weapon_lon)

#     vec = kill_ecef - weapon_ecef

#     e = np.dot(vec, east)

#     n = np.dot(vec, north)

#     az = degrees(atan2(e, n))

#     if az < 0:
#         az += 360

#     return az


# ############################################################
# # Elevation
# ############################################################

# def calculate_elevation(weapon_ecef, kill_ecef, weapon_lat, weapon_lon):

#     east, north, up = enu_basis(weapon_lat, weapon_lon)

#     vec = kill_ecef - weapon_ecef

#     e = np.dot(vec, east)

#     n = np.dot(vec, north)

#     u = np.dot(vec, up)

#     horizontal = sqrt(e * e + n * n)

#     return degrees(atan2(u, horizontal))


# ############################################################
# # Fire Control Solution
# ############################################################

# def fire_control_solution(weapon, target, vertical_speed=0.0):

#     weapon_ecef = geodetic_to_ecef(weapon["position"])
#     target_ecef = geodetic_to_ecef(target["position"])
    
#     velocity = target_velocity_ecef(
#         target["position"][0], target["position"][1],
#         target["speed"], target["heading"], vertical_speed
#     )

#     launch_delay = weapon.get("lunch_delay", 1) 
#     launch_time = launch_delay 

#     launch_point = target_ecef + velocity * launch_time

#     R = launch_point - weapon_ecef
#     flight_time = solve_intercept_time(R, velocity, weapon["missile_speed"])

#     if flight_time is None:
#         return {"status": False, "reason": "No intercept solution"}

#     kill_point = launch_point + velocity * flight_time
    
#     missile_distance = np.linalg.norm(kill_point - weapon_ecef)

#     azimuth = calculate_azimuth(weapon_ecef, kill_point, weapon["position"][0], weapon["position"][1]) # زاویه افقی
#     elevation = calculate_elevation(weapon_ecef, kill_point, weapon["position"][0], weapon["position"][1]) # زاویه عمودی

#     return {
#         "status": True,
#         "lunch_time": round(launch_time, 2),
#         "launch_point": ecef_to_geodetic(launch_point),
#         # این همان زمان طی مسیر هدف از LaunchPoint تا KillPoint است:
#         "kill_time": round(flight_time, 2), 
#         "kill_point": ecef_to_geodetic(kill_point),
#         "missile_distance": round(missile_distance, 2),
#         "azimuth": azimuth,
#         "elevation": elevation
#     }

# if __name__ == "__main__":
#     weapon = {
#         "id": 1,
#         "name": "SAM-1",
#         "type": "SAM",
#         "position": [35.6892, 51.3890, 1200], # deg, deg, meters
#         "min_range": 500,
#         "max_range": 6000,
#         "min_altitude": 50,
#         "max_altitude": 18000,
#         "altitudes": [1000, 2000, 3000, 4000, 5000, 6000], # meters
#         "ranges": [500, 1000, 1500, 2000, 2500, 5000], #meters
#         "ammo": 8,
#         "missile_speed": 416.66666667, # 1500 km/h
#         "lunch_delay": 0.5, # s
#         "status": "READY",
#         "engagement_channels": 4,
#         "used_channels": 1
#     }
    
#     target = {
#         "id": 1,
#         "type": "CRUISE_MISSILE",
#         "position":  [35.7020, 51.3890, 1500],
#         "altitude": 1500,
#         "speed": 277.77777778, # 1000 km/h
#         "heading": 45, # deg
#         "priority": 9,
#         "value": 10
#     }

#     result = fire_control_solution(weapon, target)

#     print(result)


from math import sin, cos, atan2, radians, degrees, sqrt
from typing import Tuple, Dict, Optional, Any
import numpy as np

############################################################
# WGS84 constants
############################################################

WGS84_A = 6378137.0
WGS84_B = 6356752.314245
WGS84_E2 = 1.0 - (WGS84_B ** 2) / (WGS84_A ** 2)

############################################################
# Geodetic <-> ECEF
############################################################

def geodetic_to_ecef(position: Tuple[float, float, float]) -> np.ndarray:
    """
    Convert (lat_deg, lon_deg, h_m) -> ECEF (x, y, z) meters
    """
    lat_deg, lon_deg, h = position
    lat = radians(lat_deg)
    lon = radians(lon_deg)

    sin_lat = sin(lat)
    cos_lat = cos(lat)
    sin_lon = sin(lon)
    cos_lon = cos(lon)

    N = WGS84_A / sqrt(1.0 - WGS84_E2 * sin_lat ** 2)

    x = (N + h) * cos_lat * cos_lon
    y = (N + h) * cos_lat * sin_lon
    z = (N * (1.0 - WGS84_E2) + h) * sin_lat

    return np.array([x, y, z], dtype=float)


def ecef_to_geodetic(ecef: np.ndarray) -> Tuple[float, float, float]:
    """
    Convert ECEF (x, y, z) -> (lat_deg, lon_deg, h_m)
    Simple iterative method (sufficient for this use case)
    """
    x, y, z = ecef
    lon = atan2(y, x)
    p = sqrt(x * x + y * y)

    # Initial guess
    lat = atan2(z, p * (1.0 - WGS84_E2))

    for _ in range(6):
        sin_lat = sin(lat)
        N = WGS84_A / sqrt(1.0 - WGS84_E2 * sin_lat ** 2)
        h = p / cos(lat) - N
        lat = atan2(z, p * (1.0 - WGS84_E2 * (N / (N + h))))

    return (degrees(lat), degrees(lon), h)


############################################################
# Local ENU basis
############################################################

def enu_basis(lat_deg: float, lon_deg: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lat = radians(lat_deg)
    lon = radians(lon_deg)

    east = np.array([-sin(lon), cos(lon), 0.0])
    north = np.array([-sin(lat) * cos(lon), -sin(lat) * sin(lon), cos(lat)])
    up = np.array([cos(lat) * cos(lon), cos(lat) * sin(lon), sin(lat)])

    return east, north, up


############################################################
# Target velocity in ECEF
############################################################

def target_velocity_ecef(lat: float, lon: float, speed: float, heading: float, vertical_speed: float = 0.0) -> np.ndarray:
    """
    Convert speed + heading (and optional vertical speed) to ECEF velocity vector.
    Heading: 0 = North, 90 = East (degrees)
    """
    east, north, up = enu_basis(lat, lon)
    heading_rad = radians(heading)

    horizontal = east * sin(heading_rad) + north * cos(heading_rad)
    velocity = horizontal * speed + up * vertical_speed
    return velocity


############################################################
# Intercept time solver (constant speed missile vs constant velocity target)
############################################################

def solve_intercept_time(R: np.ndarray, V: np.ndarray, missile_speed: float) -> Optional[float]:
    """
    Solve |R + V*t| = Vm * t  for the smallest t > 0
    Returns None if no positive real solution exists.
    """
    a = np.dot(V, V) - missile_speed ** 2
    b = 2.0 * np.dot(R, V)
    c = np.dot(R, R)

    EPS = 1e-9

    # Linear case (missile speed ≈ target speed)
    if abs(a) < EPS:
        if abs(b) < EPS:
            return None
        t = -c / b
        return t if t > 0.0 else None

    delta = b * b - 4.0 * a * c
    if delta < 0.0:
        return None

    sqrt_delta = sqrt(delta)
    t1 = (-b + sqrt_delta) / (2.0 * a)
    t2 = (-b - sqrt_delta) / (2.0 * a)

    candidates = [t for t in (t1, t2) if t > 0.0]
    if not candidates:
        return None

    return min(candidates)


############################################################
# Azimuth & Elevation (weapon local ENU)
############################################################

def calculate_azimuth(weapon_ecef: np.ndarray, kill_ecef: np.ndarray, weapon_lat: float, weapon_lon: float) -> float:
    east, north, _ = enu_basis(weapon_lat, weapon_lon)
    vec = kill_ecef - weapon_ecef

    e = np.dot(vec, east)
    n = np.dot(vec, north)

    az = degrees(atan2(e, n))
    if az < 0.0:
        az += 360.0
    return az


def calculate_elevation(weapon_ecef: np.ndarray, kill_ecef: np.ndarray, weapon_lat: float, weapon_lon: float) -> float:
    east, north, up = enu_basis(weapon_lat, weapon_lon)
    vec = kill_ecef - weapon_ecef

    e = np.dot(vec, east)
    n = np.dot(vec, north)
    u = np.dot(vec, up)

    horizontal = sqrt(e * e + n * n)
    return degrees(atan2(u, horizontal))


############################################################
# Main Fire Control Solution
############################################################

def fire_control_solution(weapon: Dict[str, Any], target: Dict[str, Any], vertical_speed: float = 0.0) -> Dict[str, Any]:
    """
    Compute launch point / time and kill point / time for a constant-speed
    missile against a constant-velocity target, with a fixed launch delay.

    Definitions used:
    - launch_time  : fixed preparation delay (weapon ready → fire)
    - launch_point : predicted target position at launch_time
    - kill_time    : missile flight time after launch
    - kill_point   : predicted target position at launch_time + kill_time
    """

    # Current positions
    weapon_ecef = geodetic_to_ecef(weapon["position"])
    target_ecef = geodetic_to_ecef(target["position"])

    # Target velocity (ECEF)
    velocity = target_velocity_ecef(
        lat=target["position"][0],
        lon=target["position"][1],
        speed=target["speed"],
        heading=target["heading"],
        vertical_speed=vertical_speed
    )

    # Fixed launch delay
    launch_delay = float(weapon.get("launch_delay", 0.5))
    launch_time = launch_delay

    # Predicted target position when missile is launched
    launch_point_ecef = target_ecef + velocity * launch_time

    # Relative vector from weapon to launch point
    R = launch_point_ecef - weapon_ecef

    # Solve for missile flight time
    flight_time = solve_intercept_time(R, velocity, weapon["missile_speed"])

    if flight_time is None:
        return {"status": False, "reason": "No intercept solution"}

    # Kill point
    kill_point_ecef = launch_point_ecef + velocity * flight_time

    # Geometry
    missile_distance = float(np.linalg.norm(kill_point_ecef - weapon_ecef))
    azimuth = calculate_azimuth(weapon_ecef, kill_point_ecef, weapon["position"][0], weapon["position"][1])
    elevation = calculate_elevation(weapon_ecef, kill_point_ecef, weapon["position"][0], weapon["position"][1])

    return {"status": True, 
            "launch_time": round(launch_time, 3),          # seconds until fire
            "launch_point": ecef_to_geodetic(launch_point_ecef),
            "kill_time": round(flight_time, 3),            # missile flight time
            "kill_point": ecef_to_geodetic(kill_point_ecef),
            "total_time": round(launch_time + flight_time, 3),
            "missile_distance": round(missile_distance, 2),
            "azimuth": round(azimuth, 4),
            "elevation": round(elevation, 4)
            }


############################################################
# Example / Test
############################################################

if __name__ == "__main__":
    weapon = {
        "id": 1,
        "name": "SAM-1",
        "type": "SAM",
        "position": [35.6892, 51.3890, 1200],      # lat, lon, alt (m)
        "min_range": 500,
        "max_range": 6000,
        "min_altitude": 50,
        "max_altitude": 18000,
        "missile_speed": 416.66666667,             # ~1500 km/h
        "launch_delay": 0.5,                       # seconds
        "status": "READY",
        "engagement_channels": 4,
        "used_channels": 1
    }

    target = {
        "id": 1,
        "type": "CRUISE_MISSILE",
        "position": [35.7020, 51.3890, 1500],      # lat, lon, alt (m)
        "speed": 277.77777778,                     # ~1000 km/h
        "heading": 45,                             # degrees
        "priority": 9,
        "value": 10
    }

    result = fire_control_solution(weapon, target)
    print(result)
