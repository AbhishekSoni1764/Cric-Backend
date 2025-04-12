from fastapi import APIRouter

router = APIRouter()


@router.get("/players/")
async def list_players():
    return {"message": "Players endpoint (TBD)"}


@router.get("/players/{player_id}")
async def get_player(player_id: str):
    return {"message": f"Player {player_id} endpoint (TBD)"}
