import unittest
from src.rules.base_rule import BaseRule
from src.rules.ammo_rule import AmmoRule
from src.entities.weapon import WeaponStatus
from src.rules.status_rule import StatusRule
from src.rules.range_rule import RangeRule
from src.rules.compatibility_rule import CompatiblityRule
from src.rules.altitude_rule import AltituedRule
from src.rules.pk_rule import PKRule
from src.repositories.compatibility_repository import CompatibilityRepository
from src.repositories.base_repository import Repositroy
from src.repositories.weapon_repository import WeapnRepository
from src.repositories.target_repository import TargetRepository
from src.rules.pk_rule import PKRule
from src.repositories.pk_repository import PKRepository
from src.entities.rule_result import RuleResult
from src.validator.assignment_validator import AssignmentValidator
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.entities.assignment import Assignment
from src.entities.validation_report import ValidationReport
from typing import List, Dict
from copy import deepcopy

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.weapons: List[Weapon] = WeapnRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/weapon.json").load()
        self.targets: List[Target] = TargetRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/target.json").load()
        self.compatibiltiy: Dict[str, List[str]] = CompatibilityRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json").load()
        
        
    def test_valid_assignment(self):
        validator = AssignmentValidator(rules=[StatusRule()])
        weapon = self.weapons[0]
        target = self.targets[0]

        report = validator.validate(weapon, target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))

        self.assertTrue(report.valid)
    
    def test_invalid_status(self):
        validator = AssignmentValidator(rules=[StatusRule()])
        
        weapon = self.weapons[0]

        weapon.status = WeaponStatus.RELOADING

        target = self.targets[0]

        report = validator.validate(weapon, target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))

        self.assertFalse(report.valid)

    def test_no_ammo(self):
        validator = AssignmentValidator(rules=[StatusRule(), AmmoRule()])
        
        weapon = self.weapons[0]

        weapon.ammo = 0

        target = self.targets[0]

        report = validator.validate(weapon, target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))

        self.assertFalse(report.valid)
        print(report.result[0].reason)
        
    def test_incompatible_weapon_target(self):
        validator = AssignmentValidator(rules=[StatusRule(), AmmoRule(), CompatiblityRule(CompatibilityRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json"))])
        weapon = deepcopy(self.weapons[3])      # AAA
        target = deepcopy(self.targets[1])      # BALISTIC MISSILE

        report: ValidationReport = validator.validate(weapon=weapon, target=target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))

        self.assertFalse(report.valid)



    def test_target_out_of_range(self):
        validator = AssignmentValidator(rules=[StatusRule(), AmmoRule(), CompatiblityRule(CompatibilityRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json")), RangeRule()])

        weapon = deepcopy(self.weapons[0])

        target = deepcopy(self.targets[0])

        # target.position = (40.000000, 58.000000, 1000)

        report = validator.validate(weapon=weapon, target=target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))

        self.assertFalse(report.valid)

    def test_target_out_of_altitude_range(self):
        validator = AssignmentValidator(rules=[AltituedRule()])
        weapon = self.weapons[0]
        target = self.targets[0]
        
        report = validator.validate(weapon=weapon, target=target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))
        
        self.assertTrue(report.valid)

    def test_valid_prob_of_kill(self):
        validator = AssignmentValidator(rules=[PKRule(thereshold=0.5, repo=PKRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/pk.json"))])
        weapon = self.weapons[0]
        target = self.targets[0]
        
        report = validator.validate(weapon=weapon, target=target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))
        self.assertTrue(report.valid)
