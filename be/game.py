import json
import random
from urllib.parse import parse_qs, urlparse
from uuid import UUID
import websockets
from websockets import ServerConnection as Conn

R = 6 # 반지름.
board = [[] for _ in range(R * 2 - 1)] # 한 변의 길이가 R인 육각형 게임판.
for i in range(R):
    board[i] = [0 for _ in range(R + i)]
    board[R * 2 - 2 - i] = [0 for _ in range(R + i)]

STARTING = { # 인원에 따른 시작지점
    3: ((0, 0), (R * 2 - 1, R - 1), (0, R * 2 - 1)), # 정삼각형
    4: ((0, 0), (R - 1, 0), (0, R * 2 - 1), (R - 1, R * 2 - 1)), # 직사각형
    5: ((0, 0), (R - 1, 0), (R * 2 - 1, R - 1), (R - 1, R * 2 - 1), (0, R * 2 - 1)), # 각 꼭짓점을 채우되 한 곳은 비움
    6: ((0, 0), (R - 1, 0), (R * 2 - 1, R - 1), (R - 1, R * 2 - 1), (0, R * 2 - 1), (0, R - 1)) # 모든 꼭짓점을 채움
}
online: list[Conn] = list()
players: list[Conn] = list()
positions: dict[Conn, tuple[int, int]] = dict()
accuracy: dict[Conn, float] = dict()
ongoing = False
turn: Conn | None = None

async def handle(ws: Conn):
    global turn
    online.append(ws)
    players.append(ws)
    await ws.send(board)
    query = parse_qs(urlparse(ws.request.path).query)
    if "name" in query:
        name = query["name"][0]
        broadcast_event({"type": "name", "id": ws.id, "name": name})
    else:
        broadcast_event({"type": "name", "id": ws.id, "name": str(ws.id)})
    broadcast_event({"type": "connect", "id": ws.id})
    await ws.send(json.dumps({
        "type": "online",
        "online": [p.id for p in online],
        "players": [p.id for p in players],
        "ongoing": ongoing,
        "turn": turn.id if turn else None,
        "board": board,
        "names": {p.id: p.name for p in online},
    }))
    async for msg in ws:
        cmd = json.loads(msg)
        match cmd["type"]:
            case "start":
                if not ongoing:
                    # 전원 준비 완료. 게임 시작
                    random.shuffle(players)
                    for i, pos in enumerate(STARTING[len(players)]):
                        place(players[i], pos)
                        accuracy[players[i]] = random.random()
                    broadcast_event({"type": "board", "board": board})
                    ongoing = True
                    turn = players[0]
                    broadcast_event({"type": "turn", "turn": turn.id})
            case "move":
                if adjacent(cmd["pos"], positions[ws]) and board[cmd["pos"][0]][cmd["pos"][1]] == 0:
                    clear(positions[ws])
                    place(ws, cmd["pos"])
                    broadcast_event({"type": "board", "board": board})
                    next_turn()
            case "shoot":
                if not isinstance(board[cmd["pos"][0]][cmd["pos"][1]], UUID):
                    continue
                if board[cmd["pos"][0]][cmd["pos"][1]] == ws.id:
                    continue
                if accuracy[ws] < random.random():
                    continue
                for p in players:
                    if board[cmd["pos"][0]][cmd["pos"][1]] == p.id:
                        clear(positions[p])
                        players.remove(p)
                        broadcast_event({"type": "dead", "killing": ws.id, "killed": p.id})
                        break
                broadcast_event(board)
                if len(players) == 1:
                    reset()
                else:
                    next_turn()
            case "wall":
                if adjacent(cmd["pos"], positions[ws]) and board[cmd["pos"][0]][cmd["pos"][1]] == 0:
                    build_wall(cmd["pos"])
                    broadcast_event(board)
                    next_turn()
    online.remove(ws)
    players.remove(ws)
    if ws in positions:
        clear(positions[ws])
    if ws == turn:
        next_turn()
    broadcast_event({"type": "disconnect", "id": ws.id})

def broadcast_event(event: dict):
    websockets.broadcast(online, event)

def next_turn():
    global turn
    turn = players[(players.index(turn) + 1) % len(players)]
    broadcast_event({"type": "turn", "turn": turn.id})

def adjacent(c1: tuple[int, int], c2: tuple[int, int]):
    return True

def place(player: Conn, pos: tuple[int, int]):
    board[pos[0]][pos[1]] = player.id
    positions[player] = pos

def clear(pos: tuple[int, int]):
    board[pos[0]][pos[1]] = 0

def build_wall(pos: tuple[int, int]):
    board[pos[0]][pos[1]] = 1

def reset():
    global online, players, positions, accuracy, ongoing, turn
    online = []
    players = []
    positions = {}
    accuracy = {}
    ongoing = False
    turn = None
    for i in range(len(board)):
        for j in range(len(board[i])):
            board[i][j] = 0