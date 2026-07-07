from src.repositories.base_repository import Repositroy
from typing import Dict, List
class CompatibilityRepository(Repositroy):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        pass
    
    def load(self) -> Dict[str, List[str]]:
        data = super()._load_json()
        return data
