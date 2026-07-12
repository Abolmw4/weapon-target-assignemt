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
import argparse

def main(args):
    weapons: Weapon = WeapnRepository(args.weapon_data).load()
    targets: Target = TargetRepository(args.target_data).load()

    validator = AssignmentValidator(rules=[StatusRule(), AmmoRule(),
                                           CompatiblityRule(repo=CompatibilityRepository(args.compatibility_data)),
                                           RangeRule(),
                                           AltituedRule(),
                                           ChannelRule(),
                                           PKRule(repo=PKRepository(args.pk_data), thereshold=args.threshold)])
    
    target, weapon = targets[0], weapons[0]
    manual_engine = ManualEngine(validator=validator)
    
    validation_assignment: ValidationReport = manual_engine.run(weapon=weapon, target=target, assignment=Assignment(assignment_id=1, weapon_id=weapon.id, target_id=target.id))
    
    print(validation_assignment.valid)
    if not validation_assignment.valid:
        for rule in validation_assignment.result:
            if not rule.passed:
                print(f"weapon: {weapons[0].name} can't be assigned to target: {targets[0].target_type}")
                print(rule)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="weapon target assignment", epilog="python -m src.main -i")
    parser.add_argument("--weapon_data", '-iw', default="/home/abolfazl/Documents/weapon-target-assignemt/data/weapon.json")
    parser.add_argument("--target_data", '-it', default="/home/abolfazl/Documents/weapon-target-assignemt/data/target.json")
    parser.add_argument("--compatibility_data", '-ic' , default="/home/abolfazl/Documents/weapon-target-assignemt/data/compatibility.json")
    parser.add_argument("--pk_data", '-ip', default="/home/abolfazl/Documents/weapon-target-assignemt/data/pk.json")
    parser.add_argument("--threshold", '-ithr', default=0.7)
    args = parser.parse_args()
    
    main(args)
