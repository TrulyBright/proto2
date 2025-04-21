from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from game import Game

app = FastAPI()

games: dict[int, Game] = {}

async def streamer(game: Game):
    """게임의 상태가 바뀔 때마다 스트리밍합니다."""
    while True:
        yield game.state()
        await game.state_changed.wait()

@app.get("/{game_id}/watch")
async def watch(game_id: int):
    if game_id not in games:
        return {"error": "Game not found"}
    game = games[game_id]
    return StreamingResponse(streamer(game))

@app.post("/create")
async def create():
    game_id = games.keys()[-1] + 1 if games else 0
    games[game_id] = Game()
    return game_id

@app.post("/{game_id}/join")
async def join(game_id: int, name: str):
    if game_id not in games:
        return {"error": "Game not found"}
    game = games[game_id]

@app.post("/{game_id}/{player_id}/move")
async def move(game_id: int, player_id: int, x: int, y: int):
    if game_id not in games:
        return {"error": "Game not found"}
    game = games[game_id]
    player = game.get_player(player_id)
    if player is None:
        return {"error": "Player not found"}
    if not player.alive:
        return {"error": "Player is not alive"}
    if not game.move(player, x, y):
        return {"error": "Invalid move"}
    return game.state()

@app.post("/{game_id}/{player_id}/build")
async def build(game_id: int, x: int, y: int):
    raise NotImplementedError("Build function is not implemented yet.")

@app.post("/{game_id}/{player_id}/shoot")
async def shoot(game_id: int, x: int, y: int):
    raise NotImplementedError("Shoot function is not implemented yet.")