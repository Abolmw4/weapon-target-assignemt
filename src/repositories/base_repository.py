from abc import ABC, abstractmethod
from pathlib import Path
import json

class Repositroy(ABC):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = Path(file_path)
        
    def __load_json(self):
        with open(self.file_path, "r", encoding='utf-8') as file:
            return json.load(file)
