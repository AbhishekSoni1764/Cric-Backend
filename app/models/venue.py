from pydantic import BaseModel
from typing import Optional, Dict


class Venue(BaseModel):
    venue_id: str
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    pitch_type: Optional[str] = None
    average_scores: Optional[Dict[str, float]] = (
        None  # e.g., {"test": 300.5, "odi": 250.0}
    )
    toss_stats: Optional[Dict[str, float]] = None  # e.g., {"bat_win_percentage": 55.0}
