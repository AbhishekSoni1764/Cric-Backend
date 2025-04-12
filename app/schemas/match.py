from bson import ObjectId
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .player import PyObjectId


class TeamInMatchSchema(BaseModel):
    team_id: PyObjectId
    score: Optional[int] = None
    wickets: Optional[int] = None
    overs: Optional[float] = None


class TossSchema(BaseModel):
    winner_team_id: PyObjectId
    decision: str


class ResultSchema(BaseModel):
    winner_team_id: Optional[PyObjectId] = None
    margin: Optional[str] = None


class WeatherSchema(BaseModel):
    condition: Optional[str] = None
    temperature: Optional[float] = None


class MatchSchema(BaseModel):
    id: PyObjectId
    match_id: str
    date: datetime
    tournament: Optional[str] = None
    format: str
    venue_id: PyObjectId
    teams: List[TeamInMatchSchema]
    toss: Optional[TossSchema] = None
    result: Optional[ResultSchema] = None
    weather: Optional[WeatherSchema] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
