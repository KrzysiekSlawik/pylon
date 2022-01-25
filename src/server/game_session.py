from asyncio import Queue
from typing import Any, List, Dict
from pydantic import BaseModel
from common.pylon import Board, GameState


class Resource:
    '''
    object representing resource that could be created in the future
    '''
    def __init__(self) -> None:
        self._resource = Queue()


    def get_nowait(self) -> Any:
        res = self._resource.get_nowait()
        self._resource.put_nowait(res)
        return res


    async def get(self) -> Any:
        res = await self._resource.get()

    def put(self, value: Any):
        self._resource.put_nowait(value)


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

    async def get_turn(self, turn_id: int=None) -> Any:
        '''
        get game turn,
        ---
        if turn_id==None (default) blocks until new turn is added and returns it
        ---
        if turn_id>=current_turn blocks until turn with turn_id is added and returns it
        ---
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
            print(f"join Session with too many players {self._players}")
            return None
        self._players.append(player_id)
        if len(self._players) == 2:
            self.put_turn([[[0 for _ in range(0,k)]
                            for _ in range(0,k)]
                           for k in [4,3,2,1]])
        print(f"join_session {self._players}")
        return await self.get_turn(len(self._players) - 1)



class GameSessionSchema(BaseModel):
    game_id: int
    players_id: List[int]
    game_state: GameState


