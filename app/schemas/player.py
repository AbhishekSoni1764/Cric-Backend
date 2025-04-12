from bson import ObjectId
from pydantic import BaseModel


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class PlayerSchema(BaseModel):
    id: PyObjectId
    player_id: str
    name: str
    country: str
    role: str | None = None
    batting_style: str | None = None
    bowling_style: str | None = None
    created_at: str
    updated_at: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
