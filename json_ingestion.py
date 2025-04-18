import json
import os
from datetime import datetime
from bson import ObjectId
from app.config.database import db
import logging
import glob
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_cricsheet_json(json_paths: list[str]):
    """
    Ingest multiple Cricsheet JSON files into MongoDB.

    Args:
        json_paths: List of paths to JSON files

    Returns:
        Dict with ingestion statistics
    """
    if not json_paths:
        logger.error("No JSON files provided")
        raise ValueError("No JSON files provided")

    stats = {
        "matches_ingested": 0,
        "players": 0,
        "teams": 0,
        "venues": 0,
        "performances": 0,
    }

    try:
        # Connect to MongoDB
        await db.connect()
        logger.info("MongoDB connection established")

        for json_path in json_paths:
            if not os.path.exists(json_path):
                logger.error(f"JSON file not found: {json_path}")
                continue

            logger.info(f"Processing JSON: {json_path}")
            try:
                # Read JSON
                with open(json_path, "r") as f:
                    data = json.load(f)

                info = data.get("info", {})
                match_id = str(info.get("match_type_number", ObjectId()))

                # Teams
                teams = info.get("teams", [])
                team_map = {}
                for team_name in teams:
                    team_name = team_name.strip()
                    # Check if team exists
                    existing_team = await db.db["teams"].find_one({"name": team_name})
                    if existing_team:
                        team_id = existing_team["team_id"]
                    else:
                        team_id = str(ObjectId())
                        team_doc = {
                            "team_id": team_id,
                            "name": team_name,
                            "country": team_name,  # Using team name as country for simplicity
                            "created_at": datetime.utcnow().isoformat(),
                            "updated_at": datetime.utcnow().isoformat(),
                        }
                        await db.db["teams"].insert_one(team_doc)
                        stats["teams"] += 1
                    team_map[team_name] = team_id

                # Venue
                venue_name = info.get("venue", "Unknown")
                city = info.get("city", "Unknown")
                country = (
                    "Uganda" if city == "Entebbe" else None
                )  # Specific to this match
                existing_venue = await db.db["venues"].find_one({"name": venue_name})
                if existing_venue:
                    venue_id = existing_venue["venue_id"]
                else:
                    venue_id = str(ObjectId())
                    venue_doc = {
                        "venue_id": venue_id,
                        "name": venue_name,
                        "city": city,
                        "country": country,
                        "pitch_type": None,
                        "average_scores": {},
                        "toss_stats": {},
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                    await db.db["venues"].insert_one(venue_doc)
                    stats["venues"] += 1

                # Players
                player_map = {}
                # Identify players who batted or bowled
                batting_players = set()
                bowling_players = set()
                for inning in data.get("innings", []):
                    for over in inning.get("overs", []):
                        for delivery in over.get("deliveries", []):
                            batter = delivery.get("batter", "").strip()
                            bowler = delivery.get("bowler", "").strip()
                            if batter:
                                batting_players.add(batter)
                            if bowler:
                                bowling_players.add(bowler)

                for team in teams:
                    for player_name in info.get("players", {}).get(team, []):
                        player_name = player_name.strip()
                        player_id = (
                            info.get("registry", {})
                            .get("people", {})
                            .get(player_name, str(ObjectId()))
                        )
                        existing_player = await db.db["players"].find_one(
                            {"player_id": player_id}
                        )
                        role = "batsman" if player_name in batting_players else None
                        bowling_role = (
                            "bowler" if player_name in bowling_players else None
                        )
                        if role and bowling_role:
                            role = "all-rounder"
                        elif bowling_role:
                            role = "bowler"
                        if not existing_player:
                            player_doc = {
                                "player_id": player_id,
                                "name": player_name,
                                "country": team,
                                "role": role,
                                "batting_style": "NA",  # Placeholder until specific data is available
                                "bowling_style": "NA",  # Placeholder until specific data is available
                                "created_at": datetime.utcnow().isoformat(),
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                            await db.db["players"].insert_one(player_doc)
                            stats["players"] += 1
                        player_map[player_name] = player_id

                # Calculate team stats from innings
                team_stats = {
                    team: {"score": 0, "wickets": 0, "overs": 0} for team in teams
                }
                for inning in data.get("innings", []):
                    team_name = inning.get("team")
                    if team_name not in team_map:
                        continue
                    total_runs = 0
                    total_wickets = 0
                    overs = len(inning.get("overs", []))
                    for over in inning.get("overs", []):
                        for delivery in over.get("deliveries", []):
                            total_runs += delivery["runs"]["total"]
                            total_wickets += len(delivery.get("wickets", []))
                    team_stats[team_name]["score"] = total_runs
                    team_stats[team_name]["wickets"] = total_wickets
                    team_stats[team_name]["overs"] = overs

                # Match
                toss_winner = info.get("toss", {}).get("winner", "").strip()
                toss_decision = info.get("toss", {}).get("decision")
                winner = info.get("outcome", {}).get("winner")
                margin_type = "runs"  # Specific to this match outcome
                margin_value = info.get("outcome", {}).get("by", {}).get("runs")

                match_doc = {
                    "match_id": match_id,
                    "date": datetime.strptime(
                        info.get("dates", ["1970-01-01"])[0], "%Y-%m-%d"
                    ),
                    "tournament": info.get("event", {}).get("name", "Unknown"),
                    "format": info.get("match_type", "T20"),
                    "match_number": info.get("event", {}).get("match_number"),
                    "gender": info.get("gender", "female"),
                    "season": info.get("season", "Unknown"),
                    "venue_id": venue_id,
                    "teams": [
                        {
                            "team_id": team_map[teams[0]],
                            "score": team_stats[teams[0]]["score"],
                            "wickets": team_stats[teams[0]]["wickets"],
                            "overs": team_stats[teams[0]]["overs"],
                        },
                        {
                            "team_id": team_map[teams[1]],
                            "score": team_stats[teams[1]]["score"],
                            "wickets": team_stats[teams[1]]["wickets"],
                            "overs": team_stats[teams[1]]["overs"],
                        },
                    ],
                    "toss": {
                        "winner_team_id": team_map.get(toss_winner),
                        "decision": toss_decision,
                    },
                    "result": {
                        "winner_team_id": team_map.get(winner),
                        "margin": {"type": margin_type, "value": margin_value},
                    },
                    "player_of_match": player_map.get(
                        info.get("player_of_match", [None])[0]
                    ),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "officials": {
                        "umpires": [
                            player_map.get(u)
                            for u in info.get("officials", {}).get("umpires", [])
                        ],
                        "reserve_umpires": [
                            player_map.get(r)
                            for r in info.get("officials", {}).get(
                                "reserve_umpires", []
                            )
                        ],
                    },
                }

                # Check if match already exists
                existing_match = await db.db["matches"].find_one({"match_id": match_id})
                if existing_match:
                    await db.db["matches"].update_one(
                        {"match_id": match_id}, {"$set": match_doc}
                    )
                else:
                    await db.db["matches"].insert_one(match_doc)
                    stats["matches_ingested"] += 1

                # Performances (ball-by-ball)
                for inning in data.get("innings", []):
                    team_name = inning.get("team")
                    team_id = team_map.get(team_name)
                    if not team_id:
                        continue
                    for over in inning.get("overs", []):
                        for delivery in over.get("deliveries", []):
                            batter = delivery.get("batter", "").strip()
                            bowler = delivery.get("bowler", "").strip()
                            non_striker = delivery.get("non_striker", "").strip()
                            performance_doc = {
                                "match_id": match_id,
                                "team_id": team_id,
                                "batter_id": player_map.get(batter),
                                "bowler_id": player_map.get(bowler),
                                "non_striker_id": player_map.get(non_striker),
                                "over": over.get("over"),
                                "runs": delivery["runs"].get("batter", 0),
                                "extras": delivery.get("extras", {}),
                                "total_runs": delivery["runs"].get("total", 0),
                                "wickets": [
                                    {
                                        "player_out_id": player_map.get(
                                            w.get("player_out")
                                        ),
                                        "kind": w.get("kind"),
                                        "fielders": [
                                            player_map.get(f.get("name"))
                                            for f in w.get("fielders", [])
                                        ],
                                    }
                                    for w in delivery.get("wickets", [])
                                ],
                                "created_at": datetime.utcnow().isoformat(),
                            }
                            await db.db["performances"].insert_one(performance_doc)
                            stats["performances"] += 1

                logger.info(f"Successfully ingested match {match_id}")

            except Exception as e:
                logger.error(f"Error processing JSON {json_path}: {str(e)}")
                continue

        return stats

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise

    finally:
        await db.close()
        logger.info("MongoDB connection closed")


if __name__ == "__main__":
    # Find all JSON files in the directory
    json_files = glob.glob("data/cricsheet/*.json")
    if not json_files:
        logger.error("No JSON files found in data/cricsheet/")
    else:
        result = asyncio.run(ingest_cricsheet_json(json_files))
        logger.info(f"Ingestion complete: {result}")
        print(result)
