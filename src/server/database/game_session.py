from typing import Any, List, Dict
from pydantic import BaseModel
from common.pylos import Board, GameState, empty_game_state_factory
from common.resource import Resource


class GameSessionState(BaseModel):
    game_id: int
    game_name: str
    players_id: List[int]


class GameSession:
    def __init__(self, session_id: int, session_name: str) -> None:
        self.id = session_id
        self.name = session_name
        self._players = []
        self._turns: Dict[int, Resource] = {}
        self._current_turn_id = 0
        self.put_turn(empty_game_state_factory())

    @property
    def state(self) -> GameSessionState:
        return GameSessionState(
            game_id=self.id,
            game_name=self.name,
            players_id=self._players
        )

    def put_turn(self, turn: GameState):
        '''
        puts new turn
        '''
        try:
            self._turns[self._current_turn_id].put(turn)
        except KeyError:
            self._turns[self._current_turn_id] = Resource()
            self._turns[self._current_turn_id].put(turn)
        finally:
            self._current_turn_id += 1

    async def get_turn(self, turn_id: int) -> GameState:
        '''
        get game turn (blocking until turn exist)
        '''
        if not turn_id:
            turn_id = self._current_turn_id
        try:
            return await self._turns[turn_id].get()
        except KeyError:
            self._turns[turn_id] = Resource()
            return await self._turns[turn_id].get()

    def get_turn_nowait(self) -> GameState:
        '''
        get last game turn
        '''
        return self._turns[self._current_turn_id - 1].get_nowait()

    async def join_session(self, player_id: int) -> Board:
        if len(self._players) >= 2:
            return None
        self._players.append(player_id)
        self.put_turn(empty_game_state_factory())
        return await self.get_turn(len(self._players) - 1)



