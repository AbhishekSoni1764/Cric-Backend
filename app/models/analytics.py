from pydantic import BaseModel
from typing import List, Optional


class Collapse(BaseModel):
    team_id: str
    overs: float
    wickets_lost: int


class TurningPoint(BaseModel):
    over: float
    event: str


class PlayerFormTrend(BaseModel):
    player_id: str
    recent_avg: float
    recent_strike_rate: float


class Analytics(BaseModel):
    match_id: str
    venue_id: str
    collapses: Optional[List[Collapse]] = None
    turning_points: Optional[List[TurningPoint]] = None
    player_form_trends: Optional[List[PlayerFormTrend]] = None
