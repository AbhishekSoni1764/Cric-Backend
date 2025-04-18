from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Team(BaseModel):
    team_id: str
    score: Optional[int] = None
    wickets: Optional[int] = None
    overs: Optional[int] = None


class Toss(BaseModel):
    winner_team_id: Optional[str] = None
    decision: Optional[str] = None


class Margin(BaseModel):
    type: Optional[str] = None  # e.g., 'wickets' or 'runs'
    value: Optional[int] = None  # e.g., 4


class Result(BaseModel):
    winner_team_id: Optional[str] = None
    margin: Optional[Margin] = None


class Match(BaseModel):
    match_id: str
    date: datetime
    tournament: str
    format: str
    venue_id: str
    teams: List[Team]
    toss: Optional[Toss] = None
    result: Optional[Result] = None
    player_of_match: Optional[str] = None
    created_at: str
    updated_at: str
