from dataclasses import dataclass
import datetime

@dataclass
class DistanceCumulativeData:
    period_id:           int
    distance_traveled:   float
    weight_waste:        float
    start_hour:          datetime
    cumulative_distance: float 