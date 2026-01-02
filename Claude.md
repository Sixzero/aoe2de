# AOE2Lobby API Documentation

## Overview

AOE2Lobby (https://aoe2lobby.com) provides real-time Age of Empires 2 DE lobby information via WebSocket, with additional REST API endpoints for player data.

## WebSocket Endpoints

### Lobby Stream
```
wss://data.aoe2lobby.com/ws/lobby/
```
Real-time stream of all open game lobbies. The server pushes:
- Initial state with all current lobbies on connect
- Updates when lobbies are created, modified, or removed

### Spectate Stream
```
wss://data.aoe2lobby.com/ws/spectate/
```
Real-time stream of games available for spectating.

## REST API Endpoints

Base URL: `https://data.aoe2lobby.com`

### Search Players
```
GET /api/search-players?query={query}&offset={offset}&size={size}
```
Returns: `{items: [...], total: int, offset: int, size: int}`

### Get Players by ID
```
POST /api/players
Content-Type: application/json
Body: {"profileids": [id1, id2, ...]}
```

## Match Data Structure

Each match object from WebSocket contains:

| Field | Description |
|-------|-------------|
| `matchid` | Unique match identifier |
| `description` | Lobby title/description |
| `created_time` | When the lobby was created |
| `mapid` / `map_name` | Map identifier and name |
| `game` | Game type |
| `mode` | Game mode |
| `slots` | Array of player slot objects |
| `slots_taken` | Number of players in lobby |
| `slots_total` | Maximum players allowed |
| `open_slots` | Available slots |
| `host_profileid` | Host's profile ID |
| `server` | Server region |
| `password` | Whether lobby is password protected |
| `steam_lobbyid` | Steam lobby ID for joining |
| `observable` | Whether spectating is allowed |
| `speed` | Game speed setting |
| `population` | Population limit |
| `starting_age` | Starting age |
| `resources` | Resource setting |

## WebSocket Message Format

Messages are JSON. The server sends these message types in order:

1. **Theme config**: `{"themes": {...}, "cuinum": 0}`
2. **Schema/mappings**: `{"schema": {"mapid": {...}, "civilization": {...}, ...}}`
3. **Initial lobby state**: `{"lobby_match_all": {"matchid1": {...}, "matchid2": {...}, ...}}`
4. **Real-time updates**:
   - `{"lobby_match_add": {"matchid": {...}}}` - New lobby created
   - `{"lobby_match_update": {"matchid": {...}}}` - Lobby changed
   - `{"lobby_match_remove": ["matchid1", "matchid2"]}` - Lobbies closed

## Server Codes

From the schema, server IDs map to:
- `0`: brazilsouth
- `1`: australiasoutheast
- `2`: ukwest
- `3`: southeastasia
- `4`: westeurope
- `5`: westus3
- `6`: koreacentral
- `7`: centralindia
- `8`: eastus

## Usage Notes

- The WebSocket connection must stay open to receive updates
- No authentication required for reading lobby data
- The `data.` subdomain is used for API/WebSocket (not the main domain)
