from dataclasses import dataclass, Field
from typing import Tuple
from enum import Enum

class WeaponStatus(Enum):
    DESTROYED = 1
    RELOADING = 2
    MAINTANENCE = 3
    OFFLINE = 4
    READY = 5
    
class WeapnType(Enum):
    SAM = 1
    AAA = 2
    JAMER = 3
    AIRBASE = 4 
    

@dataclass
class Weapon:
    id: int
    name: str
    weapon_type: WeapnType
    positon: Tuple[float, float, float]
    ranges: Tuple[float]
    min_range: float
    max_range: float
    min_altitude: float
    max_altitude: float
    ammo: int
    status: WeaponStatus
    engagement_channels: int
    used_channels: int
