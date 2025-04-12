from pydantic import BaseModel
from typing import Optional


class BattingStats(BaseModel):
    runs: Optional[int] = None
    balls_faced: Optional[int] = None
    strike_rate: Optional[float] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    dismissal: Optional[str] = None


class BowlingStats(BaseModel):
    overs: Optional[float] = None
    runs_conceded: Optional[int] = None
    wickets: Optional[int] = None
    economy: Optional[float] = None


class PlayerPerformance(BaseModel):
    player_id: str
    venue_id: str
    match_id: str
    format: str
    batting: Optional[BattingStats] = None
    bowling: Optional[BowlingStats] = None


class TeamPerformance(BaseModel):
    team_id: str
    venue_id: str
    format: str
    matches_played: int
    wins: int
    losses: int
    win_percentage: float
    average_score: Optional[float] = None
