from asyncio import sleep
from typing import List, Dict
from common.messages import (
    BadMsgResp,
    GameOverMsg,
    GameStateMsg,
    YourMoveMsg,
    MoveMsg,
    Msg,
)
from fastapi import WebSocket
from pydantic import BaseModel
from common.pylos import Board, generate_empty_board, legal_moves
from server.database.models.user import Users, user_pydantic


class GameSessionState(BaseModel):
    game_id: int
    game_name: str
    players_ids: List[int]
    players_names: List[str]
    is_finished: bool


class GameSession:
    """
    Represents game session
    - **id**: session id (the same as game id)
    - **name**: session name
    """
    def __init__(self, session_id: int, session_name: str) -> None:
        self.id: int = session_id
        self.name: str = session_name
        self._players_ids: List[int] = []
        self._players_names: List[str] = []
        self._players_connections: List[WebSocket] = []
        self._connections: List[WebSocket] = []
        self._turn: int = 0
        self._tokens: List[int] = [15, 15]
        self._board: Board = generate_empty_board()
        self._next_legal = self._legal()
        self._is_finished = False

    async def connect(self, websocket: WebSocket, player_id: int):
        """
        Connect to game session, if game is full (2 players), join as spectator
        - **websocket**: websocket used for connection
        - **player_id**: id of player that connects, if **player_id** == 0 => join as spectator
        """
        await websocket.accept()
        if player_id == 0:
            self._connections.append(websocket)
            return
        if len(self._players_ids) < 2:
            self._players_ids.append(player_id)
            player_db = await user_pydantic.from_queryset_single(
                Users.get(id=player_id)
            )
            self._players_names.append(player_db.dict()["username"])
            self._players_connections.append(websocket)
        self._connections.append(websocket)
        if len(self._players_ids) >= 2:
            await self.__start_game()

    async def disconnect(self, websocket: WebSocket, player_id: int):
        """
        Disconnect from game session, if game is not finished, player that leaves resignes the game
        """
        self._connections.remove(websocket)
        if websocket in self._players_connections:
            winner = 0 if self._players_connections[1] == websocket else 1
            self._players_connections.remove(websocket)
            await self._end_game(winner_override=winner)

    async def __start_game(self):
        await self._broadcast(self._state_msg())
        await self._players_connections[(self._turn + 1) % 2].send_json(
            self._your_move_msg().to_dict()
        )

    def _state_msg(self) -> GameStateMsg:
        """
        Factory for GameStateMsg returning current state
        """
        return GameStateMsg(
            {
                "turn": self._turn,
                "players_ids": self._players_ids,
                "players_names": self._players_names,
                "tokens": self._tokens,
                "board": self._board,
                "legal": self._legal(),
            }
        )

    def _your_move_msg(self) -> YourMoveMsg:
        """
        Factory for YourMoveMsg returning current state
        """
        return YourMoveMsg(
            {
                "turn": self._turn,
                "players_ids": self._players_ids,
                "players_names": self._players_names,
                "tokens": self._tokens,
                "board": self._board,
                "legal": self._legal(),
            }
        )

    def _legal(self) -> List[Dict]:
        """
        legal moves of player that should move now
        """
        if self._tokens[(self._turn + 1) % 2] == 0:
            return []
        return legal_moves(self._board, self._turn + 1)

    async def _broadcast(self, msg: Msg):
        """
        send message to all connected websockets (players and spectators)
        """
        for connection in self._connections:
            await connection.send_json(msg.to_dict())

    async def handle_msg(self, websocket: WebSocket, player_id: int, msg: Msg):
        if type(msg) is MoveMsg:
            if not self._is_authorized_for_move(websocket, player_id):
                await websocket.send_json(
                    BadMsgResp({"detail": "permission denied"}).to_dict()
                )
                return
            msg.__dict__.pop("type", None)
            move = msg.__dict__
            if move not in self._next_legal:
                await websocket.send_json(
                    BadMsgResp({"detail": f"illegal move: {move}"}).to_dict()
                )
                await self._end_game()
                return
            await self._update_state(move)

    async def _end_game(self, winner_override=None):
        if self._is_finished:
            return
        self._is_finished = True
        if winner_override:
            winner_id = winner_override
        else:
            winner_id = self._turn % 2

        await self._broadcast(
            GameOverMsg(
                {
                    "winner_id": self._players_ids[winner_id],
                    "winner_name": self._players_names[winner_id],
                    "winner_tokens": self._tokens[winner_id],
                }
            )
        )
        winner = await user_pydantic.from_queryset_single(
            Users.get(id=self._players_ids[winner_id])
        )
        loser = await user_pydantic.from_queryset_single(
            Users.get(id=self._players_ids[(winner_id + 1) % 2])
        )
        winner = winner.dict()
        winner["wins"] += 1
        winner.pop("id", None)
        loser = loser.dict()
        loser["loses"] += 1
        loser.pop("id", None)
        await Users.filter(id=self._players_ids[winner_id]).update(**winner)
        await Users.filter(id=self._players_ids[(winner_id + 1) % 2]).update(**loser)
        for connection in self._connections:
            await connection.close()

    async def _update_state(self, move: Dict):
        self._turn += 1
        player = self._turn % 2

        if move["cat"] == "put":
            put_level = move["level"]
            put_x = move["x"]
            put_y = move["y"]
            self._board[put_level][put_x][put_y] = player + 1
            self._tokens[player] -= 1
            await sleep(0.5)
            await self._broadcast(self._state_msg())

        if move["cat"] == "move":
            take_level = move["take_level"]
            take_x = move["take_x"]
            take_y = move["take_y"]
            assert self._board[take_level][take_x][take_y] == player + 1
            self._board[take_level][take_x][take_y] = 0
            self._tokens[player] += 1
            await sleep(0.5)
            await self._broadcast(self._state_msg())
            put_level = move["level"]
            put_x = move["x"]
            put_y = move["y"]
            self._board[put_level][put_x][put_y] = player + 1
            self._tokens[player] -= 1
            await sleep(0.5)
            await self._broadcast(self._state_msg())

        if move["cat"] == "square":
            put_level = move["level"]
            put_x = move["x"]
            put_y = move["y"]
            self._board[put_level][put_x][put_y] = player + 1
            self._tokens[player] -= 1
            await sleep(0.5)
            await self._broadcast(self._state_msg())
            take_level = move["take_level"]
            take_x = move["take_x"]
            take_y = move["take_y"]
            assert self._board[take_level][take_x][take_y] == player + 1
            self._board[take_level][take_x][take_y] = 0
            self._tokens[player] += 1
            await sleep(0.5)
            await self._broadcast(self._state_msg())
            if move["take_sq_level"] != -1:
                take_sq_level = move["take_sq_level"]
                take_sq_x = move["take_sq_x"]
                take_sq_y = move["take_sq_y"]
                assert self._board[take_sq_level][take_sq_x][take_sq_y] == player + 1
                self._board[take_sq_level][take_sq_x][take_sq_y] = 0
                self._tokens[player] += 1
                await sleep(0.5)
                await self._broadcast(self._state_msg())

        self._next_legal = self._legal()
        await sleep(0.5)
        await self._broadcast(self._state_msg())
        await self._players_connections[(self._turn + 1) % 2].send_json(
            self._your_move_msg().to_dict()
        )
        if len(self._next_legal) == 0:
            await self._end_game()

    def _is_authorized_for_move(self, websocket: WebSocket, player_id: int) -> bool:
        """
        Check if player is authorized for move, its their turn and
        their websocket corresponds to websocket saved in game session
        """
        current_turn = self._turn + 1
        current_player = current_turn % 2
        return (
            player_id == self._players_ids[current_player]
            and websocket == self._players_connections[current_player]
        )

    @property
    def state(self) -> GameSessionState:
        """
        current game session state
        - **game_id**: ...
        - **game_name**: ...
        - **players_ids**: ...
        - **players_names**: ...
        """
        return GameSessionState(
            game_id=self.id,
            game_name=self.name,
            players_ids=self._players_ids,
            players_names=self._players_names,
            is_finished=self._is_finished
        )
