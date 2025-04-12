from fastapi import APIRouter

router = APIRouter()


@router.get("/matches/")
async def list_matches():
    return {"message": "Matches endpoint (TBD)"}


@router.get("/matches/{match_id}")
async def get_match(match_id: str):
    return {"message": f"Match {match_id} endpoint (TBD)"}
