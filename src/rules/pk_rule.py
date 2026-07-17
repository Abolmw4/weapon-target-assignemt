from src.rules.base_rule import BaseRule
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.rule_result import RuleResult
from src.repositories.base_repository import Repositroy
class PKRule(BaseRule):
    def __init__(self, thereshold: float, repo: Repositroy) -> None:
        super().__init__()
        self.thresh = thereshold
        self.pk_table = repo.load()
        
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        if self.pk_table[weapon.weapon_type.name][target.target_type.name] >= self.thresh:
            return RuleResult(rule_name="PKRule", passed=True)
        
        return RuleResult(rule_name="PKRule", passed=False, reason=f"prob of kill less than {self.thresh}")

