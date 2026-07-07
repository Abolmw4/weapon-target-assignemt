from abc import ABC, abstractmethod
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.rule_result import RuleResult


class BaseRule(ABC):
    @abstractmethod
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        pass
