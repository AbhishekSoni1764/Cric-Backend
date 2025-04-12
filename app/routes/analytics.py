from fastapi import APIRouter

router = APIRouter()


@router.get("/analytics/collapses/{match_id}")
async def get_collapses(match_id: str):
    return {"message": f"Collapses for match {match_id} endpoint (TBD)"}


@router.get("/analytics/form/{player_id}")
async def get_player_form(player_id: str):
    return {"message": f"Player form {player_id} endpoint (TBD)"}
