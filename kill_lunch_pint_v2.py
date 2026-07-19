from __future__ import annotations

from math import sin, cos, atan2, radians, degrees, sqrt, asin
from typing import Tuple, Dict, Optional, Any, List
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")


############################################################
# WGS84
############################################################
WGS84_A = 6378137.0
WGS84_B = 6356752.314245
WGS84_E2 = 1.0 - (WGS84_B ** 2) / (WGS84_A ** 2)
EARTH_RADIUS = 6378137.0  # meter


############################################################
# Geodetic <-> ECEF
############################################################

def geodetic_to_ecef(position: Tuple[float, float, float]) -> np.ndarray:
    """(lat_deg, lon_deg, h_m) -> ECEF meters"""
    lat_deg, lon_deg, h = position
    lat = radians(lat_deg)
    lon = radians(lon_deg)

    sin_lat, cos_lat = sin(lat), cos(lat)
    sin_lon, cos_lon = sin(lon), cos(lon)

    N = WGS84_A / sqrt(1.0 - WGS84_E2 * sin_lat ** 2)
    x = (N + h) * cos_lat * cos_lon
    y = (N + h) * cos_lat * sin_lon
    z = (N * (1.0 - WGS84_E2) + h) * sin_lat
    return np.array([x, y, z], dtype=float)


def ecef_to_geodetic(ecef: np.ndarray) -> Tuple[float, float, float]:
    """ECEF -> (lat_deg, lon_deg, h_m)"""
    x, y, z = map(float, ecef)
    lon = atan2(y, x)
    p = sqrt(x * x + y * y)

    lat = atan2(z, p * (1.0 - WGS84_E2))
    h = 0.0
    for _ in range(8):
        sin_lat = sin(lat)
        N = WGS84_A / sqrt(1.0 - WGS84_E2 * sin_lat ** 2)
        h = p / cos(lat) - N
        lat = atan2(z, p * (1.0 - WGS84_E2 * (N / (N + h))))

    return (degrees(lat), degrees(lon), float(h))


############################################################
# Local ENU
############################################################

def enu_basis(lat_deg: float, lon_deg: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lat = radians(lat_deg)
    lon = radians(lon_deg)
    east = np.array([-sin(lon), cos(lon), 0.0])
    north = np.array([-sin(lat) * cos(lon), -sin(lat) * sin(lon), cos(lat)])
    up = np.array([cos(lat) * cos(lon), cos(lat) * sin(lon), sin(lat)])
    return east, north, up


def target_velocity_ecef(
    lat: float,
    lon: float,
    speed: float,
    heading: float,
    vertical_speed: float = 0.0,
) -> np.ndarray:
    """
    speed [m/s], heading [deg] (0=N, 90=E), vertical_speed [m/s] -> ECEF velocity
    """
    east, north, up = enu_basis(lat, lon)
    h = radians(heading)
    horizontal = east * sin(h) + north * cos(h)
    return horizontal * float(speed) + up * float(vertical_speed)


def target_accel_ecef(
    lat: float,
    lon: float,
    accel_horizontal: float = 0.0,
    accel_heading_deg: Optional[float] = None,
    heading_deg: float = 0.0,
    accel_vertical: float = 0.0,
    accel_enu: Optional[Tuple[float, float, float]] = None,
) -> np.ndarray:
    """
    شتاب هدف در ECEF.

    روش‌ها:
    1) accel_enu = (ae, an, au) مستقیم
    2) accel_horizontal در راستای accel_heading_deg (یا heading فعلی) + accel_vertical
    """
    east, north, up = enu_basis(lat, lon)

    if accel_enu is not None:
        ae, an, au = accel_enu
        return east * ae + north * an + up * au

    ah = float(accel_horizontal)
    av = float(accel_vertical)
    if ah == 0.0 and av == 0.0:
        return np.zeros(3, dtype=float)

    hdg = heading_deg if accel_heading_deg is None else accel_heading_deg
    h = radians(hdg)
    horiz_dir = east * sin(h) + north * cos(h)
    return horiz_dir * ah + up * av


############################################################
# Motion prediction (CV / CA)
############################################################

def predict_position(
    p0: np.ndarray,
    v0: np.ndarray,
    a0: Optional[np.ndarray],
    dt: float,
) -> np.ndarray:
    """
    پیش‌بینی موقعیت بعد از dt ثانیه.
    a0=None یا صفر => Constant Velocity
    وگرنه Constant Acceleration: p + v*t + 0.5*a*t^2
    """
    if dt < 0.0:
        raise ValueError("dt must be >= 0")
    if a0 is None:
        return p0 + v0 * dt
    return p0 + v0 * dt + 0.5 * a0 * (dt ** 2)


def predict_velocity(
    v0: np.ndarray,
    a0: Optional[np.ndarray],
    dt: float,
) -> np.ndarray:
    if a0 is None:
        return v0.copy()
    return v0 + a0 * dt


############################################################
# Closed-form intercept (CV only) — initial guess / fallback
############################################################

def solve_intercept_time_cv(R: np.ndarray, V: np.ndarray, missile_speed: float) -> Optional[float]:
    """
    |R + V*t| = Vm * t  for smallest t > 0
    فقط وقتی هدف در کل پرواز سرعت ثابت فرض شود دقیق است.
    """
    a = float(np.dot(V, V) - missile_speed ** 2)
    b = float(2.0 * np.dot(R, V))
    c = float(np.dot(R, R))
    EPS = 1e-9

    if abs(a) < EPS:
        if abs(b) < EPS:
            return 0.0 if c <= 0.0 else None
        t = -c / b
        return t if t > 0.0 else None

    delta = b * b - 4.0 * a * c
    if delta < 0.0:
        return None

    sd = sqrt(delta)
    t1 = (-b + sd) / (2.0 * a)
    t2 = (-b - sd) / (2.0 * a)
    cand = [t for t in (t1, t2) if t > 1e-9]
    return min(cand) if cand else None


############################################################
# Iterative intercept (recommended when target maneuvers)
############################################################

def solve_intercept_iterative(
    weapon_ecef: np.ndarray,
    target_ecef: np.ndarray,
    target_vel_ecef: np.ndarray,
    missile_speed: float,
    launch_time: float,
    target_acc_ecef: Optional[np.ndarray] = None,
    max_iter: int = 30,
    tol: float = 1e-4,
    t_f_max: float = 300.0,
) -> Optional[Dict[str, Any]]:
    """
    از «الان»:
      t_L = launch_time
      t_f = flight time after launch
      total = t_L + t_f

    launch_point = predict(target, t_L)     # هدف وقتی شلیک می‌شود
    kill_point   = predict(target, t_L+t_f)

    موشک سرعت‌ثابت از launcher_point:
      |kill - weapon| ≈ Vm * t_f
    """
    if missile_speed <= 0.0:
        return None

    # --- initial guess ---
    p_at_launch_guess = predict_position(target_ecef, target_vel_ecef, target_acc_ecef, launch_time)
    R0 = p_at_launch_guess - weapon_ecef
    v_at_launch = predict_velocity(target_vel_ecef, target_acc_ecef, launch_time)

    t_f = solve_intercept_time_cv(R0, v_at_launch, missile_speed) # Initial killtime
    if t_f is None:
        # fallback geometric
        t_f = float(np.linalg.norm(R0) / missile_speed)
    t_f = float(np.clip(t_f, 1e-6, t_f_max))

    converged = False
    last_err = None

    for _ in range(max_iter):
        total = launch_time + t_f
        p_kill = predict_position(target_ecef, target_vel_ecef, target_acc_ecef, total)
        range_to_kill = float(np.linalg.norm(p_kill - weapon_ecef))
        t_f_new = range_to_kill / missile_speed # missile time needed to arrive killpoint

        if t_f_new <= 0.0 or t_f_new > t_f_max:
            return None

        err = abs(t_f_new - t_f)
        last_err = err
        t_f = t_f_new
        if err < tol:
            converged = True
            break

    total = launch_time + t_f
    launch_point_ecef = predict_position(target_ecef, target_vel_ecef, target_acc_ecef, launch_time)
    kill_point_ecef = predict_position(target_ecef, target_vel_ecef, target_acc_ecef, total)

    # residual: should be ~0 if consistent with constant-Vm model
    residual = abs(float(np.linalg.norm(kill_point_ecef - weapon_ecef)) - missile_speed * t_f)

    return {
        "launch_time": float(launch_time),
        "kill_time": float(t_f),
        "total_time": float(total),
        "launch_point_ecef": launch_point_ecef,
        "kill_point_ecef": kill_point_ecef,
        "missile_distance": float(np.linalg.norm(kill_point_ecef - weapon_ecef)),
        "converged": converged,
        "residual_m": float(residual),
        "time_error_s": float(last_err if last_err is not None else -1.0),
    }


############################################################
# Az / El
############################################################

def calculate_azimuth(weapon_ecef, point_ecef, weapon_lat, weapon_lon) -> float:
    east, north, _ = enu_basis(weapon_lat, weapon_lon)
    vec = point_ecef - weapon_ecef
    e, n = float(np.dot(vec, east)), float(np.dot(vec, north))
    az = degrees(atan2(e, n))
    return az + 360.0 if az < 0.0 else az


def calculate_elevation(weapon_ecef, point_ecef, weapon_lat, weapon_lon) -> float:
    east, north, up = enu_basis(weapon_lat, weapon_lon)
    vec = point_ecef - weapon_ecef
    e, n, u = float(np.dot(vec, east)), float(np.dot(vec, north)), float(np.dot(vec, up))
    return degrees(atan2(u, sqrt(e * e + n * n)))


############################################################
# Envelope check
############################################################

def check_envelope(
    weapon: Dict[str, Any],
    kill_geodetic: Tuple[float, float, float],
    missile_distance: float,
    azimuth: float,
    elevation: float,
) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    k_alt = kill_geodetic[2]

    if "min_range" in weapon and missile_distance < float(weapon["min_range"]):
        reasons.append("below_min_range")
    if "max_range" in weapon and missile_distance > float(weapon["max_range"]):
        reasons.append("above_max_range")
    if "min_altitude" in weapon and k_alt < float(weapon["min_altitude"]):
        reasons.append("below_min_altitude")
    if "max_altitude" in weapon and k_alt > float(weapon["max_altitude"]):
        reasons.append("above_max_altitude")

    if "min_elevation" in weapon and elevation < float(weapon["min_elevation"]):
        reasons.append("below_min_elevation")
    if "max_elevation" in weapon and elevation > float(weapon["max_elevation"]):
        reasons.append("above_max_elevation")

    # optional sector [min_az, max_az] with wrap support if needed later
    if "min_azimuth" in weapon and "max_azimuth" in weapon:
        mn, mx = float(weapon["min_azimuth"]), float(weapon["max_azimuth"])
        if mn <= mx:
            ok = mn <= azimuth <= mx
        else:
            ok = azimuth >= mn or azimuth <= mx
        if not ok:
            reasons.append("outside_azimuth_sector")

    return (len(reasons) == 0), reasons


############################################################
# Main Fire Control Solution
############################################################

def fire_control_solution(
    weapon: Dict[str, Any],
    target: Dict[str, Any],
    *,
    vertical_speed: float = 0.0,
    # شتاب اختیاری هدف (برای مانور). اگر ندارید صفر بماند => CV
    accel_horizontal: float = 0.0,
    accel_heading_deg: Optional[float] = None,
    accel_vertical: float = 0.0,
    accel_enu: Optional[Tuple[float, float, float]] = None,
    # اگر از فیلتر، velocity/accel ECEF مستقیم دارید:
    velocity_ecef: Optional[np.ndarray] = None,
    accel_ecef: Optional[np.ndarray] = None,
    # doctrine / search
    launch_time: Optional[float] = None,          # None => weapon launch_delay
    search_later_launches: bool = True,
    max_launch_wait: float = 20.0,
    launch_search_dt: float = 0.5,
    require_envelope: bool = True,
) -> Dict[str, Any]:
    """
    محاسبهٔ fire solution.

    launch_point = موقعیت هدف در لحظهٔ شلیک (طبق تعریف شما).
    این تابع را باید روی هر آپدیت track دوباره صدا بزنید.

    ورودی‌های مفید برای هدف مانوردار:
    - vertical_speed
    - accel_*  یا accel_ecef از فیلتر
    - velocity_ecef از فیلتر (بهتر از speed/heading خام)
    """
    # ---- positions ----
    launcher_point_geo = tuple(weapon["position"]) # launcher(I mean weapon postion) position
    weapon_ecef = geodetic_to_ecef(launcher_point_geo) # weapon position based on x, y, z
    target_ecef = geodetic_to_ecef(tuple(target["position"])) # target position based on x, y, z

    lat_t, lon_t = float(target["position"][0]), float(target["position"][1]) # target lat, lon
    lat_w, lon_w = float(weapon["position"][0]), float(weapon["position"][1]) # weapon lat, lon

    # ---- target kinematics ----
    if velocity_ecef is not None:
        v = np.asarray(velocity_ecef, dtype=float)
    else:
        v = target_velocity_ecef(
            lat=lat_t,
            lon=lon_t,
            speed=float(target["speed"]),
            heading=float(target["heading"]),
            vertical_speed=float(target.get("vertical_speed", vertical_speed)),
        ) # for converting speed in ECEF

    if accel_ecef is not None:
        a = np.asarray(accel_ecef, dtype=float)
    else:
        a = target_accel_ecef(
            lat=lat_t,
            lon=lon_t,
            accel_horizontal=float(target.get("accel_horizontal", accel_horizontal)),
            accel_heading_deg=target.get("accel_heading", accel_heading_deg),
            heading_deg=float(target["heading"]),
            accel_vertical=float(target.get("accel_vertical", accel_vertical)),
            accel_enu=target.get("accel_enu", accel_enu),
        )
        if float(np.linalg.norm(a)) < 1e-12:
            a = None  # pure CV

    missile_speed = float(weapon["missile_speed"])
    ready = float(weapon.get("launch_delay", 0.5)) if launch_time is None else float(launch_time)
    if ready < 0.0:
        return {"status": False, "reason": "launch_time_negative"}

    # candidate launch times: immediate ready, then optional later times
    if search_later_launches:
        t_candidates = np.arange(ready, ready + max_launch_wait + 1e-9, launch_search_dt)
    else:
        t_candidates = np.array([ready], dtype=float)

    last_fail_reason = "No intercept solution"
    best_out_of_envelope: Optional[Dict[str, Any]] = None

    for t_L in t_candidates:
        sol = solve_intercept_iterative(
            weapon_ecef=weapon_ecef,
            target_ecef=target_ecef,
            target_vel_ecef=v,
            missile_speed=missile_speed,
            launch_time=float(t_L),
            target_acc_ecef=a,
        )
        if sol is None:
            last_fail_reason = "No intercept solution"
            continue

        launch_geo = ecef_to_geodetic(sol["launch_point_ecef"])
        kill_geo = ecef_to_geodetic(sol["kill_point_ecef"])
        az = calculate_azimuth(weapon_ecef, sol["kill_point_ecef"], lat_w, lon_w)
        el = calculate_elevation(weapon_ecef, sol["kill_point_ecef"], lat_w, lon_w)

        ok_env, env_reasons = check_envelope(
            weapon, kill_geo, sol["missile_distance"], az, el
        )

        result = {
            "status": True,
            # زمان‌ها نسبت به «الان» (لحظهٔ محاسبه / آپدیت track)
            "launch_time": round(sol["launch_time"], 3),
            "kill_time": round(sol["kill_time"], 3),
            "total_time": round(sol["total_time"], 3),
            # نقاط
            "launcher_point": launcher_point_geo,  # مبدأ واقعی موشک
            "launch_point": (                     # هدف در لحظهٔ شلیک  << تعریف شما
                round(launch_geo[0], 7),
                round(launch_geo[1], 7),
                round(launch_geo[2], 2),
            ),
            "kill_point": (
                round(kill_geo[0], 7),
                round(kill_geo[1], 7),
                round(kill_geo[2], 2),
            ),
            # هندسه
            "missile_distance": round(sol["missile_distance"], 2),
            "azimuth": round(az, 4),
            "elevation": round(el, 4),
            # کیفیت حل
            "converged": bool(sol["converged"]),
            "residual_m": round(sol["residual_m"], 4),
            "model": "CA" if a is not None else "CV",
            "envelope_ok": ok_env,
            "envelope_reasons": env_reasons,
        }

        if not require_envelope or ok_env:
            return result

        # نگه داشتن اولین solution هرچند خارج envelope (برای دیباگ)
        if best_out_of_envelope is None:
            best_out_of_envelope = result
        last_fail_reason = "Intercept found but outside envelope: " + ",".join(env_reasons)

    if best_out_of_envelope is not None:
        out = dict(best_out_of_envelope)
        out["status"] = False
        out["reason"] = last_fail_reason
        return out

    return {"status": False, "reason": last_fail_reason}




def destination_point(lat: float, lon: float, distance: float, bearing: float) -> Tuple[float, float]:
    '''
    This function generate new point from start point in bearing side and specefic distance
    :param lat: start point that I created another point from it (weapon position)
    :param lon: start point that I created another point from it (weapon position)
    :param distance: how to much missile distance from start point to another point (meter) in other words is the same is 'ranges' in weapon data
    :param bearing: which side
    :return: new point based on deg
    :rtype: tuple[float, float]
    '''
    lat1 = radians(lat)
    lon1 = radians(lon)
    bearing = radians(bearing)

    angular_distance = distance / EARTH_RADIUS

    lat2 = asin(sin(lat1) * cos(angular_distance) + cos(lat1) * sin(angular_distance) * cos(bearing))

    lon2 = lon1 + atan2(sin(bearing) * sin(angular_distance) * cos(lat1), cos(angular_distance) - sin(lat1) * sin(lat2))

    return (degrees(lat2), degrees(lon2))

def calculate_kill_zone(weapon_position: float, radius: float, start_angle: float=0, end_angle: float=360, step: float=50) -> List[Tuple[float, float]]:
    '''
    generate boundray points of killzone
    
    :param weapon_position: lat, lon, alt of weapon or luncher
    :param radius: this parameter same is 'ranges' in weapon data json file. this paramter specified range in specefic altitude or layer
    :param start_angle: which scope is considered for creating killingzone.eq(0 deg is front of weapon)
    :param end_angle: which scope is considered for creating killingzone.eq(90 deg is front of weapon)
    :param step: after generating each point increase agle based on step. eq(angel+=step)
    '''
    lat, lon, _ = weapon_position
    polygon = []
    angle = start_angle
    while angle <= end_angle:
        point = destination_point(lat, lon, radius, angle)
        polygon.append(point)
        angle += step
    return polygon

def calculate_all_kill_zones(weapon: Dict[str, Any]) -> Dict[float, List[Tuple[float, float]]]:
    result = {}
    for altitude, radius in zip(weapon["altitudes"], weapon["ranges"]):
        polygon = calculate_kill_zone(weapon_position=weapon["position"], radius=radius, start_angle=0, end_angle=360, step=50)
        result[altitude] = polygon
    return result





############################################################
# Example
############################################################

# if __name__ == "__main__":
#     weapon = {
#         "id": 1,
#         "name": "SAM-1",
#         "type": "SAM",
#         "position": [35.6892, 51.3890, 1200],
#         "min_range": 500,
#         "max_range": 6000,
#         "min_altitude": 50,
#         "max_altitude": 18000,
#         "missile_speed": 416.66666667,  # ~1500 km/h
#         "launch_delay": 0.5,
#         "status": "READY",
#     }

#     target = {
#         "id": 1,
#         "type": "CRUISE_MISSILE",
#         "position": [35.7020, 51.3890, 1500],
#         "speed": 277.77777778,  # ~1000 km/h
#         "heading": 45,
#         # اختیاری برای مانور:
#         # "vertical_speed": 0.0,
#         # "accel_horizontal": 5.0,   # m/s^2
#         # "accel_vertical": 0.0,
#     }

#     result = fire_control_solution(weapon, target)
#     print(result)

#     # نمونه با شتاب افقی (تغییر سرعت/مانور)
#     # result_ca = fire_control_solution(
#     #     weapon,
#     #     target,
#     #     accel_horizontal=8.0,          # m/s^2 در راستای heading
#     #     vertical_speed=0.0,
#     # )
#     # print(result_ca)

if __name__ == "__main__":
    weapon = {
        "id": 1,
        "name": "SAM-1",
        "type": "SAM",
        "position": [35.6892, 51.3890, 1200],
        "min_range": 500,
        "max_range": 6000,
        "min_altitude": 50,
        "max_altitude": 18000,
        "altitudes": [50, 5000, 10000, 15000, 18000],
        "ranges": [500, 1000, 1500, 2000, 6000],
        "missile_speed": 416.66666667,
        "launch_delay": 0.5,
        "status": "READY",
        "engagement_channels": 4,
        "used_channels": 1,
    }

    target = {
        "id": 1,
        "type": "CRUISE_MISSILE",
        "position": [35.7020, 51.3890, 1500],
        "speed": 277.77777778,
        "heading": 45,
        "priority": 9,
        "value": 10,
    }

    result = fire_control_solution(weapon, target)
    print(result)

    zones = calculate_all_kill_zones(weapon)

    plt.figure(figsize=(9, 9))

    colors = ["green", "lime", "yellow", "orange", "red"]
    for color, altitude in zip(colors, zones):
        polygon = zones[altitude]
        lats = [p[0] for p in polygon]
        lons = [p[1] for p in polygon]
        lats.append(lats[0])
        lons.append(lons[0])
        plt.plot(lons, lats, color=color, linewidth=1.5, label=f"KZ @ {altitude} m")

    # ── 2) SAM  ──────────────────────────────────
    w_lat, w_lon, w_alt = weapon["position"]
    plt.scatter(w_lon, w_lat, c="black", s=100, marker="x", zorder=5, label="SAM (launcher)")

    # ── 3) target current position ───────────────────────────────────
    t_lat, t_lon, t_alt = target["position"]
    plt.scatter(t_lon, t_lat, c="blue", s=80, marker="o", zorder=5, label="Target (now)")

    # ── 4) Launch point + Kill point از fire_control_solution ─
    if result.get("status"):
        # launch_point / kill_point = (lat, lon, alt)
        lp_lat, lp_lon, lp_alt = result["launch_point"]
        kp_lat, kp_lon, kp_alt = result["kill_point"]

        # points
        plt.scatter(lp_lon, lp_lat, c="cyan", s=100, marker="s", zorder=6, label="Launch point (target@t_L)")
        plt.scatter(kp_lon, kp_lat, c="magenta", s=120, marker="*", zorder=6, label="Kill point")

        # predicted target path: now → launch → kill
        plt.plot([t_lon, lp_lon, kp_lon], [t_lat, lp_lat, kp_lat], color="blue", linestyle="--", linewidth=1.5, zorder=4, label="Target track",)

        # missle path: SAM → kill
        plt.plot([w_lon, kp_lon], [w_lat, kp_lat], color="red", linestyle="-", linewidth=1.8, zorder=4, label="Missile path",)


        plt.annotate(f"LP t={result['launch_time']}s", (lp_lon, lp_lat), textcoords="offset points", xytext=(6, 6), fontsize=8)
        
        plt.annotate(f"KP t={result['total_time']}s\nR={result['missile_distance']:.0f}m", (kp_lon, kp_lat), textcoords="offset points", xytext=(6, 6), fontsize=8)

        # هشدار envelope (اختیاری)
        md = result["missile_distance"]
        if not (weapon["min_range"] <= md <= weapon["max_range"]):
            print(f"[WARN] missile_distance {md:.1f}m خارج از [{weapon['min_range']}, {weapon['max_range']}]")
        if not (weapon["min_altitude"] <= kp_alt <= weapon["max_altitude"]):
            print(f"[WARN] kill alt {kp_alt:.1f}m خارج از envelope ارتفاع")
    else:
        print("No FCS:", result.get("reason"))

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Kill Zones + Launch Point + Kill Point")
    plt.grid(True)
    plt.legend(loc="best")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

