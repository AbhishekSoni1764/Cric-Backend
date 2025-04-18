import pandas as pd
import os
from datetime import datetime
from bson import ObjectId
from app.config.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_cricsheet_csv(csv_path: str):
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        # Connect to MongoDB
        await db.connect()
        logger.info("MongoDB connection established")

        # Read CSV
        logger.info(f"Reading CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        matches_ingested = 0
        players_ingested = 0
        teams_ingested = 0
        venues_ingested = 0

        for _, row in df.iterrows():
            try:
                match_id = str(row["info__match_type_number"])
                team_map = {}

                # Teams
                teams = [row["info__teams__001"], row["info__teams__002"]]
                teams = [
                    str(t).strip() for t in teams if pd.notna(t)
                ]  # Normalize team names
                logger.info(f"Processing teams: {teams}")
                for team_name in teams:
                    team_id = str(ObjectId())
                    team_doc = {
                        "team_id": team_id,
                        "name": team_name,
                        "country": team_name,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                    await db.db["teams"].insert_one(team_doc)
                    team_map[team_name] = team_id
                    teams_ingested += 1

                # Venue
                venue_id = str(ObjectId())
                venue_doc = {
                    "venue_id": venue_id,
                    "name": row["info__venue"],
                    "city": None,
                    "country": None,
                    "pitch_type": None,
                    "average_scores": {},
                    "toss_stats": {},
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                await db.db["venues"].insert_one(venue_doc)
                venues_ingested += 1

                # Players
                player_map = {}
                for team in teams:
                    players_key = f"info__players__{team}"
                    if players_key in row and pd.notna(row[players_key]):
                        players = row[players_key].split(",")
                        players = [p.strip() for p in players]
                        for player_name in players:
                            player_id = str(ObjectId())
                            player_doc = {
                                "player_id": player_id,
                                "name": player_name,
                                "country": team,
                                "role": None,
                                "batting_style": None,
                                "bowling_style": None,
                                "created_at": datetime.utcnow().isoformat(),
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                            await db.db["players"].insert_one(player_doc)
                            player_map[player_name] = player_id
                            players_ingested += 1

                # Match
                toss_winner = str(row["info__toss__winner"]).strip()
                if toss_winner not in team_map:
                    logger.error(
                        f"Toss winner '{toss_winner}' not in team_map: {team_map}"
                    )
                    continue  # Skip match if toss winner is invalid

                match_info = {
                    "match_id": match_id,
                    "date": datetime.strptime(row["info__dates__001"], "%Y-%m-%d"),
                    "tournament": row["info__event__name"],
                    "format": row["info__match_type"],
                    "venue_id": venue_id,
                    "teams": [
                        {
                            "team_id": team_map[teams[0]],
                            "score": None,
                            "wickets": None,
                            "overs": None,
                        },
                        {
                            "team_id": team_map[teams[1]],
                            "score": None,
                            "wickets": None,
                            "overs": None,
                        },
                    ],
                    "toss": {
                        "winner_team_id": team_map[toss_winner],
                        "decision": row["info__toss__decision"],
                    },
                    "result": {
                        "winner_team_id": team_map.get(
                            row.get("info__outcome__winner")
                        ),
                        "margin": None,
                    },
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                await db.db["matches"].insert_one(match_info)
                matches_ingested += 1
                logger.info(f"Ingested match {match_id}")

            except Exception as e:
                logger.error(f"Error processing row for match {match_id}: {str(e)}")
                continue

        return {
            "matches_ingested": matches_ingested,
            "players": players_ingested,
            "teams": teams_ingested,
            "venues": venues_ingested,
        }

    except Exception as e:
        logger.error(f"Error ingesting CSV {csv_path}: {str(e)}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(ingest_cricsheet_csv("data/cricsheet/t20i_match.csv"))
    print(result)
