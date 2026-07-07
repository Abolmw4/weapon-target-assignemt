from dataclasses import dataclass
from enum import Enum
from typing import Tuple

class TargetClass(Enum):
    HUSTILE = 1
    ZOMBI = 2
    X_RAY = 3
    UNKNOWN = 4

class TargetType(Enum):
    BALLISTIC_MISSILE = 1
    CRUISE_MISSILE = 2
    AIRCRAFT = 3
    HELICOPTER = 4
    DRONE = 5
    BOMBER = 6
    UNKNOWN = 7
    

@dataclass
class Target:
    id: int
    target_class: TargetClass
    target_type: TargetType
    position: Tuple[float, float, float]
    altitude: float
    speed: float
    heading: float
    value: float
    priority: int
