"""Async Riot API client for League of Legends match lookups."""

import os
from typing import Any

import httpx
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
    base = REGION_URLS[region]
    url = f"{base}/lol/match/v5/matches/{match_id}"
    return await _get_json(url, client=client)
