from pydantic import BaseModel
from typing import List


Board = List[List[List[int]]]


class GameState(BaseModel):
    game_id: int
    player_id: int  # player id != 0
    endtime: float  # epoch time
    board: Board
