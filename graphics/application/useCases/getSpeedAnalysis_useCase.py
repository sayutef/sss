from dataclasses import dataclass
from graphics.domain.repositories.graphics_repository import IGraphics
from typing import List, Dict, Any

@dataclass
class GetSpeedAnalysis:
    def __init__(self, db: IGraphics):
        self.db = db
    
    def run(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        return self.db.get_gps_speed_analysis(user_id, days)