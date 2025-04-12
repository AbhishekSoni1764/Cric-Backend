from bson import ObjectId
from pydantic import BaseModel
from typing import Optional
from .player import PyObjectId


class TeamSchema(BaseModel):
    id: PyObjectId
    team_id: str
    name: str
    country: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
