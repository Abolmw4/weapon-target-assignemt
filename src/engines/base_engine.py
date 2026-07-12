from abc import ABC, abstractmethod
from typing import List
from src.entities.assignment import Assignment

class BaseEngine(ABC):
    def __init__(self):
        super().__init__()
        pass
    
    @abstractmethod
    def run(self) -> List[Assignment]:
        pass
