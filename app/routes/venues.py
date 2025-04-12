from fastapi import APIRouter, HTTPException
from typing import Optional
from app.config.database import db
from app.models.venue import Venue

router = APIRouter()


@router.get("/venues/", response_model=list[Venue])
async def list_venues(city: Optional[str] = None, country: Optional[str] = None):
    query = {}
    if city:
        query["city"] = city
    if country:
        query["country"] = country

    venues = await db.db["venues"].find(query).to_list(100)
    if not venues:
        return []

    return [Venue(**v) for v in venues]


@router.get("/venues/{venue_id}", response_model=Venue)
async def get_venue(venue_id: str):
    venue = await db.db["venues"].find_one({"venue_id": venue_id})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    return Venue(**venue)
