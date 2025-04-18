from typing import Optional, List, Dict
from bson import ObjectId
from app.config.database import db
from datetime import datetime


class AnalyticsService:
    async def calculate_batting_stats(
        self, player_id: str, venue_id: Optional[str] = None
    ) -> Dict:
        # Build query
        query = {"batter_id": player_id}
        if venue_id:
            # Get match IDs for the venue
            match_ids = await db.db["matches"].distinct(
                "match_id", {"venue_id": venue_id}
            )
            if not match_ids:
                return {"average": 0.0, "strike_rate": 0.0, "runs": 0}
            query["match_id"] = {"$in": match_ids}

        # Fetch performances (ball-by-ball)
        performances = await db.db["performances"].find(query).to_list(None)
        if not performances:
            return {"average": 0.0, "strike_rate": 0.0, "runs": 0}

        # Aggregate by match to compute per-match stats
        match_stats = {}
        for p in performances:
            match_id = p["match_id"]
            if match_id not in match_stats:
                match_stats[match_id] = {
                    "runs": 0,
                    "balls_faced": 0,
                    "dismissed": False,
                }
            match_stats[match_id]["runs"] += p["runs"]
            match_stats[match_id]["balls_faced"] += 1  # Each performance is one ball
            if p["wickets"]:
                match_stats[match_id][
                    "dismissed"
                ] = True  # Assume one wicket per dismissal

        total_runs = sum(m["runs"] for m in match_stats.values())
        total_balls = sum(m["balls_faced"] for m in match_stats.values())
        dismissals = sum(1 for m in match_stats.values() if m["dismissed"])

        average = total_runs / dismissals if dismissals > 0 else total_runs
        strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0.0

        return {
            "average": round(average, 2),
            "strike_rate": round(strike_rate, 2),
            "runs": total_runs,
        }

    async def calculate_bowling_stats(
        self, player_id: str, venue_id: Optional[str] = None
    ) -> Dict:
        # Build query
        query = {"bowler_id": player_id}
        if venue_id:
            match_ids = await db.db["matches"].distinct(
                "match_id", {"venue_id": venue_id}
            )
            if not match_ids:
                return {"economy": 0.0, "wickets": 0}
            query["match_id"] = {"$in": match_ids}

        # Fetch performances
        performances = await db.db["performances"].find(query).to_list(None)
        if not performances:
            return {"economy": 0.0, "wickets": 0}

        # Aggregate by match
        match_stats = {}
        for p in performances:
            match_id = p["match_id"]
            if match_id not in match_stats:
                match_stats[match_id] = {
                    "runs_conceded": 0,
                    "wickets": 0,
                    "balls_bowled": 0,
                }
            match_stats[match_id]["runs_conceded"] += p["total_runs"]
            match_stats[match_id]["wickets"] += len(p["wickets"])
            match_stats[match_id]["balls_bowled"] += 1  # Each performance is one ball

        total_wickets = sum(m["wickets"] for m in match_stats.values())
        total_runs = sum(m["runs_conceded"] for m in match_stats.values())
        total_balls = sum(m["balls_bowled"] for m in match_stats.values())
        total_overs = total_balls / 6  # Convert balls to overs

        economy = (total_runs / total_overs) if total_overs > 0 else 0.0

        return {"economy": round(economy, 2), "wickets": total_wickets}

    async def detect_collapses(self, match_id: str) -> List[Dict]:
        # Fetch performances for the match, sorted by over
        performances = (
            await db.db["performances"]
            .find({"match_id": match_id})
            .to_list(length=None)
        )
        if not performances:
            return []

        # Group by team and analyze wicket clusters
        collapses = []
        for team_id in set(p["team_id"] for p in performances):
            team_performances = [p for p in performances if p["team_id"] == team_id]
            wickets_by_over = {}
            for p in team_performances:
                over = p["over"]
                if over not in wickets_by_over:
                    wickets_by_over[over] = 0
                wickets_by_over[over] += len(p["wickets"])

            # Detect collapses (e.g., 3+ wickets in 2 consecutive overs)
            for over in sorted(wickets_by_over.keys()):
                current_wickets = wickets_by_over.get(over, 0)
                next_wickets = wickets_by_over.get(over + 1, 0)
                if current_wickets + next_wickets >= 3:
                    collapses.append(
                        {
                            "team_id": str(team_id),
                            "overs": [over, over + 1],
                            "wickets_lost": current_wickets + next_wickets,
                        }
                    )

        return collapses

    async def get_player_form(self, player_id: str, last_n_matches: int = 5) -> Dict:
        # Get recent match IDs for the player
        performances = (
            await db.db["performances"]
            .find({"$or": [{"batter_id": player_id}, {"bowler_id": player_id}]})
            .sort("created_at", -1)
            .to_list(None)
        )

        # Get unique match IDs (limit to last_n_matches)
        match_ids = list(dict.fromkeys(p["match_id"] for p in performances))[
            :last_n_matches
        ]
        if not match_ids:
            return {"recent_avg": 0.0, "recent_strike_rate": 0.0}

        # Fetch batting performances for these matches
        batting_performances = (
            await db.db["performances"]
            .find({"batter_id": player_id, "match_id": {"$in": match_ids}})
            .to_list(None)
        )

        # Aggregate by match
        match_stats = {}
        for p in batting_performances:
            match_id = p["match_id"]
            if match_id not in match_stats:
                match_stats[match_id] = {
                    "runs": 0,
                    "balls_faced": 0,
                    "dismissed": False,
                }
            match_stats[match_id]["runs"] += p["runs"]
            match_stats[match_id]["balls_faced"] += 1
            if p["wickets"]:
                match_stats[match_id]["dismissed"] = True

        total_runs = sum(m["runs"] for m in match_stats.values())
        total_balls = sum(m["balls_faced"] for m in match_stats.values())
        dismissals = sum(1 for m in match_stats.values() if m["dismissed"])

        recent_avg = total_runs / dismissals if dismissals > 0 else total_runs
        recent_strike_rate = (
            (total_runs / total_balls * 100) if total_balls > 0 else 0.0
        )

        return {
            "recent_avg": round(recent_avg, 2),
            "recent_strike_rate": round(recent_strike_rate, 2),
        }


analytics_service = AnalyticsService()
