from src.rules.base_rule import BaseRule
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.validation_report import ValidationReport
from src.entities.assignment import Assignment
from typing import List


class AssignmentValidator:
    def __init__(self, rules: List[BaseRule]) -> None:
        self.rules = rules
    
    def validate(self, weapon: Weapon, target: Target, assignment: Assignment) -> ValidationReport:
        results = []
        
        for rule in self.rules:
            result = rule.check(weapon=weapon, target=target)
            results.append(result)
            
        valid = all(result.passed for result in results)
        
        return ValidationReport(assignment=assignment, valid=valid, result=results)
