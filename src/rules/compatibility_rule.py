from src.rules.base_rule import BaseRule
from src.entities.rule_result import RuleResult
from src.repositories.base_repository import Repositroy
from src.repositories.compatibility_repository import CompatibilityRepository
from src.entities.weapon import Weapon
from src.entities.target import Target
from typing import Dict, List

class CompatiblityRule(BaseRule):
    def __init__(self, repo: Repositroy):
        self.compatibility: Dict[str, List[str]] = repo.load()
        
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        if weapon.weapon_type.name in self.compatibility and target.target_type.name in self.compatibility[weapon.weapon_type.name]:
            return RuleResult(rule_name="CompatiblityRule",  passed=True)

        return RuleResult(rule_name="CompatiblityRule", 
                              passed=False,
                              reason=f"Weapon {weapon.weapon_type.name} not sutable for target {target.target_type.name}")
