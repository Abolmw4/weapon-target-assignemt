from src.rules.base_rule import BaseRule

from src.entities.weapon import Weapon, WeapnType
from src.entities.target import Target
from src.entities.rule_result import RuleResult
from src.utils.utils import calculate_distance, calculate_horizontal_distance
from typing import List
class RangeRule(BaseRule):
    def __init__(self):
        super().__init__()
        pass
    
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        # distance = calculate_distance(weapon.positon, target.position)
        range = calculate_horizontal_distance(weapon.positon, target.position)
        
        if weapon.weapon_type == WeapnType.SAM:
            for i, r in enumerate(weapon.ranges):
                if range <= r:
                    return RuleResult(rule_name="RangeRule", passed=True, reason=f"Target is in range layer {i+1}")
            return RuleResult(
            rule_name="RangeRule", passed=False, reason="Target is outside all range layers.")
                
        if weapon.min_range < range < weapon.max_range:
            return RuleResult(rule_name="RangeRule", passed=True)
        return RuleResult(rule_name="RangeRule", passed=False, reason=f"target distance: {range} is out of weapon range: min->{weapon.max_range}, max->{weapon.max_range}")

    
    def __sam_can_engage(weapon) -> bool:
        pass
