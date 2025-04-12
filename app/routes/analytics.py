from fastapi import APIRouter, HTTPException
from typing import Optional
from bson import ObjectId
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/analytics/collapses/{match_id}")
async def get_collapses(match_id: str):
    collapses = await analytics_service.detect_collapses(match_id)
    if not collapses:
        return []

    return collapses


@router.get("/analytics/form/{player_id}")
async def get_player_form(player_id: str, last_n_matches: Optional[int] = 5):
    form = await analytics_service.get_player_form(player_id, last_n_matches)
    if not form:
        raise HTTPException(status_code=404, detail="No form data found")

    return form
