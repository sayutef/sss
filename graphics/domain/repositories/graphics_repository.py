from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IGraphics(ABC):
    
    @abstractmethod
    def get_user_prototype_id(self, user_id: int) -> str:
        pass
    
    @abstractmethod
    def get_waste_types_distribution(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_weight_periods_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_distance_cumulative_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_gps_speed_analysis(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        pass