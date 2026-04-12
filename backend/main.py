"""FastAPI backend for LoL Matchup Checker."""

import json
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx

from riot_api import get_puuid, get_match_ids, get_match_detail, API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@app.get("/api/check")
async def check_matchup(
    player1: str = Query(..., description="Riot ID as Name#Tag"),
    player2: str = Query(..., description="Riot ID as Name#Tag"),
    region: str = Query("europe", description="Routing region"),
):
    async def stream():
        try:
            if not API_KEY:
                yield sse_event({"type": "error", "message": "RIOT_API_KEY not configured on server"})
                return

            if "#" not in player1 or "#" not in player2:
                yield sse_event({"type": "error", "message": "Use the format Name#Tag"})
                return

            name1, tag1 = player1.rsplit("#", 1)
            name2, tag2 = player2.rsplit("#", 1)

            # Look up PUUIDs
            yield sse_event({"type": "progress", "message": f"Looking up {name1}#{tag1}..."})
            try:
                puuid1 = await get_puuid(name1, tag1, region)
            except httpx.HTTPStatusError as e:
                yield sse_event({"type": "error", "message": f"Could not find player {name1}#{tag1}: {e.response.status_code}"})
                return

            yield sse_event({"type": "progress", "message": f"Looking up {name2}#{tag2}..."})
            try:
                puuid2 = await get_puuid(name2, tag2, region)
            except httpx.HTTPStatusError as e:
                yield sse_event({"type": "error", "message": f"Could not find player {name2}#{tag2}: {e.response.status_code}"})
                return

            # Fetch match histories
            async def progress1(count):
                pass  # We yield from the main generator below

            yield sse_event({"type": "progress", "message": f"Fetching match history for {name1}#{tag1}..."})
            matches1_list = await get_match_ids(puuid1, region)
            matches1 = set(matches1_list)
            yield sse_event({"type": "progress", "message": f"Found {len(matches1)} matches for {name1}#{tag1}"})

            yield sse_event({"type": "progress", "message": f"Fetching match history for {name2}#{tag2}..."})
            matches2_list = await get_match_ids(puuid2, region)
            matches2 = set(matches2_list)
            yield sse_event({"type": "progress", "message": f"Found {len(matches2)} matches for {name2}#{tag2}"})

            common = matches1 & matches2

            if not common:
                yield sse_event({
                    "type": "result",
                    "data": {
                        "player1": {"name": name1, "tag": tag1},
                        "player2": {"name": name2, "tag": tag2},
                        "total_common": 0,
                        "stats": {"same_team": 0, "opponents": 0, "player1_wins": 0, "player2_wins": 0},
                        "matches": [],
                    },
                })
                return

            yield sse_event({"type": "progress", "message": f"Found {len(common)} common match(es)! Fetching details..."})

            match_details = []
            same_team_count = 0
            opponent_count = 0
            p1_wins = 0
            p2_wins = 0
            game_modes = set()

            for i, match_id in enumerate(sorted(common)):
                yield sse_event({"type": "progress", "message": f"Fetching match {i + 1}/{len(common)}..."})
                try:
                    detail = await get_match_detail(match_id, region)
                except httpx.HTTPStatusError:
                    continue

                info = detail["info"]
                participants = info["participants"]

                p1 = next((p for p in participants if p["puuid"] == puuid1), None)
                p2 = next((p for p in participants if p["puuid"] == puuid2), None)
                if not p1 or not p2:
                    continue

                same_team = p1["teamId"] == p2["teamId"]
                if same_team:
                    same_team_count += 1
                else:
                    opponent_count += 1

                if p1["win"]:
                    p1_wins += 1
                if p2["win"]:
                    p2_wins += 1

                game_mode = info.get("gameMode", "UNKNOWN")
                game_modes.add(game_mode)

                match_details.append({
                    "match_id": match_id,
                    "game_mode": game_mode,
                    "game_type": info.get("gameType", "MATCHED_GAME"),
                    "game_version": info.get("gameVersion", ""),
                    "platform_id": info.get("platformId", match_id.split("_", 1)[0]),
                    "queue_id": info.get("queueId", 0),
                    "map_id": info.get("mapId", 0),
                    "timestamp": info.get("gameCreation", 0),
                    "duration": info.get("gameDuration", 0),
                    "player1": {
                        "champion": p1["championName"],
                        "kills": p1["kills"],
                        "deaths": p1["deaths"],
                        "assists": p1["assists"],
                        "win": p1["win"],
                        "position": (
                            p1.get("individualPosition")
                            or p1.get("teamPosition")
                            or p1.get("lane")
                            or "UNKNOWN"
                        ),
                        "damage": p1.get("totalDamageDealtToChampions", 0),
                        "cs": p1.get("totalMinionsKilled", 0) + p1.get("neutralMinionsKilled", 0),
                        "vision_score": p1.get("visionScore", 0),
                        "gold_earned": p1.get("goldEarned", 0),
                        "level": p1.get("champLevel", 0),
                    },
                    "player2": {
                        "champion": p2["championName"],
                        "kills": p2["kills"],
                        "deaths": p2["deaths"],
                        "assists": p2["assists"],
                        "win": p2["win"],
                        "position": (
                            p2.get("individualPosition")
                            or p2.get("teamPosition")
                            or p2.get("lane")
                            or "UNKNOWN"
                        ),
                        "damage": p2.get("totalDamageDealtToChampions", 0),
                        "cs": p2.get("totalMinionsKilled", 0) + p2.get("neutralMinionsKilled", 0),
                        "vision_score": p2.get("visionScore", 0),
                        "gold_earned": p2.get("goldEarned", 0),
                        "level": p2.get("champLevel", 0),
                    },
                    "same_team": same_team,
                })

            yield sse_event({
                "type": "result",
                "data": {
                    "player1": {"name": name1, "tag": tag1},
                    "player2": {"name": name2, "tag": tag2},
                    "total_common": len(match_details),
                    "stats": {
                        "same_team": same_team_count,
                        "opponents": opponent_count,
                        "player1_wins": p1_wins,
                        "player2_wins": p2_wins,
                    },
                    "matches": match_details,
                    "filters": {"game_modes": sorted(game_modes)},
                },
            })

        except Exception as e:
            yield sse_event({"type": "error", "message": str(e)})

    return StreamingResponse(stream(), media_type="text/event-stream")
