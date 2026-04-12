"""Async Riot API client for League of Legends match lookups."""

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY", "")

REGION_URLS = {
    "europe": "https://europe.api.riotgames.com",
    "americas": "https://americas.api.riotgames.com",
    "asia": "https://asia.api.riotgames.com",
}


def _headers():
    return {"X-Riot-Token": API_KEY}


async def get_puuid(game_name: str, tag_line: str, region: str) -> str:
    base = REGION_URLS[region]
    url = f"{base}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=_headers())
        r.raise_for_status()
        return r.json()["puuid"]


async def get_match_ids(
    puuid: str, region: str, on_progress=None
) -> list[str]:
    base = REGION_URLS[region]
    url = f"{base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    all_ids: list[str] = []
    start = 0
    count = 100
    async with httpx.AsyncClient() as client:
        while True:
            r = await client.get(
                url, headers=_headers(), params={"start": start, "count": count}
            )
            r.raise_for_status()
            batch = r.json()
            if not batch:
                break
            all_ids.extend(batch)
            start += count
            if on_progress:
                await on_progress(len(all_ids))
    return all_ids


async def get_match_detail(match_id: str, region: str) -> dict:
    base = REGION_URLS[region]
    url = f"{base}/lol/match/v5/matches/{match_id}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=_headers())
        r.raise_for_status()
        return r.json()
