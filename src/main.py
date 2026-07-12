import numpy as np
import argparse
from typing import Dict, List, Any
from src.repositories.compatibility_repository import CompatibilityRepository
from src.repositories.weapon_repository import WeapnRepository
from src.repositories.target_repository import TargetRepository
from src.repositories.compatibility_repository import CompatibilityRepository
from src.repositories.pk_repository import PKRepository
from src.entities.weapon import Weapon
from src.entities.target import Target
from src.engines.manual_engine import ManualEngine
from src.validator.assignment_validator import AssignmentValidator
from src.rules.ammo_rule import AmmoRule
from src.rules.status_rule import StatusRule
from src.rules.channel_rule import ChannelRule
from src.rules.range_rule import RangeRule
from src.rules.compatibility_rule import CompatiblityRule
from src.rules.pk_rule import PKRule
from src.rules.altitude_rule import AltituedRule
from src.entities.assignment import Assignment
from src.entities.validation_report import ValidationReport

def main():
    weapons: Weapon = WeapnRepository("/home/abolfazl/Documents/weapon-target-assignemt/data/weapon.json").load()    
    targets: Target = TargetRepository("/home/abolfazl/Documents/weapon-target-assignemt/data/target.json").load()

    validator = AssignmentValidator(rules=[StatusRule(), AmmoRule(),
                                           CompatiblityRule(repo=CompatibilityRepository("/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json")),
                                           RangeRule(),
                                           AltituedRule(),
                                           ChannelRule(),
                                           PKRule(repo=PKRepository("/home/abolfazl/Documents/weapon-target-assignemt/data/pk.json"), thereshold=0.7)])
    
    manual_engine = ManualEngine(validator=validator)
    
    
    validation_assignment: ValidationReport = manual_engine.run(weapon=weapons[0], target=targets[0], assignment=Assignment(assignment_id=1, weapon_id=weapons[0].id, target_id=targets[0].id))
    
    print(validation_assignment.valid)
    if not validation_assignment.valid:
        for rule in validation_assignment.result:
            if not rule.passed:
                print(rule)

if __name__ == "__main__":
    main()
