import pandas as pd
from datetime import datetime
from bson import ObjectId
from app.config.database import db
from app.services.utils import get_current_timestamp
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_cricsheet_csv(csv_path: str):
    # Ensure CSV exists
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        # Connect to MongoDB
        await db.connect()
        logger.info("MongoDB connection established")

        # Read CSV
        logger.info(f"Reading CSV: {csv_path}")
        df = pd.read_csv(csv_path, low_memory=False)

        # Extract match metadata
        match_info = {
            "match_id": str(df["info__match_type_number"].iloc[0]),
            "date": datetime.strptime(df["info__dates__-"].iloc[0], "%Y-%m-%d"),
            "tournament": df["info__event__name"].iloc[0],
            "format": df["info__match_type"].iloc[0],
            "venue_id": str(ObjectId()),
            "teams": [
                {
                    "team_id": str(ObjectId()),
                    "score": None,
                    "wickets": None,
                    "overs": None,
                },
                {
                    "team_id": str(ObjectId()),
                    "score": None,
                    "wickets": None,
                    "overs": None,
                },
            ],
            "toss": {
                "winner_team_id": None,
                "decision": df["info__toss__decision"].iloc[0],
            },
            "result": {
                "winner_team_id": None,
                "margin": df.get("info__outcome__by__wickets", [None])[0]
                or df.get("info__outcome__by__runs", [None])[0],
            },
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
        }

        # Teams
        teams = df["info__teams"].iloc[0].split(", ")
        team_map = {}
        for i, team_name in enumerate(teams):
            team_doc = {
                "team_id": match_info["teams"][i]["team_id"],
                "name": team_name,
                "country": team_name,
                "created_at": get_current_timestamp(),
                "updated_at": get_current_timestamp(),
            }
            await db.db["teams"].insert_one(team_doc)
            team_map[team_name] = team_doc["team_id"]

        # Update toss and result
        toss_winner = df["info__toss__winner"].iloc[0]
        match_info["toss"]["winner_team_id"] = team_map[toss_winner]
        winner = df.get("info__outcome__winner", [None])[0]
        if winner:
            match_info["result"]["winner_team_id"] = team_map[winner]

        # Venue
        venue_doc = {
            "venue_id": match_info["venue_id"],
            "name": df["info__venue"].iloc[0],
            "city": None,
            "country": (
                "Australia" if "Australia" in df["info__venue"].iloc[0] else None
            ),
            "pitch_type": None,
            "average_scores": {},
            "toss_stats": {},
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
        }
        await db.db["venues"].insert_one(venue_doc)

        # Players
        player_map = {}
        for team in teams:
            players = df[f"info__players__{team}"].iloc[0].split(", ")
            for player_name in players:
                player_id = str(ObjectId())
                player_doc = {
                    "player_id": player_id,
                    "name": player_name,
                    "country": team,
                    "role": None,
                    "batting_style": None,
                    "bowling_style": None,
                    "created_at": get_current_timestamp(),
                    "updated_at": get_current_timestamp(),
                }
                await db.db["players"].insert_one(player_doc)
                player_map[player_name] = player_id

        # Innings and Performances
        innings = df.groupby("innings__team")
        for team_name, team_data in innings:
            team_id = team_map[team_name]
            total_runs = team_data["innings__overs__deliveries__runs__total"].sum()
            wickets = (
                team_data["innings__overs__deliveries__wickets__player_out"]
                .notna()
                .sum()
            )
            balls = team_data["innings__overs__deliveries__batter"].count()
            overs = balls // 6 + (balls % 6) / 10

            for team in match_info["teams"]:
                if team["team_id"] == team_id:
                    team["score"] = int(total_runs)
                    team["wickets"] = int(wickets)
                    team["overs"] = float(overs)

            # Batting Performances
            batters = team_data.groupby("innings__overs__deliveries__batter")
            for batter_name, batter_data in batters:
                player_id = player_map.get(batter_name)
                if not player_id:
                    continue
                runs = batter_data["innings__overs__deliveries__runs__batter"].sum()
                balls = batter_data["innings__overs__deliveries__batter"].count()
                dismissals = (
                    batter_data["innings__overs__deliveries__wickets__player_out"]
                    .notna()
                    .sum()
                )

                performance_doc = {
                    "player_id": player_id,
                    "venue_id": venue_doc["venue_id"],
                    "match_id": match_info["match_id"],
                    "format": "T20",
                    "batting": {
                        "runs": int(runs),
                        "balls_faced": int(balls),
                        "strike_rate": round(
                            (runs / balls * 100) if balls > 0 else 0, 2
                        ),
                        "dismissal": (
                            batter_data[
                                "innings__overs__deliveries__wickets__kind"
                            ].iloc[-1]
                            if dismissals > 0
                            else None
                        ),
                    },
                    "bowling": None,
                    "created_at": get_current_timestamp(),
                    "updated_at": get_current_timestamp(),
                }
                await db.db["playerPerformances"].insert_one(performance_doc)

            # Bowling Performances
            opposing_team = [t for t in teams if t != team_name][0]
            opposing_data = (
                innings.get_group(opposing_team)
                if opposing_team in innings.groups
                else pd.DataFrame()
            )
            if not opposing_data.empty:
                bowlers = opposing_data.groupby("innings__overs__deliveries__bowler")
                for bowler_name, bowler_data in bowlers:
                    player_id = player_map.get(bowler_name)
                    if not player_id:
                        continue
                    runs_conceded = bowler_data[
                        "innings__overs__deliveries__runs__total"
                    ].sum()
                    wickets = (
                        bowler_data["innings__overs__deliveries__wickets__player_out"]
                        .notna()
                        .sum()
                    )
                    balls = bowler_data["innings__overs__deliveries__bowler"].count()
                    overs = balls // 6 + (balls % 6) / 10

                    performance_doc = {
                        "player_id": player_id,
                        "venue_id": venue_doc["venue_id"],
                        "match_id": match_info["match_id"],
                        "format": "T20",
                        "batting": None,
                        "bowling": {
                            "overs": float(overs),
                            "runs_conceded": int(runs_conceded),
                            "wickets": int(wickets),
                            "economy": round(
                                (runs_conceded / overs) if overs > 0 else 0, 2
                            ),
                        },
                        "created_at": get_current_timestamp(),
                        "updated_at": get_current_timestamp(),
                    }
                    await db.db["playerPerformances"].insert_one(performance_doc)

        # Team Performances
        for team_name in teams:
            team_id = team_map[team_name]
            wins = 1 if match_info["result"]["winner_team_id"] == team_id else 0
            team_perf_doc = {
                "team_id": team_id,
                "venue_id": venue_doc["venue_id"],
                "format": "T20",
                "matches_played": 1,
                "wins": wins,
                "losses": 1 - wins,
                "win_percentage": wins * 100,
                "average_score": match_info["teams"][teams.index(team_name)]["score"],
                "created_at": get_current_timestamp(),
                "updated_at": get_current_timestamp(),
            }
            await db.db["teamPerformances"].insert_one(team_perf_doc)

        # Analytics (Collapses)
        collapses = []
        for team_name, team_data in innings:
            overs = team_data.groupby("innings__overs__over")
            for over, over_data in overs:
                wickets = (
                    over_data["innings__overs__deliveries__wickets__player_out"]
                    .notna()
                    .sum()
                )
                if wickets >= 3:
                    collapses.append(
                        {
                            "team_id": team_map[team_name],
                            "overs": float(over),
                            "wickets_lost": int(wickets),
                        }
                    )

        analytics_doc = {
            "match_id": match_info["match_id"],
            "venue_id": venue_doc["venue_id"],
            "collapses": collapses,
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
        }
        await db.db["analytics"].insert_one(analytics_doc)

        # Insert match
        await db.db["matches"].insert_one(match_info)

        logger.info(f"Ingested match {match_info['match_id']}")
        return {
            "matches_ingested": 1,
            "players": len(player_map),
            "teams": len(team_map),
            "venues": 1,
        }

    except Exception as e:
        logger.error(f"Error ingesting CSV {csv_path}: {str(e)}")
        raise

    finally:
        # Close MongoDB connection
        await db.close()


async def ingest_multiple_cricsheet_csvs(csv_folder: str):
    results = {"matches_ingested": 0, "players": 0, "teams": 0, "venues": 0}
    for csv_file in os.listdir(csv_folder):
        if csv_file.endswith(".csv"):
            csv_path = os.path.join(csv_folder, csv_file)
            try:
                result = await ingest_cricsheet_csv(csv_path)
                for key in results:
                    results[key] += result[key]
            except Exception as e:
                logger.error(f"Skipping {csv_path}: {str(e)}")
    return results
