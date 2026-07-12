from src.engines.base_engine import BaseEngine
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.validator.assignment_validator import AssignmentValidator
from src.entities.assignment import Assignment
from src.entities.validation_report import ValidationReport
from typing import List
class ManualEngine(BaseEngine):
    def __init__(self, validator: AssignmentValidator):
        self.validator = validator

    def run(self, weapon: Weapon, target: Target, assignment: Assignment) -> ValidationReport:
        return self.validator.validate(weapon=weapon, target=target, assignment=assignment)
