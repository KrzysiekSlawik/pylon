from typing import Any, List, Dict
from common.messages import BadMsgResp, GameOverMsg, GameStateMsg, MoveMsg, Msg
from fastapi import WebSocket
from pydantic import BaseModel
from common.pylos import Board, generate_empty_board, legal_moves
from database.models.user import Users, user_pydantic


class GameSessionState(BaseModel):
    game_id: int
    game_name: str
    players_ids: List[int]
    players_names: List[str]


class GameSession:
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

    async def connect(self, websocket: WebSocket, player_id: int):
        if len(self._players_ids) < 2:
            self._players_ids.append(player_id)
            self._players_names.append(
                await user_pydantic.from_queryset_single(Users.get(id=player_id))
            )
            self._players_connections.append(websocket)
        self._connections.append(websocket)
        if len(self._players_ids >= 2):
            self.__start_game()

    async def __start_game(self):
        await self._broadcast(
            self._state_msg()
        )

    def _state_msg(self) -> GameStateMsg:
        GameStateMsg(
            {
                'turn': self._turn,
                'players_ids': self._players_ids,
                'players_names': self._players_names,
                'tokens': self._tokens,
                'board': self._board,
                'legal': self._legal()
            }
        )

    def _legal(self) -> List[Dict]:
        return legal_moves(self._board, self._turn + 1)

    async def _broadcast(self, msg: Msg):
        for connection in self._connections:
            await connection.send_json(
                msg.to_json()
            )

    async def handle_msg(self, websocket: WebSocket, player_id: int, msg: Msg):
        if type(msg) is MoveMsg:
            if not self._is_authorized_for_move(websocket, player_id):
                websocket.send_json(
                    BadMsgResp(
                        {
                            'detail': "permission denied"
                        }
                    ).to_json()
                )
                return
            move = msg.__dict__.pop('type', None)
            if move not in self._next_legal:
                await websocket.send_json(
                    BadMsgResp(
                        {
                            'detail': "illegal move"
                        }
                    ).to_json()
                )
                self._end_game()
                return
            self._update_state(move)

    async def _end_game(self):
        winner_id = self._turn % 2
        await self._broadcast(
            GameOverMsg(
                {
                    'winner_id': self._players_ids[winner_id],
                    'winner_name': self._players_names[winner_id],
                    'winner_tokens': self._tokens[winner_id]
                }
            )
        )
        winner = await user_pydantic.from_queryset_single(Users.get(id=self._players_ids[winner_id])).dict()
        loser = await user_pydantic.from_queryset_single(Users.get(id=self._players_ids[(winner_id + 1) % 2])).dict()
        winner['wins'] += 1
        loser['loses'] += 1
        await Users.filter(id=self._players_ids[winner_id]).update(**winner)
        await Users.filter(id=self._players_ids[(winner_id + 1) % 2]).update(**loser)
        for connection in self._connections:
            connection.close()

    async def _update_state(self, move: Dict):
        self._turn += 1
        player = self._turn % 2
        cost = 0 if move['cat'] is 'move' else 1
        put_level = move['level']
        put_x = move['x']
        put_y = move['y']
        self._board[put_level][put_x][put_y] = player
        if move['cat'] is 'move':
            take_level = move['take_level']
            take_x = move['take_x']
            take_y = move['take_y']
            self._board[take_level][take_x][take_y] = 0
        self._tokens[player] -= cost
        self._next_legal = self._legal()
        self._broadcast(self._state_msg())
        if len(self._next_legal) == 0:
            self._end_game()

    def _is_authorized_for_move(self, websocket: WebSocket, player_id: int) -> bool:
        current_turn = self._turn + 1
        current_player = current_turn % 2
        return (
            player_id == self._players_ids[current_player] and
            websocket == self._players_connections[current_player]
        )

    @property
    def state(self) -> GameSessionState:
        return GameSessionState(
            game_id=self.id,
            game_name=self.name,
            players_ids=self._players_ids,
            players_names=self._players_names
        )
