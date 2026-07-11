from src.rules.base_rule import BaseRule
from src.entities.rule_result import RuleResult
from src.entities.weapon import Weapon, WeaponStatus
from src.entities.target import Target

class StatusRule(BaseRule):
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        if weapon.status == WeaponStatus.READY:
            return RuleResult(rule_name="StatusRule", 
                              passed=True)
    
        return RuleResult(rule_name="StatusRule", 
                              passed=False,
                              reason=f"Weapon status is {weapon.status.name}.")
