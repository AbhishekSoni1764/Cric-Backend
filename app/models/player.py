from pydantic import BaseModel
from typing import Optional


class BattingStats(BaseModel):
    average: float
    strike_rate: float
    runs: int


class BowlingStats(BaseModel):
    economy: float
    wickets: int


class Player(BaseModel):
    player_id: str
    name: str
    country: str
    role: Optional[str] = None
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    created_at: str
    updated_at: str
    batting_stats: Optional[BattingStats] = None
    bowling_stats: Optional[BowlingStats] = None
