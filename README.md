# Tic-Tac-Toe

Browser-based Tic-Tac-Toe with three play modes, difficulty selection, and online multiplayer.

**Live:** https://tictactoe.tailb97cdb.ts.net

## Features

- **vs Computer** — Easy (random), Medium (blocks/takes wins), or Hard (unbeatable minimax)
- **2 Players** — hot-seat mode on the same device
- **Online Multiplayer** — create a room, share the 6-character code, play from any device
- Score tracking across rounds, confetti on wins, dark UI

## Stack

Single `index.html` (no build step) + Python `aiohttp` server that serves static files and handles WebSocket connections on the same port.

## Running locally

```bash
pip install aiohttp
python3 server.py
# → http://localhost:4600
```

## Deployment (optiplex)

Files live at `/home/optiplex/tictactoe/`, served by `tictactoe.service` on port 4600, exposed via Tailscale Funnel.

```bash
# deploy
git pull
sudo systemctl restart tictactoe.service
```
