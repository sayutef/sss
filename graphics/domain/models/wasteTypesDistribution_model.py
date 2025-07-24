from dataclasses import dataclass

@dataclass
class WasteTypesDistribution: 
    waste_type:   int
    count:        int
    total_amount: int