from dataclasses import dataclass
import datetime

@dataclass 
class GPSSpeedAnalysis:
    avg_speed: float
    max_speed: float
    min_speed: float
    total_readings: float
    date: datetime