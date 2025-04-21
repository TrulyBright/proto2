import random
import asyncio

def starting_points(R: int, n: int):
    """한 변의 길이를 주면 인원수에 맞는 시작 좌표를 반환합니다."""
    match n:
        case 3:
            return ((0, 0), (R - 1, R - 1), (R * 2 - 1, R * 2 - 1)) # 정삼각형
        case 4:
            return ((0, 0), (R - 1, 0), (0, R * 2 - 1), (R - 1, R * 2 - 1)) # 직사각형
        case 5:
            return ((0, 0), (R - 1, 0), (R * 2 - 1, R - 1), (R - 1, R * 2 - 1), (0, R * 2 - 1)) # 각 꼭짓점을 채우되 한 곳은 비움
        case _:
            raise ValueError("Invalid number of players")

class Player:
    def __init__(self, index: int, name: str):
        self.index = index
        self.name = name
        self.alive = True
        self.accuracy = random.uniform(0.01, 0.99)
        self.x: int | None = None
        self.y: int | None = None
    
    def json(self):
        return {
            "index": self.index,
            "name": self.name,
            "alive": self.alive,
            "accuracy": self.accuracy,
        }

class Game:
    def __init__(self, R: int = 6):
        """한 변의 길이가 R인 정육각형 게임판을 생성합니다."""
        if R < 3:
            raise ValueError("R must be at least 3")
        self.board = [None for _ in range(R * 2 - 1)]
        for i in range(R):
            self.board[i] = [None for _ in range(R + i)]
            self.board[R * 2 - 2 - i] = [None for _ in range(R + i)]
        self.players: list[Player] = []
        self.R = R
        self.turn = 0
        self.ongoing = False
        self.time = 0
        self.timer: asyncio.Task | None = None
        self.state_changed = asyncio.Event()

    def state(self):
        return {
            "board": [[item.json() if isinstance(item, Player) else item for item in row] for row in self.board],
            "players": [p.json() for p in self.players],
            "turn": self.turn,
            "ongoing": self.ongoing,
            "time": self.time
        }
    
    def broadcast(self):
        """게임 상태가 변경되었음을 모든 리스너들에게 알립니다."""
        self.state_changed.set()
        self.state_changed.clear()
    
    def add_player(self, player: Player):
        """게임에 플레이어를 추가합니다."""
        if len(self.players) >= 6:
            raise ValueError("Maximum number of players reached")
        if player in self.players:
            raise ValueError("Player already in game")
        if player.index != len(self.players):
            raise ValueError("Player index does not match current player count")
        if self.ongoing:
            raise ValueError("Cannot add player to an ongoing game")
        self.players.append(player)
        self.broadcast()
    
    def remove_player(self, index: int):
        """게임에서 플레이어를 제거합니다."""
        if index < 0 or index >= len(self.players):
            raise ValueError("Invalid player index")
        if self.ongoing:
            raise ValueError("Cannot remove player from an ongoing game")
        del self.players[index]
        self.broadcast()
    
    def start(self):
        """게임을 시작합니다."""
        self.turn = 0
        self.ongoing = True
        for i, (x, y) in enumerate(starting_points(self.R, len(self.players))):
            self.board[x][y] = self.players[i]
            self.players[i].x = x
            self.players[i].y = y
        self.give_turn(0)
    
    async def countdown(self, seconds: int):
        """제한시간을 카운트다운합니다."""
        for i in range(seconds, 0, -1):
            self.time = i
            self.broadcast()
            await asyncio.sleep(1)
    
    def give_turn(self, index: int):
        """index번째 플레이어에게 턴을 넘깁니다."""
        if index < 0 or index >= len(self.players):
            raise ValueError("Invalid player index")
        if not self.ongoing:
            raise ValueError("Game is not ongoing")
        self.turn = index
        if self.timer is not None:
            self.timer.cancel()
        self.timer = asyncio.create_task(self.countdown(10))
        self.timer.add_done_callback(self.next_turn)
        self.broadcast()
    
    def next_turn(self, timer: asyncio.Task):
        """타이머를 확인하고 다음 턴으로 넘어갑니다."""
        if not self.ongoing:
            return
        if timer.exception() is not None:
            raise timer.exception()
        if timer.done() and not timer.cancelled():
            self.eliminate(self.players[self.turn])
        self.give_turn((self.turn + 1) % len(self.players))
    
    def eliminate(self, player: Player):
        """플레이어를 죽입니다."""
        if not self.ongoing:
            raise ValueError("Game is not ongoing")
        if player.index != self.turn:
            raise ValueError("Not your turn")
        if not player.alive:
            raise ValueError("Player is already dead")
        player.alive = False
        self.board[player.x][player.y] = None
    
    def move(self, player: Player, x: int, y: int):
        """플레이어가 이동합니다."""
        if not self.ongoing:
            raise ValueError("Game is not ongoing")
        if player.index != self.turn:
            raise ValueError("Not your turn")
        if not player.alive:
            raise ValueError("Player is not alive")
        # if not 인접칸: TODO
        #     raise ValueError("Invalid move")
        if self.board[x][y] is not None:
            raise ValueError("Cell already occupied")
        # Move the player
        if player.x is not None and player.y is not None:
            self.board[player.x][player.y] = None
        self.board[x][y] = player
        player.x = x
        player.y = y
        self.timer.cancel()
        self.next_turn(self.timer)
    
    def shoot(self, shooting: Player, target: Player):
        """플레이어가 총을 쏩니다."""
        if not self.ongoing:
            raise ValueError("Game is not ongoing")
        if target.index == self.turn:
            raise ValueError("Cannot shoot yourself")
        if not target.alive:
            raise ValueError("Target is not alive")
        if random.random() > shooting.accuracy:
            return False
        self.eliminate(target)
        self.timer.cancel()
        self.next_turn(self.timer)