from fastapi import APIRouter

router = APIRouter()


@router.get("/teams/{team_id}/performance/")
async def get_team_performance(team_id: str):
    return {"message": f"Team {team_id} performance endpoint (TBD)"}
