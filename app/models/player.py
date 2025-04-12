from pydantic import BaseModel
from typing import Optional


class Player(BaseModel):
    player_id: str
    name: str
    country: str
    role: Optional[str] = None
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
