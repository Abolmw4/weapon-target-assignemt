from typing import List, Dict, Any, Tuple
import json
from math import radians, sin, cos, sqrt, asin
from datetime import datetime
import redis

# redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def weapon_target_assignment_functionality(weapon_id: int, target_id: int, target_type: str, redis_client):
    
    # Problem assumptions
    WGS84_A = 6378137.0
    WGS84_B = 6356752.314245
    WGS84_E2 = 1 - (WGS84_B ** 2) / (WGS84_A ** 2)
    EARTH_RADIUS = 6371000.0  # meters
    PROB_OF_KILL_THERESHOLD = 0.7
        
    weapon_compatibility = {
        "SAM": ["CRUISE_MISSILE", "AIRCRAFT", "HELICOPTER", "DRONE"],
        "AAA": ["HELICOPTER", "AIRCRAFT", "DRONE"],
        "JAMMER": ["DRONE"],
        "FIGHTER": ["AIRCRAFT", "BOMBER", "HELICOPTER"]
    }
    
    pk = {
        "SAM": {"BALLISTIC_MISSILE": 0.67,
                "CRUISE_MISSILE": 0.92,
                "AIRCRAFT": 0.88,
                "DRONE": 0.70},
        
        "AAA": {"AIRCRAFT": 0.55,
                "DRONE": 0.80},

        "JAMMER": {"DRONE": 0.90,
                   "AIRCRAFT": 0.88},
        
        "AIRCRAFT": {"CRUISE_MISSILE": 0.92,
                     "AIRCRAFT": 0.88,
                     "DRONE": 0.70}
        }


    def calculate_horizontal_distance(position1: Tuple[float, float, float], position2: Tuple[float, float, float]) -> float:

        lat1, lon1, _ = position1
        lat2, lon2, _ = position2

        lat1 = radians(lat1)
        lon1 = radians(lon1)

        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2)

        c = 2 * asin(sqrt(a))

        return EARTH_RADIUS * c
    

    # getting weapon and target
    try:
        # target: Dict[str, Any] = get_target(target_id)
        # weapon: Dict[str, Any] = get_weapon(weapon_id)

        target: Dict[str, Any] = {
            "id": 1,
            "type": "CRUISE_MISSILE",
            "position":  [35.7020, 51.3890, 1500],
            "altitude": 1500,
            "speed": 250,
            "heading": 45,
            "priority": 9,
            "value": 10
            }
        
        weapon: Dict[str, Any] = {
            "id": 1,
            "name": "SAM-1",
            "type": "SAM",
            "position": [35.6892, 51.3890, 1200],
            "min_range": 500,
            "max_range": 2500,
            "min_altitude": 50,
            "max_altitude": 18000,
            "ranges": [500, 1000, 1500, 2000, 2500],
            "ammo": 8,
            "status": "READY",
            "engagement_channels": 4,
            "used_channels": 1
            }
    
    
    except RuntimeError as error:
        print("can't getting target and weapon")
        return {"level": "Error", "description": "can't getting target and weapon in weapon_target_assignment_functionality"}
    
    
    if weapon is None or target is None:
        print(f"can't get target and weapn. target and weapon is None")
        return {"level": "Error", "description": "can't get target and weapn. target or weapon is None"}
    
    # checking assignment
    keys = list(redis_client.scan_iter("assignment:*"))

    keys = [k for k in keys if k != "assignment:id"]
    
    if len(keys) != 0:
        for k in keys:
            assignment = json.loads(redis_client.get(k))
            if weapon_id == assignment["weapon_id"] and target_id == assignment["target_id"]:
                 return {"assignment_id": assignment["assignment_id"], "weapon_id": weapon["id"], "target_id": target["id"]}
    
    
    
    
    # checking rules
    result: Dict[str, Dict[str, Any]] = {}
    base_rules = ["StatusRule", "AmmoRule","CompatiblityRule", "RangeRule", "AltituedRule", "ChannelRule", "PKRule"]
    
    for rule in base_rules:
        if rule == "StatusRule":
            if weapon["status"].upper() == "READY":
                result[rule] = {"status": True, "description": ""}
                continue
            result[rule] = {"status": False, "description": "weapon not READY"}
            
        elif rule == "AmmoRule":
            if weapon["ammo"] > 0:
                result[rule] = {"status": True, "description": ""}
                continue
            result[rule] = {"status": False, "description": "weapon haven't ammo"}
        
        elif rule == "CompatiblityRule":
            if weapon["type"] in weapon_compatibility:
                if target_type in weapon_compatibility[weapon["type"]]:
                    result[rule] = {"status": True, "description": ""}
                    continue
                result[rule] = {"status": False, "description": f"based on weapon_compatibility weapon {weapon['type']} can't engaged with target {target_type}"}
            else:
                raise ValueError(f"Weapon type not valid weapot type must be '[SAM, AAA, JAMMER, FIGHTER]'")
        
        elif rule == "RangeRule":
            Range = calculate_horizontal_distance(weapon["position"], target["position"])
            if weapon["type"].upper() == "SAM":
                for i, r in enumerate(weapon["ranges"]):
                    if Range <= r:
                        result[rule] = {"status": True, "description": ""}
                        break
                
                if rule not in result:
                    result[rule] = {"status": False, "description": "target not in weapon range"}
                
            elif weapon["min_range"] < Range < weapon["max_range"]:
                result[rule] = {"status": True, "description": ""}
            
            else:
                result[rule] = {"status": False, "description": "target not in weapon range"}
        
        elif rule == "AltituedRule":
            if weapon["min_altitude"] < target["altitude"] < weapon["max_altitude"]:
                result[rule] = {"status": True, "description": ""}
                continue
            result[rule] = {"status": False, "description": "target altitude not in weapon altitude"}
        
        elif rule == "ChannelRule":
            if weapon["used_channels"] < weapon["engagement_channels"]:
                result[rule] = {"status": True, "description": ""}
                continue
            result[rule] = {"status": False, "description": "weapon engagment channel in used."}
        
        elif rule == "PKRule":
            if pk[weapon["type"]][target_type] >= PROB_OF_KILL_THERESHOLD:
                result[rule] = {"status": True, "description": ""}
                continue
            result[rule] = {"status": False, "description": f"because of prob of kill {weapon['type']} -> target {target_type} {pk[weapon['type']][target_type]} <= {PROB_OF_KILL_THERESHOLD}"}
        
        else:
            raise RuntimeError(f"this is fucking invalid '{rule}'")
    
    valid: bool = all(value["status"] for value in result.values())
    
    if valid:
        # write to redis
        assignment_id = redis_client.incr("assignment:id")
        assignment = {"assignment_id": assignment_id, "weapon_id": weapon['id'], "target_id": target['id'], "weapon_info": weapon, "target_info": target, "results": result}        
        try:
            redis_client.set(f"assignment:{assignment_id}", json.dumps(assignment))    
            return {"assignment_id": assignment_id, "weapon_id": weapon["id"], "target_id": target["id"]}
        except RuntimeError as error:
            return {"level":"Error", "description": f"assignment don. but can't write in redis."}
    else:
        return {"level": "warning", "description": f"these rules not passed {[k for k, value in result.items() if not value['status']]}"}
    
if __name__ == "__main__":
    result = weapon_target_assignment_functionality(1, 1, redis_client=redis_client)
    print(result)
