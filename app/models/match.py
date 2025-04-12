from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TeamInMatch(BaseModel):
    team_id: str
    score: Optional[int] = None
    wickets: Optional[int] = None
    overs: Optional[float] = None


class Toss(BaseModel):
    winner_team_id: str
    decision: str  # "bat" or "bowl"


class Result(BaseModel):
    winner_team_id: Optional[str] = None
    margin: Optional[str] = None


class Weather(BaseModel):
    condition: Optional[str] = None
    temperature: Optional[float] = None


class Match(BaseModel):
    match_id: str
    date: datetime
    tournament: Optional[str] = None
    format: str  # "Test", "ODI", "T20"
    venue_id: str
    teams: List[TeamInMatch]
    toss: Optional[Toss] = None
    result: Optional[Result] = None
    weather: Optional[Weather] = None
