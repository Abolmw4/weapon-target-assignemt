from src.rules.base_rule import BaseRule
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.rule_result import RuleResult
from src.utils.utils import calculate_distance

class RangeRule(BaseRule):
    def __init__(self):
        super().__init__()
        pass
    
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        distance = calculate_distance(weapon.positon, target.position)
        
        if weapon.min_range < distance < weapon.max_range:
            return RuleResult(rule_name="RangeRule", passed=True)
        
        return RuleResult(rule_name="RangeRule", passed=False, reason=f"target distance: {distance} is out of weapon range: min->{weapon.max_range}, max->{weapon.max_range}")
