from fastapi import APIRouter

router = APIRouter()


@router.get("/venues/")
async def list_venues():
    return {"message": "Venues endpoint (TBD)"}


@router.get("/venues/{venue_id}")
async def get_venue(venue_id: str):
    return {"message": f"Venue {venue_id} endpoint (TBD)"}
