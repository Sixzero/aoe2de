#!/usr/bin/env python3
"""
AOE2 Lobby Watcher - Monitors for lobbies matching a search term (default: "10x")
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Please install websockets: pip install websockets")
    sys.exit(1)

WEBSOCKET_URL = "wss://data.aoe2lobby.com/ws/lobby/"
SEARCH_TERMS = ["10x", "256"]
# SEARCH_TERMS = ["256"]


def play_notification_sound():
    """Play a notification sound."""
    try:
        # Try Linux paplay with a system sound
        sound_paths = [
            "/usr/share/sounds/freedesktop/stereo/complete.oga",
            "/usr/share/sounds/freedesktop/stereo/message.oga",
            "/usr/share/sounds/gnome/default/alerts/drip.ogg",
        ]
        for sound in sound_paths:
            if os.path.exists(sound):
                subprocess.Popen(
                    ["paplay", sound],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
        # Fallback to terminal bell
        print("\a", end="", flush=True)
    except Exception:
        # Last resort: terminal bell
        print("\a", end="", flush=True)


def format_match(match: dict, title_changed: bool = False) -> str:
    """Format a match for display."""
    desc = match.get("description", "No description")
    map_name = match.get("map_name", "Unknown")
    slots_taken = match.get("slots_taken", 0)
    slots_total = match.get("slots_total", 0)
    server = match.get("server", "Unknown")
    speed = match.get("speed", "Unknown")
    host_id = match.get("host_profileid", "Unknown")
    match_id = match.get("matchid", "Unknown")
    steam_lobbyid = match.get("steam_lobbyid", "")

    join_link = f"https://aoe2lobby.com/s/{steam_lobbyid}" if steam_lobbyid and steam_lobbyid != "0" else "N/A"

    header = "TITLE CHANGED" if title_changed else "MATCH FOUND"
    return f"""
{'='*60}
[{datetime.now().strftime('%H:%M:%S')}] {header}!
Title: {desc}
Map: {map_name}
Players: {slots_taken}/{slots_total}
Server: {server}
Speed: {speed}
Host ID: {host_id}
Match ID: {match_id}
Join: {join_link}
{'='*60}
"""


async def watch_lobbies(search_terms: list = SEARCH_TERMS):
    """Connect to WebSocket and watch for matching lobbies."""
    print(f"Connecting to {WEBSOCKET_URL}...")
    print(f"Watching for lobbies containing: {search_terms}")
    print("-" * 60)

    seen_matches = set()
    match_titles = {}  # match_id -> description

    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("Connected! Listening for lobbies...\n")

        async for message in ws:
            try:
                data = json.loads(message)

                # Handle different message formats
                matches = []
                if isinstance(data, dict):
                    # Initial full lobby state: {"lobby_match_all": {...}}
                    if "lobby_match_all" in data:
                        matches = list(data["lobby_match_all"].values())
                    # Updates: {"lobby_match_add": {...}} or {"lobby_match_update": {...}}
                    elif "lobby_match_add" in data:
                        matches = list(data["lobby_match_add"].values())
                    elif "lobby_match_update" in data:
                        matches = list(data["lobby_match_update"].values())
                    elif "matchid" in data:
                        matches = [data]
                elif isinstance(data, list):
                    matches = data

                # Check each match for search terms
                for match in matches:
                    if not isinstance(match, dict):
                        continue

                    match_id = match.get("matchid")
                    description = match.get("description", "")
                    old_desc = match_titles.get(match_id)
                    title_changed = old_desc is not None and old_desc != description

                    if match_id:
                        match_titles[match_id] = description

                    if any(term.lower() in description.lower() for term in search_terms):
                        # Notify if new match OR title changed to contain query
                        is_new = match_id not in seen_matches
                        if match_id and (is_new or title_changed):
                            seen_matches.add(match_id)
                            print(format_match(match, title_changed=not is_new and title_changed))
                            play_notification_sound()

            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")


def main():
    search_terms = sys.argv[1:] if len(sys.argv) > 1 else SEARCH_TERMS

    try:
        asyncio.run(watch_lobbies(search_terms))
    except KeyboardInterrupt:
        print("\nStopped watching.")
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
