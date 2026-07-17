import yaml
from typing import Tuple
from math import radians, sin, cos, sqrt, asin
from typing import List

# WGS84 ellipsoid constants
WGS84_A = 6378137.0
WGS84_B = 6356752.314245
WGS84_E2 = 1 - (WGS84_B ** 2) / (WGS84_A ** 2)

EARTH_RADIUS = 6371000.0  # meters

def read_config_file(file_src: str="configs/scenario1.yaml") -> dict:
    with open(file_src, 'r') as stream:
        try:
            configs = yaml.safe_load(stream)
            # print(configs)
            return configs
        except yaml.YAMLError as exc:
            print(exc)


def geodetic_to_ecef(position: Tuple[float, float, float]) -> Tuple[float, float, float]:
    lat_deg, lon_deg, alt_m = position

    lat = radians(lat_deg)
    lon = radians(lon_deg)

    sin_lat = sin(lat)
    cos_lat = cos(lat)
    cos_lon = cos(lon)
    sin_lon = sin(lon)

    # Prime vertical radius of curvature
    n = WGS84_A / sqrt(1 - WGS84_E2 * sin_lat ** 2)

    x = (n + alt_m) * cos_lat * cos_lon
    y = (n + alt_m) * cos_lat * sin_lon
    z = (n * (1 - WGS84_E2) + alt_m) * sin_lat

    return x, y, z


def calculate_distance(position1: Tuple[float, float, float], position2: Tuple[float, float, float]) -> float:
    x1, y1, z1 = geodetic_to_ecef(position1)
    x2, y2, z2 = geodetic_to_ecef(position2)

    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2

    return sqrt(dx ** 2 + dy ** 2 + dz ** 2)



# from math import radians, sin, cos, asin, sqrt



def calculate_horizontal_distance(position1, position2):

    lat1, lon1, _ = position1
    lat2, lon2, _ = position2

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * asin(sqrt(a))

    return EARTH_RADIUS * c
