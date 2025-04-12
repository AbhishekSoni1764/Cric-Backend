from bson import ObjectId
from pydantic import BaseModel
from typing import List, Optional
from .player import PyObjectId


class CollapseSchema(BaseModel):
    team_id: PyObjectId
    overs: float
    wickets_lost: int


class TurningPointSchema(BaseModel):
    over: float
    event: str


class PlayerFormTrendSchema(BaseModel):
    player_id: PyObjectId
    recent_avg: float
    recent_strike_rate: float


class AnalyticsSchema(BaseModel):
    id: PyObjectId
    match_id: PyObjectId
    venue_id: PyObjectId
    collapses: Optional[List[CollapseSchema]] = None
    turning_points: Optional[List[TurningPointSchema]] = None
    player_form_trends: Optional[List[PlayerFormTrendSchema]] = None
    created_at: str
    updated_at: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
