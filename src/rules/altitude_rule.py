from src.rules.base_rule import BaseRule
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.rule_result import RuleResult

class AltituedRule(BaseRule):
    def __init__(self):
        super().__init__()
    
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        if weapon.min_altitude < target.altitude < weapon.max_altitude:
            return RuleResult(rule_name="AltituedRule", passed=True)
        
        return RuleResult(rule_name="AltituedRule", passed=False, reason=f"target:{target.altitude} out of range altitude of weapon:{weapon.min_altitude}-{weapon.max_altitude}")
