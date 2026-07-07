from dataclasses import dataclass
from typing import Tuple
from enum import Enum

class WeaponStatus(Enum):
    DESTROYED = 1
    RELOADING = 2
    MAINTANENCE = 3
    OFFLINE = 4
    READY = 5

@dataclass
class Weapon:
    id: int
    name: str
    positon: Tuple[float, float, float]
    min_range: float
    max_range: float
    min_altitude: float
    max_altitude: float
    ammo: int
    status: WeaponStatus
    engagement_channels: int
    used_channels: int
