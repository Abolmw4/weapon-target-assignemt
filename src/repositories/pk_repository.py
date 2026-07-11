from src.repositories.base_repository import Repositroy
from typing import Dict, Any
class PKRepository(Repositroy):
    def __init__(self, file_path):
        super().__init__(file_path)
        pass
    
    def load(self) -> Dict[str, Any]:
        data = super()._load_json()
        return data
