from pydantic import BaseModel
from typing import List


Board = List[List[List[int]]]


class GameState(BaseModel):
    turn: int
    board: Board
    tokens: List[int]
