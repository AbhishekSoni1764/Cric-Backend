from bson import ObjectId
from pydantic import BaseModel
from typing import Optional
from .player import PyObjectId


class BattingStatsSchema(BaseModel):
    runs: Optional[int] = None
    balls_faced: Optional[int] = None
    strike_rate: Optional[float] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    dismissal: Optional[str] = None


class BowlingStatsSchema(BaseModel):
    overs: Optional[float] = None
    runs_conceded: Optional[int] = None
    wickets: Optional[int] = None
    economy: Optional[float] = None


class PlayerPerformanceSchema(BaseModel):
    id: PyObjectId
    player_id: PyObjectId
    venue_id: PyObjectId
    match_id: PyObjectId
    format: str
    batting: Optional[BattingStatsSchema] = None
    bowling: Optional[BowlingStatsSchema] = None
    created_at: str
    updated_at: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TeamPerformanceSchema(BaseModel):
    id: PyObjectId
    team_id: PyObjectId
    venue_id: PyObjectId
    format: str
    matches_played: int
    wins: int
    losses: int
    win_percentage: float
    average_score: Optional[float] = None
    created_at: str
    updated_at: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
