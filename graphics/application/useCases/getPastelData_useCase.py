from dataclasses import dataclass
from graphics.domain.repositories.graphics_repository import IGraphics
from typing import List, Dict, Any

@dataclass
class GetPastelData:
    def __init__(self, db: IGraphics):
        self.db = db
    
    def run(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        return self.db.get_waste_types_distribution(user_id, days)