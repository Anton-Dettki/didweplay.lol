"""Async Riot API client for League of Legends match lookups."""

import json
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY", "")
MATCH_CACHE_DIR = Path(__file__).resolve().parent / ".cache" / "matches"

REGION_URLS = {
    "europe": "https://europe.api.riotgames.com",
    "americas": "https://americas.api.riotgames.com",
    "asia": "https://asia.api.riotgames.com",
}


def _headers():
    return {"X-Riot-Token": API_KEY}


async def _get_json(
    url: str,
    *,
    client: httpx.AsyncClient | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    if client is not None:
        response = await client.get(url, headers=_headers(), params=params)
        response.raise_for_status()
        return response.json()

    async with httpx.AsyncClient() as local_client:
        response = await local_client.get(url, headers=_headers(), params=params)
        response.raise_for_status()
        return response.json()


async def get_puuid(
    game_name: str,
    tag_line: str,
    region: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> str:
    base = REGION_URLS[region]
    url = f"{base}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    data = await _get_json(url, client=client)
    return data["puuid"]


async def get_match_ids(
    puuid: str,
    region: str,
    on_progress=None,
    *,
    client: httpx.AsyncClient | None = None,
) -> list[str]:
    base = REGION_URLS[region]
    url = f"{base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    all_ids: list[str] = []
    start = 0
    count = 100

    async def load_with(active_client: httpx.AsyncClient) -> list[str]:
        nonlocal start
        while True:
            batch = await _get_json(
                url,
                client=active_client,
                params={"start": start, "count": count},
            )
            if not batch:
                break
            all_ids.extend(batch)
            start += count
            if on_progress:
                await on_progress(len(all_ids))
        return all_ids

    if client is not None:
        return await load_with(client)

    async with httpx.AsyncClient() as local_client:
        return await load_with(local_client)


async def get_match_detail(
    match_id: str,
    region: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> dict:
    cache_path = MATCH_CACHE_DIR / region / f"{match_id}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache_path.unlink(missing_ok=True)

    base = REGION_URLS[region]
    url = f"{base}/lol/match/v5/matches/{match_id}"
    detail = await _get_json(url, client=client)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(detail), encoding="utf-8")

    return detail
