import numpy as np
import argparse
from src.utils.utils import read_config_file
from typing import Dict, List, Any
from src.repositories.compatibility_repository import CompatibilityRepository

def main():
    # conf = read_config_file(args.input)
    
    # # targets: List[Dict[str, Any]] = conf.get("Targets")
    # weapons: Dict[str, Dict[Dict[str, Any]]] = conf.get("Weapons")
    
    # weapons_platforms: list[str] = list(weapons.keys())
    # number_of_weapon_platform: int = len(list(weapons.keys()))
    
    # number_of_each_weapon_platform: Dict[str, int] = {weapon: len(weapons[weapon]) for weapon in weapons}
    

    # parser = argparse.ArgumentParser(description='WEAPON TARGET ASSIGNMENT')
    # parser.add_argument('-i','--input', help='input config file', default="/home/abolfazl/Documents/weapon-target-assignment/configs/scenario1.yaml")
    
    # args = parser.parse_args()
    # main(args)

    repo = CompatibilityRepository(file_path="data/compatibility.json")
    print(repo.load())
if __name__ == "__main__":
    main()