from src.entities.target import Target, TargetClass, TargetType
from src.repositories.base_repository import Repositroy
from typing import List



class TargetRepository(Repositroy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        pass
    
    def load(self) -> List[Target]:
        results = []
        data = self.__load_json()
        for item in data:
            result = Target(id=item.get("id"), 
                            target_class = TargetType[item.get("type")],
                            position = item.get("position"),
                            altitude = item.get("altitude"),
                            speed = item.get("speed"),
                            heading = item.get("heading"),
                            value = item.get("value"),
                            priority = item.get("priority"))
            results.append(result)
        return results
