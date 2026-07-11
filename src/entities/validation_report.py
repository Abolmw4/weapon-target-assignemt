from dataclasses import dataclass
from src.entities.assignment import Assignment
from src.entities.rule_result import RuleResult
from typing import List

@dataclass
class ValidationReport:
    assignment: Assignment
    valid: bool
    result: List[RuleResult]
