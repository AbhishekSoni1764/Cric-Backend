import pandas as pd
from app.config.database import db


async def ingest_match_data(csv_path: str):
    # Read CSV (e.g., from Cricsheet)
    df = pd.read_csv(csv_path)
    # Basic cleaning
    df = df.dropna(subset=["match_id"])
    # Insert into MongoDB
    matches = df.to_dict("records")
    await db.db["matches"].insert_many(matches)
    return len(matches)
