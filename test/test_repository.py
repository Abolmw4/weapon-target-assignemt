import unittest
from src.repositories.base_repository import Repositroy
from src.repositories.pk_repository import PKRepository

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = PKRepository(file_path="/home/abolfazl/Documents/weapon-target-assignemt/data/pk.json")

    def test_load_data(self):
        data = self.repo.load()
        print(data["SAM"]["DRONE"])