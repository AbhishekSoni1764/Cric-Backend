from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from app.config.database import db
from app.models.match import Match

router = APIRouter()


@router.get("/matches/", response_model=list[Match])
async def list_matches(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    tournament: Optional[str] = None,
):
    query = {}
    if date_from:
        query["date"] = {"$gte": datetime.fromisoformat(date_from)}
    if date_to:
        query["date"] = query.get("date", {})
        query["date"]["$lte"] = datetime.fromisoformat(date_to)
    if tournament:
        query["tournament"] = tournament

    matches = await db.db["matches"].find(query).to_list(100)
    if not matches:
        return []

    return [Match(**m) for m in matches]


@router.get("/matches/{match_id}", response_model=Match)
async def get_match(match_id: str):
    match = await db.db["matches"].find_one({"match_id": match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return Match(**match)
