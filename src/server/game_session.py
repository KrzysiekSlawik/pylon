from typing import Any, List, Dict
from pydantic import BaseModel
from common.pylon import Board, GameState
from common.resource import Resource


class GameSession:
    def __init__(self, game_id: int) -> None:
        self.game_id = game_id
        self._players = []
        self._turns: Dict[int, Resource] = {}
        self._current_turn_id = 0

    def put_turn(self, turn):
        '''
        puts new turn
        '''
        try:
            self._turns[self._current_turn_id].put(turn)
        except KeyError:
            self._turns[self._current_turn_id] = Resource()
            self._turns[self._current_turn_id].put(turn)
        finally:
            print(f"put {self._current_turn_id}")
            self._current_turn_id += 1

    async def get_turn(self, turn_id: int) -> Any:
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

    def get_turn_nowait(self) -> Any:
        '''
        get last game turn
        '''
        return self._turns[self._current_turn_id - 1].get_nowait()

    async def join_session(self, player_id: int) -> Board:
        if len(self._players) >= 2:
            return None
        self._players.append(player_id)
        if len(self._players) == 2:
            self.put_turn([[[0 for _ in range(0,k)]
                            for _ in range(0,k)]
                           for k in [4,3,2,1]])
        print(f"join_session {self._players}")
        return await self.get_turn(len(self._players) - 1)



class GameSessionState(BaseModel):
    game_id: int
    game_name: str
    players_id: List[int]
    game_state: GameState
