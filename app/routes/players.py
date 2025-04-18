from fastapi import APIRouter, HTTPException
from typing import Optional
from app.config.database import db
from app.models.player import Player
from app.services.analytics_service import analytics_service
from typing import List

router = APIRouter()


@router.get("/players/", response_model=List[Player])
async def list_players(season: Optional[str] = None, venue_id: Optional[str] = None):
    query = {}
    if season:
        query["created_at"] = {
            "$gte": f"{season}-01-01T00:00:00",
            "$lte": f"{season}-12-31T23:59:59",
        }

    players = await db.db["players"].find(query).to_list(100)
    if not players:
        return []

    if venue_id:
        for player in players:
            player["batting_stats"] = await analytics_service.calculate_batting_stats(
                player["player_id"], venue_id
            )
            player["bowling_stats"] = await analytics_service.calculate_bowling_stats(
                player["player_id"], venue_id
            )

    return [Player(**p) for p in players]


@router.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str, venue_id: Optional[str] = None):
    player = await db.db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player["batting_stats"] = await analytics_service.calculate_batting_stats(
        player_id, venue_id
    )
    player["bowling_stats"] = await analytics_service.calculate_bowling_stats(
        player_id, venue_id
    )

    return Player(**player)
