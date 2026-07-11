from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.rule_result import RuleResult
from src.rules.base_rule import BaseRule

class AmmoRule(BaseRule):
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        if weapon.ammo > 0:
            return RuleResult(rule_name="AmmoRule", passed=True)
        
        return RuleResult(rule_name="AmmoRule", passed=False, reason=("ammunition"))
