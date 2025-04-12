from fastapi import APIRouter, HTTPException
from typing import Optional
from app.config.database import db
from app.models.team import Team
from app.models.performance import TeamPerformance

router = APIRouter()


@router.get("/teams/{team_id}/performance/", response_model=TeamPerformance)
async def get_team_performance(team_id: str, venue_id: Optional[str] = None):
    query = {"team_id": team_id}
    if venue_id:
        query["venue_id"] = venue_id

    performance = await db.db["teamPerformances"].find_one(query)
    if not performance:
        raise HTTPException(status_code=404, detail="Team performance not found")

    team = await db.db["teams"].find_one({"team_id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    performance["team_name"] = team["name"]
    return TeamPerformance(**performance)
