#!/usr/bin/env python3
"""Check if two League of Legends accounts have ever played against each other."""

import requests
import sys
import os

API_KEY = "RGAPI-92b495e7-8611-4a58-8f96-87999c793904"
ACCOUNT_BASE = "https://europe.api.riotgames.com"
MATCH_BASE = "https://europe.api.riotgames.com"

HEADERS = {"X-Riot-Token": API_KEY}


def get_puuid(game_name: str, tag_line: str) -> str:
    url = f"{ACCOUNT_BASE}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()["puuid"]


def get_match_ids(puuid: str, start: int = 0, count: int = 100) -> list[str]:
    url = f"{MATCH_BASE}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    all_ids = []
    while True:
        r = requests.get(url, headers=HEADERS, params={"start": start, "count": count})
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        all_ids.extend(batch)
        start += count
        print(f"  Fetched {len(all_ids)} match IDs so far...")
    return all_ids


def get_match_detail(match_id: str) -> dict:
    url = f"{MATCH_BASE}/lol/match/v5/matches/{match_id}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def main():
    if not API_KEY:
        print("Error: Set the RIOT_API_KEY environment variable first.")
        print("  export RIOT_API_KEY='RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'")
        sys.exit(1)

    print("=== League of Legends Matchup Checker ===\n")
    acct1 = input("Enter first account (Name#Tag): ").strip()
    acct2 = input("Enter second account (Name#Tag): ").strip()

    if "#" not in acct1 or "#" not in acct2:
        print("Error: Use the format Name#Tag (e.g. Faker#KR1)")
        sys.exit(1)

    name1, tag1 = acct1.rsplit("#", 1)
    name2, tag2 = acct2.rsplit("#", 1)

    print(f"\nLooking up {name1}#{tag1}...")
    puuid1 = get_puuid(name1, tag1)
    print(f"Looking up {name2}#{tag2}...")
    puuid2 = get_puuid(name2, tag2)

    print(f"\nFetching match history for {name1}#{tag1}...")
    matches1 = set(get_match_ids(puuid1))
    print(f"  Total: {len(matches1)} matches")

    print(f"\nFetching match history for {name2}#{tag2}...")
    matches2 = set(get_match_ids(puuid2))
    print(f"  Total: {len(matches2)} matches")

    common = matches1 & matches2
    if not common:
        print(f"\nNo common matches found between {acct1} and {acct2}.")
        return

    print(f"\nFound {len(common)} common match(es)! Fetching details...\n")

    for match_id in sorted(common):
        detail = get_match_detail(match_id)
        info = detail["info"]
        participants = info["participants"]

        p1 = next((p for p in participants if p["puuid"] == puuid1), None)
        p2 = next((p for p in participants if p["puuid"] == puuid2), None)
        if not p1 or not p2:
            continue

        same_team = p1["teamId"] == p2["teamId"]
        relation = "SAME TEAM" if same_team else "OPPONENTS"

        print(f"Match: {match_id}")
        print(f"  Mode: {info.get('gameMode', '?')}")
        print(f"  {name1}#{tag1}: {p1['championName']} ({p1['kills']}/{p1['deaths']}/{p1['assists']}) - {'Win' if p1['win'] else 'Loss'}")
        print(f"  {name2}#{tag2}: {p2['championName']} ({p2['kills']}/{p2['deaths']}/{p2['assists']}) - {'Win' if p2['win'] else 'Loss'}")
        print(f"  Relationship: {relation}")
        print()


if __name__ == "__main__":
    main()
