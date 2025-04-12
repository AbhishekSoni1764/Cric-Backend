from pydantic import BaseModel
from typing import Optional


class Team(BaseModel):
    team_id: str
    name: str
    country: Optional[str] = None
