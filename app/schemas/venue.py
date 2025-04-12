from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, Dict
from .player import PyObjectId


class VenueSchema(BaseModel):
    id: PyObjectId
    venue_id: str
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    pitch_type: Optional[str] = None
    average_scores: Optional[Dict[str, float]] = None
    toss_stats: Optional[Dict[str, float]] = None
    created_at: str
    updated_at: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
