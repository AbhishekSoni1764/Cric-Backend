from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models.performance import TeamPerformance
from app.config.database import db

router = APIRouter()


@router.get("/teams/{team_id}/performance/", response_model=TeamPerformance)
async def get_team_performance(team_id: str, venue_id: Optional[str] = None):
    # Validate team exists
    team = await db.db["teams"].find_one({"team_id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Build match query
    match_query = {"teams.team_id": team_id}  # Match where team_id is in teams array
    if venue_id:
        match_query["venue_id"] = venue_id

    # Aggregate match data
    matches = await db.db["matches"].find(match_query).to_list(1000)
    if not matches:
        raise HTTPException(status_code=404, detail="No matches found for team")

    matches_played = len(matches)
    wins = sum(1 for m in matches if m["result"]["winner_team_id"] == team_id)
    losses = matches_played - wins  # Assuming no ties for simplicity
    win_percentage = (wins / matches_played * 100) if matches_played > 0 else 0.0

    # Get format (assume all matches have same format, e.g., T20)
    format_type = matches[0]["format"] if matches else "Unknown"

    performance = {
        "team_id": team_id,
        "team_name": team["name"],
        "venue_id": venue_id,
        "format": format_type,
        "matches_played": matches_played,
        "wins": wins,
        "losses": losses,
        "win_percentage": round(win_percentage, 2),
    }

    return TeamPerformance(**performance)
