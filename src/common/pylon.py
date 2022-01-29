from pydantic import BaseModel
from typing import List


Board = List[List[List[int]]]


class GameState(BaseModel):
    turn: int
    board: Board
    tokens: List[int]

def empty_game_state_factory()->GameState:
    return GameState(
        turn = 0,
        board=[[[0 for _ in range(0,k)]
                for _ in range(0,k)]
            for k in [4,3,2,1]],
        tokens=[0,0]
    )
