from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from game import Game, Player

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game = Game(6)

async def streamer(game: Game):
    """게임의 상태가 바뀔 때마다 스트리밍합니다."""
    while True:
        yield game.state()
        await game.state_changed.wait()

@app.get("/watch")
async def watch():
    return StreamingResponse(streamer(game))

@app.post("/join")
async def join(name: str):
    """게임에 플레이어를 추가합니다."""
    joining = Player(game.players[-1].index + 1 if game.players else 0, name)
    try:
        game.add_player(joining)
    except ValueError as e:
        return {"error": str(e)}
    return joining.json()

@app.post("/start")
async def start():
    """게임을 시작합니다."""
    if game.ongoing:
        return {"error": "Game is already ongoing"}
    game.start()
    return {"message": "Game started"}
