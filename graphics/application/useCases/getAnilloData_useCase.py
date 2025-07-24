from dataclasses import dataclass
from graphics.domain.repositories.graphics_repository import IGraphics
from typing import List, Dict, Any

@dataclass
class GetAnilloData:
    def __init__(self, db: IGraphics):
        self.db = db
    
    def run(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        return self.db.get_weight_periods_data(user_id, days)