from typing import Optional
from bson import ObjectId
from app.config.database import db


class AnalyticsService:
    async def calculate_batting_stats(
        self, player_id: str, venue_id: Optional[str] = None
    ):
        # Placeholder: Query MongoDB for batting stats
        query = {"player_id": ObjectId(player_id)}
        if venue_id:
            query["venue_id"] = ObjectId(venue_id)

        performances = await db.db["playerPerformances"].find(query).to_list(None)
        if not performances:
            return {"average": 0.0, "strike_rate": 0.0, "runs": 0}

        total_runs = sum(
            p["batting"]["runs"]
            for p in performances
            if p.get("batting", {}).get("runs")
        )
        total_balls = sum(
            p["batting"]["balls_faced"]
            for p in performances
            if p.get("batting", {}).get("balls_faced")
        )
        dismissals = sum(
            1 for p in performances if p.get("batting", {}).get("dismissal")
        )

        average = total_runs / dismissals if dismissals > 0 else total_runs
        strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0.0

        return {
            "average": round(average, 2),
            "strike_rate": round(strike_rate, 2),
            "runs": total_runs,
        }

    async def calculate_bowling_stats(
        self, player_id: str, venue_id: Optional[str] = None
    ):
        # Placeholder: Query MongoDB for bowling stats
        query = {"player_id": ObjectId(player_id)}
        if venue_id:
            query["venue_id"] = ObjectId(venue_id)

        performances = await db.db["playerPerformances"].find(query).to_list(None)
        if not performances:
            return {"economy": 0.0, "wickets": 0}

        total_wickets = sum(
            p["bowling"]["wickets"]
            for p in performances
            if p.get("bowling", {}).get("wickets")
        )
        total_overs = sum(
            p["bowling"]["overs"]
            for p in performances
            if p.get("bowling", {}).get("overs")
        )
        total_runs = sum(
            p["bowling"]["runs_conceded"]
            for p in performances
            if p.get("bowling", {}).get("runs_conceded")
        )

        economy = (total_runs / total_overs) if total_overs > 0 else 0.0

        return {"economy": round(economy, 2), "wickets": total_wickets}

    async def detect_collapses(self, match_id: str):
        # Placeholder: Detect batting collapses
        # Assume collapse = 3+ wickets in 5 overs
        analytics = await db.db["analytics"].find_one({"match_id": ObjectId(match_id)})
        if not analytics or not analytics.get("collapses"):
            return []

        return [
            {
                "team_id": str(c["team_id"]),
                "overs": c["overs"],
                "wickets_lost": c["wickets_lost"],
            }
            for c in analytics["collapses"]
        ]

    async def get_player_form(self, player_id: str, last_n_matches: int = 5):
        # Placeholder: Get recent performance trends
        performances = (
            await db.db["playerPerformances"]
            .find({"player_id": ObjectId(player_id)})
            .sort("created_at", -1)
            .limit(last_n_matches)
            .to_list(None)
        )

        if not performances:
            return {"recent_avg": 0.0, "recent_strike_rate": 0.0}

        total_runs = sum(
            p["batting"]["runs"]
            for p in performances
            if p.get("batting", {}).get("runs")
        )
        total_balls = sum(
            p["batting"]["balls_faced"]
            for p in performances
            if p.get("batting", {}).get("balls_faced")
        )
        dismissals = sum(
            1 for p in performances if p.get("batting", {}).get("dismissal")
        )

        recent_avg = total_runs / dismissals if dismissals > 0 else total_runs
        recent_strike_rate = (
            (total_runs / total_balls * 100) if total_balls > 0 else 0.0
        )

        return {
            "recent_avg": round(recent_avg, 2),
            "recent_strike_rate": round(recent_strike_rate, 2),
        }


analytics_service = AnalyticsService()
