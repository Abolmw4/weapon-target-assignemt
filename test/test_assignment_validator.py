import unittest
from src.rules.base_rule import BaseRule
from src.rules.ammo_rule import AmmoRule
from src.entities.weapon import WeaponStatus
from src.rules.status_rule import StatusRule
from src.rules.range_rule import RangeRule
from src.rules.compatibility_rule import CompatiblityRule
from src.repositories.compatibility_repository import CompatibilityRepository
from src.repositories.base_repository import Repositroy
from src.repositories.weapon_repository import WeapnRepository
from src.repositories.target_repository import TargetRepository
from src.entities.rule_result import RuleResult
from src.validator.assignment_validator import AssignmentValidator
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.assignment import Assignment
from typing import List, Dict


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.weapons: List[Weapon] = WeapnRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/weapon.json").load()
        self.target: List[Target] = TargetRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/target.json").load()
        self.compatibiltiy: Dict[str, List[str]] = CompatibilityRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json").load()
        self.validator = AssignmentValidator(rules=[StatusRule(), AmmoRule(), RangeRule(), CompatiblityRule(CompatibilityRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json"))])
        
    def test_valid_assignment(self):

        weapon = self.weapons[0]
        weapon.status = WeaponStatus.RELOADING
        target = self.target[0]
        report = self.validator.validate(weapon=weapon, target=target, assignment=Assignment(weapon_id=1, target_id=1, assignment_id=1))
        self.assertFalse(report.valid)
