import unittest
from src.utils.utils import read_config_file

class MyTestCase(unittest.TestCase):
    def test_read_configs(self):
        config = read_config_file("/home/abolfazl/Documents/weapon-target-assignment/configs/scenario1.yaml")
        expected_keys = {"Targets", "Weapons"}
        self.assertEqual(set(config.keys()), expected_keys)
        
        
    def test_check_specefic_weapon_config(self):
        config = read_config_file("/home/abolfazl/Documents/weapon-target-assignment/configs/scenario1.yaml").get("Weapons")
        expected_keys = {"AAA", "samsite", "Jamers", "AirBase"}

        self.assertEqual(set(config.keys()), expected_keys)
    
    def test_get_output(self):
        from src.repositories.base_repository import Repositroy
        from src.repositories.compatibility_repository import CompatibilityRepository
        
        rpo = CompatibilityRepository(file_path="data/compatibility.json")
        print(rpo.load())
        
    
if __name__ == '__main__':
    unittest.main()
