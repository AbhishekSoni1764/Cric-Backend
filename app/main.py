from fastapi import FastAPI
from app.config.database import db
from app.routes import matches, players, teams, venues, analytics

app = FastAPI(title="Cricket Venue Insights Platform")

# Include routers
app.include_router(matches.router, prefix="/api", tags=["Matches"])
app.include_router(players.router, prefix="/api", tags=["Players"])
app.include_router(teams.router, prefix="/api", tags=["Teams"])
app.include_router(venues.router, prefix="/api", tags=["Venues"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


@app.on_event("startup")
async def startup_db():
    await db.connect()


@app.on_event("shutdown")
async def shutdown_db():
    await db.disconnect()


@app.get("/")
async def root():
    return {"message": "Welcome to Cricket Venue Insights Platform"}
