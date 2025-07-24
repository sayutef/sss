from dataclasses import dataclass
import datetime

@dataclass 
class WeightPeriodsData:
    period_id:      int
    start_hour:     datetime
    end_hour:       datetime
    day_work:       str
    avg_weight:     float
    readings_count: float