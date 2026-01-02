# AOE2DE Lobby Watcher

Just a fun little project I use in my freetime when playing Age of Empires 2 DE.

Monitors AOE2DE lobbies via WebSocket and notifies when lobbies matching search terms appear or when existing lobby titles change to contain the query.

## Usage

```bash
pip install websockets
python lobby_watcher.py [search_terms...]
```

Default search terms: `10x`, `256`
