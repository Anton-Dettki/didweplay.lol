"""FastAPI backend for LoL Matchup Checker."""

import asyncio
import json
import os

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from riot_api import API_KEY, get_match_detail, get_match_ids, get_puuid

REQUEST_TIMEOUT = httpx.Timeout(30.0)
MATCH_SCAN_BATCH_SIZE = 5


def get_allowed_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def parse_riot_id(player: str) -> tuple[str, str] | None:
    if "#" not in player:
        return None

    name, tag = player.rsplit("#", 1)
    name = name.strip()
    tag = tag.strip()
    if not name or not tag:
        return None

    return name, tag


def player_label(name: str, tag: str) -> str:
    return f"{name}#{tag}" if tag else name


def empty_matchup_result(
    name1: str,
    tag1: str,
    puuid1: str | None,
    name2: str,
    tag2: str,
    puuid2: str | None,
) -> dict:
    return {
        "player1": {"name": name1, "tag": tag1, "puuid": puuid1},
        "player2": {"name": name2, "tag": tag2, "puuid": puuid2},
        "total_common": 0,
        "stats": {
            "same_team": 0,
            "opponents": 0,
            "player1_wins": 0,
            "player2_wins": 0,
        },
        "matches": [],
    }


def extract_participant_identity(participant: dict) -> tuple[str, str]:
    name = (
        participant.get("riotIdGameName")
        or participant.get("summonerName")
        or participant.get("puuid")
        or "Unknown Player"
    )
    tag = participant.get("riotIdTagline") or ""
    return str(name), str(tag)


async def safe_get_match_detail(
    match_id: str,
    region: str,
    client: httpx.AsyncClient,
) -> dict | None:
    try:
        return await get_match_detail(match_id, region, client=client)
    except httpx.HTTPStatusError:
        return None


async def stream_matchup_result(
    *,
    region: str,
    player1_name: str,
    player1_tag: str,
    player2_name: str,
    player2_tag: str,
    player1_puuid: str | None = None,
    player2_puuid: str | None = None,
):
    try:
        if not API_KEY:
            yield sse_event({"type": "error", "message": "RIOT_API_KEY not configured on server"})
            return

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            if not player1_puuid:
                yield sse_event({"type": "progress", "message": f"Looking up {player_label(player1_name, player1_tag)}..."})
                try:
                    player1_puuid = await get_puuid(player1_name, player1_tag, region, client=client)
                except httpx.HTTPStatusError as exc:
                    yield sse_event({
                        "type": "error",
                        "message": f"Could not find player {player_label(player1_name, player1_tag)}: {exc.response.status_code}",
                    })
                    return

            if not player2_puuid:
                yield sse_event({"type": "progress", "message": f"Looking up {player_label(player2_name, player2_tag)}..."})
                try:
                    player2_puuid = await get_puuid(player2_name, player2_tag, region, client=client)
                except httpx.HTTPStatusError as exc:
                    yield sse_event({
                        "type": "error",
                        "message": f"Could not find player {player_label(player2_name, player2_tag)}: {exc.response.status_code}",
                    })
                    return

            yield sse_event({
                "type": "progress",
                "message": f"Fetching match history for {player_label(player1_name, player1_tag)}...",
            })
            matches1 = set(await get_match_ids(player1_puuid, region, client=client))
            yield sse_event({
                "type": "progress",
                "message": f"Found {len(matches1)} matches for {player_label(player1_name, player1_tag)}",
            })

            yield sse_event({
                "type": "progress",
                "message": f"Fetching match history for {player_label(player2_name, player2_tag)}...",
            })
            matches2 = set(await get_match_ids(player2_puuid, region, client=client))
            yield sse_event({
                "type": "progress",
                "message": f"Found {len(matches2)} matches for {player_label(player2_name, player2_tag)}",
            })

            common = matches1 & matches2
            if not common:
                yield sse_event({
                    "type": "result",
                    "data": empty_matchup_result(
                        player1_name,
                        player1_tag,
                        player1_puuid,
                        player2_name,
                        player2_tag,
                        player2_puuid,
                    ),
                })
                return

            yield sse_event({
                "type": "progress",
                "message": f"Found {len(common)} common match(es). Fetching details...",
            })

            match_details = []
            same_team_count = 0
            opponent_count = 0
            p1_wins = 0
            p2_wins = 0
            game_modes = set()

            for index, match_id in enumerate(sorted(common), start=1):
                yield sse_event({
                    "type": "progress",
                    "message": f"Fetching common match {index}/{len(common)}...",
                })

                detail = await safe_get_match_detail(match_id, region, client)
                if detail is None:
                    continue

                info = detail.get("info", {})
                participants = info.get("participants", [])

                p1 = next((participant for participant in participants if participant.get("puuid") == player1_puuid), None)
                p2 = next((participant for participant in participants if participant.get("puuid") == player2_puuid), None)
                if not p1 or not p2:
                    continue

                same_team = p1.get("teamId") == p2.get("teamId")
                if same_team:
                    same_team_count += 1
                else:
                    opponent_count += 1

                if p1.get("win"):
                    p1_wins += 1
                if p2.get("win"):
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
                        "champion": p1.get("championName", "Unknown"),
                        "kills": p1.get("kills", 0),
                        "deaths": p1.get("deaths", 0),
                        "assists": p1.get("assists", 0),
                        "win": p1.get("win", False),
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
                        "champion": p2.get("championName", "Unknown"),
                        "kills": p2.get("kills", 0),
                        "deaths": p2.get("deaths", 0),
                        "assists": p2.get("assists", 0),
                        "win": p2.get("win", False),
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
                    "player1": {"name": player1_name, "tag": player1_tag, "puuid": player1_puuid},
                    "player2": {"name": player2_name, "tag": player2_tag, "puuid": player2_puuid},
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
    except Exception as exc:
        yield sse_event({"type": "error", "message": str(exc)})


@app.get("/api/check")
async def check_matchup(
    player1: str = Query(..., description="Riot ID as Name#Tag"),
    player2: str = Query(..., description="Riot ID as Name#Tag"),
    region: str = Query("europe", description="Routing region"),
):
    parsed_player1 = parse_riot_id(player1)
    parsed_player2 = parse_riot_id(player2)
    if not parsed_player1 or not parsed_player2:
        async def invalid_stream():
            yield sse_event({"type": "error", "message": "Use the format Name#Tag"})

        return StreamingResponse(invalid_stream(), media_type="text/event-stream")

    name1, tag1 = parsed_player1
    name2, tag2 = parsed_player2
    return StreamingResponse(
        stream_matchup_result(
            region=region,
            player1_name=name1,
            player1_tag=tag1,
            player2_name=name2,
            player2_tag=tag2,
        ),
        media_type="text/event-stream",
    )


@app.get("/api/check-pair")
async def check_matchup_pair(
    player1_name: str = Query(..., description="Display name for player 1"),
    player1_tag: str = Query("", description="Tag line for player 1"),
    player1_puuid: str = Query(..., description="PUUID for player 1"),
    player2_name: str = Query(..., description="Display name for player 2"),
    player2_tag: str = Query("", description="Tag line for player 2"),
    player2_puuid: str = Query(..., description="PUUID for player 2"),
    region: str = Query("europe", description="Routing region"),
):
    return StreamingResponse(
        stream_matchup_result(
            region=region,
            player1_name=player1_name.strip(),
            player1_tag=player1_tag.strip(),
            player1_puuid=player1_puuid.strip(),
            player2_name=player2_name.strip(),
            player2_tag=player2_tag.strip(),
            player2_puuid=player2_puuid.strip(),
        ),
        media_type="text/event-stream",
    )


@app.get("/api/repeat-teammates")
async def repeat_teammates(
    player: str = Query(..., description="Riot ID as Name#Tag"),
    region: str = Query("europe", description="Routing region"),
):
    async def stream():
        try:
            if not API_KEY:
                yield sse_event({"type": "error", "message": "RIOT_API_KEY not configured on server"})
                return

            parsed_player = parse_riot_id(player)
            if not parsed_player:
                yield sse_event({"type": "error", "message": "Use the format Name#Tag"})
                return

            name, tag = parsed_player

            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                yield sse_event({"type": "progress", "message": f"Looking up {player_label(name, tag)}..."})
                try:
                    puuid = await get_puuid(name, tag, region, client=client)
                except httpx.HTTPStatusError as exc:
                    yield sse_event({
                        "type": "error",
                        "message": f"Could not find player {player_label(name, tag)}: {exc.response.status_code}",
                    })
                    return

                yield sse_event({"type": "progress", "message": f"Fetching match history for {player_label(name, tag)}..."})
                match_ids = await get_match_ids(puuid, region, client=client)
                if not match_ids:
                    yield sse_event({
                        "type": "result",
                        "data": {
                            "player": {"name": name, "tag": tag, "puuid": puuid},
                            "total_matches_scanned": 0,
                            "total_repeat_teammates": 0,
                            "teammates": [],
                        },
                    })
                    return

                yield sse_event({
                    "type": "progress",
                    "message": f"Scanning {len(match_ids)} matches for repeat teammates...",
                })

                met_players: dict[str, dict[str, object]] = {}
                total_matches = len(match_ids)

                for batch_start in range(0, total_matches, MATCH_SCAN_BATCH_SIZE):
                    batch_ids = match_ids[batch_start:batch_start + MATCH_SCAN_BATCH_SIZE]
                    batch_details = await asyncio.gather(
                        *(safe_get_match_detail(match_id, region, client) for match_id in batch_ids)
                    )

                    for offset, detail in enumerate(batch_details, start=batch_start + 1):
                        yield sse_event({
                            "type": "progress",
                            "message": f"Scanning match {offset}/{total_matches}...",
                        })

                        if detail is None:
                            continue

                        info = detail.get("info", {})
                        participants = info.get("participants", [])
                        current_player = next((participant for participant in participants if participant.get("puuid") == puuid), None)
                        if not current_player:
                            continue

                        player_team_id = current_player.get("teamId")
                        game_mode = info.get("gameMode", "UNKNOWN")
                        timestamp = info.get("gameCreation", 0)

                        for participant in participants:
                            teammate_puuid = participant.get("puuid")
                            if not teammate_puuid or teammate_puuid == puuid:
                                continue

                            met_player = met_players.setdefault(
                                teammate_puuid,
                                {
                                    "puuid": teammate_puuid,
                                    "name": "Unknown Player",
                                    "tag": "",
                                    "games_met": 0,
                                    "games_together": 0,
                                    "opponent_games": 0,
                                    "wins_together": 0,
                                    "last_played": 0,
                                    "game_modes": set(),
                                },
                            )

                            met_player["games_met"] += 1
                            met_player["game_modes"].add(game_mode)

                            if participant.get("teamId") == player_team_id:
                                met_player["games_together"] += 1
                                if participant.get("win"):
                                    met_player["wins_together"] += 1
                            else:
                                met_player["opponent_games"] += 1

                            if timestamp >= met_player["last_played"]:
                                display_name, display_tag = extract_participant_identity(participant)
                                met_player["name"] = display_name
                                met_player["tag"] = display_tag
                                met_player["last_played"] = timestamp

                repeated_teammates = [
                    {
                        "puuid": teammate["puuid"],
                        "name": teammate["name"],
                        "tag": teammate["tag"],
                        "games_met": teammate["games_met"],
                        "games_together": teammate["games_together"],
                        "opponent_games": teammate["opponent_games"],
                        "wins_together": teammate["wins_together"],
                        "last_played": teammate["last_played"],
                        "game_modes": sorted(teammate["game_modes"]),
                    }
                    for teammate in met_players.values()
                    if teammate["games_together"] > 1
                ]
                repeated_teammates.sort(
                    key=lambda teammate: (
                        -teammate["games_together"],
                        -teammate["last_played"],
                        teammate["name"].lower(),
                        teammate["tag"].lower(),
                    )
                )

                yield sse_event({
                    "type": "progress",
                    "message": f"Found {len(repeated_teammates)} repeat teammate(s) for {player_label(name, tag)}.",
                })
                yield sse_event({
                    "type": "result",
                    "data": {
                        "player": {"name": name, "tag": tag, "puuid": puuid},
                        "total_matches_scanned": total_matches,
                        "total_repeat_teammates": len(repeated_teammates),
                        "teammates": repeated_teammates,
                    },
                })
        except Exception as exc:
            yield sse_event({"type": "error", "message": str(exc)})

    return StreamingResponse(stream(), media_type="text/event-stream")
