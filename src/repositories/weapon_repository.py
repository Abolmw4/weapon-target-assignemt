from src.repositories.base_repository import Repositroy
from src.entities.weapon import Weapon, WeaponStatus, WeapnType
from typing import List

class WeapnRepository(Repositroy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        pass
    
    def load(self) -> List[Weapon]:
        data = super()._load_json()
        weapons = []
        
        for item in data:
            weapon = Weapon(id = item.get("id"), 
                            name = item.get("name"),
                            weapon_type = WeapnType[item.get("type")],
                            positon = item.get("position"),
                            ranges = item.get("ranges"),
                            min_range = item.get("min_range"),
                            max_range = item.get("max_range"),
                            min_altitude = item.get("min_altitude"),
                            max_altitude = item.get("max_altitude"),
                            ammo = item.get("ammo"),
                            status = WeaponStatus[item.get("status")],
                            engagement_channels = item.get("engagement_channels"),
                            used_channels = item.get("used_channels"))
            weapons.append(weapon)
        return weapons
